# Ura — the complete guide

This guide explains how Ura works from the first installation to the first confirmed message,
what is transmitted, who decides what, and how the encryption keeps the server blind.
For command-by-command installation see [INSTALL-HUB.md](INSTALL-HUB.md) and
[INSTALL-SERVER.md](INSTALL-SERVER.md).

![World map of a Ura network: hubs, links and live traffic](img/map-world.jpg)

---

## 1. The idea in one picture

```
          mesh A                                                         mesh B
  ┌─────────────────────┐                                       ┌─────────────────────┐
  │ phones and nodes     │                                       │ phones and nodes     │
  │        ~~ LoRa ~~    │                                       │    ~~ LoRa ~~        │
  │   hub radio (USB)    │                                       │   hub radio (USB)    │
  │       ura-hub A  ════╪═══ TLS ═══►  ura-server  ◄═══ TLS ═══╪═══  ura-hub B        │
  │  ▲ decides EVERYTHING│              meeting point             │ decides EVERYTHING ▲ │
  └──┼──────────────────┘              (blind relay,             └──────────────────┼──┘
     │                                  map, statistics)                            │
     └──────────── sealed boxes: only hub A and hub B can open them ────────────────┘
```

| | **ura-hub** (one per mesh) | **ura-server** (one public meeting point) |
|---|---|---|
| Who runs it | the operator of a local mesh | whoever hosts the network (one per network) |
| Decides | which partners, which channels, which direction, positions or not, multi-hop, airtime | nothing about traffic |
| Sees | the packets of its own mesh (as its radio does) | that hub A sent hub B a box of N bytes — **never what is inside** |
| Can change | its own radio and rules | its own list of approved hubs — not a single hub setting |

The server is a **connection point**, like a post office that forwards sealed envelopes: it
knows that an envelope went from A to B, not what it contains, and it cannot reseal or alter it.

---

## 2. From zero to the first message

### Step 1 — Someone runs a server
A network needs one ura-server with a public address (ideally a domain name). The operator
installs it ([INSTALL-SERVER.md](INSTALL-SERVER.md)), sets the admin password and lets the server
get its free Let's Encrypt certificate for the website. The server shows its **certificate
fingerprint** on the page *Register a hub* — every hub operator will compare it.

### Step 2 — Each mesh prepares a hub radio
One radio per mesh becomes the hub radio. It gets Meshtastic 2.7 with the small Ura patch
([FIRMWARE.md](FIRMWARE.md)) so that packets from other meshes go on air as normal LoRa packets.
Place it where it hears the local mesh well. No other radio needs changes.

### Step 3 — Install the hub
On a Raspberry Pi, mini PC or virtual machine next to the radio:
```bash
git clone https://github.com/ximi87/Ura-mesh.git && cd Ura-mesh && sudo bash contrib/install-hub.sh
```
Open `https://<hub>:8091`, choose a password.

### Step 4 — Connect and prepare the radio (*Radio*)
Choose the USB port (or the radio's IP). The page shows the radio's name, firmware and the
checklist **Ready for Ura**. *Prepare radio for Ura* sets everything in one go (MQTT through the
hub, encryption kept, uplink/downlink on every channel, *Ignore MQTT* off). The radio itself
can be fully programmed under **Device settings** — name, position, channels and keys, LoRa
region and preset, every module.

### Step 5 — Describe the hub (*Settings*)
Hub name, the operator's e-mail (only the server admin sees it), country code + place code
(`XX-YY`, one hub per place), and the location — automatically from the radio or typed in.

### Step 6 — Register and wait for approval (*Settings → Ura server*)
Enter the server address, press *Check server*, **compare the fingerprint** with the server's
*Register a hub* page, trust it, *Send registration request*. The hub waits for the
administrator. Once approved it appears on the public map with its nodes — **but no traffic
flows yet**. Being registered does not mean anyone can send you anything.

### Step 7 — Ask for a link; the other side accepts (*Links & rules*)
Under *Other hubs on the server*, press *Ask for a link*. The other operator sees *"… asks to
link with you"* and presses **Accept** — or ignores / declines it. A link is active only when
**both** sides accepted. Either side can end it at any time (*End link*); traffic stops at once.

### Step 8 — Compare the safety code
Each active link shows a **safety code** (four groups of five digits). The two operators compare
it once (phone, chat). The same code on both sides proves that the end-to-end keys are the
hubs' own — that nobody, not even the server, sits in between. If a partner's key ever changes,
the link turns red and traffic stops until the operator compares the new code and trusts it.

### Step 9 — Set your rules
For every link, separately for **Send** (what you pass to the partner) and **Receive** (what you
let onto your air from the partner): link open in this direction, public channel, each private
group, private messages, positions, multi-hop. Details in section 3.

![A hub's Links & rules page: end-to-end safety code, send and receive rules, multi-hop destinations](img/hub-links.jpg)

### Step 10 — Confirm that it works
- **Diagnostics** (*Radio* page): pick any node — local or in the other mesh — and send a
  *private message with delivery check*. **"Delivered — the node confirmed it"** means the
  message reached the node and its acknowledgement came all the way back: both directions work.
  *Traceroute* shows the route (the bridge counts as one hop), *telemetry* and *position* requests
  get the node's answer.
- **Phones:** remote nodes appear in the Meshtastic app's node list and, if they share a position,
  on its map. Tap one, *Send message* — the app shows *delivered* when the remote node confirms.
- **Counters** on the Status page and per link (*sent, received, put on air,* and *why* anything
  was stopped).
- **The server map** shows the link, and dots run along it whenever packets pass.

---

## 3. What is transmitted — and who decides

### What a hub can pass on
Everything the hub radio receives on the channels it has, plus its own packets, travels as the
original Meshtastic packet — still encrypted with the channel key (or, for private messages,
end-to-end between the sending and the receiving radio by Meshtastic itself). The hub reads only its *type*, to apply
the rules:

| packet | examples | governed by |
|---|---|---|
| text on the public channel | chat on the default channel | **Public group** |
| text on a private group | your club's channel | **Groups** (by channel name) |
| private message | one person to another | **Private messages** |
| position, waypoint | map dots | **Positions** |
| node info | name, hardware | the channel it is sent on |
| telemetry | battery, temperature | the channel it is sent on |
| routing / acknowledgements | "delivered" confirmations | the channel it is sent on |
| traceroute, position and telemetry requests | diagnostics | the channel / private messages |

### Every hub decides for itself — in both directions

- **Hub A decides what leaves mesh A** (its *Send* rules) and **what enters mesh A** (its
  *Receive* rules). Hub B decides the same for mesh B. Neither can change the other's rules, and the
  server can change neither.
- A packet crosses only if **the sender's Send rule and the receiver's Receive rule both allow it.**

Examples:

| Situation | Who sets what |
|---|---|
| Mesh A does not want to share positions | Hub A: *Send → Positions* off. Positions never leave mesh A. |
| Mesh B does not want foreign public chatter on its air | Hub B: *Receive → Public group* off. Private messages still arrive. |
| Only a club channel should be shared | Both radios get the channel with the same name and key; both hubs tick that group; *Public group* off on both. |
| One direction only (e.g. a mesh that only listens) | The listening hub: *Send → Link open* off. |
| Too much traffic on the air | *Settings → Airtime limit*: remote packets above the limit are not transmitted. |
| A partner misbehaves | *End link* — immediate. Or contact the server admin / file a public complaint. |

Every hub **publishes its rules** on the server (transparency): anyone can read on the hub's page
what it passes on and accepts.

![A hub's public page on the server: its links, rules (including multi-hop), traffic and nodes](img/server-hub.jpg)

---

## 4. Multi-hop: passing traffic through a hub

A hub with several links can pass traffic between its partners — for example
hub A → hub B → hub C — but **only where every hub involved agrees**:

1. **Hub B offers.** In *Settings → Multi-hop* B turns transit on and sets the longest chain it takes part in; per link it
   chooses whether it passes other hubs' packets to that partner. B then publishes the list of
   partners it offers.
2. **Hub A chooses for its own packets — separately on every link.** On its link to B, A answers
   *"How far may my packets go through B?"*: *Only to B* (the default), *1, 2 … hubs further*, or
   *Anywhere*. For 1 hub or more it ticks **which of B's links** its packets may continue on.
   A hub with four links can say: link 1 only to that partner, link 2 one hub further (through
   the ticked links), link 3 only to that partner, link 4 anywhere.
3. **The choice travels sealed.** A's distance and its ticked links are sealed
   inside every box — B, C and the server cannot change them.
4. **Hub C can refuse.** *Receive → Accept packets from hubs beyond this one* off = C takes only
   traffic that started at its direct partner.
5. **No loops, no duplicates.** Every box records the hubs it passed; it never returns to one of
   them, and copies arriving over two routes are dropped.

![Multi-hop settings on a hub](img/hub-settings.jpg)

---

## 5. Encryption: three layers, the server holds no key

| layer | protects | keys known to |
|---|---|---|
| **Meshtastic channel / private-message encryption** (unchanged) | the message on the radio and everywhere after it | the radios on that channel; for private messages only the sending and the receiving radio |
| **Ura end-to-end boxes** (X25519 key agreement, AES-256-CTR, HMAC-SHA256) | everything one hub sends another: the packet, its channel, sender, multi-hop list | **only the two hubs of a link** — each hub keeps its private key; the server only relays public keys |
| **TLS to the server** with a pinned certificate | the connection itself, registration, rules | hub and server (the server sees the sealed boxes, never their content) |

What the server **does** know: which hubs exist (name, code, position, the operator's e-mail for
the admin), which links exist, how many boxes and bytes pass per hour, the nodes each hub reports
for the public map. What it **never** knows: message text, channel keys, who wrote to whom, what
kind of packet a box contains.

Even a server operator with full access to the server cannot read traffic, and cannot slip a fake
key in without the operators noticing — the safety codes would no longer match.

---

## 6. The public view

- **Map** — all hubs, their nodes (heard in the last days) and links; live packet dots.
- **Hubs** — every hub with its code, status and links; each hub page shows its rules and traffic.
- **Statistics** — per link, packets in both directions over 24 hours, 7 or 30 days.
- **Complaints** — anyone can report a problem with a hub or node; every case and its answer is
  public.

![Live map close-up: nodes heard by one hub](img/map-nodes.jpg)

![Statistics: one chart per link, both directions](img/server-stats.jpg)

---

## 7. Day-to-day

- Updates: `git pull` and restart the service — see the install guides.
- Backups: the hub's `identity.key` and `config.json`; the server's database and certificate.
- Troubleshooting, counters, airtime: [OPERATIONS.md](OPERATIONS.md).
- MeshCore support is planned; the architecture (hubs decide, server relays sealed boxes) stays the
  same.

*The pictures in this guide show a demonstration network with made-up hubs.*
