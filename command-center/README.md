# Morning Command Center

A small static morning dashboard for Uday Kiran Reddy (Asia/Calcutta). Six panels: Today, Schedule, Reminders, Commute, Quick links, and Focus.

## Open locally

ES modules need a local HTTP server (not `file://`).

From the repo root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Then open [http://127.0.0.1:8765/command-center/](http://127.0.0.1:8765/command-center/).

## Persistence

All state lives in one JSON document in `localStorage` under the key `command-center`. Reminders, focus, quick links, and the day note are editable and survive reload. Weather and commute are sample fetches cached per calendar day. Schedule uses in-document sample events until a calendar is connected.

## Layout

The page follows the composer sketch: storage → commands → compose → shell mount. Panel logic lives in `compose/contributions/`; the shell only mounts slots by `slotId`.
