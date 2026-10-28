"""Build the send plan (duplicates, late, malformed) and the ground-truth log lines.

A send plan is everything the simulator will send, in send order. Pure functions: no
network, no files, no real clock. The same seed gives the same plan.
"""

import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from event_generator import EVENT_TYPES, Event, format_event_time

# My choice inside the guide ranges: duplicates 1 to 2 %, late 2 to 5 %, malformed 0.5 %.
MALFORMED_RATE = 0.005
LATE_RATE = 0.03
DUPLICATE_RATE = 0.015
MIN_LATE_SECONDS = 60
MAX_LATE_SECONDS = 600
MAX_DUPLICATE_GAP_SECONDS = 30

REQUIRED_FIELDS = frozenset(
    {
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
)
# user_id is not removed: anonymous users send the key with an empty value.
REMOVABLE_FIELDS = ("event_id", "event_type", "event_time", "product_id", "price")
ALLOWED_EVENT_TYPES = frozenset(name for name, _ in EVENT_TYPES)


@dataclass(frozen=True)
class PlannedSend:
    """One thing the simulator will send. kind is valid, duplicate, late or malformed."""

    seq: int
    kind: str
    send_time: datetime
    text: str


def is_valid_event_text(text: str) -> bool:
    """The field check: valid JSON, exactly the guide fields, sensible types."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return False
    if not isinstance(data, dict) or set(data) != REQUIRED_FIELDS:
        return False
    version = data["schema_version"]
    if not isinstance(version, int) or isinstance(version, bool):
        return False
    try:
        Decimal(data["price"])
        datetime.fromisoformat(data["event_time"])
        return data["event_type"] in ALLOWED_EVENT_TYPES
    except (InvalidOperation, TypeError, ValueError):
        return False


def break_event(rng: random.Random, event: Event) -> str:
    """Return a broken version of a valid event as text. There are three kinds of damage."""
    variant = rng.choice(("missing_field", "wrong_type", "broken_json"))
    broken = dict(event)
    if variant == "missing_field":
        del broken[rng.choice(REMOVABLE_FIELDS)]
    elif variant == "wrong_type":
        broken["schema_version"] = "two"
    else:
        return json.dumps(event)[:-12]
    return json.dumps(broken)


def build_send_plan(events: list[Event], seed: int) -> list[PlannedSend]:
    """Give every event one fate and return all sends in send-time order.

    Fates are exclusive: malformed, late, duplicate (sent twice) or valid. The same
    events and the same seed always give the same plan.
    """
    rng = random.Random(seed)
    drafts: list[tuple[datetime, int, str, str]] = []
    for event in events:
        event_time = datetime.fromisoformat(str(event["event_time"]))
        text = json.dumps(event)
        roll = rng.random()
        if roll < MALFORMED_RATE:
            drafts.append((event_time, len(drafts), "malformed", break_event(rng, event)))
        elif roll < MALFORMED_RATE + LATE_RATE:
            delay = timedelta(seconds=rng.randint(MIN_LATE_SECONDS, MAX_LATE_SECONDS))
            drafts.append((event_time + delay, len(drafts), "late", text))
        elif roll < MALFORMED_RATE + LATE_RATE + DUPLICATE_RATE:
            drafts.append((event_time, len(drafts), "valid", text))
            gap = timedelta(seconds=rng.randint(1, MAX_DUPLICATE_GAP_SECONDS))
            drafts.append((event_time + gap, len(drafts), "duplicate", text))
        else:
            drafts.append((event_time, len(drafts), "valid", text))
    drafts.sort(key=lambda draft: (draft[0], draft[1]))
    return [
        PlannedSend(seq=number, kind=kind, send_time=send_time, text=text)
        for number, (send_time, _, kind, text) in enumerate(drafts, start=1)
    ]


def ground_truth_line(send: PlannedSend) -> str:
    """One JSON line for the log. event_id and event_time are filled only if the text has them."""
    event_id: object = None
    event_time: object = None
    try:
        data = json.loads(send.text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        event_id = data.get("event_id")
        event_time = data.get("event_time")
    return json.dumps(
        {
            "seq": send.seq,
            "kind": send.kind,
            "event_id": event_id,
            "event_time": event_time,
            "send_time": format_event_time(send.send_time),
        }
    )


def ground_truth_lines(plan: Sequence[PlannedSend]) -> list[str]:
    """One log line per planned send, duplicates and malformed sends included."""
    return [ground_truth_line(send) for send in plan]
