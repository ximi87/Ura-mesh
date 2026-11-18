# Ura

*Every mesh, one world.* — *Ura* is Albanian for **bridge**.

Ura links separate LoRa mesh networks over the internet, so people far apart can
talk as if they were on the same mesh. A node in Tirana shows up in a phone app in
Ludwigsburg like any other node — on the node list, on the map — and you message it
the normal way: open it, *Send message*. Public channels, private messages, groups,
positions, telemetry and traceroute all work across the bridge.

**Status:** Meshtastic works end-to-end and is tested with real radios between
Albania and Germany. MeshCore is next.

```
 Ludwigsburg                                                                   Tirana
 phones ~~LoRa~~ radio ==USB/IP== ura-hub ==TLS== ura-server ==TLS== ura-hub ==USB/IP== radio ~~LoRa~~ phones
                 (antenna)       (all rules)      (meeting point,     (all rules)       (antenna)
                                                   map, statistics)
                          └──────────── end-to-end encrypted between the two hubs ────────────┘
```

## Two programs

| | **ura-hub** — one per site | **ura-server** — one, public |
|---|---|---|
| Runs on | mini PC or Raspberry Pi next to the radio | any small Linux server with a public address |
| Does | connects the radio, applies *your* rules, seals traffic end-to-end, programs the radio | lets hubs find each other, relays sealed boxes, shows the public map and statistics |
| Website | `https://<hub>:8091` — owner only (password) | `https://<server>:8443` — public, plus an admin login |
| Needs | Python 3.10+ and the `meshtastic` package | Python 3.10+ only (standard library) |

The server never reads, stores or controls messages. **Every rule lives in the hubs**,
and every hub decides for itself — the server cannot change a hub, and a hub cannot
change the server.

## What you get

**On each hub's website**
- **Status** — radio, server connection, traffic counters, airtime, the nodes heard here
  (searchable, paged) and the nodes that came from each linked hub, on a map.
- **Links & rules** — ask other hubs for a link; both sides must accept. Per link and per
  direction: public channel, private groups, private messages, positions — and
  **multi-hop**: which further hubs your packets may reach through this partner.
- **Radio** — connect over USB or Wi-Fi/IP, one-click *Prepare radio for Ura*,
  **Diagnostics** (private message with delivery check, traceroute, telemetry/position request).
- **Device settings** — program the radio from the browser: name, fixed position,
  channels with secure random keys, and every Meshtastic setting (built from the firmware's
  own definitions).
- **Settings** — hub details and location (from the radio or by hand), server
  registration with certificate check, airtime limit, multi-hop, and every operational value
  as an *Advanced setting*.

**On the server's website**
- A map of all hubs, their nodes and links — with **live traffic** running along the links.
- Hub and node pages, link statistics (both directions per link), the list of hubs and
  their codes, a transparent complaints process, and the admin page (approve hubs, handle
  complaints, advanced settings).

**Security**
- Hubs connect *out* to the server over TLS with a pinned certificate fingerprint — no
  port forwarding at sites. Each hub has its own key (stored hashed on the server).
- Traffic between hubs is **end-to-end encrypted** (X25519 + AES-256 + HMAC); the server only
  passes on boxes it cannot open. Operators can compare a **safety code**; a changed key stops
  traffic until the operator trusts it again.
- Logins have lockouts; websites send strict security headers.

Both websites are in **English and Albanian**.

## Get started

- **Run a hub:** [docs/INSTALL-HUB.md](docs/INSTALL-HUB.md)
- **Run a server:** [docs/INSTALL-SERVER.md](docs/INSTALL-SERVER.md)
- **Hub radio firmware** (one small patch, why it's needed, how to flash): [docs/FIRMWARE.md](docs/FIRMWARE.md)
- **How it works:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · **Wire protocol:** [docs/PROTOCOL.md](docs/PROTOCOL.md)
- **Running it day to day, troubleshooting:** [docs/OPERATIONS.md](docs/OPERATIONS.md)
- **Security reports:** [SECURITY.md](SECURITY.md)

## Repository

```
server/   ura_server.py + web/        the server (relay, website, admin)
hub/      ura_hub.py, meshcrypto.py   the hub (radio, rules, end-to-end crypto) + web/
common/   ura.css, ura.js, leaflet/   shared look, translations, map library
firmware/ *.patch                     the small Meshtastic firmware patch for hub radios
contrib/  install-*.sh, *.service     install scripts and systemd units
tests/    ui_test.py, multihop_test.py, live/   browser, multi-hop and live-radio tests
docs/                                 documentation
```

## Legal

You are responsible for following the radio rules where your hub transmits (for example
the EU 868 MHz duty cycle — the hub has an airtime limit for that) and the rules about
relaying traffic over the internet in your country.

## Shqip

Ura lidh rrjete LoRa (Meshtastic, së shpejti MeshCore) përmes internetit: një nyje në
Tiranë shfaqet në aplikacionin e një telefoni në Gjermani si çdo nyje tjetër, dhe i
shkruani normalisht. Çdo vend ka një **ura-hub** pranë radios (rregullat i vendos vetë),
ndërsa **ura-server** publik vetëm i ndihmon hub-et të gjejnë njëri-tjetrin dhe tregon
hartën e statistikat — trafiku ndërmjet hub-eve është i enkriptuar skaj-më-skaj. Faqet
e internetit janë në anglisht dhe shqip. Udhëzimet e instalimit gjenden te `docs/`.

## License

MIT — see [LICENSE](LICENSE). Map data © OpenStreetMap contributors; map library Leaflet (BSD-2).
