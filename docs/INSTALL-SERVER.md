# Installing a Ura server

The server is the public meeting point: hubs register with it, find each other and pass
sealed boxes through it. It shows the public map and statistics. It needs **only Python 3**
(standard library) and `openssl` for its certificate.

## What you need

- A small Linux server (1 CPU, 512 MB RAM is plenty) with a public address, Debian/Ubuntu.
- A domain name pointing to it (e.g. `ura.example.org`) — recommended; Ura then gets its own
  browser-trusted certificate automatically.
- Two open TCP ports: **8100** (hubs) and **8443** (website). Both can be changed.

## 1. Install

```bash
git clone https://github.com/ximi87/Ura-mesh.git
cd Ura-mesh
sudo bash contrib/install-server.sh
```

The script asks first. It installs `git`, `openssl`, `python3`, creates a system user `ura`,
puts Ura in `/opt/ura`, keeps data in `/var/lib/ura-server` and starts the service
`ura-server`.

<details><summary>Manual installation</summary>

```bash
sudo apt install git openssl python3
sudo useradd --system --home /var/lib/ura-server --shell /usr/sbin/nologin ura
sudo git clone https://github.com/ximi87/Ura-mesh.git /opt/ura
sudo install -d -o ura -g ura -m 700 /var/lib/ura-server
sudo cp /opt/ura/contrib/ura-server.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now ura-server
```

Startup options (service file): `URA_DATA` (data folder), `URA_PORT` (hub port, default
`8100`), `URA_WEB_PORT` (website, default `8443`). Everything else is an *Advanced setting*
on the admin page.
</details>

## 2. Open the firewall

```bash
sudo ufw allow 8100/tcp     # hubs
sudo ufw allow 8443/tcp     # website
```

## 3. Choose the admin password

Open `https://<server>:8443/#/admin`, accept the self-signed certificate once and choose the
admin password.

## 4. Publish the fingerprint

On first start the server creates its certificate (`/var/lib/ura-server/tls.crt`) and logs
its **SHA-256 fingerprint**:

```bash
journalctl -u ura-server | grep fingerprint
```

The same fingerprint is shown on the public page **Register a hub**. Hub operators compare it
before they trust the server. **Never replace `tls.crt`/`tls.key`** once hubs use the server —
every hub would see a different fingerprint and refuse to connect (that is the protection
working). Back them up.

## 5. Approve hubs — *Admin*

New hubs appear under **Waiting for approval** with name, code, e-mail and position. Approve
or remove them. Removing a hub ends all its links and takes its nodes off the map.

E-mail confirmation is not automatic yet (no mail sending); you can mark an address as
confirmed by hand after checking it.

## 6. Advanced settings — *Admin*

Every operational value is a setting with limits: whether new registrations are accepted,
node age shown, flood limit per hub, largest box, statistics retention, complaint limits,
session and lockout values, map tile source and cache, and the **project / install-guide
links** shown on the *Register a hub* page.

## Domain and certificates

Point a name (e.g. `ura.example.org`) at the server and forward the public ports to it — for
example public **443 → server 8443** (website) and **8100 → 8100** (hubs).

**Website certificate — built in, nothing to install.** In *Admin → Advanced settings* turn on
*Let's Encrypt certificate for the website*, enter the public name (and optionally an e-mail) and
save. Ura obtains a free, browser-trusted certificate from Let's Encrypt by itself (ACME with the
TLS-ALPN-01 check, which runs over the website port — no port 80 needed) and renews it 30 days
before it expires. *Admin → Website certificate* shows its state; *Get / renew certificate now*
runs it at once. Use *Test mode* first if you want to try without touching Let's Encrypt's limits.

The Let's Encrypt certificate is used only for visitors who open the website **by its name**.
Hubs, and anyone connecting by IP address, keep getting Ura's own certificate — so the
fingerprint hubs pinned never changes, also not when Let's Encrypt renews.

Requirements: the name resolves to your public address, and that address's port 443 reaches the
server's website port.

**Hubs inside the server's own network.** If a hub sits in the same network as the server and uses
the public name, many routers cannot send a connection from inside back in to their own public
address ("hairpin NAT") — the hub's *Check server* then reports that the server could not be
reached. Either let such hubs use the server's internal address (just as secure: they pin the same
fingerprint), or add a hairpin rule on the router. MikroTik example (internal network
192.168.0.0/16, server 192.168.77.20):

```
/ip firewall nat add chain=srcnat action=masquerade protocol=tcp src-address=192.168.0.0/16 \
    dst-address=192.168.77.20 dst-port=8100,8443 connection-nat-state=dstnat comment="Ura hairpin"
```

## Map tiles

Map tiles come from OpenStreetMap through the server's own cache (OpenStreetMap blocks
anonymous browser requests and asks apps to identify themselves and cache). Hubs without
internet get their tiles through the server too. Source, cache time and the contact sent to
the tile server are advanced settings. For heavy public use, consider a commercial tile
provider (change the tile source).

## Updating

```bash
cd /opt/ura && sudo git pull && sudo systemctl restart ura-server
```

## Backup

`/var/lib/ura-server`: `ura.db` (hubs, links, nodes, statistics, complaints, settings) and
`tls.crt` / `tls.key` (the identity hubs pinned).
