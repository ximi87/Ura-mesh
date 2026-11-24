# Running Ura on Proxmox containers (CT / LXC)

Both programs run unchanged in an **unprivileged Ubuntu 24.04 container** (the defaults of *Create CT*).
How to install them in a CT is in [INSTALL-SERVER.md](INSTALL-SERVER.md) and
[INSTALL-HUB.md](INSTALL-HUB.md#running-the-hub-in-a-proxmox-container-ct--lxc) (USB radio passthrough,
GID 20). This page covers the **day-to-day setup that was then run for real** (2026-11): the server
moved from a virtual machine into a CT, and one site split into **one hub per radio** — a Meshtastic hub
in a VM and a MeshCore hub in a CT, each with its own address.

The examples use CT 100 for the server, CT 103 for a hub, VM 101 for another hub, and addresses from
`192.168.1.0/24` — use your own.

## The setup that runs

```
                      Ura server  (CT 100, 192.168.1.20)
                     /            |              \
   hub XX-AAA (VM 101)    hub XX-AAM (CT 103)    hub YY-BBB (another site)
   Meshtastic radio       MeshCore radio         Meshtastic + MeshCore radio
   192.168.1.10           192.168.1.21
```

- Two hubs at one site are simply **two hubs**: each has its own address, identity, login password,
  registration and approval on the server. Neither knows about the other.
- Each hub has the tunnel of its own radio: XX-AAA a Meshtastic tunnel, XX-AAM a MeshCore tunnel.
- YY-BBB has both radios, so it has both tunnels and connects **its Meshtastic tunnel with XX-AAA**
  and **its MeshCore tunnel with XX-AAM** — two connections, to two different hubs.

## Moving a running server from a VM into a CT (the hubs notice nothing)

The hubs know the server by its **address** and its **TLS fingerprint**. Keep both, and every hub
reconnects by itself, without a warning and without anything to trust or register again. The
fingerprint lives in the server's data folder (`tls.key` / `tls.crt`), so copying that folder keeps it.

1. Install the server in the CT as in [INSTALL-SERVER.md](INSTALL-SERVER.md) (the installer's data
   folder is `/var/lib/ura-server`, user `ura`). Give the CT a free address for now.
2. Stop the server on both, and copy the **whole data folder** from the VM into the CT:

   ```bash
   # in the CT
   systemctl stop ura-server
   mv /var/lib/ura-server /var/lib/ura-server.empty && mkdir -m 700 /var/lib/ura-server
   # on the VM (old data folder: the URA_DATA of its service)
   sudo systemctl stop ura-server
   cd /opt/ura/data && tar cf - . | ssh root@<CT address> 'tar xf - -C /var/lib/ura-server'
   # in the CT
   chown -R ura:ura /var/lib/ura-server
   ```

   It holds the database (hubs, approvals, connections, settings), `tls.key` / `tls.crt` (the
   fingerprint), the Let's Encrypt account and certificate (`acme/`), logs and the map tile cache.
   Copy `ura.db-wal` / `ura.db-shm` too — they belong to the database.
3. Shut the VM down, then give the CT the **VM's address** and restart it (on the Proxmox host):

   ```bash
   qm shutdown <VM>
   pct set 100 -net0 name=eth0,bridge=vmbr0,gw=192.168.1.1,ip=192.168.1.20/24,type=veth   # keep your hwaddr= if shown
   pct reboot 100
   ```

   The router's port forwards (website 443 → 8443, hubs 8100) and the hubs' saved address now reach
   the CT. Nothing changes on the router or on any hub.
4. Check: the log says `TLS fingerprint …` — the **same** as before; the hubs come online within
   seconds (`hub … online … status approved`); the website still shows the Let's Encrypt certificate.

**Going back:** stop the server in the CT, copy the data folder back to the VM (`chown` to the VM's
service user), give the CT its own address again, start the VM.

Tested: both hubs reconnected within 10 s (one over the internet through the public name, one over
the LAN), same fingerprint, Let's Encrypt certificate served, Meshtastic and MeshCore traffic between
the hubs, no errors.

## One hub per radio: moving a radio from a VM hub into a CT hub

Starting point: one hub in a VM with both radios. Goal: the VM keeps the Meshtastic radio, a new hub in
a CT gets the MeshCore radio.

1. **On the VM hub's website**, remove the MeshCore radio (*MeshCore → Radio*). Its MeshCore
   connections end and the partner hubs forget its MeshCore nodes; the Meshtastic connections stay.
2. **On the Proxmox host**, take the radio away from the VM:

   ```bash
   qm config 101 | grep usb           # e.g. usb1: host=239a:8029 is the MeshCore radio
   qm set 101 -delete usb1            # USB hot-unplug, the VM keeps running
   ```

   If the host has a **udev rule or script that re-attaches the radio to the VM** (some setups use one
   so a radio that resets comes back to the VM), remove the radio's line from it too — otherwise it
   gives the radio back to the VM the next time it resets.
3. **Pass the radio into the CT** by its fixed name with GID 20 (see
   [INSTALL-HUB.md](INSTALL-HUB.md#running-the-hub-in-a-proxmox-container-ct--lxc)):

   ```bash
   ls -l /dev/serial/by-id/            # the radio now shows on the host
   pct set 103 -dev0 /dev/serial/by-id/usb-RAKwireless_WisCore_RAK3401_Board_…-if00,gid=20
   ```

   On Proxmox VE 9.1 this worked on the **running** CT: the device appeared inside at the same
   `/dev/serial/by-id/…` path, group `dialout`, without a restart. On older versions restart the CT.
4. **In the CT**, install the hub (or reset it to a fresh hub), open its website, choose the login
   password, and set it up with the wizard: the radio is found under its own name, the server address
   is filled in, *Connect*, then connect the MeshCore tunnel with the other hubs' MeshCore tunnels.

Tested: the CT hub registered as its own hub with its own address; its MeshCore tunnel connected with
the other site's MeshCore tunnel; 51 MeshCore packets passed in 20 minutes in one direction, adverts in
the other; the VM hub's Meshtastic connection carried nodeinfo and telemetry at the same time.

## Start on boot and names

A new CT does **not** start when the Proxmox host boots. For the server and the hubs, turn it on
(*CT → Options → Start at boot*, or on the host):

```bash
pct set 100 -onboot 1
```

The programs inside start with the CT by themselves (`systemctl is-enabled ura-server` / `ura-hub`
says `enabled`).

> **A CT with a USB radio passed in may refuse to start if the radio is not plugged in** — the
> passthrough needs the device to exist. Keep the radio plugged in when the host boots.

Renaming a CT (e.g. from a test name) without restarting it:

```bash
pct set 103 -hostname ura-hub                  # on the host: Proxmox's name, used at the next start
# inside the CT, so it takes effect now:
hostnamectl set-hostname ura-hub
sed -i 's/<old name>/ura-hub/g' /etc/hosts
```

The programs keep running; a hub's name on the server is its own *Hub details*, not the CT's name.
