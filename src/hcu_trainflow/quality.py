"""Validity before acceptance: model contracts, numerical checks and staged loss."""
import math
import statistics

from .analysis import number
from .core import FlowError, fingerprint


def _same_json(left, right):
    """Model semantics include key presence and JSON value types, recursively."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same_json(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_json(a, b) for a, b in zip(left, right))
    return left == right


def proxy_contract(full, candidate, authorization=None):
    """Check an explicit proxy's scope, never claim runtime or full-model validity.

    Layer-only reduction remains the default. Dimension reduction requires a
    recorded user authorization listing each numeric field; architecture and
    numerical validity are separate evidence obligations.
    """
    if not isinstance(full, dict) or not isinstance(candidate, dict):
        raise FlowError('Model contracts must be JSON objects')
    changes = {k: {"full": full.get(k), "candidate": candidate.get(k),
                   "full_present": k in full, "candidate_present": k in candidate}
               for k in full.keys() | candidate.keys()
               if k not in full or k not in candidate or not _same_json(full[k], candidate[k])}
    dimensions = []
    if authorization is not None:
        if not isinstance(authorization, dict) or set(authorization) - {'authority', 'reason', 'allowed_dimension_reductions'}:
            raise FlowError('Proxy authorization requires authority, reason and explicit dimension fields')
        for key in ('authority', 'reason'):
            if not isinstance(authorization.get(key), str) or not authorization[key].strip():
                raise FlowError('Proxy authorization must record user authority and reason')
        dimensions = authorization.get('allowed_dimension_reductions')
        if not isinstance(dimensions, list) or not dimensions or any(not isinstance(k, str) or not k.strip() or k == 'num_layers' for k in dimensions) or len(set(dimensions)) != len(dimensions):
            raise FlowError('List each authorized dimension field exactly once; layer reduction is already supported')
    allowed_fields = {'num_layers', *dimensions}
    reasons = []
    for key in changes:
        if key not in allowed_fields:
            reasons.append(key + ':unauthorized-change')
        elif not all(type(x.get(key)) is int for x in (full, candidate)) or not 0 < candidate[key] < full[key]:
            reasons.append(key + ':requires-positive-integer-reduction')
    return {'status': 'fail' if reasons else 'pass', 'changes': changes,
            'is_proxy': bool(changes), 'full_model_equivalent': not changes,
            'runtime_validated': False, 'reasons': reasons,
            'authorization': authorization,
            'scope': 'dimension-proxy' if set(changes) - {'num_layers'} else 'layer-proxy' if changes else 'unchanged',
            'required_followup': ['architecture-constraints', 'numerical-baseline', 'selected-configuration-scaling'] if changes else [],
            'limits': 'Static scope check only. A reduced model does not validate full-model memory, loss convergence or scaling.'}


def validate_measurement(value, context, path_required=True):
    missing = []
    if value.get("context") != context:
        missing.append("context-mismatch")
    if not isinstance(value.get("executed"), int) or isinstance(value.get("executed"), bool) or value["executed"] <= 0:
        missing.append("no-executed-tests")
    if value.get("failures") or value.get("status") in {"fail", "failed", "incomplete"}:
        missing.append("reported-test-failures")
    if value.get("skipped_required", 0):
        missing.append("required-tests-skipped")
    if value.get("required_missing"):
        missing.append("required-coverage-missing")
    if path_required and value.get("candidate_path_exercised") is not True:
        missing.append("candidate-dispatch-not-confirmed")
    if not value.get("evidence"):
        missing.append("missing-raw-evidence")
    return missing


def compare_loss(contract, baseline, candidate):
    required = {"context", "sample_fingerprint", "aggregation", "min_steps", "atol", "rtol", "tolerance_basis"}
    if required - contract.keys() or any(not contract[x] for x in ("context", "sample_fingerprint", "aggregation", "tolerance_basis")):
        raise FlowError("QualityContract must freeze samples, aggregation, window and justified tolerances")
    if not isinstance(contract["min_steps"], int) or isinstance(contract["min_steps"], bool) or contract["min_steps"] < 1:
        raise FlowError("min_steps must be positive")
    atol, rtol = number(contract["atol"], "atol"), number(contract["rtol"], "rtol")
    if atol < 0 or rtol < 0:
        raise FlowError("Tolerances cannot be negative")
    reasons = []
    for label, record in (("baseline", baseline), ("candidate", candidate)):
        reasons += [label + ":" + x for x in validate_measurement(record, contract["context"], label == "candidate")]
        for key in ("sample_fingerprint", "aggregation"):
            if record.get(key) != contract[key]:
                reasons.append(label + ":" + key + "-mismatch")
    left, right = baseline.get("loss", []), candidate.get("loss", [])
    if len(left) != len(right) or len(left) < contract["min_steps"]:
        reasons.append("unaligned-or-short-loss-window")
    for series in (left, right):
        if any(not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) for x in series):
            reasons.append("nonfinite-or-invalid-loss")
    if baseline.get("steps") != candidate.get("steps") or not baseline.get("steps") or len(baseline["steps"]) != len(left):
        reasons.append("step-alignment-missing")
    else:
        steps = baseline["steps"]
        if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 for x in steps) or any(a >= b for a,b in zip(steps, steps[1:])):
            reasons.append("steps-must-advance-without-duplicates")
    if reasons:
        return {"status": "incomplete", "reasons": reasons, "contract": fingerprint(contract)}
    errors = [abs(a-b) for a, b in zip(left, right)]
    failures = [i for i, (a, b) in enumerate(zip(left, right)) if abs(a-b) > atol + rtol * abs(a)]
    return {"status": "fail" if failures else "pass", "failures": failures, "max_abs_error": max(errors),
            "mean_abs_error": statistics.mean(errors), "executed": len(left), "contract": fingerprint(contract),
            "limits": "Matched frozen window, not proof of arbitrary long-run convergence. Initial reference remains immutable across optimization iterations."}


def assess_iteration(correctness, baseline_times, candidate_times, context, max_regression=0.0):
    reasons = validate_measurement(correctness, context)
    if correctness.get("profiler_off") is not True or not correctness.get("measurement_protocol"):
        reasons.append("profiler-off-and-measurement-protocol-required")
    if number(max_regression, "max_regression") < 0:
        raise FlowError("max_regression cannot be negative")
    if correctness.get("failures"):
        return {"status": "rejected", "reason": "correctness-failed", "quality": "not-accepted"}
    if reasons or len(baseline_times) < 3 or len(candidate_times) != len(baseline_times):
        return {"status": "incomplete", "reasons": reasons + ["Need at least three matched profiler-off repetitions"], "quality": "pending"}
    b = [number(x, "baseline time", True) for x in baseline_times]
    c = [number(x, "candidate time", True) for x in candidate_times]
    ratio = statistics.median(c) / statistics.median(b)
    return {"status": "iteration-kept" if ratio <= 1 + max_regression else "rejected", "time_ratio": ratio,
            "paired_ratios": [y/x for x, y in zip(b, c)], "quality": "pending-stage-validation", "production_default": False}
