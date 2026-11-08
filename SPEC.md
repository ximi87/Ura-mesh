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
| Menu | The same full menu on every page, server and point alike: 🗺️ Map · 📊 Dashboard · ⚙️ Manage points (server) · 📡 Points ▾ (every approved point, online dot, opens its page) · and on a point also 📊 Status · ⚙️ Admin of that point | (same menu) |

Each point may give its **page address** (Admin → This point, e.g. `https://192.168.99.165:8091/`); it is
sent to the server with the point's info. The server passes the list of approved points (name, country,
online, page address) to every approved point for its menu — never to the public map. Each page still
needs its own login.

## Independence — nobody controls anybody (decided 2026-11-07)

Every point and the server are **separate, self-governed machines**. They only exchange relayed messages and
the rules that apply to them; they monitor what crosses, they never manage each other.

- **The server cannot control a point.** It cannot change a point's settings, switches, checklist, radio or
  password, cannot restart it, cannot read its pages and has no login on it. What the server sends is only:
  its own rules (which rooms exist, what it accepts from that point, whether #Public is open), relayed
  messages and results. A point applies them only where its own owner agreed (channel links, send / receive
  switches, checklist — "both owners" rule) and can leave at any time.
- **A point cannot control the server or other points.** It can only offer messages and its own info; the
  server checks everything against its own rules and may refuse. A point never gets the server's admin data,
  other points' settings, keys or statistics beyond its own deliveries.
- **Each side has its own login, keys and certificate.** Point pages and server pages run over HTTPS, each
  with its own self-signed certificate (fingerprint shown on its own page). Links in the menu are only links:
  opening another page still needs that page's own login.
- Sharing a page address in the Points menu is the point owner's choice (empty = not listed as a link).

## Privacy rules

1. **Message text is never shown and never stored**, on the client or the server. It exists only in memory,
   for the moment it is being relayed.
2. Statistics are **per point** (group), never per person. Radio/user names of individuals are not collected.
3. The server log keeps only: time, from which point, which room, size, delivered to how many points, or
   refused and why.
4. Only channels a point owner links are relayed. The local default channel (Meshtastic primary /
   MeshCore Public, index 0) is not linked — except under the public-channel rule below.
5. Only what the checklist allows crosses (below). Nodes & positions: passed on unchanged, as the radios report them.

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

## Who may connect

Not every repeater may connect: **one point per city, or per place the others cannot reach by radio**
(one-point-per-area rule, server owner approves every point). So a group is represented by one point.

## What may cross — the checklist (decided 2026-11-07)

Every item crosses only if **both** the point owner **and** the server owner allow it. All start **off**,
except group messages on the dedicated Ura channel.

| Item | What it means |
|---|---|
| Group messages | Messages on the linked Ura channel(s) (e.g. channel 1 "Ura") |
| Public channel | The local public channel (channel 0) is linked to the other places' public channels (room #Public) |
| Private messages | Person-to-person messages through the point: `@Name text` to the point's radio |
| Nodes & positions | The radios heard at a point, as they report themselves (name, id, shared position) — to the other points and the server map |

## Public-channel rule

1. **Off until the point owner turns it on** (and the server owner allows the item).
2. Each point counts messages on its local public channel (counted, never read): messages in the last hour.
3. If a group's public channel is **busier than the limit** (server owner sets it, default 10 messages/hour),
   group messages stop crossing for that group — **private messages still work**. It opens again by itself
   below 80 % of the limit.
4. When it pauses / opens again, the group gets **one** short notice on its public channel, e.g.
   `[Ura] Link to other places paused – channel too busy. Private messages still work.` Someone who writes
   while it is paused gets a direct message (at most once per hour).

## Private messages

- Meshtastic private messages are encrypted for one radio, so the point cannot read or forward a normal DM.
  To write to someone at another place, send a **direct message to the point's radio**:
  `@Name text` (or `@Name/Place text` if the name exists at several places).
- The other place's point looks the name up among the radios it hears (Meshtastic long/short name or
  node id, MeshCore contact name) and sends it as a direct message: `[DE] Sender: text`. The person answers
  the same way, with a direct message to their point: `@Sender text`.
- The writer gets the result as a direct message: delivered (the receiving radio acknowledged it),
  sent but not confirmed, or not found. Names pass through the server in memory only, never stored.
- If the public channel is paused, private messages still work (busy-sender and airtime rules still apply).

## Nodes & positions (changed 2026-11-08, owner's decision)

Information goes on **as it comes — nothing is changed**. The radios heard at a point (last 24 hours) are passed
to the other points and to the server map exactly as they report themselves: name, short name, id, and the
position their owner chose to share (no rounding, no hiding; a node that shares no position shows none).
Each point's Status page lists the nodes of the other places; the server map shows them with their names.
Crosses only when the checklist item **Nodes & positions** is on at both points and allowed by the server owner.
Kept in memory only (server: 1 hour), refreshed every 5 minutes.

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
   - **MeshCore "repeated N×".** After a point puts a message on a MeshCore channel, its radio listens for
     30 s for copies of that same message re-sent by repeaters (MeshCore repeaters add their short id to the
     packet's path). Each different repeater counts once. N ≥ 1 = *heard* (✅ for the sender), 0 = *unheard*
     (📡). To recognise its own copy the point decrypts the channel packet in memory and compares it with what
     it sent; nothing is stored or logged. The number N travels with the result, never the text.
5. Statistics show, per point pair, how many messages were heard on the other side (and the most MeshCore
   repeaters seen for one message), and each point's channel busy % / transmit %.

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
- **Point pages over HTTPS (2026-11-07):** each point creates its own self-signed certificate on first start
  (`DATA_DIR/tls.crt` + `tls.key`), serves its Status/Admin pages only over https on WEB_PORT, and shows the
  fingerprint on its Admin page and in its log. `WEB_TLS=0` only behind a reverse proxy that does TLS.

## Not part of Ura

Telegram, a message list, sending messages from a web page, public message feeds. Those belong to the
separate project *mesh-bridge*. In Ura, messages come only from the radios.

## Later options (to be specified)

- end-to-end encryption (option B)
- …
