#!/bin/bash
# Install ura-hub on Debian/Ubuntu/Raspberry Pi OS. Run as root:  sudo bash contrib/install-hub.sh
# It shows every change first and asks before doing anything.
set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/ximi87/Ura-mesh.git}"
# Optional: the Ura server this hub will connect to (host:port) — it is then already filled in on the hub's
# website, the operator only presses "Connect". Example:  URA_SERVER=ura.example.org:8100 sudo -E bash contrib/install-hub.sh
URA_SERVER="${URA_SERVER:-}"
cat <<INFO
This will:
  1. install the packages git, python3-venv and openssl (apt)
  2. create a system user "ura" (member of "dialout" for the USB radio)
  3. put Ura in /opt/ura (git clone of $REPO_URL) and a Python environment in /opt/ura/venv
     with the Meshtastic package
  4. keep the hub's data in /var/lib/ura-hub
  5. install and start the systemd service "ura-hub" (website on port 8091)${URA_SERVER:+
  6. offer the Ura server $URA_SERVER to this hub (filled in, connect with one click)}
INFO
read -r -p "Continue? [y/N] " ok; [ "$ok" = "y" ] || [ "$ok" = "Y" ] || exit 1
apt-get update -q && apt-get install -y -q git python3-venv openssl
id ura >/dev/null 2>&1 || useradd --system --home /var/lib/ura-hub --shell /usr/sbin/nologin ura
usermod -aG dialout ura
[ -d /opt/ura/.git ] || git clone "$REPO_URL" /opt/ura
python3 -m venv /opt/ura/venv
/opt/ura/venv/bin/pip install -q -r /opt/ura/hub/requirements.txt
install -d -o ura -g ura -m 700 /var/lib/ura-hub
install -m 644 /opt/ura/contrib/ura-hub.service /etc/systemd/system/ura-hub.service
if [ -n "$URA_SERVER" ]; then
  sed -i "/^Environment=URA_WEB_PORT=/a Environment=URA_DEFAULT_SERVER=$URA_SERVER" /etc/systemd/system/ura-hub.service
fi
systemctl daemon-reload
systemctl enable --now ura-hub
sleep 3
systemctl --no-pager status ura-hub | head -5
IP=$(hostname -I | awk '{print $1}')
echo
echo "Done. Open https://$IP:8091 in a browser (accept the self-signed certificate once),"
echo "choose the login password; the setup wizard then guides you (docs/INSTALL-HUB.md, step 3)."
