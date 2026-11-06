# Ura link protocol (v1)

Bridges connect **out** to the Hub over one WebSocket: `ws(s)://<hub>/link`. All frames are JSON objects
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
| hub → bridge | `{"type":"welcome","status","hub":"name","rooms":[{"name","description"}],"limits":{"per_min","max_bytes"}}` | `status` = `pending`, `approved` or `blocked`. Only approved bridges send/receive messages. |
| hub → bridge | `{"type":"status", …same fields as welcome…}` | Sent when the admin changes the bridge (approve, block, rooms, limits). |
| bridge → hub | `{"type":"msg","id","room","net","sender","text"}` | A message heard on a linked channel (or written by the operator). `id` is a random id (dedupe). |
| hub → bridge | `{"type":"msg","id","room","net","sender","text","ts","from":{"bridge_id","name","country","city"}}` | A message from another bridge. |
| hub → bridge | `{"type":"ack","id","ok","to":N,"reason"}` | Result for a `msg` the bridge sent: delivered to N bridges, or rejected (rate limit, duplicate, not approved, too long). |
| bridge → hub | `{"type":"nodes","count":N,"shared":[{"net","name","lat","lon"}]}` | Every few minutes. `shared` only if the bridge owner enabled position sharing; the hub rounds positions to ~2 km anyway. |

## Rules the hub enforces

- Only `approved` bridges, and only rooms the bridge belongs to.
- `per_min` messages per minute per bridge (token bucket), `max_bytes` per message.
- Duplicate `id`s, and the same text in the same room within 10 minutes, are dropped (stops loops when two
  bridges hear each other's radio).
- Bridge positions are rounded to ~1 km, shared node positions to ~2 km.

## Rules the bridge follows

- Only channels the owner linked are sent to the hub. Channel 0 (Meshtastic primary / MeshCore Public) can never be linked.
- Messages from the hub go out over the radio as `[CC] Sender: text` (CC = country code), through a
  rate-limited queue set by the bridge owner.
- Text already starting with `[CC] ` (a message another Ura bridge put on the air) is never sent back to the hub.
