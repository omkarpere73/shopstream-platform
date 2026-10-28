"""Tests for the pure event builder. Run: .venv/bin/pytest simulator -q"""

import random
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from event_generator import (
    EVENT_TYPES,
    LOGIN_REQUIRED,
    PRODUCT_COUNT,
    Event,
    build_event,
    generate_events,
    price_for_product,
)

START = datetime(2026, 10, 27, 10, 0, 0, tzinfo=UTC)
STEP = timedelta(milliseconds=100)
FIELDS = {
    "event_id",
    "event_type",
    "event_time",
    "user_id",
    "session_id",
    "product_id",
    "price",
    "device",
    "country",
    "schema_version",
}


def make(seed: int = 42, count: int = 2000) -> list[Event]:
    return generate_events(seed, count, START, STEP)


def test_same_seed_gives_same_events() -> None:
    assert make(seed=1, count=200) == make(seed=1, count=200)


def test_different_seed_gives_different_events() -> None:
    assert make(seed=1, count=200) != make(seed=2, count=200)


def test_generate_events_returns_the_requested_count() -> None:
    assert len(make(count=7)) == 7


def test_event_has_exactly_the_guide_fields() -> None:
    for event in make(count=50):
        assert set(event) == FIELDS


def test_event_ids_are_unique_uuid4() -> None:
    ids = [str(event["event_id"]) for event in make()]
    assert len(set(ids)) == len(ids)
    assert all(uuid.UUID(event_id).version == 4 for event_id in ids)


def test_all_five_event_types_appear() -> None:
    allowed = {name for name, _ in EVENT_TYPES}
    assert {event["event_type"] for event in make()} == allowed


def test_event_time_is_utc_text_that_follows_the_clock_input() -> None:
    assert [event["event_time"] for event in make(count=3)] == [
        "2026-10-27T10:00:00.000Z",
        "2026-10-27T10:00:00.100Z",
        "2026-10-27T10:00:00.200Z",
    ]


def test_naive_time_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_event(random.Random(1), datetime(2026, 10, 27, 10, 0, 0))


def test_checkout_and_purchase_always_have_a_user() -> None:
    for event in make(count=3000):
        if event["event_type"] in LOGIN_REQUIRED:
            assert event["user_id"] is not None


def test_anonymous_rate_is_below_the_contract_limit() -> None:
    events = make(count=5000)
    rate = sum(event["user_id"] is None for event in events) / len(events)
    assert 0.05 < rate < 0.40


def test_same_product_always_has_the_same_price() -> None:
    first_price_seen: dict[object, object] = {}
    for event in make(count=3000):
        first = first_price_seen.setdefault(event["product_id"], event["price"])
        assert first == event["price"]


def test_price_is_between_100_and_4999_with_two_decimals() -> None:
    for number in range(1, PRODUCT_COUNT + 1):
        price = price_for_product(number)
        assert Decimal("100.00") <= price <= Decimal("4999.00")
        assert price == price.quantize(Decimal("0.01"))


def test_schema_version_is_2() -> None:
    assert {event["schema_version"] for event in make(count=20)} == {2}
