# Ura wire protocol (version 0.3)

## Hub ↔ server

TLS on TCP (default port 8100), server certificate pinned by its SHA-256 fingerprint (colon-
separated upper-case hex of the DER certificate). The connection carries **JSON objects, one per
line** (UTF-8, `\n`-terminated). The hub always connects; the server never connects to hubs.

### Registration (one-off connection)

```
hub → {"t":"join","name":"Tirana","email":"op@example.org","country":"AL","city":"TR",
       "lat":41.34847,"lon":19.897555,"description":""}
srv → {"t":"joined","hub":"h_0123456789ab","key":"<48 hex>","status":"pending"}
   or {"t":"join_refused","reason":"name_required|email_required|code_invalid|code_taken|registrations_closed"}
```

The hub stores `hub` and `key`. The server stores only `sha256(key)`. A hub that only checks the
server's fingerprint opens the TLS connection and closes it without sending anything.

### Session

```
hub → {"t":"hello","hub":"h_…","key":"…","version":"0.3.0",
       "info":{"rules":{…},"radios":[{"net":"mt","name":"…","hw":"…","firmware":"…","connected":true}],
               "pubkey":"<base64 X25519 public key, 32 bytes>"}}
srv → {"t":"welcome","hub":"h_…","status":"pending|approved","server_version":"0.3.0",
       "hubs":[<directory>],"links":[<links>]}
   or {"t":"refused","reason":"unknown_hub|removed"}
```

After `welcome`, messages in any order:

| direction | message | meaning |
|---|---|---|
| hub → srv | `{"t":"ping"}` / srv → `{"t":"pong"}` | keep-alive (default every 30 s) |
| hub → srv | `{"t":"info","info":{…}}` | rules / radios / public key changed |
| hub → srv | `{"t":"location","lat":…,"lon":…}` | hub position changed |
| hub → srv | `{"t":"nodes","net":"mt","nodes":[{id,name,short,hw,role,lat,lon,alt,last_heard,hops,own}]}` | full list of the hub's local nodes (replaces the previous list) |
| hub → srv | `{"t":"link_request","to":"h_…"}` | ask another approved hub for a link |
| hub → srv | `{"t":"link_accept","link":12}` / `{"t":"link_remove","link":12}` | accept / end a link |
| hub → srv | `{"t":"mesh","net":"mt","boxes":{"h_peer":"<base64 box>", …}}` | sealed packets, one box per partner |
| srv → hub | `{"t":"mesh","net":"mt","from":"h_…","box":"<base64>"}` | a sealed packet from a partner |
| srv → hub | `{"t":"directory","hubs":[…]}` | approved hubs changed (incl. their public rules and keys) |
| srv → hub | `{"t":"links","links":[…]}` | this hub's links changed |
| srv → hub | `{"t":"peer_nodes","hub":"h_…","ids":["!…",…]}` | which nodes belong to a partner hub |
| srv → hub | `{"t":"status","status":"approved|removed"}` | registration changed |

Pending hubs may connect, but the server ignores `nodes`, `link_*` and `mesh` until they are
approved. The server relays a box only if the link between sender and receiver is **active**
(both accepted), the receiver is online, the box is within the size limit and the sender is within
its rate limit.

**Directory entry:** `{id, name, code, country, city, lat, lon, description, online, last_seen,
approved, version, rules, radios, pubkey, e2e}`.
**Link entry (as seen by one hub):** `{id, peer, peer_name, peer_code, peer_online, state:
"pending|active", requested_by, i_accepted, peer_accepted, created, activated}`.

## Sealed box (hub ↔ hub, end-to-end)

Keys per link: `shared = X25519(my_private, peer_public)`;
`k = HKDF-SHA256(ikm=shared, salt="ura-link-v1", info="ura e2e " ‖ min(pubA,pubB) ‖ max(pubA,pubB), L=64)`;
`enc = k[0:32]`, `mac = k[32:64]`. Both hubs derive the same keys.

```
box = 0x01 | time (uint32 big-endian, unix seconds) | nonce (16 random bytes) | ciphertext | tag (16 bytes)
ciphertext = AES-256-CTR(enc, counter block = nonce, counter = last 4 bytes big-endian, plaintext)
tag        = HMAC-SHA256(mac, version|time|nonce|ciphertext)[0:16]
```

Receivers reject boxes with a wrong tag, a time outside the replay window (default ±600 s) or a
nonce seen before.

**Plaintext** (JSON):

```json
{"topic": "msh/EU_868/2/e/LongFast/!36cb40cc",
 "data": "<base64 Meshtastic ServiceEnvelope, packet still channel-encrypted>",
 "path": ["h_origin", "h_transit"],
 "allow": ["h_dest1", "h_dest2"],
 "max_hops": 2}
```

`path` lists every hub the packet passed (origin first). `allow` and `max_hops` are set by the
origin per partner and copied unchanged by transit hubs.

**Safety code** shown to operators: the first 10 bytes of
`SHA-256("ura safety " ‖ min(pubA,pubB) ‖ max(pubA,pubB))` as an integer, modulo 10²⁰, written as
four groups of five digits.

## Meshtastic side

The hub radio runs MQTT with `proxy_to_client_enabled`, `encryption_enabled` and a private
address (default `127.0.0.1`, never contacted; a private address makes firmware 2.7 pass every
packet). Uplink: `FromRadio.mqttClientProxyMessage {topic, data}`. Downlink:
`ToRadio.mqttClientProxyMessage {topic, data}`. The hub forwards topic and data unchanged.

## Public HTTP API (server, read-only, JSON)

`GET /api/public/info` · `/api/public/hubs` · `/api/public/nodes` · `/api/public/hub/<id>` ·
`/api/public/node/<hub>/<net>/<id>` · `/api/public/stats?hours=N` · `/api/public/live?after=<seq>` ·
`/api/public/complaints` · `POST /api/public/complaints` · map tiles `GET /tiles/<z>/<x>/<y>.png`.
