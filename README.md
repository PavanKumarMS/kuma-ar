# kuma-ar — WebAR prototype for Uptime Kuma monitors

A single-page WebAR proof of concept: selected monitors render as 3D "totems"
(status orb + latency bar strip + label) anchored to a printed/displayed marker
card. Works in any modern phone browser (iOS Safari, Android Chrome) — no app,
no WebXR required. Built with [three.js](https://threejs.org/) +
[MindAR](https://hiukim.github.io/mind-ar-js-doc/) image tracking, loaded from CDN.

## Files

- `ar.html` — the whole prototype (data polling + 3D scene + AR).
- `marker.html` — shows the MindAR demo image target full-screen so you can
  point a phone at your desktop monitor (or print it).

## Modes

| Mode | URL | What it does |
|------|-----|--------------|
| Demo (default) | `ar.html` | Six **simulated** monitors — API, database, push, ping, DNS, TCP port — polled every 2 s with fake latency profiles, random outages, and type-specific error messages. Each type has its own 3D shape: sphere (API), stacked cylinders (database), beacon cone with pulse ring (push), spinning octahedron (ping), torus (DNS), cube (TCP). No Kuma server needed. In Kuma mode the monitor `type` from the status page picks the shape automatically. |
| Flat preview | `ar.html?flat=1` | Same 3D scene without camera/AR — for desktop testing. Orbit with the mouse. |
| Kuma | `ar.html?base=https://your-kuma&slug=ar` | Polls a real Uptime Kuma **status page**: `/api/status-page/heartbeat/<slug>` + `/api/status-page/<slug>`. Add monitors to that status page to choose what appears in AR. |

## Quick start (desktop)

```powershell
python -m http.server 8123 --directory C:\git\kuma-ar
# or, if you have Node: npx --yes http-server C:\git\kuma-ar -p 8123 -c-1
# open http://localhost:8123/ar.html?flat=1
```

## Phone AR

Camera access requires **HTTPS** (localhost is exempt, but your phone isn't
localhost). Easiest options:

1. **Tunnel**: `npx --yes cloudflared tunnel --url http://localhost:8123`
   → open the printed `https://…trycloudflare.com/ar.html` on the phone.
2. **Static host**: it's one HTML file — GitHub Pages / S3 / anything works.
3. **Serve from Kuma itself** (best for Kuma mode — same origin, no CORS):
   drop `ar.html` into the server's static dir or add an Express route.

Then: open `marker.html` on your desktop (or print the card), open `ar.html`
on the phone, tap **Start AR**, allow camera, aim at the card.

## Gestures

- **Tap** a totem → detail card (tap is press+release without movement).
- **Swipe left/right** (AR mode) → pans the totem row side to side.
- In flat preview, drag orbits the camera instead (OrbitControls).

## Tap to inspect

Tapping/clicking any totem opens a detail card: status, the error message (in
a red box when DOWN), how long it has been down (computed from the heartbeat
window — `≥` means the outage started before the visible window), uptime, and
a **Re-check now** button that forces an immediate poll.

The card also shows a **24 h timeline** (demo mode: simulated): 48 half-hour
segments colored up/partial/down, a summary line (uptime %, incident count,
minutes down), and tapping a segment shows what happened in that window —
including the error message and when the outage started.

**Error messages in Kuma mode:** the public status-page API deliberately blanks
the heartbeat `msg` field — see `server/model/heartbeat.js` `toPublicJSON()`
(line ~23: `msg: "", // Hide for public`) in the fork. To see real errors
("connect ECONNREFUSED", "Request failed with status code 503", …) in AR,
change that line to pass `this.msg` through — ideally gated behind a token
query param or a per-status-page flag, since error text can leak internal
hostnames on a truly public page. Until then the card shows a hint instead.

## Kuma mode notes

- The status page API is public (no auth) — selection of monitors == what you
  put on the status page.
- If `ar.html` is hosted on a different origin than Kuma, the browser needs
  CORS headers from Kuma (`Access-Control-Allow-Origin`), or just serve the
  page from the Kuma server.
- Heartbeat statuses: 1 = up (green), 0 = down (red, pulsing), 2/3 =
  pending/maintenance (amber). Uptime ring uses the `_24` (24 h) value.

## Next steps beyond the prototype

- Custom marker: compile your own card image with the
  [MindAR image-target compiler](https://hiukim.github.io/mind-ar-js-doc/tools/compile)
  and put a QR code to this page on the same card.
- Tap-to-focus a monitor (raycast), `navigator.vibrate` on status change.
- Multiple cards with different `?slug=` per location/team.
