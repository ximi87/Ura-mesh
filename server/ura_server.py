#!/usr/bin/env python3
"""ura-server: minimal rendezvous + relay between ura-hubs.

Hubs connect OUT over TLS and exchange JSON lines. The server forwards
mesh frames between hubs and counts them. It never decodes mesh payloads
(Meshtastic packets stay encrypted inside their ServiceEnvelope).
"""
import asyncio, base64, hashlib, json, logging, os, ssl, subprocess, time
from collections import defaultdict

DATA_DIR = os.environ.get("URA_DATA", os.path.dirname(os.path.abspath(__file__)) + "/data")
PORT = int(os.environ.get("URA_PORT", "8100"))
HUBS_FILE = os.path.join(DATA_DIR, "hubs.json")      # {hub_id: {"name":..,"key":..,"approved":bool}}
DEDUP_SECONDS = 600

log = logging.getLogger("ura-server")
online = {}                                           # hub_id -> writer
seen = {}                                             # sha256(payload) -> time
stats = defaultdict(int)                              # (src, dst, net) -> frames


def load_hubs():
    try:
        with open(HUBS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def tls_context():
    crt, key = os.path.join(DATA_DIR, "tls.crt"), os.path.join(DATA_DIR, "tls.key")
    if not os.path.exists(crt):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256",
                        "-nodes", "-days", "3650", "-subj", "/CN=ura-server", "-keyout", key, "-out", crt],
                       check=True, capture_output=True)
        os.chmod(key, 0o600)
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain(crt, key)
    der = ssl.PEM_cert_to_DER_cert(open(crt).read())
    fp = hashlib.sha256(der).hexdigest().upper()
    log.info("TLS fingerprint %s", ":".join(fp[i:i + 2] for i in range(0, len(fp), 2)))
    return ctx


async def send(writer, obj):
    writer.write((json.dumps(obj, separators=(",", ":")) + "\n").encode())
    await writer.drain()


def duplicate(payload: bytes) -> bool:
    now = time.time()
    for k in [k for k, t in seen.items() if now - t > DEDUP_SECONDS]:
        del seen[k]
    h = hashlib.sha256(payload).digest()
    if h in seen:
        return True
    seen[h] = now
    return False


async def handle(reader, writer):
    peer = writer.get_extra_info("peername")
    hub_id = None
    try:
        hello = json.loads(await asyncio.wait_for(reader.readline(), 15))
        hubs = load_hubs()
        h = hubs.get(hello.get("hub"))
        if hello.get("t") != "hello" or not h or h.get("key") != hello.get("key") or not h.get("approved"):
            log.warning("refused %s from %s", hello.get("hub"), peer)
            await send(writer, {"t": "refused"})
            return
        hub_id = hello["hub"]
        old = online.pop(hub_id, None)
        if old:
            old.close()
        online[hub_id] = writer
        await send(writer, {"t": "welcome", "hub": hub_id})
        log.info("hub %s (%s) online from %s", hub_id, h.get("name"), peer)
        while line := await reader.readline():
            msg = json.loads(line)
            if msg.get("t") == "ping":
                await send(writer, {"t": "pong"})
            elif msg.get("t") == "mesh":
                payload = base64.b64decode(msg["data"])
                if duplicate(payload):
                    continue
                out = {"t": "mesh", "net": msg["net"], "from": hub_id, "topic": msg.get("topic", ""), "data": msg["data"]}
                for other, w in list(online.items()):
                    if other == hub_id:
                        continue
                    try:
                        await send(w, out)
                        stats[(hub_id, other, msg["net"])] += 1
                        log.info("relay %s -> %s %s %d bytes", hub_id, other, msg["net"], len(payload))
                    except Exception as e:
                        log.warning("send to %s failed: %s", other, e)
    except Exception as e:
        log.warning("hub %s connection error: %s", hub_id or peer, e)
    finally:
        if hub_id and online.get(hub_id) is writer:
            del online[hub_id]
            log.info("hub %s offline", hub_id)
        writer.close()


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    os.makedirs(DATA_DIR, exist_ok=True)
    server = await asyncio.start_server(handle, "0.0.0.0", PORT, ssl=tls_context())
    log.info("listening on %d", PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
