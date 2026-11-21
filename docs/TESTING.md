# Testing Ura

Every function is tested by its **effect**, not only by "saved OK": a rule is ticked off, a packet is
sent, and the test checks that the other hub's radio did — or did not — put it on air.

## The tests

| Test | What it does | Checks |
|---|---|---|
| `tests/functions_test.py` | Test server + hubs A, B, C, D with simulated radios (`tests/fake_radio.py`), from scratch: registration, links, every rule, defaults, multi-hop and max hops (chain of 4), hourly and daily airtime, duplicates, replayed and altered packets, diagnostics, prepare radio, key change, removal, leaving, registering again, every hub and server advanced setting by its effect, server restart with queued packets, frozen server, lockouts, watchdog, channels and keys (unreadable channel warning, saved copy + restore, add from a link, same name with another key, two channels with one name, region check, forget a node, logs view/filter/download, restart/stop of hub and server, automatic clean-up when a link ends, what is plugged into each port — Meshtastic / MeshCore / not a radio — and refusing anything but Meshtastic, removing a radio clears its nodes from the server) | 259 |
| `tests/ui_controls_test.py` | Clicks every control on the hub pages in a real browser (rules, reach and onward ticks, link ask/decline/cancel/accept/end, trust new key, settings, older nodes, remote nodes by hub, diagnostics, prepare, channel, fixed position, channel warning, restore channels, add channels from a link, copy key, logs page, restart program, server admin log/program, port list naming each device), saves, checks the setting changed **and that the partner's page shows it** | 76 |
| `tests/ui_test.py` | Browser walk through all server and hub pages (start with `tests/run_test.sh`) | 64 |
| `tests/multihop_test.py`, `tests/links_test.py` | Multi-hop chains/triangles; link and registration consistency | 12 + 12 |

Run (the hubs need a Python with `meshtastic`; the browser tests need `playwright`):

```bash
URA_HUB_PYTHON=/path/to/venv/bin/python python tests/functions_test.py      # writes $URA_TEST_DIR/report.md
URA_HUB_PYTHON=/path/to/venv/bin/python python tests/ui_controls_test.py
```

The simulated radio behaves like Meshtastic's interface (channels LongFast public + a private group
"Team", local nodes with positions, every settings section) and records what the hub sends to it,
readable at `GET /api/test/radio` — only when the hub runs with `URA_TEST_INJECT=1`.

## What the full check found (2026-11) and how it was fixed

| Problem | Effect | Fix |
|---|---|---|
| The partner's rules table did not show its hub-wide multi-hop setting; the per-link "pass on" row read *on* even while multi-hop was off | Ticking "Pass traffic between my linked hubs" seemed to do nothing on the other side | Table split into the link rules and a **Multi-hop** block: how far its own packets go, whether it passes traffic (max hops), whether it passes traffic on to us, which hubs it offers, whether it accepts packets we pass on |
| Nodes were reported while the hub was still waiting for approval (the server ignores them), then not again for 10 minutes | A newly approved hub had an empty map for up to 10 minutes; same after every reconnect | Nodes and location are reported at once on approval, on every (re)connection and when a setting changes |
| Location changes were sent only every 30 s | Saved positions appeared late | Sent at once when saved |
| A link without saved rules followed the hub's *current* defaults | Changing "defaults for new links" silently changed existing links | Each link gets its own copy of the defaults when it appears |
| Leaving the server kept old link rules and partner keys; the link list received on connect skipped the clean-up | Rules of old registrations stayed in the hub's settings | Leaving clears them; rules are kept only for hubs the hub is linked with |
| Packets heard while the server was unreachable were sent the moment the hub reconnected — before its partners were back — and the server dropped them; the queue size only changed after a restart | "Packets kept while the server is unreachable" did not work | After a reconnect the hub waits (up to 15 s) until its linked hubs are online; the size limit applies at once |
| Old statistics were only removed when traffic flowed | Retention did nothing on a quiet server | Clean-up at start and every hour |
| Keepalive and server timeout were read only at the start of each wait (up to 2 min) | A frozen server went unnoticed; changed values applied late | Both re-read continuously |
| A node's channel key differed from the hub radio's (the radio heard the messages but could not read them) | Public messages silently did not cross Ura; nothing on the hub said why | Status warns with the channel code and the nodes; channels show their code and key; add channels from a Meshtastic link; the hub keeps a copy of the channels to restore; same name + other key at the partner is reported as *other key* |
| The hub never asked what was plugged into a port: it listed bare file names, said "Saved" without checking and treated any device as Meshtastic | Choosing a MeshCore radio looked like the Meshtastic one had been registered | The Radio page lists the USB devices at once and then asks every port in the background (Meshtastic and MeshCore handshakes; a radio with debug output on needs ~15 s) and shows the real device and name; Save connects for real and shows the radio's name and node count, or what else is on the port — then nothing is kept. "No answer" is never shown as "not a radio" |
| A reconnected radio's nodes were reported to the server only at the next periodic report; removing a radio left its nodes on the map | Empty or stale map after connecting/removing a radio | Nodes are reported at once on every radio connect; removing the radio deletes its nodes on the server |
| Diagnostics took a node's plain "received" confirmation as the answer to a telemetry/position/traceroute request | Showed "delivered" although no data came back (seen live with a Tag) | Waits for the data; otherwise "received, but no data" |

After the fixes both live hubs left the server, registered again from scratch, were approved and linked;
end-to-end keys, safety code, defaults, nodes, locations and traffic in both directions were checked live.

## Live checks on the real radios (2026-11-20)

| From | To | Test | Result |
|---|---|---|---|
| hub 1 | other hub's radio, across the link | private message, traceroute | delivered, confirmed by the target / answered |
| hub 2 | other hub's radio, across the link | private message, telemetry | delivered / answered |
| hub 1 | a nearby node | position, traceroute | answered |
| hub 1 | a nearby node | telemetry | "received, but no data" (that node does not send telemetry) |
| hub 1 | a nearby node | private message | the node answered NO_CHANNEL — it holds an outdated key for the hub's radio (fix on that node: remove the radio from its node list so it learns the key again) |

Not covered by tests: Let's Encrypt (needs a public domain; runs live), and `refused_retry_s` (how long a
refused hub waits before trying again).
