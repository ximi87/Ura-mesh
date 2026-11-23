# Running Ura day to day

## The hub's counters (Meshtastic → Overview, MeshCore → Overview)

| counter | meaning |
|---|---|
| Heard by radio | packets the radio received over LoRa from other nodes since the hub started |
| Sent to linked hubs | own-site packets sealed and sent (one count per packet, any number of partners) |
| Received from hubs | packets that arrived from partners (before rules) |
| Put on air | packets handed to the radio for transmission |
| Passed on for other hubs | multi-hop transit traffic |
| On the Ura map | local nodes heard within the node-age setting, incl. this radio — the same number the server shows |
| In the radio's memory | everything the radio remembers, incl. old entries and nodes from other hubs |

*Links & rules* shows, per link, what was sent and received and **why** something was stopped:
direction off, public group, group not allowed, private message, position, airtime limit, no
end-to-end key / key changed, box could not be opened, went round in a circle, from a hub further
away, transit not allowed, radio not connected.

## Logs

Every hub has a **Logs** page; the server has a **Logs** page in the menu (visible to the admin only). They show the program's own
log, newest at the bottom: filter *everything / warnings and errors / errors only*, search text, update
every 5 seconds. Each file (the last ~5 MB, in the data folder under `logs/`) can be downloaded as a text
file to send to someone. The hub writes one line per packet: sent to which hubs (or why not), put on air
(or why not), with channel, kind and sender.

## Restarting or stopping the program

*Hub → Settings → Program* and *Server → Admin → Program*: **Restart program** loads the program again
(links pause for a few seconds, the page reloads by itself); **Stop program** ends it and it stays off —
the computer keeps running. Start it again on the computer: `sudo systemctl start ura-hub` (or
`ura-server`), or restart the computer. (The service file has `RestartPreventExitStatus=64` for this;
older installations: add that line under `RestartSec=` and run `sudo systemctl daemon-reload`.)

## Deleting leaves nothing behind

- **Ending a link:** see below.
- **Leaving the server** (*Links & rules → Link settings → Ura server → Forget*): the server address, its trusted fingerprint,
  the registration, all links, partner keys and the partners' nodes on the radio are deleted — the hub is
  as if it had never used that server.
- **On the server:** a hub that leaves or is removed is deleted completely (the hub, its links, their
  statistics, its nodes). The server also clears leftovers by itself at start and every hour: statistics of
  links that no longer exist, ended links, removed hubs and their nodes. The *Statistics* page shows only
  links that exist.
- **Removing the radio** (*Radio → Remove this radio from the hub*): its port, the saved copy of its channels
  and which partner its nodes came from are forgotten; connect a radio again as if it were new. Nothing on
  the radio itself is changed.

## Factory reset (hub)

*Settings → Factory reset* brings the hub back to the state right after installing. Enter your login password for the hub, type `RESET`, confirm, and
the page follows the steps until the hub is back in first-start mode:

1. The server is told that the hub leaves: it deletes the hub, its links, statistics and nodes; partners are told
   and clean up on their side. (If the server cannot be reached, it is said so; the administrator removes the hub.)
2. The partners' nodes are removed from the radio, 2 s apart, then checked on the radio. The radio's own settings
   are not changed.
3. Settings, password, hub name, end-to-end keys, saved radio and channels, node memory, logs and map cache are deleted.
4. The program restarts: choose a new password; the setup wizard starts at step 1. The new log begins with
   "factory reset done".

Only the website's certificate stays (it holds no data; the browser would otherwise warn again).

## MeshCore lane

The hub talks to a MeshCore companion radio on USB with MeshCore's own serial protocol. Every raw packet the
radio receives (`PUSH_CODE_LOG_RX_DATA`) is sealed end-to-end and sent to the linked hubs that allow MeshCore;
there it is put on air unchanged (`CMD_SEND_RAW_PACKET`). Copies of the same packet (repeated along other
paths) are recognised by MeshCore's own packet hash and cross only once; packets that came from a partner are
not sent back. The partner's airtime limit applies. Packets larger than ~173 bytes do not fit through the
companion's USB frame (rare). The hub radio's own advert and its own-mesh contacts' adverts are announced with
`CMD_EXPORT_CONTACT`. Log lines: `MeshCore radio -> flood text (6 hops): sent to …`, `from … MeshCore …: put on air`,
`MeshCore advert of “…” announced to …`. The server map shows MeshCore nodes with a dark-orange rim and a filter;
statistics show each link's packets per network.

## Nodes are announced across links

Live packets cross a link the moment the radio hears them. A node that stays quiet while the link is up would never
be known on the other side, so each hub also **announces the nodes its radio knows from its own mesh** (name, key,
and position if the node shares one) to its linked hubs: one node every 15 s, each again every 6 h, everything again
when a partner comes back. The link's send rules and the partner's airtime limit apply as for live packets.
Settings → Advanced → *Nodes and location* has the switch and the timings.

## Ending a link cleans up by itself

When a link ends — either side ends it, the admin removes a hub, or a hub leaves the server — both hubs
delete everything about it, as if it never existed: the per-link rules, the partner's pinned end-to-end
key, the counters, and **the partner's nodes on the radio** (their names and keys; a node that was reset
meanwhile is learned fresh after the next link). The server deletes the link and its statistics. A new
link starts from the defaults and a new key check (compare the safety code again).

## Troubleshooting

**Remote nodes do not appear on phones near my hub**
- Is the hub radio running the [Ura firmware patch](FIRMWARE.md)? Without it, nodes with *Ignore
  MQTT* drop the bridged packets.
- Is anything else connected to the hub radio (app over Bluetooth/Wi-Fi, a script over TCP)? Only
  the hub may be connected.
- Radio → *Ready for Ura* all green? If not: *Prepare radio for Ura*.
- Does the phone's radio actually hear the hub radio? (Diagnostics → traceroute from the hub to the
  phone's radio.)

**Nothing goes out from my site**
- Status → *Heard by radio* stays 0 and *What the radio hears* shows little channel use: the radio
  hears nobody — place it higher or use a better antenna.
- Links & rules → is the link **active** and the send rule on for that kind of traffic?
- Status → *Last message from the radio*: a connected radio reports at least every minute. If this
  grows to minutes, the radio has stopped giving the hub its packets although the USB/IP connection
  is still open. The **watchdog** restarts such a radio after 10 minutes of silence (Advanced
  settings → Radio) and shows a warning on Meshtastic → Overview. If the warning keeps coming back, make
  sure nothing else is connected to that radio (an app over Wi-Fi or Bluetooth takes the packets
  meant for the hub) and check its power supply.

**"Last heard" times are wrong / nodes missing on the map**
The radio's clock was wrong (no GPS, no internet). The hub sets it every hour (Advanced setting);
times become right as nodes are heard again.

**Packets during a restart**
After the hub or the radio restarts, the radio needs up to a minute to reconnect. Packets arriving
in that window are counted as *radio not connected*.

**"The server could not be reached"**
Check address and port (`name:8100`). If the hub is in the server's own network and uses the public
name, the router probably lacks hairpin NAT — use the internal address or see
[INSTALL-SERVER.md](INSTALL-SERVER.md#domain-and-certificates).

**Server shows "certificate changed!"**
The server's certificate fingerprint is not the one you trusted. Do not accept it blindly — ask
the server administrator. Only if they confirm a planned change: Settings → Check server → trust.

**A partner's key changed (red warning on the link)**
That hub was reinstalled — or someone is trying to sit in between. Call the operator, compare the
new safety code, then press *trust the new key*.

**Map is grey**
The hub gets map tiles through the server. If the server has no internet, set another tile source
(Advanced settings) or live without the background map.

## Airtime

EU 868 MHz sub-bands allow 1 % or 10 % duty cycle. *Settings → Airtime* limits how much of each
hour (and day) remote packets may use on your radio; packets above the limit are not put on air
(counted as *airtime limit*). Keep your rules tight (only the groups you need, positions off if
not wanted) to stay well below the limit.

## Updates and backups

See the update and backup sections of [INSTALL-HUB.md](INSTALL-HUB.md) and
[INSTALL-SERVER.md](INSTALL-SERVER.md). The two files that must never be lost are the hub's
`identity.key` and the server's `tls.crt`/`tls.key`.

## Tests (for developers)

```bash
python3 hub/meshcrypto.py                       # crypto test vectors
tests/run_test.sh && python tests/ui_test.py    # full browser test (Playwright), test ports 8196–8199
python tests/multihop_test.py                   # three hubs, multi-hop rules (needs the meshtastic package)
python tests/reach_test.py                      # five hubs, per-link reach (how far packets go through each partner)
tests/live/diag.sh <hub-url> <node> dm trace    # live: diagnostics through a real hub (URA_HUB_PW)
```
