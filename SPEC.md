# Ura-mesh — specification

*Every mesh, one world.* This file is the agreed plan. New features are added here first.

## Purpose

Meshtastic and MeshCore carry messages by radio only as far as the waves reach. Groups that cannot reach
each other because of distance or terrain (other cities, other countries) stay apart.

Ura-mesh connects these groups **through a server, in a controlled way**, without disturbing the people in
each group. It is a **private relay between radio groups**, not a chat application.

## Parts

| | **ura-mesh-client** | **ura-mesh-server** |
|---|---|---|
| Runs | At each point, connected to that group's radio (next to the repeater) | Central (Tirana today, could be Germany or anywhere) |
| Used by | The person responsible for that point | The server owner |
| Admin page | Connection to the server, radio settings, linked channel(s), radio limits | All points: approve / block / delete, limits, rooms, one-point-per-area rule |
| Dashboard | Statistics only (see below) | Statistics only (see below) |

## Privacy rules

1. **Message text is never shown and never stored**, on the client or the server. It exists only in memory,
   for the moment it is being relayed.
2. Statistics are **per point** (group), never per person. Radio/user names of individuals are not collected.
3. The server log keeps only: time, from which point, which room, size, delivered to how many points, or
   refused and why.
4. Only channels a point owner links are relayed. The local default channel (Meshtastic primary /
   MeshCore Public, index 0) can never be linked.
5. Node positions are not shared (may become an opt-in option later, rounded to ~2 km).

## Statistics

**Client dashboard (one point):**
- connection to the server (online, since when), point status (pending / approved / blocked)
- per remote point: messages received from it / sent to it, last activity
- per network (Meshtastic / MeshCore): messages in / out
- messages held back or dropped by the radio limit
- activity over time (hour / day)

**Server dashboard (all points):**
- every point: online / offline, last seen, version, messages in / out
- **who talks to whom**: point A ↔ point B message counts
- activity over time, refusals by reason (rate limit, duplicate, not approved, …)

## Security

- **Option A (now):** client ↔ server connection encrypted with TLS (`wss://`). Each point has its own
  key, issued on join and approved by the server owner. The server never stores or shows message text,
  but relays it in memory.
- **Option B (later):** end-to-end encryption between points, so the server cannot read messages at all.
- **Certificates:** without a domain, the server creates its own certificate. On join the client shows the
  server's certificate fingerprint; the point owner compares it once with the fingerprint on the server
  admin page, then the client pins it (refuses any other certificate). With a domain later: Let's Encrypt.

## Not part of Ura

Telegram, a message list, sending messages from a web page, public message feeds. Those belong to the
separate project *mesh-bridge*. In Ura, messages come only from the radios.

## Later options (to be specified)

- end-to-end encryption (option B)
- opt-in node map
- …
