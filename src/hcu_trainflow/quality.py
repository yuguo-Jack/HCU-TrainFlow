"""Validity before acceptance: model contracts, numerical checks and staged loss."""
import math
import json
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
    if not isinstance(value, dict):
        raise FlowError("Measurement must be a JSON object")
    missing = []
    if value.get("context") != context:
        missing.append("context-mismatch")
    if not isinstance(value.get("executed"), int) or isinstance(value.get("executed"), bool) or value["executed"] <= 0:
        missing.append("no-executed-tests")
    # Legacy records may omit status. An explicit outcome must be affirmative:
    # unknown/blocked/rejected is not successful numerical evidence.
    if value.get("failures") or ("status" in value and value["status"] != "pass"):
        missing.append("reported-test-failures")
    if value.get("skipped_required", 0):
        missing.append("required-tests-skipped")
    if value.get("required_missing"):
        missing.append("required-coverage-missing")
    if path_required and value.get("candidate_path_exercised") is not True:
        missing.append("candidate-dispatch-not-confirmed")
    evidence = value.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(x, str) or not x.strip() for x in evidence):
        missing.append("missing-raw-evidence")
    return missing


def compare_loss(contract, baseline, candidate):
    if not isinstance(contract, dict):
        raise FlowError("QualityContract must be a JSON object")
    required = {"context", "sample_fingerprint", "aggregation", "min_steps", "atol", "rtol", "tolerance_basis"}
    if required - contract.keys() or any(not isinstance(contract[x], str) or not contract[x].strip() for x in ("context", "sample_fingerprint", "aggregation", "tolerance_basis")):
        raise FlowError("QualityContract must freeze samples, aggregation, window and justified tolerances")
    if not isinstance(contract["min_steps"], int) or isinstance(contract["min_steps"], bool) or contract["min_steps"] < 1:
        raise FlowError("min_steps must be positive")
    atol, rtol = number(contract["atol"], "atol"), number(contract["rtol"], "rtol")
    if atol < 0 or rtol < 0:
        raise FlowError("Tolerances cannot be negative")
    identity_fields = ["sample_fingerprint", "aggregation"]
    for key in ("initial_state_fingerprint", "training_recipe_fingerprint"):
        if key in contract:
            if not isinstance(contract[key], str) or not contract[key].strip():
                raise FlowError(key + " must identify the frozen comparison inputs")
            identity_fields.append(key)
    reasons = []
    for label, record in (("baseline", baseline), ("candidate", candidate)):
        reasons += [label + ":" + x for x in validate_measurement(record, contract["context"], label == "candidate")]
        for key in identity_fields:
            if record.get(key) != contract[key]:
                reasons.append(label + ":" + key + "-mismatch")
    missing_identities = [key for key in ("initial_state_fingerprint", "training_recipe_fingerprint")
                          if key not in contract]
    for key in missing_identities:
        if key in baseline or key in candidate:
            reasons.append("contract-missing-declared-identity:" + key)
    left, right = baseline.get("loss", []), candidate.get("loss", [])
    if not isinstance(left, list) or not isinstance(right, list):
        raise FlowError("Loss series must be arrays of finite numbers")
    if len(left) != len(right) or len(left) < contract["min_steps"]:
        reasons.append("unaligned-or-short-loss-window")
    for series in (left, right):
        if any(not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x) for x in series):
            reasons.append("nonfinite-or-invalid-loss")
    for label, record, losses in (("baseline", baseline, left), ("candidate", candidate, right)):
        steps = record.get("steps")
        if not isinstance(steps, list) or not steps or len(steps) != len(losses):
            reasons.append(label + ":step-alignment-missing")
        elif any(type(x) is not int or x < 0 for x in steps) or any(a >= b for a,b in zip(steps, steps[1:])):
            reasons.append(label + ":steps-must-advance-without-duplicates")
    if not _same_json(baseline.get("steps"), candidate.get("steps")):
        reasons.append("step-alignment-missing")
    if reasons:
        return {"status": "incomplete", "reasons": reasons, "contract": fingerprint(contract),
                "stage_eligible": False, "stage_missing": missing_identities}
    errors = [abs(a-b) for a, b in zip(left, right)]
    failures = [i for i, (a, b) in enumerate(zip(left, right)) if abs(a-b) > atol + rtol * abs(a)]
    return {"status": "fail" if failures else "pass", "failures": failures, "max_abs_error": max(errors),
            "mean_abs_error": statistics.mean(errors), "executed": len(left), "contract": fingerprint(contract),
            "matched_identity_fields": identity_fields,
            "stage_eligible": not failures and not missing_identities, "stage_missing": missing_identities,
            "limits": "Matched frozen window, not proof of arbitrary long-run convergence. Initial reference remains immutable across optimization iterations."}


def validate_stage_report(store, report):
    """Recompute stage acceptance from retained inputs, not a claimed PASS flag."""
    pointer = report.get("quality_inputs")
    if not isinstance(pointer, str) or pointer not in report.get("evidence", []):
        raise FlowError("Stage quality requires retained quality_inputs in report evidence")
    try:
        inputs = json.loads(store.artifact(pointer))
        if not isinstance(inputs, dict) or any(key not in inputs for key in ("contract", "baseline", "candidate")):
            raise FlowError("quality_inputs must contain contract, baseline and candidate")
        result = compare_loss(inputs["contract"], inputs["baseline"], inputs["candidate"])
        if result["status"] != "pass" or result["stage_eligible"] is not True:
            raise FlowError("Stage quality needs a passing comparison with frozen initial-state and recipe identities")
        if inputs["contract"]["context"] != report.get("context"):
            raise FlowError("Stage quality inputs belong to another context")
        snapshot = report.get("candidate_snapshot")
        if not isinstance(snapshot, str) or not snapshot or inputs["candidate"].get("candidate_snapshot") != snapshot:
            raise FlowError("Stage quality candidate snapshot does not match the report")
        store.artifact(snapshot)
        for record in (inputs["baseline"], inputs["candidate"]):
            for sha in record["evidence"]:
                store.artifact(sha)
        return result
    except (TypeError, KeyError, ValueError) as exc:
        if isinstance(exc, FlowError):
            raise
        raise FlowError("Invalid retained stage quality inputs") from exc


def assess_iteration(correctness, baseline_times, candidate_times, context, max_regression=0.0):
    reasons = validate_measurement(correctness, context)
    protocol = correctness.get("measurement_protocol")
    if correctness.get("profiler_off") is not True or not isinstance(protocol, (str, dict)) or not protocol or (isinstance(protocol, str) and not protocol.strip()):
        reasons.append("profiler-off-and-measurement-protocol-required")
    if number(max_regression, "max_regression") < 0:
        raise FlowError("max_regression cannot be negative")
    if correctness.get("failures"):
        return {"status": "rejected", "reason": "correctness-failed", "quality": "not-accepted"}
    if not isinstance(baseline_times, list) or not isinstance(candidate_times, list):
        raise FlowError("Performance repetitions must be arrays")
    if reasons or len(baseline_times) < 3 or len(candidate_times) != len(baseline_times):
        return {"status": "incomplete", "reasons": reasons + ["Need at least three matched profiler-off repetitions"], "quality": "pending"}
    b = [number(x, "baseline time", True) for x in baseline_times]
    c = [number(x, "candidate time", True) for x in candidate_times]
    medians = [statistics.median(series) for series in (b, c)]
    spreads = [statistics.median(abs(x - median) for x in series) / median
               for series, median in zip((b, c), medians)]
    timing = {'repetitions': len(b), 'baseline_median': medians[0], 'candidate_median': medians[1],
              'baseline_relative_mad': spreads[0], 'candidate_relative_mad': spreads[1],
              'stability': 'not-specified'}
    if isinstance(protocol, dict) and 'max_relative_mad' in protocol:
        threshold = number(protocol['max_relative_mad'], 'max_relative_mad')
        if threshold < 0:
            raise FlowError('max_relative_mad cannot be negative')
        timing.update(max_relative_mad=threshold, stability='pass' if max(spreads) <= threshold else 'incomplete')
        if timing['stability'] != 'pass':
            return {'status': 'incomplete', 'reasons': ['performance-repetitions-unstable'],
                    'timing': timing, 'quality': 'pending', 'production_default': False}
    ratio = medians[1] / medians[0]
    return {"status": "iteration-kept" if ratio <= 1 + max_regression else "rejected", "time_ratio": ratio,
            "paired_ratios": [y/x for x, y in zip(b, c)], "timing": timing,
            "quality": "pending-stage-validation", "production_default": False,
            "limits": "Median comparison is not statistical significance. Check dispersion, paired order and site drift against the predeclared measurement protocol."}
