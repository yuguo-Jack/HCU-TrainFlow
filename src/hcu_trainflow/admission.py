"""Conservative occupancy evidence checks, separate from health and reservation.

Collectors normalize site-specific tools into this contract. This module does
not run probes, assume that a missing process list is empty, reserve hardware,
or authorize a launch. An observed-idle result still needs site coordination
and an immediate recheck before the operation starts.
"""
from datetime import datetime, timezone
from copy import deepcopy
import math
import re

from .core import FlowError


def _number(value, name, *, minimum=0, maximum=None, integer=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < minimum
            or (maximum is not None and value > maximum)
            or (integer and not isinstance(value, int))):
        raise FlowError("Invalid " + name)
    return value


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise FlowError("Invalid " + name)
    return value


def _instant(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise FlowError("Observation time must be timezone-aware ISO 8601") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FlowError("Observation time must be timezone-aware ISO 8601")
    return parsed.timestamp()


def _evidence(value):
    return (isinstance(value, list) and bool(value)
            and all(isinstance(x, str) and re.fullmatch(r"[a-f0-9]{64}", x) for x in value))


def _key(row):
    return (_text(row.get("node"), "node"), _text(row.get("device"), "device"))


def bound_remote_observation(observation, *, requested_at, received_at, elapsed_seconds):
    """Use a conservative controller-clock bound for a fresh remote probe.

    Call only around a collector executed for this request, never a cached or
    historical sample. The request start is a lower bound on measurement time,
    so it overestimates age rather than making old evidence appear younger.
    Raw remote time and evidence hashes stay intact for clock diagnosis. This
    does not synchronize clocks or establish a site reservation.
    """
    if not isinstance(observation, dict) or "collection_window" in observation:
        raise FlowError("Expected one unnormalized fresh remote observation")
    remote_time = observation.get("observed_at")
    _instant(remote_time)
    start, end = _instant(requested_at), _instant(received_at)
    elapsed = _number(elapsed_seconds, "monotonic collection duration", minimum=0.000001)
    if end < start or abs((end - start) - elapsed) > 0.5:
        raise FlowError("Controller clock changed during collection; recollect evidence")
    result = deepcopy(observation)
    result.update(observed_at=requested_at, timestamp_basis="controller-request-start-bound",
                  source_observed_at=remote_time,
                  collection_window={"requested_at": requested_at, "received_at": received_at,
                                     "elapsed_seconds": elapsed,
                                     "remote_clock_offset_bounds_seconds": [
                                         _instant(remote_time) - end, _instant(remote_time) - start],
                                     "meaning": "Fresh collector executed inside this request; request start conservatively bounds age, not exact event time"})
    return result


def _observation_window(sample):
    """Return conservative controller-clock bounds, or one exact timestamp.

    A request start bounds freshness, but is not the time of the measurement.
    Keep the full interval for quiet-period and sampling-gap decisions.
    """
    stamp = _instant(sample.get("observed_at"))
    basis = sample.get("timestamp_basis")
    if "collection_window" not in sample and basis != "controller-request-start-bound":
        return stamp, stamp
    window = sample.get("collection_window")
    required = {"requested_at", "received_at", "elapsed_seconds",
                "remote_clock_offset_bounds_seconds", "meaning"}
    if (basis != "controller-request-start-bound" or not isinstance(window, dict)
            or set(window) != required):
        raise FlowError("Bounded observation requires a complete collection window")
    start, end = _instant(window["requested_at"]), _instant(window["received_at"])
    elapsed = _number(window["elapsed_seconds"], "monotonic collection duration", minimum=0.000001)
    remote = _instant(sample.get("source_observed_at"))
    offsets = window["remote_clock_offset_bounds_seconds"]
    _text(window["meaning"], "collection window meaning")
    if (end < start or abs((end - start) - elapsed) > 0.5 or stamp != start
            or not isinstance(offsets, list) or len(offsets) != 2
            or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
                   for x in offsets)
            or any(not math.isclose(actual, expected, rel_tol=0, abs_tol=0.000001)
                   for actual, expected in zip(offsets, (remote - end, remote - start)))):
        raise FlowError("Inconsistent bounded observation clocks; recollect evidence")
    return start, end


def assess_occupancy(contract, observations, *, now=None):
    """Check selected devices against consecutive, fresh, fully covered samples.

    ``contract.devices`` contains node/device/identity, a measured idle-memory
    baseline, its explicit tolerance, utilization limit and the basis for those
    limits. Every observation must cover every requested device and shared
    resource. ``coverage`` explicitly covers device/processes/reservations.
    Any PID or reservation is busy even at zero utilization. Unknown or stale
    data is incomplete. Unrelated devices in a sample are not selected.

    Evidence hashes are checked syntactically here. The coordinator must verify
    them against retained raw artifacts and validate the collector's scope.
    """
    if (not isinstance(contract, dict) or type(contract.get("schema_version")) is not int
            or contract.get("schema_version") != 1):
        raise FlowError("Occupancy contract requires schema_version=1")
    context = _text(contract.get("context"), "context")
    expected = contract.get("devices")
    if not isinstance(expected, list) or not expected:
        raise FlowError("Choose explicit devices for occupancy admission")
    required = {}
    for device in expected:
        if not isinstance(device, dict):
            raise FlowError("Invalid required device")
        key = _key(device)
        if key in required:
            raise FlowError("Duplicate required device")
        _text(device.get("identity"), "stable device identity")
        _text(device.get("basis"), "idle-limit basis")
        _number(device.get("idle_memory_bytes"), "idle memory", integer=True)
        _number(device.get("memory_tolerance_bytes"), "memory tolerance", integer=True)
        _number(device.get("max_utilization_pct"), "utilization limit", maximum=100)
        required[key] = device
    maximum_age = _number(contract.get("max_age_seconds", 30), "max_age_seconds", minimum=0.001)
    minimum_samples = _number(contract.get("min_observations", 2), "min_observations", minimum=2, integer=True)
    quiet_period = _number(contract.get("quiet_period_seconds", 10), "quiet_period_seconds", minimum=0.001)
    maximum_gap = _number(contract.get("max_sample_gap_seconds", maximum_age), "max_sample_gap_seconds", minimum=0.001)
    if quiet_period > maximum_age:
        raise FlowError("Quiet period cannot exceed the fresh evidence window")
    shared = contract.get("shared_resources", [])
    if not isinstance(shared, list) or any(not isinstance(x, str) or not x.strip() for x in shared) or len(shared) != len(set(shared)):
        raise FlowError("Shared resources must be distinct nonempty IDs")
    if not isinstance(observations, list):
        raise FlowError("Observations must be an array")
    current = _instant(now) if now is not None else datetime.now(timezone.utc).timestamp()
    problems, intervals, proofs = [], [], set()
    rows = {key: {"node": key[0], "device": key[1], "status": "observed-idle", "reasons": []}
            for key in required}
    shared_rows = {resource: {"id": resource, "status": "observed-idle", "reasons": []} for resource in shared}

    def mark(row, reason, *, busy=False):
        if reason not in row["reasons"]:
            row["reasons"].append(reason)
        if busy:
            row["status"] = "busy"
        elif row["status"] != "busy":
            row["status"] = "incomplete"

    for sample in observations:
        if not isinstance(sample, dict):
            raise FlowError("Invalid occupancy observation")
        start, end = _observation_window(sample)
        intervals.append((start, end))
        common = []
        if sample.get("context") != context:
            common.append("context-mismatch")
        if end > current:
            common.append("observation-from-future")
        elif current - start > maximum_age:
            common.append("stale-observation")
        samples = sample.get("devices", [])
        if not isinstance(samples, list) or any(not isinstance(x, dict) for x in samples):
            raise FlowError("Invalid device observations")
        found = {}
        for device in samples:
            key = _key(device)
            if key in found:
                raise FlowError("Duplicate device within an observation")
            found[key] = device
        for key, expectation in required.items():
            row = rows[key]
            for reason in common:
                mark(row, reason)
            device = found.get(key)
            if device is None:
                mark(row, "device-not-observed")
                continue
            if device.get("identity") != expectation["identity"]:
                mark(row, "device-identity-mismatch")
            coverage = device.get("coverage", {})
            if not isinstance(coverage, dict):
                coverage = {}
            for dimension in ("device", "processes", "reservations"):
                if coverage.get(dimension) is not True:
                    mark(row, dimension + "-coverage-unknown")
            if not _evidence(device.get("evidence")):
                mark(row, "raw-evidence-missing")
            else:
                proofs.update(device["evidence"])
            for field in ("pids", "reservations"):
                values = device.get(field)
                if not isinstance(values, list):
                    mark(row, field + "-unknown")
                elif values:
                    mark(row, "process-present" if field == "pids" else "reserved-by-site", busy=True)
            try:
                memory = _number(device.get("memory_used_bytes"), "measured memory", integer=True)
                if memory > expectation["idle_memory_bytes"] + expectation["memory_tolerance_bytes"]:
                    mark(row, "memory-above-idle-envelope", busy=True)
            except FlowError:
                mark(row, "memory-unknown")
            try:
                utilization = _number(device.get("utilization_pct"), "measured utilization", maximum=100)
                if utilization > expectation["max_utilization_pct"]:
                    mark(row, "device-active", busy=True)
            except FlowError:
                mark(row, "utilization-unknown")
        measured_shared = sample.get("shared_resources", [])
        if not isinstance(measured_shared, list) or any(not isinstance(x, dict) for x in measured_shared):
            raise FlowError("Invalid shared-resource observations")
        seen_shared = {}
        for resource in measured_shared:
            name = _text(resource.get("id"), "shared resource ID")
            if name in seen_shared:
                raise FlowError("Duplicate shared resource within an observation")
            seen_shared[name] = resource
        for name, row in shared_rows.items():
            for reason in common:
                mark(row, reason)
            resource = seen_shared.get(name)
            if resource is None:
                mark(row, "shared-resource-not-observed")
                continue
            if resource.get("coverage_complete") is not True:
                mark(row, "shared-resource-coverage-unknown")
            if resource.get("active") is True:
                mark(row, "shared-resource-active", busy=True)
            elif resource.get("active") is not False:
                mark(row, "shared-resource-activity-unknown")
            if not _evidence(resource.get("evidence")):
                mark(row, "raw-evidence-missing")
            else:
                proofs.update(resource["evidence"])

    times = [start for start, _ in intervals]
    ordered = sorted(intervals)
    quiet_lower_bound = ordered[-1][0] - ordered[0][1] if ordered else 0
    gap_upper_bounds = [right[1] - left[0] for left, right in zip(ordered, ordered[1:])]
    if len(times) < minimum_samples:
        problems.append("insufficient-observations")
    if len(set(times)) != len(times):
        problems.append("duplicate-observation-time")
    if times != sorted(times):
        problems.append("observations-out-of-order")
    if any(right[0] < left[1] for left, right in zip(ordered, ordered[1:])):
        problems.append("observation-windows-overlap")
    if not times or quiet_lower_bound < quiet_period:
        problems.append("quiet-window-too-short")
    if any(gap > maximum_gap for gap in gap_upper_bounds):
        problems.append("observation-gap-too-large")
    for row in list(rows.values()) + list(shared_rows.values()):
        for reason in problems:
            mark(row, reason)
    all_rows = list(rows.values()) + list(shared_rows.values())
    status = ("busy" if any(x["status"] == "busy" for x in all_rows)
              else "incomplete" if any(x["status"] == "incomplete" for x in all_rows) else "observed-idle")
    return {"schema_version": 1, "context": context, "status": status,
            "devices": list(rows.values()), "shared_resources": list(shared_rows.values()),
            "observations": len(observations), "evidence": sorted(proofs),
            "time_bounds": {"quiet_seconds_lower_bound": quiet_lower_bound,
                            "largest_gap_seconds_upper_bound": max(gap_upper_bounds, default=0),
                            "basis": "Exact samples are zero-width intervals; remote collection retains request start/end uncertainty"},
            "reservation_acquired": False, "requires_immediate_recheck": True,
            "meaning": "Fresh observations only; site reservation/coordination and a pre-launch recheck remain required. "
                       "Independent users may start work between samples; TrainFlow leases do not reserve their hardware."}
