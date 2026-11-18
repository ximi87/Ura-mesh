#!/bin/bash
# Install ura-server on Debian/Ubuntu. Run as root:  sudo bash contrib/install-server.sh
# It shows every change first and asks before doing anything.
set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/ximi87/Ura-mesh.git}"
cat <<INFO
This will:
  1. install the packages git and openssl (apt) — the server needs nothing else (Python standard library)
  2. create a system user "ura"
  3. put Ura in /opt/ura (git clone of $REPO_URL)
  4. keep the server's data in /var/lib/ura-server
  5. install and start the systemd service "ura-server" (hubs on port 8100, website on port 8443)
Open TCP 8100 and 8443 in your firewall yourself (see docs/INSTALL-SERVER.md).
INFO
read -r -p "Continue? [y/N] " ok; [ "$ok" = "y" ] || [ "$ok" = "Y" ] || exit 1
apt-get update -q && apt-get install -y -q git openssl python3
id ura >/dev/null 2>&1 || useradd --system --home /var/lib/ura-server --shell /usr/sbin/nologin ura
[ -d /opt/ura/.git ] || git clone "$REPO_URL" /opt/ura
install -d -o ura -g ura -m 700 /var/lib/ura-server
install -m 644 /opt/ura/contrib/ura-server.service /etc/systemd/system/ura-server.service
systemctl daemon-reload
systemctl enable --now ura-server
sleep 3
journalctl -u ura-server -n 5 --no-pager
echo
echo "Done. Open https://<this-server>:8443/#/admin and choose the admin password."
echo "The certificate fingerprint shown in the log above is what hub operators compare when they register."
