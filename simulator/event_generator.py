"""Pure functions that build valid ShopStream click events (design doc 4.6, guide 8.1).

No network, no files, no real clock. The caller passes the time and a seeded random
generator, so the same seed always gives the same events.
"""

import random
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

SCHEMA_VERSION = 2

# (name, weight). The weights are my assumption: most events are page views, few are purchases.
EVENT_TYPES: tuple[tuple[str, int], ...] = (
    ("page_view", 50),
    ("product_view", 25),
    ("add_to_cart", 12),
    ("checkout_start", 8),
    ("purchase", 5),
)
# Buying needs a logged-in user, so these two types are never anonymous.
LOGIN_REQUIRED = frozenset({"checkout_start", "purchase"})
DEVICES: tuple[tuple[str, int], ...] = (("mobile", 60), ("desktop", 30), ("tablet", 10))
COUNTRIES: tuple[tuple[str, int], ...] = (
    ("IN", 70),
    ("US", 10),
    ("GB", 5),
    ("AE", 5),
    ("SG", 5),
    ("DE", 5),
)
ANONYMOUS_RATE = 0.30  # the guide contract example allows up to 0.40 empty user_id
USER_COUNT = 1000
SESSION_COUNT = 5000
PRODUCT_COUNT = 200

Event = dict[str, str | int | None]


def _pick(rng: random.Random, options: tuple[tuple[str, int], ...]) -> str:
    """Pick one name from (name, weight) pairs. More weight means picked more often."""
    names = [name for name, _ in options]
    weights = [weight for _, weight in options]
    return rng.choices(names, weights=weights, k=1)[0]


def price_for_product(product_number: int) -> Decimal:
    """Same product, same price: whole rupees from 100 to 4999."""
    return Decimal(100 + (product_number * 53) % 4900).quantize(Decimal("0.01"))


def format_event_time(moment: datetime) -> str:
    """UTC text with milliseconds and a Z at the end, for example 2026-10-27T10:00:00.000Z."""
    if moment.tzinfo is None:
        raise ValueError("moment must be timezone-aware (use UTC)")
    return moment.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_event(rng: random.Random, now: datetime) -> Event:
    """Build one valid event. It uses only its two inputs, so it is easy to test."""
    event_type = _pick(rng, EVENT_TYPES)
    product_number = rng.randint(1, PRODUCT_COUNT)
    user_id: str | None = f"u_{rng.randint(1, USER_COUNT):05d}"
    if event_type not in LOGIN_REQUIRED and rng.random() < ANONYMOUS_RATE:
        user_id = None
    return {
        "event_id": str(uuid.UUID(int=rng.getrandbits(128), version=4)),
        "event_type": event_type,
        "event_time": format_event_time(now),
        "user_id": user_id,
        "session_id": f"s_{rng.randint(1, SESSION_COUNT):05d}",
        "product_id": f"p_{product_number:04d}",
        "price": str(price_for_product(product_number)),
        "device": _pick(rng, DEVICES),
        "country": _pick(rng, COUNTRIES),
        "schema_version": SCHEMA_VERSION,
    }


def generate_events(seed: int, count: int, start: datetime, step: timedelta) -> list[Event]:
    """Build `count` events, `step` apart, starting at `start`. Same seed, same events."""
    rng = random.Random(seed)
    return [build_event(rng, start + step * i) for i in range(count)]
