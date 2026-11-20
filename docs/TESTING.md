# Testing Ura

Every function is tested by its **effect**, not only by "saved OK": a rule is ticked off, a packet is
sent, and the test checks that the other hub's radio did — or did not — put it on air.

## The tests

| Test | What it does | Checks |
|---|---|---|
| `tests/functions_test.py` | Test server + hubs A, B, C with simulated radios (`tests/fake_radio.py`), from scratch through registration, links, every rule, multi-hop, key change, removal, leaving and registering again | 133 |
| `tests/ui_controls_test.py` | Clicks every tick box and field on the hub pages in a real browser, saves, checks the setting changed **and that the partner's page shows it** | 43 |
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

After the fixes both live hubs left the server, registered again from scratch, were approved and linked;
end-to-end keys, safety code, defaults, nodes, locations and traffic in both directions were checked live.

## Not testable without real radios

Diagnostics (private message / traceroute / telemetry / position requests) need a real answer from a
node; they are checked live on the hubs' Radio page.
