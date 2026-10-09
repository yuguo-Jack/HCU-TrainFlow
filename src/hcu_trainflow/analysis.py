"""Training-window coverage and explicit, inspectable operator bounds.

This supplements TraceLens; it does not infer a distributed critical path from
unsynchronized timestamps. Overlap allocation is a stated proxy, not causality.
"""
import collections
import math
import re

from .core import FlowError, fingerprint


def number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (positive and value <= 0):
        raise FlowError(name + " must be a finite" + (" positive" if positive else "") + " number")
    return float(value)


def profile_plan(groups, available):
    available = set(available)
    selected, details = set(), []
    for group in groups:
        ranks = list(dict.fromkeys(group["ranks"]))
        if not ranks or len(ranks) != len(group["ranks"]):
            raise FlowError("Process groups must have unique, nonempty actual ranks")
        candidates = [r for r in ranks if r in available]
        needed = min(2, len(ranks))
        chosen = candidates if len(candidates) <= 2 else [candidates[0], candidates[-1]]
        selected.update(chosen)
        details.append({**group, "selected": chosen, "required": needed, "complete": len(chosen) >= needed})
    return {"status": "pass" if details and all(x["complete"] for x in details) else "incomplete",
            "ranks": sorted(selected), "groups": details,
            "limits": "Two ranks per actual group are a minimum; collective-wide models may require every rank and clock calibration."}


def model_operator(model, actual_us):
    actual = number(actual_us, "actual_us", True)
    if not model or not model.get("basis"):
        return {"status": "incomplete", "reason": "Missing workload/peak assumptions and their evidence", "decision": "collect-evidence"}
    flops, traffic = model.get("flops"), model.get("bytes")
    if model.get("kind") == "gemm":
        dims = [number(model.get(x), x, True) for x in ("m", "n", "k")]
        batch = number(model.get("batch", 1), "batch", True)
        flops = 2 * math.prod(dims) * batch
    terms = []
    if flops is not None and model.get("peak_flops_s") is not None:
        terms.append(number(flops, "flops", True) / number(model["peak_flops_s"], "peak_flops_s", True) * 1e6)
    if traffic is not None and model.get("bandwidth_bytes_s") is not None:
        terms.append(number(traffic, "bytes", True) / number(model["bandwidth_bytes_s"], "bandwidth_bytes_s", True) * 1e6)
    if model.get("latency_floor_us") is not None:
        terms.append(number(model["latency_floor_us"], "latency_floor_us", True))
    if not terms:
        return {"status": "incomplete", "reason": "No applicable compute, traffic or latency model", "decision": "collect-evidence"}
    lower = max(terms)
    ratio = lower / actual
    isolated = model.get("isolated_us")
    slowdown = actual / number(isolated, "isolated_us", True) if isolated is not None else None
    reference = model.get("reference_us")
    decision = "compare-reachable-reference"
    if ratio > 1:
        decision = "check-model-or-measurement"
    elif slowdown is not None and slowdown > model.get("slowdown_threshold", 1.2):
        decision = "investigate-system-interference"
    elif "efficiency_target" in model:
        threshold = number(model["efficiency_target"], "efficiency_target", True)
        if threshold > 1:
            raise FlowError("efficiency_target must be <=1")
        decision = "optimize-implementation" if ratio < threshold else "retain-implementation"
    return {"status": "modeled" if ratio <= 1 else "inconsistent", "flops": flops, "bytes": traffic,
            "lower_bound_us": lower, "eta_bound": ratio,
            "eta_reference": number(reference, "reference_us", True) / actual if reference is not None else None,
            "model_to_isolated": slowdown, "decision": decision, "basis": model["basis"],
            "limits": "Optimistic bound under explicit assumptions; not a measured hardware utilization or guaranteed speedup."}


def _attribution_rows(trace, window, attribution):
    if attribution is None:
        return {}
    if not isinstance(attribution, dict) or attribution.get('schema_version') != 1:
        raise FlowError('Unsupported CPU/GPU attribution export')
    source = attribution.get('source') or {}
    if not isinstance(source.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', source['sha256']):
        raise FlowError('Attribution must retain the original trace file SHA256')
    if source.get('content_hash') != fingerprint(trace):
        raise FlowError('Attribution belongs to different trace contents or event ordering')
    if attribution.get('window_hash') != fingerprint(window) or attribution.get('window') != window:
        raise FlowError('Attribution belongs to a different training window')
    events = trace.get('traceEvents') if isinstance(trace, dict) else trace
    if attribution.get('event_count') != len(events) or not isinstance(attribution.get('events'), list):
        raise FlowError('Attribution event count or mapping is invalid')
    rows = {}
    for row in attribution['events']:
        if not isinstance(row, dict):
            raise FlowError('Attribution rows must be objects')
        index = row.get('event_index')
        if type(index) is not int or not 0 <= index < len(events) or index in rows:
            raise FlowError('Attribution contains duplicate or invalid event indices')
        if row.get('event_hash') != fingerprint(events[index]):
            raise FlowError('Attribution event identity conflicts with the original trace')
        if row.get('status') not in {'matched', 'unlinked', 'ambiguous'}:
            raise FlowError('Attribution status must preserve matched/unlinked/ambiguous evidence')
        if row.get('shape') is not None:
            chosen = row.get('shape_source') or {}
            chosen_index = chosen.get('event_index')
            if type(chosen_index) is not int or not 0 <= chosen_index < len(events):
                raise FlowError('Attribution shape source is missing')
            chosen_event = events[chosen_index]
            args = chosen_event.get('args') or {}
            if chosen_event.get('cat') != 'cpu_op' or row['shape'] != args.get('Input Dims') or row.get('dtype') != args.get('Input type'):
                raise FlowError('Attribution shape/dtype conflicts with its original CPU evidence')
            if row.get('input_strides') != args.get('Input Strides'):
                raise FlowError('Attribution strides conflict with their original CPU evidence')
        rows[index] = row
    return rows


def analyze_trace(trace, window, models=None, target=0.9, attribution=None):
    start, end = [number(window[x], x) for x in ("start_us", "end_us")]
    if end <= start or not 0 < target <= 1:
        raise FlowError("A positive wall-clock training window and coverage in (0,1] are required")
    events = trace.get("traceEvents") if isinstance(trace, dict) else trace
    if not isinstance(events, list):
        raise FlowError("Expected a Chrome/PyTorch traceEvents array")
    attribution_rows = _attribution_rows(trace, window, attribution)
    models = models or {}
    by_rank = collections.defaultdict(list)
    ignored = collections.Counter()
    invalid = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict) or event.get("ph") != "X":
            ignored["non-duration-event"] += 1
            continue
        category = str(event.get("cat", "")).lower()
        if category not in {"kernel", "gpu_kernel", "hip_kernel", "cuda_kernel", "communication", "gpu_memcpy", "gpu_memset"}:
            ignored[category or "unclassified"] += 1
            continue
        try:
            begin = number(event.get("ts"), "ts")
            duration = number(event.get("dur"), "dur", True)
        except FlowError:
            invalid += 1
            continue
        left, right = max(start, begin), min(end, begin + duration)
        if right <= left:
            continue
        args = event.get("args") or {}
        name = str(event.get("name", "unnamed"))
        linked = attribution_rows.get(index, {})
        shape = args.get("Input Dims", args.get("shape"))
        dtype = args.get("Input type", args.get("dtype"))
        strides = args.get('Input Strides')
        inherited_shape = shape is None and linked.get('shape') is not None and linked.get('status') == 'matched'
        if inherited_shape:
            shape, dtype = linked['shape'], linked.get('dtype')
            strides = linked.get('input_strides')
        phase = args.get('phase', linked.get('phase', 'unknown'))
        callsite = linked.get('callsite', [])
        owner_name = (linked.get('cpu_op') or {}).get('name')
        identity = {"name": name, "shape": shape, "dtype": dtype, "phase": phase}
        if strides is not None:
            identity['input_strides'] = strides
        if attribution is not None:
            identity.update(cpu_op=owner_name, callsite=callsite, attribution_status=linked.get('status', 'missing-entry'),
                            shape_scope=linked.get('shape_scope') if inherited_shape else 'kernel-inputs' if shape is not None else 'unavailable')
        key = fingerprint(identity)[:16]
        metadata = trace if isinstance(trace, dict) else {}
        distributed = metadata.get('distributedInfo') or {}
        captured_rank = metadata.get('rank', distributed.get('rank', 'unknown') if isinstance(distributed, dict) else 'unknown')
        if captured_rank == 'unknown' and attribution is not None and attribution.get('rank') is not None:
            captured_rank = attribution['rank']
        rank = str(args.get('rank', captured_rank))
        communication = category == "communication" or bool(re.search(r"nccl|rccl|all_?reduce|all_?gather|all_?to_?all|reduce_?scatter", name, re.I))
        by_rank[rank].append({"index": index, "key": key, "name": name, "shape": shape, "dtype": dtype, 'input_strides': strides,
                              "begin": left, "end": right, "duration": duration, "communication": communication,
                              "phase": phase, "clipped": left != begin or right != begin + duration,
                              'cpu_op': owner_name, 'callsite': callsite,
                              'callsite_kind': linked.get('callsite_kind', 'unavailable'),
                              'shape_scope': linked.get('shape_scope') if inherited_shape else 'kernel-inputs' if shape is not None else 'unavailable',
                              'requires_workload_mapping': inherited_shape,
                              'attribution_status': linked.get('status', 'missing-entry') if attribution is not None else 'not-requested'})
    ranks = {}
    for rank, items in by_rank.items():
        boundaries = collections.defaultdict(list)
        groups = {}
        for item in items:
            boundaries[item["begin"]].append((1, item))
            boundaries[item["end"]].append((-1, item))
            group = groups.setdefault(item["key"], {**{k: item[k] for k in ("key", "name", "shape", "dtype", "input_strides", "communication", "phase", 'cpu_op', 'callsite', 'callsite_kind', 'shape_scope', 'requires_workload_mapping', 'attribution_status')}, "calls": 0, "raw_us": 0.0, "attributed_us": 0.0, "clipped_calls": 0})
            group["calls"] += 1
            group["raw_us"] += item["duration"]
            group["clipped_calls"] += int(item["clipped"])
        active, previous, busy, overlap = {}, start, 0.0, 0.0
        for point in sorted(boundaries):
            delta = point - previous
            if active:
                busy += delta
                if len(active) > 1:
                    overlap += delta
                for item in active.values():
                    groups[item["key"]]["attributed_us"] += delta / len(active)
            for direction, item in boundaries[point]:
                if direction == 1:
                    active[item["index"]] = item
                else:
                    active.pop(item["index"], None)
            previous = point
        ordered = sorted(groups.values(), key=lambda x: x["attributed_us"], reverse=True)
        cumulative = 0
        for group in ordered:
            group["e2e_share"] = group["attributed_us"] / (end - start)
            group["in_hot_set"] = cumulative < target
            cumulative += group["e2e_share"]
            group["cumulative_e2e_share"] = cumulative
            group["mean_kernel_us"] = group["raw_us"] / group["calls"]
            model = models.get(group["key"], models.get(group["name"]))
            if group['attribution_status'] in {'ambiguous', 'missing-entry'}:
                group['assessment'] = {'status': 'incomplete', 'reason': 'Ambiguous or missing CPU/GPU event attribution'}
            elif group["communication"] and not (model or {}).get("mixed_compute"):
                group["assessment"] = {"status": "communication", "decision": "message-topology-wait-overlap-analysis"}
            elif group["clipped_calls"]:
                group["assessment"] = {"status": "incomplete", "reason": "Window cuts through kernel calls; select complete calls"}
            elif group["in_hot_set"]:
                if group['requires_workload_mapping'] and not (model or {}).get('workload_evidence'):
                    group['assessment'] = {'status': 'incomplete', 'reason': 'CPU input shapes are context; provide explicit per-kernel workload evidence before computing bounds'}
                elif (group["shape"] is None or group["dtype"] is None) and not (model or {}).get("workload_evidence"):
                    group["assessment"] = {"status": "incomplete", "reason": "Missing shape/dtype capture or explicit workload evidence"}
                else:
                    group["assessment"] = model_operator(model, group["mean_kernel_us"])
            else:
                group["assessment"] = {"status": "outside-hot-set"}
        missing = [x["key"] for x in ordered if x["in_hot_set"] and x["assessment"]["status"] in {"incomplete", "inconsistent"}]
        ranks[rank] = {"window_us": end - start, "busy_union_us": busy, "overlap_us": overlap,
                       "unattributed_or_idle_us": end - start - busy, "operator_e2e_coverage": cumulative,
                       "target_reached": cumulative + 1e-9 >= target, "missing_models": missing,
                       "operators": ordered}
    complete = bool(ranks) and "unknown" not in ranks and not invalid and all(x["target_reached"] and not x["missing_models"] for x in ranks.values())
    return {"schema_version": 1, "status": "complete" if complete else "incomplete", "target": target,
            'cpu_gpu_attribution': {'source': attribution.get('source'), 'window_hash': attribution.get('window_hash'),
                                    'mapping_hash': fingerprint(attribution), 'parser': attribution.get('parser'),
                                    'counts': attribution.get('counts')} if attribution is not None else None,
            "ranks": ranks, "invalid_device_events": invalid, "unclassified_categories": dict(ignored),
            "time_unit": "microseconds", "attribution": "equal-share of overlapping device intervals within each rank; not a critical-path proof",
            "limits": ["No cross-rank timestamp alignment is inferred", "CPU/wait gaps remain in the wall-clock denominator", "Shapes/dtypes absent from trace require workload capture", "Profiler traces do not replace profiler-off performance measurements"]}
