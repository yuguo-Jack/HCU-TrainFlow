"""Environment admission compares compatible checks, never arbitrary peak tables."""
from .analysis import number
from .core import FlowError
from .quality import validate_measurement


def assess_health(contract, measurements):
    required = contract.get("required", [])
    if not required:
        raise FlowError("Health contract needs explicit node/device/check coverage")
    keys = [(x["node"], str(x["device"]), x["check"]) for x in required]
    if len(set(keys)) != len(keys):
        raise FlowError("Duplicate required health checks")
    observed = {}
    for item in measurements:
        key = (item["node"], str(item["device"]), item["check"])
        if key in observed:
            raise FlowError("Multiple results for a health check; select an explicit attempt")
        observed[key] = item
    rows = []
    for expectation, key in zip(required, keys):
        item = observed.get(key)
        reasons, result = [], "pass"
        if item is None:
            result, reasons = "incomplete", ["not-collected"]
        elif item.get("context") != contract.get("context") or item.get("conditions") != expectation.get("conditions"):
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
        rows.append({"node": key[0], "device": key[1], "check": key[2], "status": result, "reasons": reasons})
    status = "fail" if any(x["status"] == "fail" for x in rows) else "incomplete" if any(x["status"] == "incomplete" for x in rows) else "pass"
    return {"schema_version": 1, "context": contract["context"], "status": status, "checks": rows,
            "executed": sum(x['executed'] for x in measurements if isinstance(x.get('executed'), int)
                            and not isinstance(x['executed'], bool) and x['executed'] > 0), "failures": sum(x["status"] == "fail" for x in rows),
            "required_missing": [x for x in rows if x["status"] == "incomplete"],
            "evidence": sorted({s for x in measurements for s in x.get("evidence", [])})}
