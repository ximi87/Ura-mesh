# Installing a Ura hub

A hub is a small Linux computer next to a Meshtastic radio. It connects **out** to a Ura
server, so you need no port forwarding and no public address at your site.

You need about 30 minutes.

## What you need

| | |
|---|---|
| Computer | Raspberry Pi 3/4/5, a mini PC or a virtual machine — Debian, Ubuntu or Raspberry Pi OS, always on |
| Radio | A Meshtastic radio (tested: Heltec V3, Heltec Wireless Tracker; other ESP32 boards work the same) on **USB** (recommended) or Wi-Fi/IP |
| Firmware | Meshtastic 2.7.x **with the Ura patch** on the hub radio — see [FIRMWARE.md](FIRMWARE.md) |
| Network | Internet access to the Ura server (TCP port 8100 and 8443) |
| From the server | Its address (e.g. `ura.example.org:8100`) and its certificate fingerprint — both on the server's **Register a hub** page |

> **One rule for the hub radio:** while the hub runs, **nothing else may be connected to that
> radio** — no Meshtastic app over Bluetooth or Wi-Fi, no other program. The radio hands its
> bridge packets to whichever connected program reads first; a second connection makes
> traffic silently go missing. Use a second radio for your phone.

Place the radio where it hears your local mesh well — high up, near a window or with an
outdoor antenna. Ura can only pass on what the radio actually hears.

## 1. Flash the hub radio

Follow [FIRMWARE.md](FIRMWARE.md). Without the patch, packets from other countries are
marked "via MQTT" on air and many nodes (those with *Ignore MQTT* on) drop them.

## 2. Install the hub

On the hub computer, as a normal user with sudo rights:

```bash
git clone https://github.com/ximi87/Ura-mesh.git
cd Ura-mesh
sudo bash contrib/install-hub.sh
```

The script shows what it will change and asks first. It installs `git`, `python3-venv` and
`openssl`, creates a system user `ura` (in the `dialout` group for USB), puts Ura in
`/opt/ura` with the Meshtastic package in `/opt/ura/venv`, keeps the hub's data in
`/var/lib/ura-hub` and starts the service `ura-hub`.

<details><summary>Manual installation instead of the script</summary>

```bash
sudo apt install git python3-venv openssl
sudo useradd --system --home /var/lib/ura-hub --shell /usr/sbin/nologin ura
sudo usermod -aG dialout ura
sudo git clone https://github.com/ximi87/Ura-mesh.git /opt/ura
sudo python3 -m venv /opt/ura/venv
sudo /opt/ura/venv/bin/pip install -r /opt/ura/hub/requirements.txt
sudo install -d -o ura -g ura -m 700 /var/lib/ura-hub
sudo cp /opt/ura/contrib/ura-hub.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now ura-hub
```

Startup options (environment variables in the service file): `URA_DATA` (data folder,
default `hub/data`), `URA_WEB_PORT` (website port, default `8091`). Everything else is set
on the website.
</details>

## 3. Open the hub's website

Plug in the radio, then open `https://<hub-ip>:8091` in a browser. The certificate is
self-signed: accept it once. Choose the **hub password** (at least 8 characters).

Keep the website to your local network (a firewall rule, or simply no port forwarding).

## 4. Connect the radio — *Radio*

- **Radio type:** Meshtastic. **Connection:** USB (pick the port from the list) or Wi-Fi/IP
  (the radio's address). Save.
- When the radio shows **connected**, check the list **Ready for Ura**. If anything is red,
  press **Prepare radio for Ura**: it turns on MQTT through the hub (*client proxy*),
  encryption, a private MQTT address, uplink/downlink on all channels and switches off
  *Ignore MQTT* — in one go; the radio restarts once.

The radio's own settings (name, position, channels, LoRa, everything) are under
**Device settings**.

### Channels and keys — read this before you continue

A Meshtastic radio can only read packets on a channel it **also has, with the same name and the
same key**. The hub radio is no exception: it can only pass on what it can read (private messages
between two nodes are the only exception — they use the nodes' own keys and always pass).

- **The public channel** (LongFast, MediumFast, … depending on your region's preset) uses the
  public default key **`AQ==`**. Leave it like that on the hub radio *and* on the nodes, and their
  public messages, positions and telemetry cross Ura.
- **If your mesh uses its own key** — for the main channel or for a group — the hub radio needs that
  channel too. Easiest: in the Meshtastic app open **Channels → share** (QR code / link), then on the
  hub **Device settings → Channels → Add channels from a Meshtastic link** and paste the link.
  You can also type a key in or let the radio generate one (**Device settings → Channels → channel →
  Key**) and share it from there: each channel shows its key with a *Copy* button, and the page has
  the share link for all channels.
- **For a group to cross between two hubs**, *both* hub radios need that channel with the same name
  and key, and both operators tick it under **Links & rules**. If the names match but the keys do
  not, the receiving hub says so (*same channel name, other key*) instead of putting unreadable
  packets on air.
- Every channel shows its **code** (a number from 0 to 255 made from name and key). Radios read each
  other only when the codes are equal. The public LongFast channel has code **8**.
- **The hub warns you.** When its radio hears packets it cannot read, the *Status* page shows the
  channel code and the nodes sending on it — typically a node whose key was changed.
- **A node that was reset (factory reset, new firmware with erase) gets a new private key.** Nodes that
  knew it before — also on the other side of Ura — still hold the old key and answer its private
  messages with an error (the phone shows a key or channel mismatch). Ending and re-creating the link does this by
  itself (both radios forget the partner's nodes when a link ends); for a single node without touching
  the link: **Radio → Diagnostics → Forget this node**. Then press **Ask neighbours to answer** on the hub
  where the node is: its name card with the new key crosses Ura in seconds. The same button helps
  after a node list was cleared: nodes learn each other again at once instead of after hours.
- **The hub keeps a copy of the radio's channels.** If you replace or reset the radio, or change its
  channels with the phone app, *Device settings* tells you and offers **Write the saved channels to
  the radio** (or *Keep the radio's channels*).

## 5. Hub details and location — *Settings*

- **Hub details:** a name, your e-mail address (visible only to the server's
  administrator), a **country code** and a **place code** (2–3 letters each, e.g.
  `XX` + `YY` — use the ISO code of your country). Only one hub per place: a code always
  names exactly one hub.
- **Location of this hub:** *take the position from the radio* (follows the radio) or
  *enter manually*. If the radio has no GPS fix and no fixed position, set a fixed position
  under Device settings, or enter it here.

## 6. Register with the server — *Settings → Ura server*

1. Enter the server address (`host:8100`) and press **Check server**.
2. **Compare the fingerprint** with the one on the server's *Register a hub* page. Only if
   they are identical press **Fingerprint matches – trust this server**. (This protects you
   against someone pretending to be the server.)
3. Press **Send registration request**. The hub now waits for the administrator's approval
   — the Status page shows *waiting for the administrator's approval*.

Once approved, your hub and its nodes appear on the server's map. **No traffic flows yet.**

## 7. Link with other hubs — *Links & rules*

- Under **Other hubs on the server**, press **Ask for a link** next to the hub you want.
  The other operator sees the request and presses **Accept**. Traffic starts only when both
  sides accepted.
- For every active link you set **your rules**, separately for *Send* (what you pass to them)
  and *Receive* (what you let onto the air from them): public channel, your other groups
  (channels), private messages, positions.
- **Groups** cross only if both hubs tick the same group, and both radios have a channel with
  the same name **and** key (Device settings → Channels).
- **End-to-end encryption:** the link shows a **safety code**. Compare it with the other
  operator once (phone, chat). If it matches on both sides, nobody — not even the server —
  sits in between. If a hub's key ever changes, traffic stops with a red warning until you
  compare the new code and press *trust*.

## 8. Multi-hop (optional)

If your hub has several links, you can let traffic pass *through* it — e.g. hub A → your hub →
hub C. Each hub decides for itself:

- **Settings → Multi-hop:** *Pass traffic between my linked hubs* + the longest chain of other
  hubs' traffic you take part in. Then, per link, *Pass other hubs' packets to this hub*. Your hub
  then **offers** those links to its partners.
- **Links & rules → Send → "How far may my packets go through X?"** — chosen **per link** for
  **your own** packets: *Only to X* (default), *1, 2 … hubs further*, or *Anywhere*. For 1 or more
  hubs, tick **which of X's links** they may continue on (X publishes them). Example with four
  links: link 1 *Only to X*, link 2 *1 hub further*, link 3 *Only to X*, link 4 *Anywhere*.
- **Receive → Accept packets from hubs beyond this one:** refuse traffic that did not start at
  your direct partner.

A packet travels one hop further only if the hub it started at allowed that distance (and, at the
first step, ticked that link of its partner), the passing hub offers it, the receiver accepts
packets from further away, and the passing hub's own chain limit is not exceeded. Packets never return to a hub they already passed.

## 9. Check that it works — *Radio → Diagnostics*

Pick a node — one of yours or one from another country — and send a **private message with
delivery check**, a **traceroute**, or ask for **telemetry** or **position**. The answer
travels back the same way, so a reply proves both directions. *Send the text to this channel*
puts a test message on a channel (everyone on it receives it — use sparingly).

On your phone (connected to *another* radio near the hub) the remote nodes appear in the
node list and, if they share a position, on the map.

## Updating

```bash
cd /opt/ura && sudo git pull && sudo /opt/ura/venv/bin/pip install -r hub/requirements.txt
sudo systemctl restart ura-hub
```

## Backup

Back up `/var/lib/ura-hub`. Most important: `identity.key` (your hub's end-to-end key — if it
is lost, every partner sees a changed key and must trust the new one) and `config.json`
(settings, registration key, rules). Keep backups private.

More: [OPERATIONS.md](OPERATIONS.md) (troubleshooting, what each counter means).
