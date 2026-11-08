# Ura link protocol (v1)

Points (ura-mesh-client, called *bridges* in the field names below) connect **out** to the server (ura-mesh-server) over one encrypted WebSocket: `wss://<server>/link`.
The server certificate is self-signed; the client pins its SHA-256 fingerprint (confirmed by a human at join time) and
refuses any other certificate. All frames are JSON objects
with a `type`.

## Joining

A new bridge asks to join with an HTTP request (once):

```
POST /api/join
{ "name": "Tirana Base", "country": "AL", "city": "Tirana", "lat": 41.33, "lon": 19.82,
  "networks": ["mt", "mc"], "contact": "@someone on Telegram", "note": "free text for the hub admin" }

→ 200 { "bridge_id": "b_…", "key": "…", "status": "pending" }
```

The bridge stores `bridge_id` + `key`; the key is shown only once (the hub keeps a hash).
The hub admin then approves or rejects the bridge.

## Session

| Direction | Frame | Meaning |
|---|---|---|
| bridge → hub | `{"type":"hello","bridge_id","key","version":1,"info":{…same fields as join…}}` | First frame. Wrong key → socket closed. |
| hub → bridge | `{"type":"welcome","status","hub":"name","rooms":[{"name","description"}],"public":{…},"allow":{group,public,private,positions}}` | `status` = `pending`, `approved` or `blocked`. Only approved bridges send/receive messages. |
| hub → bridge | `{"type":"status", …same fields as welcome…}` | Sent when the admin changes the bridge (approve, block, rooms, rules). |
| bridge → hub | `{"type":"msg","id","room","net","sender","text"}` | A message heard on a linked channel. `id` is a random id (dedupe). |
| hub → bridge | `{"type":"msg","id","room","net","sender","text","ts","from":{"bridge_id","name","country","city"}}` | A message from another bridge. |
| hub → bridge | `{"type":"ack","id","ok","to":N,"to_points":[{"id","name","country"}],"reason"}` | Result for a `msg` the bridge sent: which points received it, or why it was refused (rate limit, duplicate, not approved, too long). |
| bridge → hub | `{"type":"result","id","outcome","reason","repeats"}` | After putting a relayed message on the air: `heard` (a neighbour repeated it — Meshtastic implicit ACK, or MeshCore repeaters re-sent it), `unheard`, `unknown` or `held` (busy channel, queue full, not open for receiving; `reason` says which). `repeats` (optional): how many different MeshCore repeaters were heard re-sending it. |
| hub → bridge | `{"type":"result","id","outcome","reason","repeats","point":{"id","name","country"}}` | The same report, passed to the point that sent the message, so it can tell the sender (✅ / 📡 / ❌). |
| bridge → hub | `{"type":"nodes","count":N,"shared":[],"public_rate":{"per_hour","measured_hours","count"}}` | Every few minutes: how many nodes the point hears, and how busy its local public channel is (messages counted, never read), and `air`: `{"ch_util","air_tx","busy"}` (Meshtastic channel utilisation %, own transmit airtime %, reason it holds messages back). `shared` stays empty (no positions are shared). |

## Rules the hub enforces

- Only `approved` bridges, and only rooms the bridge belongs to.
- `per_min` messages per minute per bridge (token bucket), `max_bytes` per message.
- Busy-sender rule: at most `source_max_per_hour` messages per bridge per room per rolling hour (every attempt counts);
  above it the channel is paused and resumes below 80 %.
- Duplicate `id`s, and the same text in the same room within 10 minutes, are dropped (stops loops when two
  bridges hear each other's radio).
- Node lists (`positions` frame, `nodes: [{net,id,name,short,lat,lon,heard,own}]`) are passed on unchanged; the server forwards them to the other points as `peer_nodes`.
- **Message text is relayed in memory only. The server never stores, logs or shows it**; the relay log keeps time, point, room, size and result (SPEC.md).

## Rules the bridge follows

- Only channels the owner linked are sent to the hub. Channel 0 (Meshtastic primary / MeshCore Public) can never be linked.
- Messages from the hub go out over the radio as `[CC] Sender: text` (CC = country code), through a
  rate-limited queue set by the bridge owner.
- Text already starting with `[CC] ` (a message another Ura bridge put on the air) is never sent back to the hub.
