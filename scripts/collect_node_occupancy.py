#!/usr/bin/env python3
"""Read-only Linux host occupancy evidence. No GPU allocation or external CLI.

Run on the host, not in a container. Stdlib-only so it can be copied with a
reviewed source snapshot. Output is one admission observation plus exact raw
evidence text; retain raw_evidence.utf8 bytes in the coordinator artifact store.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip(), None
    except OSError as exc:
        return None, type(exc).__name__ + ": " + str(exc)


def _integer(text):
    try:
        value = int(text)
        return value if value >= 0 else None
    except (TypeError, ValueError):
        return None


def _char_id(path):
    result = Path(path).stat()
    return result.st_rdev if stat.S_ISCHR(result.st_mode) else None


def _host_scope(proc_root, confirmed):
    markers = [str(path) for path in (Path("/.dockerenv"), Path("/run/.containerenv")) if path.exists()]
    cgroup, cgroup_error = _read(proc_root / "1/cgroup")
    if cgroup and re.search(r"docker|kubepods|containerd|libpod", cgroup):
        markers.append("pid1-cgroup-indicates-container")
    euid = os.geteuid() if hasattr(os, "geteuid") else None
    return {"confirmed_host_namespace": confirmed, "effective_uid": euid,
            "container_indicators": markers, "pid1_cgroup_error": cgroup_error,
            "complete": confirmed is True and euid == 0 and not markers and cgroup_error is None}


def _scan_processes(proc_root, handles):
    """Match /proc/*/fd character device IDs, not process command-line guesses."""
    holders, errors, device_ids = [], [], {}
    for handle in handles:
        try:
            identity = _char_id(handle)
            if identity is None:
                errors.append("not-a-character-device:" + str(handle))
            else:
                device_ids.setdefault(identity, []).append(str(handle))
        except OSError as exc:
            errors.append("device-stat:" + str(handle) + ":" + type(exc).__name__)
    try:
        processes = sorted((p for p in proc_root.iterdir() if p.name.isdecimal()), key=lambda p: int(p.name))
    except OSError as exc:
        return {"complete": False, "errors": ["proc-list:" + type(exc).__name__], "holders": [], "processes_scanned": 0}
    if not processes:
        errors.append("empty-proc-view")
    for process in processes:
        try:
            descriptors = list((process / "fd").iterdir())
        except FileNotFoundError:
            if process.exists():
                errors.append("fd-directory-missing:" + process.name)
            continue  # otherwise process ended during this observation
        except OSError as exc:
            errors.append("fd-list:" + process.name + ":" + type(exc).__name__)
            continue
        matched = set()
        for descriptor in descriptors:
            try:
                matched.update(device_ids.get(_char_id(descriptor), []))
            except FileNotFoundError:
                continue  # fd was closed or process exited
            except OSError as exc:
                errors.append("fd-stat:" + process.name + ":" + descriptor.name + ":" + type(exc).__name__)
        if matched:
            status, status_error = _read(process / "status")
            comm, comm_error = _read(process / "comm")
            uid_match = re.search(r"^Uid:\s+(\d+)", status or "", re.MULTILINE)
            uid = int(uid_match.group(1)) if uid_match else None
            if uid is None or comm_error or status_error:
                errors.append("holder-identity-unknown:" + process.name)
            holders.append({"pid": int(process.name), "uid": uid, "comm": comm,
                            "handles": sorted(matched)})
    return {"complete": not errors, "errors": errors, "holders": holders, "processes_scanned": len(processes),
            "match_basis": "character-device-st_rdev; filesystem inode and mount namespace may differ"}


def _reservation_view(record, context, node, cards, timestamp, max_age):
    unknown = {name: {"complete": False, "reservations": None} for name in cards}
    if not isinstance(record, dict):
        return unknown, ["reservation-view-not-provided"]
    reasons = []
    if record.get("schema_version") != 1 or record.get("context") != context or record.get("node") != node:
        reasons.append("reservation-scope-mismatch")
    if record.get("coverage_complete") is not True or not isinstance(record.get("basis"), str) or not record["basis"].strip():
        reasons.append("reservation-coverage-or-basis-missing")
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not re.fullmatch(r"[a-f0-9]{64}", x) for x in evidence):
        reasons.append("reservation-evidence-missing")
    try:
        when = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
        if when.tzinfo is None or not 0 <= timestamp - when.timestamp() <= max_age:
            reasons.append("reservation-observation-not-fresh")
    except (ValueError, TypeError, KeyError, AttributeError):
        reasons.append("reservation-observation-time-invalid")
    devices = record.get("devices")
    if not isinstance(devices, dict):
        reasons.append("reservation-devices-missing")
        devices = {}
    for card in cards:
        entries = devices.get(card)
        unknown[card] = {"complete": not reasons and isinstance(entries, list),
                         "reservations": entries if isinstance(entries, list) else None}
    return unknown, reasons


def collect_occupancy(context, node, *, host_scope_confirmed=False, reservations=None,
                      sysfs_root=Path("/sys/class/drm"), proc_root=Path("/proc"), dev_root=Path("/dev"),
                      max_reservation_age_seconds=30, max_collection_seconds=10):
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    raw_devices, errors, handles, mappings = [], [], [], {}
    try:
        entries = sorted(sysfs_root.iterdir(), key=lambda p: p.name)
    except OSError as exc:
        entries = []
        errors.append("sysfs-list:" + type(exc).__name__)
    kfd = dev_root / "kfd"
    if not kfd.exists():
        errors.append("kfd-device-missing")
    else:
        handles.append(kfd)
    for entry in entries:
        if not re.fullmatch(r"card\d+", entry.name):
            continue
        device = entry / "device"
        if not (device / "mem_info_vram_total").exists():
            continue  # non-GPU/display adapter
        values, read_errors = {}, {}
        for field in ("vendor", "device", "gpu_busy_percent", "mem_info_vram_used", "mem_info_vram_total"):
            values[field], problem = _read(device / field)
            if problem:
                read_errors[field] = problem
        try:
            pci = device.resolve(strict=True).name
            nodes = [p.name for p in (device / "drm").iterdir()
                     if re.fullmatch(r"(?:card|renderD)\d+", p.name)]
        except OSError as exc:
            pci, nodes = None, []
            read_errors["device-mapping"] = type(exc).__name__
        selected = [dev_root / "dri" / name for name in nodes]
        if not selected:
            read_errors["device-mapping"] = "No DRM device nodes mapped"
        handles.extend(selected)
        mappings[entry.name] = {str(p) for p in selected}
        raw_devices.append({"card": entry.name, "pci": pci, "values": values,
                            "read_errors": read_errors, "device_nodes": [str(p) for p in selected]})
    # Unmapped render/card nodes can belong to GPUs absent from the sysfs view.
    # Scan their holders too; a partial namespace must never look idle.
    try:
        extras = [p for p in (dev_root / "dri").iterdir() if re.fullmatch(r"(?:card|renderD)\d+", p.name)]
    except OSError as exc:
        extras = []
        errors.append("dri-list:" + type(exc).__name__)
    known = {str(p) for p in handles}
    unmapped = {str(p) for p in extras if str(p) not in known}
    handles.extend(p for p in extras if str(p) in unmapped)
    processes = _scan_processes(proc_root, list(dict.fromkeys(handles)))
    # A successful FD scan is not proof of complete attribution when hardware
    # concurrently reports work with no matching owner. Keep metrics intact so
    # admission still rejects activity, while exposing this evidence conflict.
    unowned_activity = []
    for device in raw_devices:
        busy = _integer(device["values"]["gpu_busy_percent"])
        matching = mappings[device["card"]] | unmapped | {str(kfd)}
        if busy is not None and busy > 0 and not any(
            set(holder["handles"]) & matching for holder in processes["holders"]
        ):
            unowned_activity.append(device["card"])
    processes["unattributed_active_devices"] = unowned_activity
    scope = _host_scope(proc_root, host_scope_confirmed)
    now = datetime.now(timezone.utc)
    duration = time.monotonic() - started
    if duration > max_collection_seconds:
        errors.append("collection-window-too-long")
    booking, booking_errors = _reservation_view(reservations, context, node,
                                                [x["card"] for x in raw_devices], now.timestamp(),
                                                max_reservation_age_seconds)
    raw = {"schema_version": 1, "collector": "linux-sysfs-proc-fd", "node": node, "context": context,
           "started_at": started_at, "observed_at": now.isoformat(), "collection_seconds": duration,
           "host_scope": scope, "devices": raw_devices, "process_scan": processes,
           "unmapped_device_nodes": sorted(unmapped), "reservations": reservations,
           "reservation_errors": booking_errors, "errors": errors}
    raw_text = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    proof = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    observed = []
    for device in raw_devices:
        card = device["card"]
        values = device["values"]
        total, used, utilization = (_integer(values[field]) for field in
                                    ("mem_info_vram_total", "mem_info_vram_used", "gpu_busy_percent"))
        identity = "pci:" + device["pci"] if device["pci"] and re.fullmatch(r"[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]", device["pci"]) else None
        holders = [entry for entry in processes["holders"]
                   if set(entry["handles"]) & (mappings[card] | unmapped | {str(kfd)})]
        metrics_complete = (not device["read_errors"] and identity is not None and total is not None
                            and total > 0 and used is not None and used <= total
                            and utilization is not None and utilization <= 100)
        observed.append({"node": node, "device": card, "identity": identity,
                         "memory_used_bytes": used, "memory_total_bytes": total,
                         "utilization_pct": utilization, "pids": holders,
                         "reservations": booking[card]["reservations"], "evidence": [proof],
                         "coverage": {"device": metrics_complete and not errors,
                                      "processes": scope["complete"] and processes["complete"] and not errors
                                                   and card not in unowned_activity,
                                      "reservations": booking[card]["complete"]}})
    return {"schema_version": 1, "context": context, "observed_at": now.isoformat(), "devices": observed,
            "shared_resources": [], "raw_evidence": {"sha256": proof, "utf8": raw_text},
            "collector": {"kind": "linux-sysfs-proc-fd", "read_only": True,
                          "device_id_kind": "DRM card name; not HIP/ROCR ordinal",
                          "meaning": "No resource reservation. Global KFD or unmapped-device holders conservatively affect every selected GPU. "
                                     "Retain exact raw evidence; reservations and shared NIC activity need separate site evidence."}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--node", required=True, help="Stable node identity used in the task contract")
    parser.add_argument("--host-scope-confirmed", action="store_true", help="Operator verified execution on host PID/device namespaces")
    parser.add_argument("--reservations", type=Path, help="Fresh explicit site reservation-view JSON; absent means unknown")
    parser.add_argument("--max-reservation-age-seconds", type=float, default=30)
    parser.add_argument("--max-collection-seconds", type=float, default=10)
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Collector must run on the Linux host; tests may inject synthetic filesystem fixtures")
    if not args.context.strip() or not args.node.strip():
        parser.error("context and node must be nonempty")
    if not 0 < args.max_reservation_age_seconds <= 300 or not 0 < args.max_collection_seconds <= 60:
        parser.error("Evidence windows must be positive and bounded (reservation <=300s, collection <=60s)")
    try:
        record = json.loads(args.reservations.read_text(encoding="utf-8")) if args.reservations else None
        result = collect_occupancy(args.context, args.node, host_scope_confirmed=args.host_scope_confirmed,
                                   reservations=record, max_reservation_age_seconds=args.max_reservation_age_seconds,
                                   max_collection_seconds=args.max_collection_seconds)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
