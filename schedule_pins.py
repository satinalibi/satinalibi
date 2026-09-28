#!/usr/bin/env python3
"""Give approved pins a publish date.

    python schedule_pins.py approve <pin-id> [<pin-id> ...]   # mark pins approved
    python schedule_pins.py reject  <pin-id> [<pin-id> ...]   # mark pins rejected
    python schedule_pins.py plan                              # date every approved, undated pin

Approvals and dates live in content/pin-schedule.yml. Only Rabia's approvals go in here:
Pinterest requires the account owner to choose each pin.

Pace ramps up so a new account doesn't look like spam: 5 a day in week one, 8 in week two,
12 in week three, 15 after that. Boards are interleaved so no board gets a burst, and
Take Up Space pins are spread evenly through the mix.
"""
import datetime as dt
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).parent
SCHEDULE = ROOT / "content/pin-schedule.yml"
TODAY = dt.datetime.now(ZoneInfo("America/Toronto")).date()
RAMP = [(7, 5), (14, 8), (21, 12), (10**6, 15)]  # (days since first pin, pins per day)


def load():
    return (yaml.safe_load(SCHEDULE.read_text()) or {}) if SCHEDULE.exists() else {}


def save(data):
    SCHEDULE.write_text("# Pin approvals and publish dates. Managed by schedule_pins.py.\n"
                        + yaml.safe_dump(dict(sorted(data.items())), sort_keys=False))


def all_pins():
    import build  # reuse the post loader so ids match the site exactly
    build.INCLUDE_ALL = True
    return {pin["id"]: dict(pin, section=p["section"]) for p in build.load_posts() for pin in p["pins"]}


def per_day(day, start):
    age = (day - start).days
    return next(n for limit, n in RAMP if age < limit)


def plan():
    data = load()
    pins = all_pins()
    dated = [dt.date.fromisoformat(str(v["publish"])) for v in data.values() if v.get("publish")]
    start = min(dated) if dated else TODAY + dt.timedelta(days=1)
    used = defaultdict(int)
    for d in dated:
        used[d] += 1
    waiting = [pid for pid, v in data.items() if v.get("status") == "approved" and not v.get("publish") and pid in pins]
    # Interleave by board so each day mixes sections
    queues = defaultdict(deque)
    for pid in sorted(waiting):
        queues[pins[pid]["board"]].append(pid)
    order = []
    while any(queues.values()):
        for board in sorted(queues):
            if queues[board]:
                order.append(queues[board].popleft())
    day = max(TODAY + dt.timedelta(days=1), start)
    for pid in order:
        while used[day] >= per_day(day, start):
            day += dt.timedelta(days=1)
        data[pid]["publish"] = day.isoformat()
        used[day] += 1
    save(data)
    print(f"Scheduled {len(order)} pins. Last one goes out {day.isoformat() if order else '-'}.")


def mark(status, ids):
    data = load()
    known = all_pins()
    for pid in ids:
        if pid not in known:
            raise SystemExit(f"Unknown pin id: {pid}")
        entry = data.setdefault(pid, {})
        entry["status"] = status
        entry.setdefault("decided", TODAY.isoformat())
        if status == "rejected":
            entry.pop("publish", None)
    save(data)
    print(f"{status}: {len(ids)} pins")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "plan":
        plan()
    elif cmd in ("approve", "reject"):
        mark("approved" if cmd == "approve" else "rejected", args)
    else:
        raise SystemExit(__doc__)
