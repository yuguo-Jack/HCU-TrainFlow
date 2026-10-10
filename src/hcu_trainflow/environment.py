"""Environment admission compares compatible checks, never arbitrary peak tables."""
import re

from .analysis import number
from .core import FlowError, fingerprint
from .quality import validate_measurement


_PERFORMANCE_DIAGNOSIS_STEPS = (
    "verify-original-reference-units-and-measurement-method",
    "check-actual-configuration-environment-and-data-path",
    "check-loaded-library-versions-and-matched-source",
    "consult-hcu-knowledge-and-relevant-implementation",
    "run-authorized-bounded-single-variable-a-b-a",
    "verify-correctness-effective-path-and-regression",
    "retain-validated-change-or-rollback",
    "escalate-unresolved-or-permission-blocked-findings",
)


def _performance_discrepancy(item):
    if "performance_discrepancy" not in item:
        return None
    value = item["performance_discrepancy"]
    if not isinstance(value, dict) or set(value) - {"summary", "evidence", "missing_conditions"}:
        raise FlowError("Performance discrepancy needs summary, evidence and optional missing_conditions")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        raise FlowError("Performance discrepancy summary cannot be empty")
    evidence = value.get("evidence")
    if (not isinstance(evidence, list) or not evidence
            or any(not isinstance(x, str) or not re.fullmatch(r"[0-9a-f]{64}", x) for x in evidence)):
        raise FlowError("Performance discrepancy evidence must contain artifact SHA256 IDs")
    # report-add verifies retained objects. Do not let these references escape
    # that existing envelope by accepting evidence absent from the observation.
    if not isinstance(item.get("evidence"), list) or any(x not in item["evidence"] for x in evidence):
        raise FlowError("Performance discrepancy evidence must be retained in observation evidence")
    missing = value.get("missing_conditions", [])
    if not isinstance(missing, list) or any(not isinstance(x, str) or not x.strip() for x in missing):
        raise FlowError("Performance discrepancy missing_conditions must be a list of nonempty strings")
    return {"summary": value["summary"], "evidence": list(evidence), "missing_conditions": list(missing)}


def assess_health(contract, measurements):
    required = contract.get("required", [])
    if not required:
        raise FlowError("Health contract needs explicit node/device/check coverage")
    keys = [(x["node"], str(x["device"]), x["check"]) for x in required]
    if len(set(keys)) != len(keys):
        raise FlowError("Duplicate required health checks")
    observed, discrepancies = {}, {}
    for item in measurements:
        key = (item["node"], str(item["device"]), item["check"])
        if key in observed:
            raise FlowError("Multiple results for a health check; select an explicit attempt")
        observed[key] = item
        discrepancy = _performance_discrepancy(item)
        if discrepancy is not None:
            if key not in keys:
                raise FlowError("Performance discrepancy must belong to a required check")
            discrepancies[key] = discrepancy
    rows = []
    for expectation, key in zip(required, keys):
        item = observed.get(key)
        reasons, result = [], "pass"
        if item is None:
            result, reasons = "incomplete", ["not-collected"]
        elif item.get("context") != contract.get("context") or fingerprint(item.get("conditions")) != fingerprint(expectation.get("conditions")):
            result, reasons = "incomplete", ["environment-or-workload-mismatch"]
        elif item.get("status") != "pass":
            result = "fail" if item.get("status") == "fail" else "incomplete"
            reasons = [item.get("reason", "check-not-passed")]
        elif validate_measurement(item, contract.get('context'), path_required=False):
            result, reasons = "incomplete", validate_measurement(item, contract.get('context'), path_required=False)
        elif expectation.get("kind") == "performance":
            if not expectation.get("basis") or expectation.get("minimum") is None:
                result, reasons = "incomplete", ["missing-matched-expectation"]
            elif number(item.get("value"), "measurement") < number(expectation["minimum"], "minimum"):
                result, reasons = "fail", ["below-matched-expectation"]
        discrepancy = discrepancies.get(key)
        if discrepancy is not None:
            if expectation.get("kind") != "performance":
                raise FlowError("Performance discrepancy requires a performance check")
            if result == "pass":
                result = "incomplete"
            reasons.append("unresolved-performance-discrepancy")
        row = {"node": key[0], "device": key[1], "check": key[2], "status": result, "reasons": reasons}
        if discrepancy is not None:
            row["performance_discrepancy"] = discrepancy
        if expectation.get("kind") == "performance" and result != "pass":
            classification = ("matched-performance-failure" if "below-matched-expectation" in reasons
                              else "check-failure" if result == "fail"
                              else "provisional-performance-discrepancy" if discrepancy is not None
                              else "evidence-gap")
            row["follow_up"] = {"classification": classification,
                                "steps": list(_PERFORMANCE_DIAGNOSIS_STEPS),
                                "execution_scope": "existing-task-authorization-and-fresh-resource-admission",
                                "reference": "docs/environment-discovery.md#6-性能不及预期时的排查顺序"}
        rows.append(row)
    status = "fail" if any(x["status"] == "fail" for x in rows) else "incomplete" if any(x["status"] == "incomplete" for x in rows) else "pass"
    return {"schema_version": 1, "context": contract["context"], "status": status, "checks": rows,
            "executed": sum(x['executed'] for x in measurements if isinstance(x.get('executed'), int)
                            and not isinstance(x['executed'], bool) and x['executed'] > 0), "failures": sum(x["status"] == "fail" for x in rows),
            "required_missing": [x for x in rows if x["status"] == "incomplete"],
            "follow_up_required": any("follow_up" in x for x in rows),
            "evidence": sorted({s for x in measurements for s in x.get("evidence", [])})}
