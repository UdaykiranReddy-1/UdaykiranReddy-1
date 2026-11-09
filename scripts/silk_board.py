#!/usr/bin/env python3
"""Draw Silk Board junction from Uday's public GitHub contribution calendar.

Commits become vehicles on the Outer Ring Road flyover. A day with none
leaves a pothole, or a cow when that day is Sunday. The script writes
light and dark SVGs and refreshes the README figure.

No third-party packages. Animation is SMIL, which GitHub renders inside an
<img>. Run from anywhere:

    python scripts/silk_board.py
"""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CACHE = ROOT / "cache" / "contributions.json"
README = ROOT / "README.md"
IST = ZoneInfo("Asia/Kolkata")
LOGIN_DEFAULT = "UdaykiranReddy-1"

W, H = 1120, 608
# Wheel contact is the top of the asphalt. The hazard fascia hangs below it,
# so potholes stay in the road and never land on the stripes.
GROUND = 268
ROAD_X, ROAD_RIGHT = 28, 1092
SLOT_LEFT, SLOT_RIGHT = 48, 936
ASPHALT_H = 28
FASCIA_H = 14
SOFFIT_H = 12
UNDER_H = 56
ASPHALT_TOP = GROUND
FASCIA_TOP = GROUND + ASPHALT_H
SOFFIT_TOP = FASCIA_TOP + FASCIA_H
UNDER_TOP = SOFFIT_TOP + SOFFIT_H
UNDER_BOTTOM = UNDER_TOP + UNDER_H
VMS_Y, VMS_H = 468, 120

GLYPH_W = {
    "pothole": 42,
    "cow": 70,
    "bike": 44,
    "auto": 58,
    "car": 62,
    "bus": 84,
}
GLYPH_H = {
    "pothole": 16,
    "cow": 50,
    "bike": 40,
    "auto": 54,
    "car": 38,
    "bus": 50,
}
# y of the lowest pixel in each sprite's own coordinates (wheels, hooves).
CONTACT_Y = {
    "cow": 48,
    "bike": 39,
    "auto": 50,
    "car": 34.4,
    "bus": 41.2,
}

FONT = "Inter, Liberation Sans, Helvetica, Arial, sans-serif"

# Hand-placed rooftops. x is the left edge, h is height above the deck.
BUILDINGS = [
    (36, 58, 46, False, False),
    (108, 42, 74, False, False),
    (164, 72, 38, False, False),
    (250, 48, 98, True, False),
    (312, 86, 54, False, False),
    (412, 38, 86, False, True),
    (464, 66, 42, False, False),
    (544, 52, 70, True, False),
    (610, 78, 34, False, False),
    (702, 44, 80, False, False),
    (760, 62, 48, False, False),
    (836, 50, 64, True, False),
]


def xe(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def themes() -> dict[str, dict]:
    light = {
        "night": False,
        "bg0": "#f4eee4",
        "bg1": "#dce7ee",
        "ink": "#221e1a",
        "muted": "#5e574c",
        "faint": "#8d8478",
        "rule": "#d9d0c2",
        "building": "#d4c9b8",
        "building2": "#c6baa8",
        "window": "#8ea3ae",
        "window_lit": "#f6e4bc",
        "tank": "#b7ab9b",
        "mast": "#8d8478",
        "track": "#a3988b",
        "metro": "#f0d56a",
        "metro_ink": "#2a261c",
        "asphalt": "#3c424c",
        "asphalt_top": "#515864",
        "fascia": "#cfc6b6",
        "soffit": "#a39b8e",
        "ground": "#d5cbbd",
        "ground_shade": "#c4b8a6",
        "pillar": "#c9c0b2",
        "pillar_shade": "#aea496",
        "junction": "#2c323b",
        "lane": "#ead9a4",
        "hazard_y": "#e2b431",
        "hazard_k": "#1e1b17",
        "wheel": "#1a1815",
        "hub": "#d9d3c8",
        "spoke": "#f4f0e8",
        "glass": "#c5dde6",
        "auto": "#f2b42a",
        "auto_dark": "#d49216",
        "roof": "#2a2622",
        "bus": "#c44734",
        "bus_dark": "#9a3424",
        "bus_band": "#f3e6d2",
        "cars": ("#f7f4ee", "#3d7a74", "#d06a45"),
        "car_dark": ("#e0d9cc", "#2c5c58", "#a85236"),
        "bike": "#2a2622",
        "rider": "#3a342e",
        "cow": "#f7f3ea",
        "cow_shade": "#e4d9c8",
        "spot": "#3a342e",
        "horn": "#5c4e3c",
        "snout": "#ecd9c8",
        "pothole": "#14171b",
        "rim": "#efe6d6",
        "water": "#3e4a55",
        "sign_bg": "#1e4e89",
        "sign_ink": "#f4f8fb",
        "signal": "#241f1b",
        "red": "#e24b45",
        "amber": "#f0a428",
        "green": "#3c9a56",
        "off": "#4a433c",
        "vms": "#14110e",
        "vms_edge": "#3d362c",
        "amber_text": "#ffb000",
        "amber_dim": "#c4923f",
        "amber_faint": "#8a6a32",
        "shadow": "rgba(28,24,20,0.16)",
        "week_track": "#e6dccf",
        "cat": "#f3efe6",
        "lamp": "#cfc6b6",
        "glow": "#f0b45a",
    }
    dark = {
        "night": True,
        "bg0": "#0c1016",
        "bg1": "#1c2836",
        "ink": "#f4eee4",
        "muted": "#c3b8a8",
        "faint": "#8f877c",
        "rule": "#2c3542",
        "building": "#18202b",
        "building2": "#212a36",
        "window": "#2a3442",
        "window_lit": "#f0c27a",
        "tank": "#2c3542",
        "mast": "#8f877c",
        "track": "#66707c",
        "metro": "#f0d56a",
        "metro_ink": "#241f14",
        "asphalt": "#2a3038",
        "asphalt_top": "#3a424c",
        "fascia": "#3c434c",
        "soffit": "#181c22",
        "ground": "#12161b",
        "ground_shade": "#0e1216",
        "pillar": "#3a424c",
        "pillar_shade": "#2a3038",
        "junction": "#0e1216",
        "lane": "#d9c48a",
        "hazard_y": "#e2b431",
        "hazard_k": "#12100c",
        "wheel": "#0c0d10",
        "hub": "#b7bcc2",
        "spoke": "#e6e8ea",
        "glass": "#b5dbe6",
        "auto": "#f0b429",
        "auto_dark": "#c48a12",
        "roof": "#0e0d0b",
        "bus": "#e15a42",
        "bus_dark": "#b14330",
        "bus_band": "#f3e6d2",
        "cars": ("#f3ecdf", "#5aa39a", "#e8835c"),
        "car_dark": ("#d5cbbd", "#3f7b74", "#c46844"),
        "bike": "#e6dfd2",
        "rider": "#f4eee4",
        "cow": "#f6f1e6",
        "cow_shade": "#ddd2c2",
        "spot": "#2a2622",
        "horn": "#5c4e3c",
        "snout": "#ecd9c8",
        "pothole": "#050607",
        "rim": "#e6dccb",
        "water": "#1c2832",
        "sign_bg": "#1e4e89",
        "sign_ink": "#f4f8fb",
        "signal": "#0e0d0b",
        "red": "#ff5d54",
        "amber": "#ffb000",
        "green": "#5dcc7a",
        "off": "#3a342e",
        "vms": "#0c0b09",
        "vms_edge": "#4a4032",
        "amber_text": "#ffb000",
        "amber_dim": "#d9a441",
        "amber_faint": "#9a7438",
        "shadow": "rgba(0,0,0,0.35)",
        "week_track": "#2a313c",
        "cat": "#f0e2c0",
        "lamp": "#d8d0c4",
        "glow": "#ffb45a",
    }
    return {"light": light, "dark": dark}


def http_json(method: str, url: str, token: str, payload: dict | None = None, timeout: int = 30):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "uday-silk-board",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read().decode()
            return res.status, json.loads(body) if body else {}, dict(res.headers)
    except urllib.error.HTTPError as err:
        raw = err.read().decode(errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"message": raw[:300]}
        return err.code, parsed, dict(err.headers)


def github_token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Set GITHUB_TOKEN. The action uses the workflow token.") from exc


def profile_login() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in repo:
        return repo.split("/", 1)[0]
    return os.environ.get("PROFILE_LOGIN", LOGIN_DEFAULT)


def fetch_days(token: str, login: str, today: date) -> list[dict]:
    start = today - timedelta(days=50)
    end = today + timedelta(days=1)
    query = """
    query($login:String!,$from:DateTime!,$to:DateTime!){
      user(login:$login){
        contributionsCollection(from:$from,to:$to){
          contributionCalendar{
            weeks{ contributionDays{ date contributionCount } }
          }
        }
      }
    }
    """
    status, payload, _ = http_json(
        "POST",
        "https://api.github.com/graphql",
        token,
        {
            "query": query,
            "variables": {
                "login": login,
                "from": f"{start.isoformat()}T00:00:00+05:30",
                "to": f"{end.isoformat()}T00:00:00+05:30",
            },
        },
    )
    user = (payload.get("data") or {}).get("user") if isinstance(payload, dict) else None
    if status != 200 or not user:
        message = payload.get("message") if isinstance(payload, dict) else payload
        raise SystemExit(f"Contribution query failed (HTTP {status}): {message}")
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    raw = []
    for week in weeks:
        for day in week["contributionDays"]:
            raw.append({"date": day["date"], "count": int(day["contributionCount"])})
    return build_window(raw, today)


def build_window(raw: list[dict], today: date, n: int = 28) -> list[dict]:
    by_date = {item["date"]: int(item["count"]) for item in raw}
    window = []
    for offset in range(n - 1, -1, -1):
        day = today - timedelta(days=offset)
        key = day.isoformat()
        window.append({"date": key, "count": by_date.get(key, 0)})
    return window


def spec_for(count: int, empty_kind: str) -> list[tuple[str, int]]:
    """Glyphs in a day, left to right. The second number tucks under the previous glyph."""
    if count <= 0:
        return [(empty_kind, 0)]
    if count == 1:
        return [("bike", 0)]
    if count == 2:
        return [("auto", 0)]
    if count == 3:
        return [("auto", 0), ("bike", 14)]
    if count == 4:
        return [("car", 0), ("bike", 12)]
    if count <= 6:
        return [("car", 0), ("auto", 20)]
    if count <= 11:
        return [("bus", 0), ("car", 30)]
    return [("bus", 0), ("car", 44), ("auto", 42)]


def packed_width(spec: list[tuple[str, int]]) -> int:
    total = 0
    for index, (kind, overlap) in enumerate(spec):
        width = GLYPH_W[kind]
        total += width if index == 0 else max(8, width - overlap)
    return total


def cow_indexes(days: list[dict]) -> set[int]:
    """One cow on an empty Sunday. If Sunday has commits, one cow on a middle empty day."""
    cows = set()
    empties = []
    for index, day in enumerate(days):
        if day["count"] > 0:
            continue
        empties.append(index)
        if date.fromisoformat(day["date"]).weekday() == 6:
            cows.add(index)
    if not cows and empties:
        cows.add(empties[len(empties) // 2])
    return cows


def empty_kind(days: list[dict], index: int) -> str:
    if days[index]["count"] > 0:
        return ""
    return "cow" if index in cow_indexes(days) else "pothole"


def status_of(days: list[dict]) -> str:
    total = sum(day["count"] for day in days)
    today = days[-1]["count"]
    peak = max(day["count"] for day in days)
    if total == 0:
        return "EMPTY"
    if today >= 7 or total >= 14:
        return "GRIDLOCK"
    if peak >= 7 and today == 0:
        return "CLEARING"
    if total >= 4:
        return "CRAWLING"
    return "LIGHT"


def eta_minutes(days: list[dict], status: str) -> int:
    total = sum(day["count"] for day in days)
    peak = max(day["count"] for day in days)
    if status == "EMPTY":
        return 3
    if status == "LIGHT":
        return 8 + total
    if status == "CRAWLING":
        return 16 + total
    if status == "CLEARING":
        return 12 + peak * 2
    return 30 + total


def _peak(days: list[dict]) -> dict:
    return max(days, key=lambda day: (day["count"], day["date"]))


def _today_clause(day: dict, kind: str) -> str:
    if day["count"] <= 0:
        return "Today is a cow." if kind == "cow" else "Today is a pothole."
    lead = spec_for(day["count"], "pothole")[0][0]
    names = {"bike": "a bike", "auto": "an auto", "car": "a car", "bus": "a bus"}
    if day["count"] == 1:
        return f"Today is {names[lead]}."
    return f"Today added {day['count']}, led by {names[lead]}."


def caption(days: list[dict]) -> dict:
    """Funny, but every number comes from the seven-day window."""
    status = status_of(days)
    eta = eta_minutes(days, status)
    total = sum(day["count"] for day in days)
    peak = _peak(days)
    peak_when = date.fromisoformat(peak["date"]).strftime("%A")
    today = days[-1]
    today_kind = empty_kind(days, len(days) - 1)
    today_clause = _today_clause(today, today_kind)
    if status == "EMPTY":
        detail = "Nothing in the last 7 days. A cow has the carriageway."
    elif status == "LIGHT":
        noun = "vehicle" if total == 1 else "vehicles"
        detail = f"{total} {noun} this week, and nobody is honking. {today_clause}"
    elif status == "CLEARING":
        detail = f"{peak_when} left {peak['count']} vehicles in the box. {today_clause}"
    elif status == "CRAWLING":
        detail = f"{total} commits are queued on the flyover. {today_clause}"
    else:
        detail = (
            f"{total} this week, peak {peak['count']} on {peak_when}. "
            "The signal has given up."
        )
    headline = f"{status}  ·  ETA {eta} MIN"
    alt = (
        f"Silk Board junction in Bengaluru. Traffic status {status}, "
        f"ETA {eta} minutes. {detail} "
        "Vehicles stand in for GitHub contributions over the last 7 days."
    )
    return {
        "status": status,
        "eta": eta,
        "headline": headline,
        "detail": detail,
        "alt": alt,
        "total": total,
    }


def weeks_of(days: list[dict]) -> list[dict]:
    tail = days[-28:]
    buckets = []
    for index in range(0, 28, 7):
        chunk = tail[index : index + 7]
        buckets.append(
            {
                "start": chunk[0]["date"],
                "total": sum(day["count"] for day in chunk),
            }
        )
    return buckets


def slot_geometry(n: int = 7) -> list[dict]:
    width = (SLOT_RIGHT - SLOT_LEFT) / n
    return [
        {
            "x": SLOT_LEFT + index * width,
            "w": width,
            "cx": SLOT_LEFT + index * width + width / 2,
        }
        for index in range(n)
    ]


def layout(days: list[dict]) -> list[dict]:
    slots = slot_geometry(len(days))
    cows = cow_indexes(days)
    placed = []
    for index, (day, slot) in enumerate(zip(days, slots)):
        kind = "cow" if index in cows else "pothole"
        spec = spec_for(day["count"], kind if day["count"] <= 0 else "pothole")
        width = packed_width(spec)
        glyphs = []
        cursor = slot["cx"] - width / 2
        for glyph_index, (name, overlap) in enumerate(spec):
            glyph_w = GLYPH_W[name]
            x = cursor if glyph_index == 0 else cursor - overlap
            glyphs.append({"kind": name, "x": x, "w": glyph_w})
            cursor = x + glyph_w
        placed.append(
            {
                "day": day,
                "slot": slot,
                "glyphs": glyphs,
                "packed": width,
                "jam": day["count"] >= 7,
            }
        )
    return placed


def wrap(text: str, limit: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and len(trial) > limit:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines[:3]


# --- sprites ---------------------------------------------------------------

def _wheel(cx: float, cy: float, radius: float, theme: dict, dur: str) -> str:
    return (
        f'<g><animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx:.1f} {cy:.1f}" to="360 {cx:.1f} {cy:.1f}" dur="{dur}" '
        f'repeatCount="indefinite"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{theme["wheel"]}"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius * 0.42:.1f}" fill="{theme["hub"]}"/>'
        f'<path d="M{cx:.1f} {cy - radius + 1.4:.1f} V{cy + radius - 1.4:.1f} '
        f'M{cx - radius + 1.4:.1f} {cy:.1f} H{cx + radius - 1.4:.1f}" '
        f'stroke="{theme["spoke"]}" stroke-width="1.3" fill="none"/>'
        f"</g>"
    )


def _crawl(inner: str, dur: str, begin: str, distance: float) -> str:
    return (
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'values="0 0; {distance:.1f} 0; 0 0" keyTimes="0;0.55;1" dur="{dur}" '
        f'begin="{begin}" repeatCount="indefinite"/>{inner}</g>'
    )


def _brake(x: float, y: float, theme: dict) -> str:
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1" fill="{theme["red"]}">'
        f'<animate attributeName="opacity" values="1;0.15;1" dur="1.1s" '
        f'repeatCount="indefinite"/></circle>'
    )


def sprite_bike(theme: dict, jam: bool) -> str:
    ink = theme["bike"]
    rider = theme["rider"]
    wheels = _wheel(11, 32, 7, theme, "1.1s") + _wheel(34, 32, 7, theme, "1.1s")
    brake = _brake(6, 20, theme) if jam else ""
    return f'''<g>
      <path d="M11 32 L20 18 L30 32" fill="none" stroke="{ink}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
      <path d="M20 18 L33 15 L34 32" fill="none" stroke="{ink}" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M28 20 L34 15 L39 17" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>
      <circle cx="23" cy="11" r="4.1" fill="{rider}"/>
      <path d="M22 15 L19 23" fill="none" stroke="{rider}" stroke-width="2.4" stroke-linecap="round"/>
      <path d="M21 17 L29 19" fill="none" stroke="{rider}" stroke-width="2" stroke-linecap="round"/>
      <circle cx="40" cy="16.5" r="1.5" fill="{theme["amber"]}"/>
      {wheels}{brake}
    </g>'''


def sprite_auto(theme: dict, jam: bool) -> str:
    """Upright cabin, black canopy, big rear wheel, small front wheel on a fork."""
    brake = _brake(8, 28, theme) if jam else ""
    return f'''<g>
      <path d="M14 22 Q16 5 32 4 Q48 5 46 18 L16 20 Z" fill="{theme["roof"]}"/>
      <path d="M8 42 V24 Q8 18 16 18 H38 L44 24 H50 Q56 26 56 32 V38 Q56 42 50 42 H10 Q8 42 8 42Z" fill="{theme["auto"]}"/>
      <path d="M34 8 L44 7 L46 18 H34 Z" fill="{theme["glass"]}"/>
      <path d="M16 22 H30 V34 H16 Z" fill="{theme["roof"]}" opacity="0.16"/>
      <circle cx="23" cy="26" r="3.1" fill="{theme["roof"]}"/>
      <path d="M9 34 H46" stroke="{theme["roof"]}" stroke-width="4" stroke-linecap="round"/>
      <path d="M44 30 L52 42" stroke="{theme["roof"]}" stroke-width="2.2" fill="none" stroke-linecap="round"/>
      <circle cx="54" cy="32" r="2" fill="{theme["hub"]}"/>
      {_wheel(18, 42, 8, theme, "1.5s")}
      {_wheel(50, 44, 6, theme, "1.5s")}
      {brake}
    </g>'''


def sprite_car(theme: dict, jam: bool, variant: int) -> str:
    body = theme["cars"][variant % 3]
    dark = theme["car_dark"][variant % 3]
    brake = _brake(8, 20, theme) if jam else ""
    return f'''<g>
      <path d="M6 28 H56 Q60 28 60 24 V22 H6 Z" fill="{dark}"/>
      <path d="M8 23 H54 Q58 23 58 20 V18 H10 Q8 18 8 20 Z" fill="{body}"/>
      <path d="M18 18 L23 8 H40 L46 18 Z" fill="{body}"/>
      <path d="M24 10 H32 L30 17 H22 Z" fill="{theme["glass"]}"/>
      <path d="M34 10 H39 L43 17 H34 Z" fill="{theme["glass"]}"/>
      <circle cx="56" cy="20" r="1.7" fill="{theme["amber"]}"/>
      {_wheel(18, 28, 6.4, theme, "1.7s")}
      {_wheel(46, 28, 6.4, theme, "1.7s")}
      {brake}
    </g>'''


def sprite_bus(theme: dict, jam: bool) -> str:
    windows = []
    for left in (12, 24, 36, 48):
        windows.append(
            f'<rect x="{left}" y="12" width="8" height="9" rx="1" fill="{theme["glass"]}"/>'
        )
    brake = _brake(8, 18, theme) if jam else ""
    return f'''<g>
      <rect x="4" y="6" width="76" height="28" rx="3" fill="{theme["bus"]}"/>
      <rect x="4" y="22" width="76" height="5" fill="{theme["bus_band"]}"/>
      <rect x="6" y="8" width="18" height="5" rx="1" fill="{theme["bus_dark"]}"/>
      {''.join(windows)}
      <rect x="62" y="12" width="8" height="18" rx="1" fill="{theme["bus_dark"]}"/>
      <rect x="74" y="12" width="4" height="8" fill="{theme["glass"]}"/>
      <circle cx="78" cy="26" r="1.6" fill="{theme["amber"]}"/>
      {_wheel(22, 34, 7.2, theme, "2.1s")}
      {_wheel(64, 34, 7.2, theme, "2.1s")}
      {brake}
    </g>'''


def sprite_cow(theme: dict) -> str:
    """Zebu profile: shoulder hump, horns, bell. Facing the queue, not the signal."""
    return f'''<g>
      <ellipse cx="42" cy="28" rx="20" ry="11" fill="{theme["cow"]}"/>
      <ellipse cx="30" cy="18" rx="9" ry="7" fill="{theme["cow"]}"/>
      <ellipse cx="36" cy="26" rx="5" ry="3.4" fill="{theme["spot"]}"/>
      <ellipse cx="50" cy="24" rx="3.2" ry="2.3" fill="{theme["spot"]}"/>
      <circle cx="16" cy="24" r="8.4" fill="{theme["cow"]}"/>
      <ellipse cx="7" cy="27" rx="5.2" ry="3.5" fill="{theme["snout"]}"/>
      <circle cx="5" cy="26.2" r="0.7" fill="{theme["spot"]}"/>
      <circle cx="8" cy="26.2" r="0.7" fill="{theme["spot"]}"/>
      <ellipse cx="18" cy="16" rx="2.6" ry="4.2" fill="{theme["cow_shade"]}"/>
      <path d="M12 16 Q8 6 15 12" fill="none" stroke="{theme["horn"]}" stroke-width="2" stroke-linecap="round"/>
      <path d="M18 14 Q22 4 26 12" fill="none" stroke="{theme["horn"]}" stroke-width="2" stroke-linecap="round"/>
      <circle cx="13" cy="23" r="1.1" fill="{theme["spot"]}"/>
      <circle cx="12" cy="32" r="2.1" fill="{theme["amber"]}"/>
      <rect x="28" y="36" width="4.2" height="12" rx="1.4" fill="{theme["cow_shade"]}"/>
      <rect x="35" y="36" width="4.2" height="12" rx="1.4" fill="{theme["spot"]}"/>
      <rect x="46" y="36" width="4.2" height="12" rx="1.4" fill="{theme["cow_shade"]}"/>
      <rect x="53" y="36" width="4.2" height="12" rx="1.4" fill="{theme["spot"]}"/>
      <g>
        <animateTransform attributeName="transform" type="rotate" values="-12 60 22; 18 60 22; -12 60 22" dur="2.6s" repeatCount="indefinite"/>
        <path d="M58 24 Q70 16 66 36" fill="none" stroke="{theme["spot"]}" stroke-width="1.8" stroke-linecap="round"/>
        <ellipse cx="66" cy="37" rx="2.4" ry="1.8" fill="{theme["spot"]}"/>
      </g>
    </g>'''


def sprite_pothole(theme: dict, variant: int) -> str:
    """Dark crater, a short broken lip, and a crack. The rim does not close."""
    shift = (0, 4, -3)[variant % 3]
    cx = 16 + shift
    return f'''<g>
      <circle cx="{cx}" cy="9" r="6.2" fill="{theme["pothole"]}"/>
      <path d="M{cx - 7} 7 A 7 7 0 0 1 {cx + 1} 3.2" fill="none" stroke="{theme["rim"]}" stroke-width="2" stroke-linecap="round"/>
      <line x1="{cx + 5}" y1="11" x2="{cx + 16}" y2="14" stroke="{theme["rim"]}" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="{cx - 4}" y1="13" x2="{cx - 10}" y2="16" stroke="{theme["rim"]}" stroke-width="1.3" stroke-linecap="round"/>
      <rect x="{cx + 12}" y="5" width="5" height="2.2" fill="{theme["rim"]}" transform="rotate({12 + shift} {cx + 14} 6)"/>
    </g>'''


def glyph_svg(kind: str, theme: dict, jam: bool, variant: int) -> str:
    if kind == "bike":
        return sprite_bike(theme, jam)
    if kind == "auto":
        return sprite_auto(theme, jam)
    if kind == "car":
        return sprite_car(theme, jam, variant)
    if kind == "bus":
        return sprite_bus(theme, jam)
    if kind == "cow":
        return sprite_cow(theme)
    return sprite_pothole(theme, variant)


# --- scene -----------------------------------------------------------------

def _buildings(theme: dict) -> str:
    parts = []
    night = theme["night"]
    for index, (x, width, height, tank, mast) in enumerate(BUILDINGS):
        top = ASPHALT_TOP - height
        fill = theme["building"] if index % 2 == 0 else theme["building2"]
        parts.append(
            f'<rect x="{x}" y="{top}" width="{width}" height="{height + 8}" fill="{fill}"/>'
        )
        cols = max(2, width // 14)
        rows = max(2, (height - 12) // 12)
        for row in range(rows):
            for col in range(cols):
                lit = (index + col * 2 + row) % (3 if night else 8) == 0
                color = theme["window_lit"] if lit else theme["window"]
                opacity = "0.95" if lit else "0.55"
                wx = x + 6 + col * 12
                wy = top + 8 + row * 12
                if wx + 5 < x + width - 4:
                    parts.append(
                        f'<rect x="{wx}" y="{wy}" width="5" height="6" fill="{color}" opacity="{opacity}"/>'
                    )
        if tank:
            cx = x + width / 2
            parts.append(
                f'<rect x="{cx - 8:.1f}" y="{top - 14}" width="16" height="14" fill="{theme["tank"]}"/>'
                f'<ellipse cx="{cx:.1f}" cy="{top - 14}" rx="8" ry="3" fill="{theme["building"]}"/>'
            )
        if mast:
            cx = x + width / 2
            parts.append(
                f'<rect x="{cx - 1:.1f}" y="{top - 26}" width="2" height="26" fill="{theme["mast"]}"/>'
                f'<path d="M{cx - 7:.1f} {top - 18} H{cx + 7:.1f} M{cx - 4:.1f} {top - 24} H{cx + 4:.1f}" '
                f'stroke="{theme["mast"]}" stroke-width="1"/>'
            )
    return "".join(parts)


def _metro(theme: dict) -> str:
    y = 150
    cars = []
    for index, origin in enumerate((0, 32, 64)):
        cars.append(
            f'<rect x="{origin}" y="0" width="28" height="16" rx="2" fill="{theme["metro"]}"/>'
            f'<rect x="{origin + 3}" y="3" width="7" height="6" fill="{theme["metro_ink"]}"/>'
            f'<rect x="{origin + 13}" y="3" width="7" height="6" fill="{theme["metro_ink"]}"/>'
        )
        if index:
            cars.append(
                f'<rect x="{origin - 4}" y="7" width="4" height="3" fill="{theme["metro_ink"]}"/>'
            )
    return (
        f'<g>'
        f'<line x1="24" y1="{y}" x2="1096" y2="{y}" stroke="{theme["track"]}" stroke-width="2"/>'
        f'<line x1="24" y1="{y + 5}" x2="1096" y2="{y + 5}" stroke="{theme["track"]}" stroke-width="1" opacity="0.7"/>'
        f'<g><animateTransform attributeName="transform" type="translate" '
        f'from="160 {y - 22}" to="1180 {y - 22}" dur="28s" repeatCount="indefinite"/>'
        f'{"".join(cars)}</g></g>'
    )


def _hazard(theme: dict) -> str:
    parts = []
    x = ROAD_X
    index = 0
    while x < ROAD_RIGHT:
        color = theme["hazard_y"] if index % 2 == 0 else theme["hazard_k"]
        width = min(12, ROAD_RIGHT - x)
        parts.append(
            f'<rect x="{x:.1f}" y="{FASCIA_TOP}" width="{width:.1f}" height="{FASCIA_H}" fill="{color}"/>'
        )
        x += 12
        index += 1
    return "".join(parts)


def _lamps(theme: dict) -> str:
    parts = []
    head = GROUND - 36
    for x in (160, 420, 680):
        parts.append(
            f'<rect x="{x}" y="{head}" width="3" height="{GROUND - head}" fill="{theme["pillar_shade"]}"/>'
            f'<rect x="{x - 10}" y="{head - 2}" width="22" height="4" rx="1" fill="{theme["pillar_shade"]}"/>'
            f'<circle cx="{x + 12}" cy="{head}" r="3.4" fill="{theme["glow"] if theme["night"] else theme["lamp"]}"/>'
        )
        if theme["night"]:
            parts.append(
                f'<ellipse cx="{x + 6}" cy="{GROUND + 10}" rx="70" ry="10" fill="{theme["glow"]}" opacity="0.22"/>'
            )
    return "".join(parts)


def _signal(theme: dict, status: str) -> str:
    lit = {"EMPTY": "green", "LIGHT": "green", "CRAWLING": "amber", "CLEARING": "amber", "GRIDLOCK": "red"}[
        status
    ]
    top = GROUND - 86
    lamps = [("red", 14), ("amber", 30), ("green", 46)]
    circles = []
    for name, dy in lamps:
        cy = top + dy
        color = theme[name] if name == lit else theme["off"]
        extra = ""
        if name == lit:
            extra = (
                f'<circle cx="968" cy="{cy}" r="8" fill="{color}" opacity="0.28">'
                f'<animate attributeName="opacity" values="0.35;0.12;0.35" dur="1.8s" repeatCount="indefinite"/>'
                f"</circle>"
            )
        circles.append(extra + f'<circle cx="968" cy="{cy}" r="4.2" fill="{color}"/>')
    return (
        f'<rect x="1004" y="{top}" width="4" height="{FASCIA_TOP - top}" fill="{theme["signal"]}"/>'
        f'<rect x="956" y="{top}" width="52" height="4" fill="{theme["signal"]}"/>'
        f'<rect x="956" y="{top + 4}" width="24" height="56" rx="3" fill="{theme["signal"]}"/>'
        f'{"".join(circles)}'
        f'<rect x="1016" y="{top + 14}" width="92" height="50" rx="3" fill="{theme["sign_bg"]}"/>'
        f'<rect x="1020" y="{top + 18}" width="84" height="42" rx="2" fill="none" stroke="{theme["sign_ink"]}" stroke-width="1" opacity="0.45"/>'
        f'<text x="1028" y="{top + 36}" fill="{theme["sign_ink"]}" font-size="12" font-weight="700">SILK BOARD</text>'
        f'<text x="1028" y="{top + 52}" fill="{theme["sign_ink"]}" font-size="10" opacity="0.9">HOSUR ROAD</text>'
    )


def _header(theme: dict, days: list[dict], generated: date) -> str:
    stamp = f"{generated.day} {generated.strftime('%b %Y').upper()}"
    buckets = weeks_of(days)
    bars = []
    max_total = max(bucket["total"] for bucket in buckets) or 1
    bar_w, gap, max_h, bar_bottom = 14, 8, 16, 96
    origin = 1084 - (4 * bar_w + 3 * gap)
    for index, bucket in enumerate(buckets):
        total = bucket["total"]
        height = 3 if total == 0 else max(6, round(max_h * total / max_total))
        if total >= 8:
            color = theme["bus"]
        elif total > 0:
            color = theme["amber"]
        else:
            color = theme["week_track"]
        x = origin + index * (bar_w + gap)
        y = bar_bottom - height
        bars.append(
            f'<rect x="{x}" y="{bar_bottom - max_h}" width="{bar_w}" height="{max_h}" rx="1.5" fill="{theme["week_track"]}"/>'
        )
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{height}" rx="1.5" fill="{color}"/>')
        if total:
            bars.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{y - 4}" text-anchor="middle" '
                f'fill="{theme["muted"]}" font-size="9">{total}</text>'
            )
    return (
        f'<text x="36" y="40" fill="{theme["ink"]}" font-size="28" font-weight="700" letter-spacing="1.5">SILK BOARD</text>'
        f'<text x="36" y="62" fill="{theme["muted"]}" font-size="13">Outer Ring Road · last 7 days of public commits</text>'
        f'<text x="1084" y="32" text-anchor="end" fill="{theme["ink"]}" font-size="14" font-weight="700">{xe(stamp)}</text>'
        f'<text x="1084" y="48" text-anchor="end" fill="{theme["faint"]}" font-size="11" letter-spacing="1.4">BENGALURU</text>'
        f'<text x="{origin - 8}" y="94" text-anchor="end" fill="{theme["faint"]}" font-size="9" letter-spacing="0.8">4 WKS</text>'
        f'{"".join(bars)}'
        f'<line x1="36" y1="112" x2="1084" y2="112" stroke="{theme["rule"]}" stroke-width="1"/>'
    )


def _labels(theme: dict, placed: list[dict]) -> str:
    parts = []
    for group in placed:
        day = date.fromisoformat(group["day"]["date"])
        cx = group["slot"]["cx"]
        count = group["day"]["count"]
        if count >= 7:
            count_fill = theme["bus"] if not theme["night"] else theme["red"]
        elif count > 0:
            count_fill = theme["amber"]
        else:
            count_fill = theme["faint"]
        base = UNDER_BOTTOM + 22
        parts.append(
            f'<text x="{cx:.1f}" y="{base}" text-anchor="middle" fill="{theme["faint"]}" font-size="10" letter-spacing="0.6">{day.strftime("%a").upper()}</text>'
            f'<text x="{cx:.1f}" y="{base + 16}" text-anchor="middle" fill="{theme["ink"]}" font-size="12" font-weight="700">{day.day} {day.strftime("%b").upper()}</text>'
            f'<text x="{cx:.1f}" y="{base + 32}" text-anchor="middle" fill="{count_fill}" font-size="11">{count}</text>'
        )
    return "".join(parts)


def _vms(theme: dict, info: dict) -> str:
    detail = wrap(info["detail"], 92)
    legend = "1 bike   ·   2-3 auto   ·   4-6 cars   ·   7+ a bus in the box   ·   0 a cow or a pothole"
    lines = [
        f'<text x="56" y="{VMS_Y + 46}" fill="{theme["amber_text"]}" font-size="20" font-weight="700" letter-spacing="0.6">{xe(info["headline"])}</text>'
    ]
    for index, line in enumerate(detail):
        lines.append(
            f'<text x="56" y="{VMS_Y + 72 + index * 18}" fill="{theme["amber_dim"]}" font-size="14">{xe(line)}</text>'
        )
    lines.append(
        f'<text x="56" y="{VMS_Y + VMS_H - 14}" fill="{theme["amber_faint"]}" font-size="11">{xe(legend)}</text>'
    )
    return (
        f'<rect x="28" y="{VMS_Y}" width="1064" height="{VMS_H}" rx="8" fill="{theme["vms"]}"/>'
        f'<rect x="34" y="{VMS_Y + 6}" width="1052" height="{VMS_H - 12}" rx="5" fill="none" stroke="{theme["vms_edge"]}" stroke-width="1"/>'
        f'<circle cx="52" cy="{VMS_Y + 20}" r="3" fill="{theme["green"]}"/>'
        f'<text x="62" y="{VMS_Y + 24}" fill="{theme["amber_faint"]}" font-size="11" letter-spacing="1.2">SILK BOARD VMS</text>'
        + "".join(lines)
    )


def render_svg(days: list[dict], theme_name: str, generated: date) -> str:
    """days is a 28-day window ending on `generated`, oldest first."""
    if len(days) < 28:
        raise ValueError("expected a 28-day window")
    theme = themes()[theme_name]
    road_days = days[-7:]
    info = caption(road_days)
    placed = layout(road_days)
    title = xe(f"Silk Board · {info['headline']}")
    desc = xe(info["alt"])

    glyphs = []
    car_variant = 0
    for group_index, group in enumerate(placed):
        for glyph in group["glyphs"]:
            kind = glyph["kind"]
            width = GLYPH_W[kind]
            height = GLYPH_H[kind]
            jam = group["jam"] and kind in {"bus", "car", "auto", "bike"}
            body = glyph_svg(kind, theme, jam, car_variant + group_index)
            if kind == "car":
                car_variant += 1
            if kind == "pothole":
                hole_y = ASPHALT_TOP + 4
                glyphs.append(
                    f'<g transform="translate({glyph["x"]:.1f} {hole_y:.1f})">{body}</g>'
                )
                continue
            # Ground-anchored: local sprite bottom sits on GROUND.
            begin = f"-{group_index * 0.35:.2f}s"
            if kind == "cow":
                inner = body
            else:
                distance = 2.5 if jam else 5
                dur = {"bus": "4.8s", "car": "3.6s", "auto": "3s", "bike": "2.4s"}[kind]
                inner = _crawl(body, dur, begin, distance)
            # Drop the sprite so its wheels or hooves sit on the asphalt.
            drop = height - CONTACT_Y[kind]
            shadow = (
                f'<ellipse cx="{width / 2:.1f}" cy="{height - 1:.1f}" rx="{width * 0.32:.1f}" '
                f'ry="2.4" fill="{theme["shadow"]}"/>'
            )
            glyphs.append(
                f'<g transform="translate({glyph["x"]:.1f} {GROUND - height})">{shadow}'
                f'<g transform="translate(0 {drop:.1f})">{inner}</g></g>'
            )

    mid = (UNDER_TOP + UNDER_BOTTOM) / 2
    junction = (
        f'<path d="M1006 {UNDER_TOP} H1074 L1088 {UNDER_BOTTOM} H992 Z" fill="{theme["junction"]}"/>'
        f'<line x1="1018" y1="{mid + 8:.0f}" x2="1062" y2="{mid + 8:.0f}" stroke="{theme["lane"]}" '
        f'stroke-width="2" stroke-dasharray="7 6" opacity="0.75"/>'
        f'<text x="1040" y="{mid - 2:.0f}" text-anchor="middle" fill="{theme["lane"]}" '
        f'font-size="12" letter-spacing="1.6">HOSUR RD</text>'
    )
    pillars = []
    for x, pw in ((110, 14), (300, 14), (500, 14), (700, 14), (984, 16), (1080, 16)):
        pillars.append(
            f'<rect x="{x}" y="{SOFFIT_TOP}" width="{pw}" height="{UNDER_BOTTOM - SOFFIT_TOP}" fill="{theme["pillar"]}"/>'
            f'<rect x="{x}" y="{SOFFIT_TOP}" width="4" height="{UNDER_BOTTOM - SOFFIT_TOP}" fill="{theme["pillar_shade"]}"/>'
        )

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">',
        "<title>" + title + "</title>",
        "<desc>" + desc + "</desc>",
        "<style><![CDATA[",
        "@media (prefers-reduced-motion: reduce) { animate, animateTransform { display: none; } }",
        "]]></style>",
        "<defs>",
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{theme["bg0"]}"/>',
        f'<stop offset="0.72" stop-color="{theme["bg1"]}"/>',
        f'<stop offset="1" stop-color="{theme["bg1"]}"/>',
        "</linearGradient>",
        f'<linearGradient id="deck" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{theme["asphalt_top"]}"/>',
        f'<stop offset="1" stop-color="{theme["asphalt"]}"/>',
        "</linearGradient>",
        "</defs>",
        f'<g font-family="{FONT}">',
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
        _header(theme, days, generated),
        _metro(theme),
        _buildings(theme),
        f'<rect x="{ROAD_X}" y="{UNDER_TOP}" width="{ROAD_RIGHT - ROAD_X}" height="{UNDER_BOTTOM - UNDER_TOP}" fill="{theme["ground"]}"/>',
        f'<rect x="{ROAD_X}" y="{UNDER_TOP}" width="{ROAD_RIGHT - ROAD_X}" height="8" fill="{theme["ground_shade"]}"/>',
        "".join(pillars),
        junction,
        f'<rect x="{ROAD_X}" y="{SOFFIT_TOP}" width="{ROAD_RIGHT - ROAD_X}" height="{SOFFIT_H}" fill="{theme["soffit"]}"/>',
        _hazard(theme),
        f'<rect x="{ROAD_X}" y="{ASPHALT_TOP}" width="{ROAD_RIGHT - ROAD_X}" height="{ASPHALT_H}" fill="url(#deck)"/>',
        f'<rect x="952" y="{ASPHALT_TOP}" width="4" height="{ASPHALT_H}" fill="{theme["cat"]}"/>',
        _lamps(theme),
        "".join(glyphs),
        _signal(theme, info["status"]),
        _labels(theme, placed),
        _vms(theme, info),
        "</g></svg>",
    ]
    return "\n".join(parts) + "\n"


def picture_block(alt: str) -> str:
    safe = html.escape(alt, quote=True)
    return "\n".join(
        [
            "<picture>",
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/silk-board-dark.svg">',
            f'  <img alt="{safe}" src="assets/silk-board-light.svg" width="100%">',
            "</picture>",
        ]
    )


def replace_block(text: str, name: str, inner: str) -> str:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if start not in text or end not in text:
        raise SystemExit(f"README is missing {start} / {end}")
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    return f"{pre}{start}\n{inner.rstrip()}\n{end}{post}"


def write_outputs(days: list[dict], generated: date) -> dict:
    info = caption(days[-7:])
    ASSETS.mkdir(parents=True, exist_ok=True)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    for name in ("light", "dark"):
        svg = render_svg(days, name, generated)
        (ASSETS / f"silk-board-{name}.svg").write_text(svg)
    payload = {
        "login": profile_login(),
        "generated_on": generated.isoformat(),
        "status": info,
        "days": days,
    }
    CACHE.write_text(json.dumps(payload, indent=2) + "\n")
    readme = README.read_text()
    README.write_text(replace_block(readme, "silk-board", picture_block(info["alt"])))
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the Silk Board SVGs.")
    parser.add_argument("--from-json", help="Render from a contributions cache instead of the API.")
    args = parser.parse_args()
    if args.from_json:
        cached = json.loads(Path(args.from_json).read_text())
        days = cached["days"]
        generated = date.fromisoformat(cached.get("generated_on", days[-1]["date"]))
    else:
        today = datetime.now(IST).date()
        days = fetch_days(github_token(), profile_login(), today)
        generated = today
    info = write_outputs(days, generated)
    print(f"{info['headline']} — {info['detail']}")


if __name__ == "__main__":
    main()
