"""Explicitly synthetic, retained stage-comparison evidence for CPU tests."""
import json


def stage_report(store, context, snapshot=None, proof=None):
    snapshot = snapshot or store.put(b"Synthetic candidate manifest")
    proof = proof or store.put(b"Synthetic raw numerical observations; no GPU validation")
    contract = {"context": context, "sample_fingerprint": "synthetic-samples",
                "initial_state_fingerprint": "synthetic-initial-state",
                "training_recipe_fingerprint": "synthetic-recipe", "aggregation": "tokens",
                "min_steps": 3, "atol": .01, "rtol": 0, "tolerance_basis": "Synthetic test only"}
    record = {**{k: contract[k] for k in ("context", "sample_fingerprint", "initial_state_fingerprint",
                                         "training_recipe_fingerprint", "aggregation")},
              "executed": 3, "evidence": [proof], "steps": [1, 2, 3], "loss": [2., 1.9, 1.8]}
    inputs = {"contract": contract, "baseline": record,
              "candidate": {**record, "candidate_snapshot": snapshot, "candidate_path_exercised": True}}
    pointer = store.put(json.dumps(inputs).encode())
    return {"context": context, "candidate_snapshot": snapshot, "status": "pass", "executed": 3,
            "evidence": [proof, pointer], "quality_inputs": pointer}
