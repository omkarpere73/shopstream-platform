"""Tests for the send plan and the ground-truth log. Run: .venv/bin/pytest simulator -q"""

import json
from datetime import UTC, datetime, timedelta
from functools import cache

from event_generator import generate_events
from send_plan import (
    PlannedSend,
    build_send_plan,
    ground_truth_lines,
    is_valid_event_text,
)

START = datetime(2026, 10, 27, 10, 0, 0, tzinfo=UTC)
STEP = timedelta(milliseconds=100)
COUNT = 20000


def make_plan(seed: int, count: int) -> list[PlannedSend]:
    return build_send_plan(generate_events(seed, count, START, STEP), seed)


@cache
def big_plan() -> tuple[PlannedSend, ...]:
    return tuple(make_plan(7, COUNT))


def parsed(send: PlannedSend) -> dict[str, object] | None:
    try:
        data = json.loads(send.text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def kind_counts() -> dict[str, int]:
    counts = {"valid": 0, "duplicate": 0, "late": 0, "malformed": 0}
    for send in big_plan():
        counts[send.kind] += 1
    return counts


def test_same_seed_gives_same_plan() -> None:
    assert make_plan(1, 3000) == make_plan(1, 3000)


def test_different_seed_gives_different_plan() -> None:
    assert make_plan(1, 3000) != make_plan(2, 3000)


def test_every_send_has_one_log_line_and_seq_counts_up() -> None:
    plan = big_plan()
    lines = ground_truth_lines(plan)
    assert len(lines) == len(plan)
    assert [json.loads(line)["seq"] for line in lines] == list(range(1, len(plan) + 1))


def test_send_count_adds_up() -> None:
    counts = kind_counts()
    assert counts["valid"] + counts["late"] + counts["malformed"] == COUNT
    assert len(big_plan()) == COUNT + counts["duplicate"]


def test_rates_are_close_to_the_targets() -> None:
    counts = kind_counts()
    assert 0.010 < counts["duplicate"] / COUNT < 0.020
    assert 0.020 < counts["late"] / COUNT < 0.040
    assert 0.002 < counts["malformed"] / COUNT < 0.008


def test_plan_is_in_send_time_order() -> None:
    times = [send.send_time for send in big_plan()]
    assert times == sorted(times)


def test_duplicate_repeats_an_earlier_valid_event() -> None:
    seen_valid_ids: set[object] = set()
    duplicates = 0
    for send in big_plan():
        if send.kind == "valid":
            data = parsed(send)
            assert data is not None
            seen_valid_ids.add(data["event_id"])
        elif send.kind == "duplicate":
            data = parsed(send)
            assert data is not None
            assert data["event_id"] in seen_valid_ids
            duplicates += 1
    assert duplicates > 0


def test_late_events_arrive_one_to_ten_minutes_after_event_time() -> None:
    late = [send for send in big_plan() if send.kind == "late"]
    assert late
    for send in late:
        data = parsed(send)
        assert data is not None
        event_time = datetime.fromisoformat(str(data["event_time"]))
        assert 60 <= (send.send_time - event_time).total_seconds() <= 600


def test_only_malformed_sends_fail_the_field_check() -> None:
    for send in big_plan():
        if send.kind == "malformed":
            assert not is_valid_event_text(send.text)
        else:
            assert is_valid_event_text(send.text)


def test_malformed_covers_broken_json_and_bad_fields() -> None:
    malformed = [send for send in big_plan() if send.kind == "malformed"]
    assert [send for send in malformed if parsed(send) is None]
    assert [send for send in malformed if parsed(send) is not None]


def test_log_lines_have_the_right_fields_and_values() -> None:
    plan = big_plan()
    lines = [json.loads(line) for line in ground_truth_lines(plan)]
    for send, line in zip(plan, lines, strict=True):
        assert set(line) == {"seq", "kind", "event_id", "event_time", "send_time"}
        assert line["kind"] == send.kind
        assert line["send_time"].endswith("Z")
        data = parsed(send)
        if data is None:
            assert line["event_id"] is None
            assert line["event_time"] is None
        else:
            assert line["event_id"] == data.get("event_id")


def test_field_check_rejects_known_bad_examples() -> None:
    good = json.dumps(generate_events(1, 1, START, STEP)[0])
    assert is_valid_event_text(good)
    assert not is_valid_event_text(good[:-12])
    assert not is_valid_event_text("[]")
    data = json.loads(good)
    for field, value in (("schema_version", "two"), ("price", "abc"), ("event_type", "refund")):
        assert not is_valid_event_text(json.dumps({**data, field: value}))
    del data["event_id"]
    assert not is_valid_event_text(json.dumps(data))
