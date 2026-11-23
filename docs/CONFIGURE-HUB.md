# Configuring the hub — every page explained

This page describes the hub's website (`https://<hub-ip>:8091`) as it is now: what is on each page and
what each setting does. To install a hub first, see [INSTALL-HUB.md](INSTALL-HUB.md). For the idea
behind Ura, see [the complete guide](GUIDE.md).

## The menu

```
 Ura (logo)      Meshtastic ▾          MeshCore ▾            Links & rules        Settings ▾
 = home map       ├ Overview            ├ Overview            (everything about    ├ Hub details
                  ├ Radio               ├ Radio                links, both         ├ Location of this hub
                  ├ Device settings     ├ Device settings      networks)           ├ Change login password
                  └ Logs                └ Logs                                     ├ Program
                                                                                   ├ Advanced settings
                                                                                   ├ Factory reset
                                                                                   ├ Setup (wizard)
                                                                                   └ Full log
```

One rule for where things are:

- **Meshtastic** and **MeshCore** — everything about that network's **radio**: what it hears, its
  settings, its airtime limit, its log. The two networks are separate and cannot talk to each other.
- **Links & rules** — everything about **links** between hubs, for both networks: which network goes
  over which link, the rules per network, the Ura server, multi-hop, link defaults.
- **Settings** — only the **hub itself**: name, location, password, restart/stop, factory reset.

On a phone the menu is a row below the logo; tap an item with ▾ to open its submenu.

## First start: the setup wizard

After choosing the hub's login password the hub opens **Setup** — one box with six steps, each turning green
by itself when it is really done:

1. **Name this hub** — hub name, your e-mail (seen only by the server's administrator), **country
   code** (2–3 letters) and **city / region code** (2–3 letters: city, province or district, as you
   know it). Together they form the hub's short code, e.g. `AB-CDE`. Letters only, capitals are
   applied automatically. **Approximate location (required):** latitude and longitude in decimal
   degrees with a point (north and east positive) — or **click / tap on the small map** and both are
   filled in. Ura keeps 2 decimals (≈ 1 km).
2. **Connect the radio** — choose the radio type (Meshtastic or MeshCore), then the USB port. The hub
   asks every USB device what it is and shows its real name; a device of the other type is greyed
   out. *Connect* answers with the radio's name and how many nodes it holds.
3. **Prepare the radio for Ura** — one click per radio (a Meshtastic radio restarts once; a MeshCore
   radio announces itself once). Includes the approximate location.
4. **Connect to the server** — the server's address is already filled in (it can be changed); press
   *Connect*: the hub reaches the server, takes its certificate and sends the registration in one step
   (the fingerprint is shown and can be compared with the server's *Register a hub* page). The approval by
   the server's administrator follows later and is shown.
5. **Connect a tunnel** — per hub and tunnel of the same kind *Ask to connect* (the other operator
   accepts on their hub), or
   *Finish setup — link later*.
6. **Ready** — summary, *Ask neighbours to answer*, *Link with more hubs*.

Once everything has been done, the wizard no longer opens by itself (it stays under Settings → Setup).
*Skip the wizard (advanced)* at its bottom lets you set everything up on the pages below instead.

## Home map (click the Ura logo)

A full map of **this hub** (green ring) with its own nodes, the **linked hubs** (rings in their colour,
a dashed line per link) and **their nodes**. Meshtastic nodes have a white rim, MeshCore nodes an orange
rim. The box at the top right: links online, and per network the nodes here, nodes from links and the
packets sent ↑ / received ↓ — with a *show* tick per network. On a phone the box is folded into one line.

Nodes of a linked hub that has been offline for long are shown grey, and hidden after a few days
(server settings *offline_grey_h*, *offline_hide_days*). Nothing is deleted from any radio for that.

## Meshtastic ▾ (and MeshCore ▾ — the same pages for the other network)

### Overview
The same map, **only this network's nodes**, then: traffic per link (sent, received, not passed with
the reason), the radio, airtime used, what the radio hears, the node lists (heard here / from linked
hubs, grouped by hub). Whether the network goes over a link is decided on *Links & rules*, not here.

### Radio
- **Connection** — the USB port (or IP for Meshtastic); each port shows what is plugged in. *Remove
  this radio* forgets it completely; the linked hubs are told to forget its nodes too.
- **Status** — name, hardware, firmware, readiness checks (✅/❌) and *Prepare radio for Ura*.
- **Diagnostics** (Meshtastic) — send a private message, traceroute, telemetry or position request to
  any node, local or across a link; *delivered* means it arrived.
- **Node list** (Meshtastic) — *Forget this node* (e.g. a node that was reset and has a new key),
  *Clear list* (the radio keeps its own position).
- **MeshCore** — *Prepare for Ura* (name, approximate location shared in adverts), contacts,
  packets heard per type, messages the radio itself received from its own mesh.

> **Companion, not repeater.** The MeshCore radio on a hub must run **companion** firmware (USB).
> Repeater and room-server firmware do not work with Ura: over USB they only offer a settings console,
> so the hub could neither see the packets nor put any on air. You do not need a repeater there — **the
> hub itself is the repeater over the internet**: what its radio hears goes to the linked hubs, and what
> they send is put on air here. A companion radio does not repeat packets by radio locally; for better
> local coverage, add separate repeater devices — they work together with the hub.

### Device settings
- **Meshtastic** — the radio's own settings, section by section (name, position, channels — including
  *Add channels from a Meshtastic link* —, LoRa, Bluetooth, modules …). Changes are written to the radio.
- **MeshCore** — name, frequency, bandwidth, spreading factor, coding rate, transmit power, location
  sharing. Use the same radio settings as your local group (EU: 869.618 MHz · 62.5 kHz · SF8 · CR8).
- **Airtime limit** (both) — how much of the air this radio may use to put packets **from links** on
  air (% per hour, % per day). Each network has its own limit.
- **Advanced settings — Meshtastic radio** — clock sync, radio watchdog, diagnostics timeout, MQTT address.

### Logs
Only this network's log lines (filter, search, refresh every 5 s, download). *Settings → Full log* has
everything.

## Links & rules

**Tunnels.** A hub connected to the Ura server has one **tunnel per radio** it has set up: a
**Meshtastic tunnel** (male) and/or a **MeshCore tunnel** (female). A tunnel connects only with a tunnel
**of the same kind** on another hub — Meshtastic with Meshtastic, MeshCore with MeshCore — on request,
once the other hub accepts. Each connection stands on its own: requested, accepted and ended separately,
also with the same hub (a hub with both radios can be connected to another hub with one tunnel or with
both). A hub with only Meshtastic connects with the Meshtastic tunnels of others; a hub with only MeshCore
with the MeshCore tunnels; a hub with both with either.

Every connection is encrypted **from hub to hub** (peer to peer): the keys are made only in the two hubs
(X25519), each tunnel type has its own key, and the server — like a torrent tracker — only shows who has
which tunnel and passes on sealed boxes it cannot open.

1. **Requests** — requests from other hubs to connect one of their tunnels with yours (the tunnel type
   is shown; *Accept* / *Decline*) and your own (Cancel).
2. **My tunnels** — the Meshtastic tunnel and the MeshCore tunnel of this hub (*ready* or *not
   available* — no radio of that kind), each with its **connections**: one line per connected hub
   (online, 🔒, packets ↑ ↓). Click a line for **what exactly passes**:
   - **Meshtastic — my rules** (table: *Send to …* / *Receive from …*): basic rules (public channel,
     private messages, positions) · groups (one per private channel of your radio) · multi-hop (how far
     my packets may go through this partner, pass other hubs' packets on to it, accept packets from
     hubs beyond it).
   - **MeshCore — my rules**: basic rules (adverts, Public channel, private messages) · groups ·
     other (other people's channels — off by default —, traceroute/control) · multi-hop.
   - *Save* (only this connection's rules), *End this connection* (only this tunnel's connection; a
     connection of the other tunnel with the same hub stays — both hubs forget each other's nodes of
     that network), and folded below: the partner's rules, traffic, the end-to-end safety code (compare
     it with the other operator).
3. **Tunnels on the server** — one row per tunnel of the other hubs: *Ask to connect* for a tunnel of
   the same kind as yours; "connected", "waiting", or "you have no … tunnel".
4. **Link settings** — the **Ura server** (address filled in, *Connect*; later its state and *Leave*),
   **defaults for new connections** (one table per network), **multi-hop** per network (does this hub
   pass traffic between its connections, and over how many at most), positions on the public map.
5. **Advanced settings — links and server** — the **Ura server offered to a new hub** (filled in on
   the Connect field; also set by the installer with `URA_SERVER=…`), reconnect / keep-alive / timeout to the server, packets
   kept while it is unreachable, the server's web port; node announcements to linked hubs (on/off, each
   node again every … hours, one node every … seconds, only nodes heard within …), node reports.

## Settings ▾ (the hub itself)

- **Hub details** — name, e-mail, country and city/region code, description (locked after registering).
- **Location of this hub** — from the radio, or typed in / clicked on the map (approximate).
- **Change login password**, *Log out*.
- **Program** — restart or stop the ura-hub program (not the computer).
- **Advanced settings** — location following, security and login, map and website.
- **Factory reset** — enter your **login password** for this hub and type `RESET` (a wrong password deletes nothing and counts like a wrong login): the server is told the hub leaves (it deletes the hub, its links,
  statistics and nodes; partners clean up), the partners' nodes are removed from the radio, all hub data
  is deleted — the old password too —, the program restarts in first-start mode and a **new login password** must be chosen. The radio's own settings are not changed.
- **Setup** — the wizard. **Full log** — every log line, with download.

## What happens when something goes away

| Event | What Ura does |
|---|---|
| You remove a radio, or switch a network off for a link | at once: partners forget your nodes of that network (sealed message, passed on multi-hop); the map is cleared |
| A link ends, a hub leaves the server, factory reset, the admin removes a hub | at once: both sides delete everything of the other |
| A radio is unplugged or fails, the internet or the server is down | nothing is deleted from any radio (keys stay, messages work again when it is back); maps show the hub's nodes grey after a day, hidden after a few days |
| Nodes in other people's devices | Ura cannot delete them (no mesh protocol allows that); they age out there |
