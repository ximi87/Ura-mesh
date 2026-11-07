"""Settings of a ura-mesh-client (one point).

Stored in <DATA_DIR>/config.json and edited on the admin page. Only these come from the
environment: DATA_DIR (./data), WEB_HOST (0.0.0.0), WEB_PORT (8091).
"""
import copy
import json
import os
import secrets

DATA_DIR = os.path.abspath(os.environ.get("DATA_DIR", "data"))
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "8091"))

DEFAULTS = {
    "point": {
        "name": "",                     # name of this point, e.g. "Tirana"
        "country": "",                  # 2-letter code, shown with relayed messages: [AL] Name: text
        "city": "",
        "lat": None,                    # location for the server map (city level is enough)
        "lon": None,
        "contact": "",                  # how the server owner can reach you
    },
    "meshtastic": {
        "enabled": False,
        "connection": "tcp",            # tcp | serial
        "host": "",
        "serial_port": "",
    },
    "meshcore": {
        "enabled": False,
        "connection": "serial",         # serial | tcp
        "serial_port": "",
        "baudrate": 115200,
        "host": "",
        "tcp_port": 5000,
    },
    "server": {
        "enabled": False,
        "url": "",                      # e.g. https://192.168.77.20:8100 (set by join / certificate check)
        "point_id": "",                 # given by the server when you ask to join
        "key": "",
        "fingerprint": "",              # pinned SHA-256 of the server certificate
        "rf_per_min": 2,                # max relayed messages per minute put on the air here
        "links": [],                    # [{"room": "Global", "mt_channel": 1, "mc_channel": 1,
                                        #   "send": true, "receive": true}], channel -1 = off
        "max_busy_pct": 25,             # channel busy above this % (Meshtastic) → hold messages from other points
        "max_tx_pct": 5,                # this radio transmitted more than this % of the last hour → hold them
        "notify": True,                 # tell the sender what happened (reaction / short notice)
        "share": {"group": True, "public": False, "private": False, "positions": False},
                                        # checklist: what this point lets cross (the server owner must allow it too)
    },
    "auth": {"password_hash": "", "session_secret": ""},
}

SECRET_FIELDS = {("server", "key")}
READONLY_FIELDS = {("server", "point_id"), ("server", "key"), ("server", "fingerprint"),
                   ("server", "url")}   # url + fingerprint change only through a certificate check
MASK = "••••••••"
LATLON = ("point.lat", "point.lon")


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(out.get(k), dict) and isinstance(v, dict):
            out[k] = _merge(out[k], v)
        elif k in out:
            out[k] = v
    return out


def load():
    os.makedirs(DATA_DIR, exist_ok=True)
    cfg = copy.deepcopy(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = _merge(DEFAULTS, json.load(f))
    if not cfg["auth"]["session_secret"]:
        cfg["auth"]["session_secret"] = secrets.token_hex(32)
        save(cfg)
    return cfg


def save(cfg):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def public_view(cfg):
    out = {k: copy.deepcopy(v) for k, v in cfg.items() if k != "auth"}
    for sec, key in SECRET_FIELDS:
        if out[sec].get(key):
            out[sec][key] = MASK
    return out


def _coerce(default, value, path):
    if isinstance(default, bool):
        if not isinstance(value, bool):
            raise ValueError(f"{path}: expected true/false")
        return value
    if isinstance(default, int) or path in LATLON:
        if value in ("", None):
            return None if default is None else default
        try:
            return float(value) if path in LATLON else int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{path}: expected a number")
    return "" if value is None else str(value).strip()


PUBLIC_ROOM = "Public"   # the only room channel 0 may be linked to (public-channel rule, decided by the server)


def _links(value):
    """Which local channel carries which server room. Channel 0 only for #Public."""
    if not isinstance(value, list):
        raise ValueError("links: expected a list")
    out, used = [], set()
    for item in value:
        if not isinstance(item, dict) or not str(item.get("room") or "").strip():
            continue
        if str(item["room"]).strip() == PUBLIC_ROOM:
            continue   # the public channel is switched on in the checklist, not linked here
        row = {"room": str(item["room"]).strip()[:30]}
        for k, net in (("mt_channel", "Meshtastic"), ("mc_channel", "MeshCore")):
            try:
                ch = int(item.get(k, -1))
            except (TypeError, ValueError):
                raise ValueError(f"{net} channel must be a number")
            if ch == 0:
                raise ValueError(f"{net} channel 0 is the local public channel: switch on \"Public channel\" in "
                                 f"the checklist instead of linking it to #{row['room']}")
            if not -1 <= ch <= 7:
                raise ValueError(f"{net} channel must be 1-7 (or off)")
            if ch > 0 and (k, ch) in used:
                raise ValueError(f"{net} channel {ch} is linked to two rooms")
            used.add((k, ch))
            row[k] = ch
        for k in ("send", "receive"):   # channel switches: local → Ura, Ura → local air
            row[k] = item.get(k, True) is not False
        if row["mt_channel"] >= 0 or row["mc_channel"] >= 0:
            out.append(row)
    return out


def apply_update(cfg, incoming):
    new = copy.deepcopy(cfg)
    for sec, fields in incoming.items():
        if sec == "auth" or sec not in DEFAULTS or not isinstance(fields, dict):
            continue
        for key, value in fields.items():
            if key not in DEFAULTS[sec] or (sec, key) in READONLY_FIELDS:
                continue
            if (sec, key) == ("server", "links"):
                new[sec][key] = _links(value)
                continue
            if (sec, key) == ("server", "share"):
                if not isinstance(value, dict):
                    raise ValueError("share: expected a checklist")
                new[sec][key] = {k: bool(value.get(k, False)) for k in DEFAULTS["server"]["share"]}
                continue
            if (sec, key) in SECRET_FIELDS and value in (MASK, "", None):
                continue
            new[sec][key] = _coerce(DEFAULTS[sec][key], value, f"{sec}.{key}")
    _validate(new)
    return new


def _validate(cfg):
    p, mt, mc, s = cfg["point"], cfg["meshtastic"], cfg["meshcore"], cfg["server"]
    p["country"] = p["country"].upper()
    if p["country"] and not (len(p["country"]) == 2 and p["country"].isalpha()):
        raise ValueError("Country must be a 2-letter code, e.g. AL, DE, US")
    if mt["connection"] not in ("tcp", "serial") or mc["connection"] not in ("tcp", "serial"):
        raise ValueError("connection must be tcp or serial")
    if mt["enabled"] and not (mt["host"] if mt["connection"] == "tcp" else mt["serial_port"]):
        raise ValueError("Meshtastic: enter a host or pick a serial port")
    if mc["enabled"] and not (mc["host"] if mc["connection"] == "tcp" else mc["serial_port"]):
        raise ValueError("MeshCore: enter a host or pick a serial port")
    if (mt["enabled"] and mc["enabled"] and mt["connection"] == mc["connection"] == "serial"
            and mt["serial_port"] == mc["serial_port"]):
        raise ValueError("Meshtastic and MeshCore cannot share one serial port")
    if s["enabled"] and not s["url"]:
        raise ValueError("Server: enter the server address")
    if not 0 <= s["rf_per_min"] <= 30:
        raise ValueError("Radio limit must be 0-30 messages per minute")
    if not 1 <= s["max_busy_pct"] <= 100 or not 1 <= s["max_tx_pct"] <= 100:
        raise ValueError("Airtime limits must be 1-100 %")
