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
   MeshCore Public, index 0) is not linked — except under the public-channel rule below.
5. Node positions are not shared (may become an opt-in option later, rounded to ~2 km).

## Statistics

**Client dashboard (one point):** *(done)*
- connection to the server (online, since when), point status (pending / approved / blocked)
- per remote point: messages received from it / sent to it, last activity
- per network (Meshtastic / MeshCore): messages in / out
- messages held back or dropped by the radio limit
- activity over time (hour / day)

**Server dashboard (all points):** `/admin/dashboard` *(done)*
- every point: online / offline, last seen, version, messages in / out
- **who talks to whom**: point A ↔ point B message counts (list + matrix)
- activity over time, refusals by reason (rate limit, duplicate, not approved, …)

## Public-channel rule

The public channel (index 0, created automatically on every radio) is where everyone in an area talks.
Linking busy public channels (e.g. Germany ↔ USA ↔ China) would bring endless noise, so:

1. Blocked by default.
2. Each point **measures** traffic on its local public channel: messages per hour, counted, never read.
3. The server owner sets a **limit** (e.g. ≤ 10 messages/hour, averaged over 24 h) and **grants permission per point**.
4. A point may link its public channel only with permission **and** below the limit, after at least 24 h of
   measurement.
5. If it gets busier than the limit, the link is **paused automatically** and resumes when it is quiet again.

*Status: done.* Server: room **#Public** (managed by the rule, cannot be edited or deleted), per point
**Allow / Deny** on *Manage points*, settings *maximum public traffic* (default 10/h) and *minimum measuring
time* (default 24 h); a paused point resumes below 80 % of the limit. Point: channel 0 may only be linked to
#Public and is relayed only while the server reports the point as active; text that Ura itself put on the air is
not counted as local traffic; measuring time runs from when measuring began (a silent channel counts too).

## Traffic rules and feedback

Goal: a busy group in one place must never flood a group in another place. Quiet channels are not limited.

1. **Channel switches (point owner).** Every linked channel has two switches: *send* (local → Ura) and
   *receive* (Ura → local air). A channel can listen only, talk only, or both.
2. **Busy sender rule (server owner).** A point's channel may send at most *N messages per hour* to a room
   (default 30, rolling hour). Quiet channels never reach it. Above the limit, that channel is **paused** and
   resumes by itself below 80 % of the limit.
3. **Airtime rule (point owner).** Before Ura puts anything on the air, the point checks its own radio:
   *channel busy %* (all radio traffic heard, measured by Meshtastic) and *Ura transmit %* (airtime this
   radio used in the last hour). Above the owner's limits (default 25 % and 5 %), messages from other points
   are **held back** so the local group is not disturbed. MeshCore does not report these values; there only
   the radio limit (messages per minute) applies.
4. **Feedback to the sender (no text stored).** The person who wrote on the linked channel learns what happened:
   - Meshtastic: a reaction on their message — ✅ heard by a radio at another point (that radio's
     transmission was repeated by a neighbour), 📡 reached another point but no radio there confirmed it,
     ❌ not sent — plus a short direct message saying why (paused, busy, no point online, …).
   - MeshCore: a short notice on the channel when a message was not sent (at most one per reason per 10 min).
   The owner can switch feedback off. Reactions and Ura notices are never relayed.
5. Statistics show, per point pair, how many messages were heard on the other side, and each point's
   channel busy % / transmit %.

## Security

- **Option A (now, done):** client ↔ server connection encrypted with TLS (`wss://`). Each point has its own
  key, issued on join and approved by the server owner. The server never stores or shows message text,
  but relays it in memory.
- **Option B (later):** end-to-end encryption between points, so the server cannot read messages at all.
- **Certificates:** without a domain, the server creates its own certificate. On join the client shows the
  server's certificate fingerprint; the point owner compares it once with the fingerprint on the server
  admin page, then the client pins it (refuses any other certificate). With a domain later: Let's Encrypt.
  *(done: server creates `tls.crt`/`tls.key` with openssl on first start, shows the fingerprint on the admin
  and public pages; client "Check certificate" → confirm → pin; mismatch = refuse to connect + warning.)*

## Not part of Ura

Telegram, a message list, sending messages from a web page, public message feeds. Those belong to the
separate project *mesh-bridge*. In Ura, messages come only from the radios.

## Later options (to be specified)

- end-to-end encryption (option B)
- opt-in node map
- …
