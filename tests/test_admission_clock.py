import copy
import pytest

from hcu_trainflow.admission import bound_remote_observation, assess_occupancy
from hcu_trainflow.core import FlowError


def sample(t="2026-01-01T00:00:01.800000+00:00"):
    return {"context":"c", "observed_at":t, "devices":[{"node":"n","device":"g","identity":"pci:1","memory_used_bytes":0,"utilization_pct":0,"pids":[],"reservations":[],"coverage":{"device":True,"processes":True,"reservations":True},"evidence":["a"*64]}]}


def bound(s, start="2026-01-01T00:00:00+00:00", end="2026-01-01T00:00:01+00:00", duration=1):
    return bound_remote_observation(s, requested_at=start, received_at=end, elapsed_seconds=duration)


def test_remote_ahead_is_preserved_but_controller_age_is_conservative():
    raw=sample();before=copy.deepcopy(raw);row=bound(raw)
    assert raw==before
    assert row["source_observed_at"]==raw["observed_at"]
    assert row["observed_at"]=="2026-01-01T00:00:00+00:00"
    assert row["devices"]==raw["devices"]
    assert row["collection_window"]["remote_clock_offset_bounds_seconds"]==pytest.approx([.8,1.8])
    row["devices"][0]["pids"].append(20)
    assert raw["devices"][0]["pids"]==[]


def test_old_request_stays_stale_even_if_remote_clock_is_future():
    first=bound(sample())
    second=bound(sample("2030-01-01T00:00:00+00:00"),"2026-01-01T00:00:11+00:00","2026-01-01T00:00:12+00:00")
    contract={"schema_version":1,"context":"c","devices":[{"node":"n","device":"g","identity":"pci:1","idle_memory_bytes":0,"memory_tolerance_bytes":0,"max_utilization_pct":0,"basis":"measured"}],"max_age_seconds":30,"quiet_period_seconds":10}
    result=assess_occupancy(contract,[first,second],now="2026-01-01T00:01:00+00:00")
    assert result["status"]=="incomplete"
    assert "stale-observation" in result["devices"][0]["reasons"]


@pytest.mark.parametrize("start,end,duration",[("2026-01-01T00:00:03+00:00","2026-01-01T00:00:01+00:00",1),("2026-01-01T00:00:00+00:00","2026-01-01T00:00:10+00:00",1),("2026-01-01T00:00:00+00:00","2026-01-01T00:00:01+00:00",True)])
def test_clock_jump_or_invalid_monotonic_evidence_rejected(start,end,duration):
    with pytest.raises(FlowError):bound(sample(),start,end,duration)


def test_rebinding_and_naive_remote_time_rejected():
    with pytest.raises(FlowError):bound(bound(sample()))
    with pytest.raises(FlowError):bound(sample("2026-01-01T00:00:00"))


def clock_contract():
    return {"schema_version": 1, "context": "c", "devices": [{"node": "n", "device": "g", "identity": "pci:1",
            "idle_memory_bytes": 0, "memory_tolerance_bytes": 0, "max_utilization_pct": 0, "basis": "Synthetic fixture"}],
            "max_age_seconds": 30, "quiet_period_seconds": 10, "max_sample_gap_seconds": 15}


def timestamp(seconds):
    return f"2026-01-01T00:00:{seconds:02d}+00:00"


def interval(start, end, measured):
    return bound(sample(timestamp(measured)), timestamp(start), timestamp(end), end-start)


def test_request_starts_cannot_fabricate_ten_seconds_of_quiet():
    # Real measurements 8s and 10s are only 2s apart. Their request starts are
    # 10s apart: this used to incorrectly admit the resources.
    rows = [interval(0, 9, 8), interval(10, 11, 10)]
    result = assess_occupancy(clock_contract(), rows, now=timestamp(12))
    assert result["status"] == "incomplete"
    assert "quiet-window-too-short" in result["devices"][0]["reasons"]
    assert result["time_bounds"]["quiet_seconds_lower_bound"] == 1


def test_slow_second_probe_cannot_hide_excessive_sampling_gap():
    # Real measurements 0s and 19s exceed the 15s gap limit despite request
    # starts 10s apart. The conservative upper gap is 20s.
    rows = [interval(0, 1, 0), interval(10, 20, 19)]
    result = assess_occupancy(clock_contract(), rows, now=timestamp(21))
    assert result["status"] == "incomplete"
    assert "observation-gap-too-large" in result["devices"][0]["reasons"]
    assert result["time_bounds"]["largest_gap_seconds_upper_bound"] == 20


def test_separated_envelopes_are_admitted_without_trusting_remote_clock_offset():
    rows = [interval(0, 1, 40), interval(11, 12, 52)]
    result = assess_occupancy(clock_contract(), rows, now=timestamp(13))
    assert result["status"] == "observed-idle"
    assert result["time_bounds"]["quiet_seconds_lower_bound"] == 10
    assert result["time_bounds"]["largest_gap_seconds_upper_bound"] == 12


def test_exact_clock_samples_and_mixed_samples_keep_conservative_bounds():
    exact = [sample(timestamp(0)), sample(timestamp(10))]
    result = assess_occupancy(clock_contract(), exact, now=timestamp(11))
    assert result["status"] == "observed-idle"
    assert result["time_bounds"]["quiet_seconds_lower_bound"] == 10
    mixed = [interval(0, 1, 40), sample(timestamp(11))]
    assert assess_occupancy(clock_contract(), mixed, now=timestamp(12))["status"] == "observed-idle"


def test_overlapping_requests_cannot_establish_consecutive_observations():
    rows = [interval(0, 10, 5), interval(9, 11, 10), interval(20, 21, 20)]
    result = assess_occupancy({**clock_contract(), "max_sample_gap_seconds": 30}, rows, now=timestamp(22))
    assert result["status"] == "incomplete"
    assert "observation-windows-overlap" in result["devices"][0]["reasons"]


def test_request_end_in_future_is_not_a_completed_fresh_probe():
    rows = [interval(0, 1, 0), interval(11, 15, 12)]
    result = assess_occupancy(clock_contract(), rows, now=timestamp(14))
    assert result["status"] == "incomplete"
    assert "observation-from-future" in result["devices"][0]["reasons"]


@pytest.mark.parametrize("corrupt", ["no-window", "no-basis", "bad-start", "bad-end", "negative-duration",
                                     "clock-jump", "bool-duration", "bad-offset", "bool-offset", "nan-offset",
                                     "missing-offset", "missing-source", "empty-meaning", "extra-window-field"])
def test_malformed_or_inconsistent_envelopes_are_rejected(corrupt):
    row = interval(0, 1, 2)
    window = row["collection_window"]
    if corrupt == "no-window": row.pop("collection_window")
    elif corrupt == "no-basis": row.pop("timestamp_basis")
    elif corrupt == "bad-start": window["requested_at"] = timestamp(1)
    elif corrupt == "bad-end": window["received_at"] = "2025-12-31T23:59:59+00:00"
    elif corrupt == "negative-duration": window["elapsed_seconds"] = -1
    elif corrupt == "clock-jump": window["elapsed_seconds"] = 9
    elif corrupt == "bool-duration": window["elapsed_seconds"] = True
    elif corrupt == "bad-offset": window["remote_clock_offset_bounds_seconds"] = [2, 3]
    elif corrupt == "bool-offset": window["remote_clock_offset_bounds_seconds"] = [True, 2]
    elif corrupt == "nan-offset": window["remote_clock_offset_bounds_seconds"] = [float('nan'), 2]
    elif corrupt == "missing-offset": window.pop("remote_clock_offset_bounds_seconds")
    elif corrupt == "missing-source": row.pop("source_observed_at")
    elif corrupt == "empty-meaning": window["meaning"] = ""
    elif corrupt == "extra-window-field": window["unreviewed"] = 2
    with pytest.raises(FlowError):
        assess_occupancy(clock_contract(), [row, interval(11, 12, 13)], now=timestamp(13))
