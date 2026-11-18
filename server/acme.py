"""Let's Encrypt for the ura-server website — built in, no extra software.

ACME (RFC 8555) with the TLS-ALPN-01 challenge (RFC 8737): Let's Encrypt connects to the
website port (public 443) with ALPN "acme-tls/1"; the server answers that connection with a
special one-day certificate that proves control of the domain. Python standard library +
the `openssl` command. Keys: account key RSA-2048 (RS256 signatures), certificate key EC P-256.
"""
import base64, hashlib, json, logging, os, ssl, subprocess, tempfile, threading, time, urllib.error, urllib.request

log = logging.getLogger("ura-server.acme")

PRODUCTION = "https://acme-v02.api.letsencrypt.org/directory"
STAGING = "https://acme-staging-v02.api.letsencrypt.org/directory"
ACME_TLS_ALPN = "acme-tls/1"
UA = "Ura-server-acme"


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def run(*args, data=None):
    return subprocess.run(list(args), input=data, capture_output=True, check=True).stdout


class Acme:
    """Obtains and renews the website certificate. Thread-safe enough for one renewal thread."""

    def __init__(self, data_dir):
        self.dir = os.path.join(data_dir, "acme")
        os.makedirs(self.dir, exist_ok=True)
        os.chmod(self.dir, 0o700)
        self.challenges = {}            # domain -> ssl.SSLContext answering acme-tls/1
        self.lock = threading.Lock()
        self.status = {"state": "off"}
        self.dirs, self.nonce, self.kid = {}, None, None

    # ───── files ─────
    def cert_path(self, domain):
        return os.path.join(self.dir, f"{domain}.crt"), os.path.join(self.dir, f"{domain}.key")

    def cert_info(self, domain):
        crt, key = self.cert_path(domain)
        if not (os.path.exists(crt) and os.path.exists(key)):
            return None
        out = run("openssl", "x509", "-in", crt, "-noout", "-enddate", "-issuer").decode()
        end = [l for l in out.splitlines() if l.startswith("notAfter=")][0].split("=", 1)[1]
        expires = ssl.cert_time_to_seconds(end)
        issuer = [l for l in out.splitlines() if l.startswith("issuer=")][0].split("=", 1)[1].strip()
        return {"expires": int(expires), "issuer": issuer, "days_left": int((expires - time.time()) // 86400)}

    def context_for(self, domain):
        """SSL context with the Let's Encrypt certificate for `domain`, or None if there is none yet."""
        crt, key = self.cert_path(domain)
        if not os.path.exists(crt):
            return None
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(crt, key)
        return ctx

    # ───── ACME plumbing ─────
    def _account_key(self):
        path = os.path.join(self.dir, "account.key")
        if not os.path.exists(path):
            run("openssl", "genrsa", "-out", path, "2048")
            os.chmod(path, 0o600)
        mod = run("openssl", "rsa", "-in", path, "-noout", "-modulus").decode().strip().split("=", 1)[1]
        self.jwk = {"e": "AQAB", "kty": "RSA", "n": b64u(bytes.fromhex(mod))}
        self.thumbprint = b64u(hashlib.sha256(json.dumps(self.jwk, separators=(",", ":"), sort_keys=True).encode()).digest())
        return path

    def _http(self, url, body=None, ctype="application/jose+json"):
        req = urllib.request.Request(url, data=body, headers={"User-Agent": UA, "Content-Type": ctype},
                                     method="POST" if body is not None else ("HEAD" if url == self.dirs.get("newNonce") else "GET"))
        try:
            r = urllib.request.urlopen(req, timeout=30)
            code, headers, data = r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            code, headers, data = e.code, e.headers, e.read()
        if headers.get("Replay-Nonce"):
            self.nonce = headers["Replay-Nonce"]
        return code, headers, data

    def _post(self, url, payload, retry=True):
        """Signed POST (payload None = POST-as-GET)."""
        if not self.nonce:
            self._http(self.dirs["newNonce"])
        protected = {"alg": "RS256", "nonce": self.nonce, "url": url}
        if self.kid:
            protected["kid"] = self.kid
        else:
            protected["jwk"] = self.jwk
        p64 = b64u(json.dumps(protected).encode())
        b64 = "" if payload is None else b64u(json.dumps(payload).encode())
        sig = run("openssl", "dgst", "-sha256", "-sign", self.key, data=f"{p64}.{b64}".encode())
        self.nonce = None
        code, headers, data = self._http(url, json.dumps({"protected": p64, "payload": b64, "signature": b64u(sig)}).encode())
        if code == 400 and retry and b"badNonce" in data:
            return self._post(url, payload, retry=False)
        if code >= 400:
            raise RuntimeError(f"ACME {code}: {data[:300].decode(errors='replace')}")
        return headers, (json.loads(data) if data and headers.get("Content-Type", "").startswith("application/") and b"{" in data[:2] else data)

    def _poll(self, url, done=("valid",), fail=("invalid",), tries=30):
        for _ in range(tries):
            _, obj = self._post(url, None)
            if obj.get("status") in done:
                return obj
            if obj.get("status") in fail:
                raise RuntimeError("ACME: " + json.dumps(obj.get("error") or obj.get("challenges") or obj)[:400])
            time.sleep(3)
        raise RuntimeError("ACME: timed out waiting for " + url)

    def _challenge_context(self, domain, key_authorization):
        """One-day certificate with the acmeIdentifier extension (RFC 8737)."""
        digest = hashlib.sha256(key_authorization.encode()).hexdigest()
        with tempfile.TemporaryDirectory(dir=self.dir) as tmp:
            crt, key = os.path.join(tmp, "c.pem"), os.path.join(tmp, "k.pem")
            run("openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes", "-days", "1",
                "-subj", f"/CN={domain}", "-addext", f"subjectAltName=DNS:{domain}",
                "-addext", f"1.3.6.1.5.5.7.1.31=critical,DER:0420{digest}", "-keyout", key, "-out", crt)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            ctx.load_cert_chain(crt, key)
        ctx.set_alpn_protocols([ACME_TLS_ALPN])
        return ctx

    # ───── public ─────
    def obtain(self, domain, email="", staging=False):
        """Run a full ACME order for `domain`. Raises on failure; returns cert_info on success."""
        with self.lock:
            self.status = {"state": "working", "detail": "contacting Let's Encrypt", "since": int(time.time())}
            self.nonce, self.kid = None, None
            directory = STAGING if staging else PRODUCTION
            self.dirs = json.loads(self._http(directory)[2])
            self.key = self._account_key()
            acc = {"termsOfServiceAgreed": True}
            if email:
                acc["contact"] = [f"mailto:{email}"]
            headers, _ = self._post(self.dirs["newAccount"], acc)
            self.kid = headers["Location"]
            headers, order = self._post(self.dirs["newOrder"], {"identifiers": [{"type": "dns", "value": domain}]})
            order_url = headers["Location"]
            for authz_url in order["authorizations"]:
                _, authz = self._post(authz_url, None)
                if authz.get("status") == "valid":
                    continue
                ch = next((c for c in authz["challenges"] if c["type"] == "tls-alpn-01"), None)
                if not ch:
                    raise RuntimeError("Let's Encrypt offered no tls-alpn-01 challenge")
                self.challenges[domain] = self._challenge_context(domain, f"{ch['token']}.{self.thumbprint}")
                try:
                    self.status["detail"] = "Let's Encrypt is checking the domain"
                    self._post(ch["url"], {})
                    self._poll(authz_url)
                finally:
                    self.challenges.pop(domain, None)
            self.status["detail"] = "requesting the certificate"
            crt_path, key_path = self.cert_path(domain)
            new_key = key_path + ".new"
            run("openssl", "req", "-new", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes",
                "-keyout", new_key, "-subj", f"/CN={domain}", "-addext", f"subjectAltName=DNS:{domain}", "-outform", "DER", "-out", new_key + ".csr")
            os.chmod(new_key, 0o600)
            csr = open(new_key + ".csr", "rb").read()
            self._post(order["finalize"], {"csr": b64u(csr)})
            order = self._poll(order_url)
            _, pem = self._post(order["certificate"], None)
            with open(crt_path + ".new", "wb") as f:
                f.write(pem if isinstance(pem, bytes) else pem.encode())
            os.replace(new_key, key_path)
            os.replace(crt_path + ".new", crt_path)
            os.remove(new_key + ".csr")
            info = self.cert_info(domain)
            self.status = {"state": "ok", "detail": "certificate installed", "since": int(time.time()), **info}
            log.info("Let's Encrypt certificate for %s installed (%s days, %s)", domain, info["days_left"], info["issuer"])
            return info


def parse_client_hello(data: bytes):
    """Return (server_name, [alpn protocols]) from a TLS ClientHello, or (None, []) if not parseable."""
    try:
        if len(data) < 43 or data[0] != 22 or data[5] != 1:
            return None, []
        p = 9 + 2 + 32                                   # record(5) + handshake hdr(4) + version + random
        p += 1 + data[p]                                 # session id
        p += 2 + int.from_bytes(data[p:p + 2], "big")    # cipher suites
        p += 1 + data[p]                                 # compression methods
        end = p + 2 + int.from_bytes(data[p:p + 2], "big")
        p += 2
        sni, alpn = None, []
        while p + 4 <= min(end, len(data)):
            typ, ln = int.from_bytes(data[p:p + 2], "big"), int.from_bytes(data[p + 2:p + 4], "big")
            body = data[p + 4:p + 4 + ln]
            if typ == 0 and len(body) > 5:               # server_name
                sni = body[5:5 + int.from_bytes(body[3:5], "big")].decode(errors="replace")
            elif typ == 16 and len(body) > 2:            # ALPN
                q = 2
                while q < len(body):
                    n = body[q]
                    alpn.append(body[q + 1:q + 1 + n].decode(errors="replace"))
                    q += 1 + n
            p += 4 + ln
        return sni, alpn
    except Exception:
        return None, []
