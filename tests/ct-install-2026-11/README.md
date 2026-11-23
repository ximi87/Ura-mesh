# Install test: Ura in Proxmox containers, done as a first-time user

**Date:** 2026-11-23 · **Software:** ura-server / ura-hub 0.3.0, as on GitHub that day.

## The two questions

1. **Does Ura run in a Proxmox container (CT / LXC)?** — **Yes.** Server and hub install and run
   unchanged. A USB radio needs one setting on the Proxmox host (*Device Passthrough* with **GID 20**);
   with that, the hub recognised, connected and used a MeshCore radio, and real LoRa traffic crossed a
   link between two hubs in containers in two countries.
2. **Does the installation work as the documents describe it?** — **Almost.** The install scripts and
   the wizard worked first try. A newcomer was stopped once (no `git` on a fresh system) and misled
   in several places by outdated text. All of it is fixed in the same commit as this report (list below).

## How the test was done

Only the public GitHub documents were followed (README, INSTALL-SERVER.md, INSTALL-HUB.md), step by
step, starting from `git clone` on fresh containers — no knowledge of the code was used. Every place
where a newcomer would get stuck or be misled was written down. Real names are replaced by test names
(hubs *CT Test A* / *CT Test B*, codes XA-CTA / XB-CTB, made-up positions).

| Container | Proxmox | Template | Role | Resources |
|---|---|---|---|---|
| test server | VE 9.0 (site A) | Ubuntu 24.04 standard, unprivileged, nesting on | ura-server | 1 core, 512 MB, 8 GB |
| test hub A | VE 9.0 (site A) | same | ura-hub, **no radio** | 1 core, 1 GB, 8 GB |
| test hub B | VE 9.1 (site B) | same | ura-hub, **MeshCore RAK3401** on USB | 1 core, 1 GB, 8 GB |

All created with the normal *Create CT* defaults and a static address.

## Server — INSTALL-SERVER.md

| Step | Result | Screenshot |
|---|---|---|
| `git clone …` | ❌ **`git: command not found`** — a fresh Ubuntu CT has no git; the guide's first command fails. Worked after `apt install git`. | |
| `sudo bash contrib/install-server.sh` | ✅ first try: service running, fingerprint in the log, website on 8443 | |
| `ufw allow 8100/tcp`, `8443/tcp` | rules added, but `ufw status` = *inactive*; the guide didn't say what that means | |
| admin password | ✅ | [s01](screenshots/s01-admin-first-open.png), [s02](screenshots/s02-admin-after-password.png) |
| *Register a hub* page | ✅ address and fingerprint — but its steps named old menus (*Settings → Ura server*, *the hub's Status page*, *In Radio choose the port*) and offered **Bluetooth**, which the hub does not support | [s03](screenshots/s03-register-page.png) |
| approve the hubs | ✅ | [s04](screenshots/s04-admin-waiting.png), [s05](screenshots/s05-admin-approved.png) |

## Hubs — README quick start + INSTALL-HUB.md

| Step | Hub A (no radio) | Hub B (RAK3401) | Screenshots |
|---|---|---|---|
| `git clone` | needs `apt install git` first | same | |
| `sudo bash contrib/install-hub.sh` | ✅ venv, meshtastic 2.7.11, user `ura` in `dialout`, service running | ✅ | |
| first page | asked for the "**admin** password" — the guide said *hub password*, factory reset *login password* | same | [hal-01](screenshots/hal-01-first-open.png) |
| wizard step 1 — name, codes, location | ✅ clear | ✅ | [hal-02](screenshots/hal-02-wizard.png), [hal-03](screenshots/hal-03-step1-filled.png) |
| wizard step 2 — radio | "No USB radio found" (correct) | after passthrough: **MeshCore radio "D2617580" — ttyACM0 (RAKwireless WisCore RAK3401 Board)**; *Connect* → 321 contacts | [hal-04](screenshots/hal-04-step2.png), [hde-05](screenshots/hde-05-step2-port-found.png), [hde-06](screenshots/hde-06-step2-connected.png) |
| step 3 — prepare | — | already "Ready for Ura" (this radio had been prepared before) | |
| step 4 — server | via *Skip the wizard* → *Links & rules* (the advanced way, because no radio) ✅ | wizard ✅ | [hal-05…09](screenshots/hal-09-registration-sent.png), [hde-07](screenshots/hde-07-step4-checked.png), [hde-08](screenshots/hde-08-step4-sent.png) |
| step 5 — link | *Accept* ✅ | *Ask for a link* ✅ | [hal-10](screenshots/hal-10-link-request.png), [hal-11](screenshots/hal-11-link-active.png), [hde-09](screenshots/hde-09-link-asked.png) |
| step 6 — ready | | ✅ "Everything works …" — but it offered *Go to the status page* (no longer exists) | [hde-10](screenshots/hde-10-wizard-after-link.png) |

**Traffic:** hub B's log: `MeshCore radio -> flood group text (10 hops): sent to XA-CTA`,
`MeshCore advert of "D2617580" announced to XA-CTA`; hub A's log: `from XB-CTB MeshCore group text:
not put on air (no MeshCore radio connected)` — correct, hub A has no radio. The test server showed
hub B with 239 MeshCore nodes and its radio connected.

## The radio in the container

| Test | Result |
|---|---|
| CT without passthrough | no `/dev/ttyACM*` inside — the hub correctly shows "No USB radio found" |
| Proxmox host had the `cdc_acm` driver blacklisted (from an earlier VM setup) | no serial port on the host at all → removed the blacklist, `modprobe cdc_acm` |
| passthrough `/dev/ttyACM0`, GID 20 | ✅ hub identifies and connects the radio; there is no `/dev/serial/by-id` inside a CT, the hub falls back to `/dev/ttyACM*` by itself |
| radio unplugged / plugged in (simulated on the host) | ✅ comes back as the same device; the hub reconnects within 20 s |
| passthrough by the fixed name `/dev/serial/by-id/…`, GID 20 | ✅ the device appears in the CT under that name; after choosing it once on the *Radio* page the hub connects; unplug/replug ✅ | 
| passthrough with GID 0 (the Proxmox default) | ❌ `[Errno 13] Permission denied` — the hub cannot open the radio |
| Meshtastic radio on USB in a CT | not tested (no spare radio); same serial code as MeshCore |

Proxmox screens: [pve-01 Resources](screenshots/pve-01-ct-resources-passthrough.png),
[pve-03 Add device](screenshots/pve-03-device-passthrough-dialog.png),
[pve-04 Advanced: GID](screenshots/pve-04-device-passthrough-advanced.png) — **the GID field is hidden
behind "Advanced"**, which is why a newcomer leaves it at 0.

After switching the passthrough from `ttyACM0` to the by-id name, the hub's *MeshCore → Radio* page said
"no radio plugged in" while its own port list showed the same radio under the new name; choosing it and
*Connect* fixed it ([hde-11](screenshots/hde-11-mc-radio-page-byid.png), [hde-12](screenshots/hde-12-mc-radio-connected-byid.png)).

## Problems found and what was fixed

| # | Problem | Fix |
|---|---|---|
| 1 | README quick start: steps 1, 2, 3, 4, **6**, 7 | renumbered |
| 2 | README / INSTALL-HUB: hub radio needs "Meshtastic 2.7 **with the Ura patch**" | checked: still true and explained in FIRMWARE.md (nodes with *Ignore MQTT* would drop Ura traffic). Building it needs a 1–2 GB tool chain — the biggest hurdle for a newcomer; ready-made binaries would help |
| 3 | no guide mentioned containers | new section *Running the hub in a Proxmox container* in INSTALL-HUB.md; CT named in README, GUIDE, INSTALL-SERVER |
| 4 | `git` missing on a fresh Debian/Ubuntu: the first command fails | every guide now starts with `sudo apt install -y git` |
| 5 | `ufw` *inactive* not explained | INSTALL-SERVER: "only if the server runs a firewall …" |
| 6 | server *Register a hub* page: old menu names, Bluetooth | texts now point to the wizard steps; Bluetooth removed |
| 7 | INSTALL-HUB wizard step 2: "MeshCore later" | "Meshtastic or MeshCore" |
| 8 | INSTALL-HUB: "problems show on *Status*" | "on the home map and the *Overview* pages" |
| 9 | install-hub.sh: "follow INSTALL-HUB from step 4" | "choose the login password; the setup wizard then guides you" |
| 10 | admin / hub / login password — three names | hub website and guides: **login password** (the server keeps *admin password*) |
| 11 | wizard: "**Trusted** fingerprint" shown before trusting | "Server fingerprint" |
| 12 | wizard end: *Go to the status page*; "the "Links" page" | *Go to the home map*; "Links & rules" |
| 13 | *Links & rules → Ura server*: "not set up — go to Settings" (the server settings are on this page) | "not set up — enter the server address below" |
| 14 | "Multi-hop (transit) MT / MC" — abbreviations | "— Meshtastic" / "— MeshCore" |
| 15 | GID hidden behind *Advanced* in Proxmox → `Permission denied` | explained with a screenshot in the CT section |

Not changed (worth doing later): when the radio's port path changes, the hub could follow the same
radio to its new path by itself instead of asking to choose it again.
