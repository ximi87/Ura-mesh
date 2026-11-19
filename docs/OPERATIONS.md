# Running Ura day to day

## The hub's counters (Status page)

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
  settings → Radio) and shows a warning on the Status page. If the warning keeps coming back, make
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
