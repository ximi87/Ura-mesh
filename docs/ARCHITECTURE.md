# How Ura works

## Parts

```
             site A                                                     site B
 ┌──────────────────────────────┐                         ┌──────────────────────────────┐
 │ LoRa nodes ~~~ hub radio     │                         │ hub radio ~~~ LoRa nodes      │
 │                 │ USB / IP    │                         │    │ USB / IP                 │
 │              ura-hub ─────────┼── TLS (pinned) ─┐ ┌─────┼─ ura-hub                     │
 │   rules, crypto, radio admin  │                 │ │     │   rules, crypto, radio admin  │
 └──────────────────────────────┘                 ▼ ▼     └──────────────────────────────┘
                                              ura-server
                                   registry · relay of sealed boxes ·
                                   public map · statistics · complaints
```

- **Hub radio** — a normal Meshtastic radio with the [Ura patch](FIRMWARE.md), running MQTT in
  *client proxy* mode: every packet it would publish to MQTT (its own and every packet it hears
  on LoRa, still channel-encrypted) is handed to the hub over USB/IP; packets the hub hands back
  go on air.
- **ura-hub** — owns the radio connection, applies the operator's rules, seals traffic
  end-to-end for each partner hub, reports its local nodes to the server, and serves the owner's
  website. Python + the `meshtastic` package.
- **ura-server** — the only public part. Registers hubs (with admin approval), keeps the list of
  links both sides accepted, relays sealed boxes only along those links, stores public node data
  for the map, counts traffic, handles complaints. Python standard library only.

## A message from Tirana to Ludwigsburg

1. A phone in Tirana sends on LongFast. Tirane-1 (hub radio) hears it and, as an MQTT proxy,
   hands the encrypted packet (a Meshtastic `ServiceEnvelope`) to the Tirana hub.
2. The hub **classifies** it: channel (public / which group / private message), and — by
   decrypting a copy in memory with the channel key from its own radio — its type (text,
   position, node info, telemetry, routing, traceroute). Nothing decrypted is stored or sent.
3. For each active link the hub applies **its send rule**. Allowed → it seals
   `{topic, data, path, allow, max_hops}` for that partner (X25519/HKDF/AES-256-CTR/HMAC) and
   sends `{"t":"mesh","boxes":{partner: box}}` to the server.
4. The server checks the link is active in both directions' acceptance, rate-limits, counts, and
   passes the box to the partner. It cannot open it.
5. The Ludwigsburg hub opens the box, drops replays/duplicates, applies **its receive rule** and
   the **airtime limit**, and hands the packet to its radio as MQTT downlink.
6. The patched tracker sends it on LoRa as a normal packet. The phone in Ludwigsburg sees the
   message; the node appears in its node list with position, and can be messaged directly.
   Private messages (PKI-encrypted end-to-end by Meshtastic) and their delivery
   acknowledgements travel the same way.

## Rules

Each hub keeps, per partner hub, a **send** and a **receive** rule:

| field | meaning |
|---|---|
| `on` | this direction of the link is open |
| `public` | the default public channel (psk `AQ==`) |
| `groups` | other channels by name (both radios need the same name + key; both hubs must tick it) |
| `private` | private messages (Meshtastic PKI, channel id `PKI`) |
| `positions` | position and waypoint packets |
| `onward_to` (send) | further hubs, offered by this partner, that **my** packets may reach |
| `transit` (send) | I pass **other hubs'** packets on to this partner (needs multi-hop on) |
| `from_beyond` (receive) | accept packets that started at a hub further away |

Plus per hub: an **airtime limit** (% of each hour / day, computed with the LoRa time-on-air
formula for the radio's modem settings), **multi-hop** on/off with a maximum hop count, and
whether node positions are shown on the public map. Every hub publishes its rules on the server
(transparency); the server never enforces or changes them.

## Multi-hop

A transit hub publishes `transit_to`: the partners it offers to pass traffic to. The origin hub
ticks, per link, which of those its packets may reach. The origin's choice (`allow`) and its hop
limit (`max_hops`) are sealed inside every box. A hub passes a box on only if: multi-hop is on
there, the next hub is in `allow`, its per-link `transit` allows it, and `len(path) + 1` does not
exceed the smaller of the origin's and its own hop limit. The receiver can refuse traffic from
further away (`from_beyond`). `path` (all hubs passed, origin first) prevents loops; a
payload-hash cache drops duplicates that arrive over different routes.

## Nodes and the map

Each hub reports its **local** nodes — heard by its own radio over LoRa within the configured
age (default 7 days), plus the radio itself — to the server, at least every 10 minutes and
within a minute of a change. Nodes that came over the bridge are never reported by the hub that
received them (they belong to the hub that heard them). The server tells each hub which nodes
belong to its partners, so a hub's Status page can group remote nodes by the hub that heard them.

The hub's own location follows its radio's **precise** position (from its settings or a GPS
fix) — never the privacy-rounded copy the radio broadcasts — or a position entered by hand.

## What the server knows

- Per hub: name, code, e-mail (admin only), position, approval state, software version,
  published rules, radio model/firmware, end-to-end **public** key, a **hash** of the hub key.
- Per link: who asked, who accepted, since when.
- Per node (from the hub that heard it): id, names, hardware, role, position (if the hub shares
  positions), last heard, hops.
- Per hour and link: number and size of boxes passed. A short in-memory list of recent relays
  (time, from, to) for the live map.
- **Never**: message content, channel keys, private keys, who talked to whom on the mesh.

## Security model

| threat | protection |
|---|---|
| someone pretends to be the server | hubs pin the server certificate's SHA-256 fingerprint (compared by the operator on registration) |
| someone pretends to be a hub | per-hub secret key (server stores only its SHA-256), admin approval, links need both sides' acceptance |
| the server (or an attacker on it) reads or changes traffic | end-to-end boxes: X25519 key agreement, HKDF-SHA256, AES-256-CTR, HMAC-SHA256 (encrypt-then-MAC); the server only relays |
| key substitution by the server | operators compare a safety code; a partner's key is pinned on first use and a change stops traffic until the operator trusts the new key |
| replay | box timestamp window + nonce cache; duplicates by payload hash |
| flooding | per-hub rate limit and box size limit on the server; airtime limit on each hub |
| password guessing | scrypt hashes, lockout after repeated failures, HttpOnly/Secure/SameSite cookies |
| web attacks | strict Content-Security-Policy, no inline scripts, frame denial, no referrer |

The crypto is implemented in pure Python (`hub/meshcrypto.py`) so hubs need no extra packages; it
is checked against FIPS-197, NIST SP 800-38A and RFC 7748 test vectors every time the hub starts
(it refuses to start if a vector fails); run it by hand with `python3 hub/meshcrypto.py`.

## Files

| | server (`URA_DATA`) | hub (`URA_DATA`) |
|---|---|---|
| state | `ura.db` (SQLite) | `config.json` (settings, rules, registration, pinned keys) |
| identity | `tls.crt`, `tls.key` | `identity.key` (end-to-end private key), `web.crt`, `web.key` |
| cache | `tiles/` | `tiles/`, `origins.json` |
