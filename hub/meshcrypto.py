"""Pure-Python AES-CTR, enough to read the type of a Meshtastic channel packet.

The hub decrypts channel packets in memory only, to apply its rules
(e.g. "no positions"). Nothing decrypted is stored or sent anywhere.
Meshtastic: AES-128/256-CTR, nonce = packet id (u64 LE) + sender (u32 LE) + 4 zero bytes,
counter = last 4 bytes, big-endian.
"""
import base64, struct

_SBOX = bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdbe0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")
_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]


def _xt(a):
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1


def _expand(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = [_SBOX[b] for b in t[1:] + t[:1]]
            t[0] ^= _RCON[i // nk - 1]
        elif nk > 6 and i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([a ^ b for a, b in zip(w[i - nk], t)])
    return [sum(w[4 * r:4 * r + 4], []) for r in range(nr + 1)]


def _encrypt_block(rk, block):
    s = [b ^ k for b, k in zip(block, rk[0])]
    nr = len(rk) - 1
    for r in range(1, nr + 1):
        s = [_SBOX[b] for b in s]
        s = [s[(i + 4 * (i % 4)) % 16] for i in range(16)]            # ShiftRows (column-major state)
        if r != nr:
            m = []
            for c in range(4):
                a = s[4 * c:4 * c + 4]
                x = a[0] ^ a[1] ^ a[2] ^ a[3]
                m += [a[i] ^ x ^ _xt(a[i] ^ a[(i + 1) % 4]) for i in range(4)]
            s = m
        s = [b ^ k for b, k in zip(s, rk[r])]
    return bytes(s)


_KEYS = {}


def aes_ctr(key: bytes, nonce: bytes, data: bytes) -> bytes:
    rk = _KEYS.get(key) or _KEYS.setdefault(key, _expand(key))
    out, ctr = bytearray(), bytearray(nonce)
    for i in range(0, len(data), 16):
        ks = _encrypt_block(rk, ctr)
        out += bytes(a ^ b for a, b in zip(data[i:i + 16], ks))
        c = (int.from_bytes(ctr[12:], "big") + 1) & 0xFFFFFFFF
        ctr[12:] = c.to_bytes(4, "big")
    return bytes(out)


DEFAULT_KEY = bytes.fromhex("d4f1bb3a20290759f0bcffabcf4e6901")


def expand_psk(psk: bytes):
    """Meshtastic channel PSK -> AES key (None = no encryption)."""
    if not psk:
        return None
    if len(psk) == 1:
        if psk[0] == 0:
            return None
        return DEFAULT_KEY[:-1] + bytes([(DEFAULT_KEY[-1] + psk[0] - 1) & 0xFF])
    if len(psk) < 16:
        return psk.ljust(16, b"\0")
    if len(psk) < 32 and len(psk) != 16:
        return psk.ljust(32, b"\0")
    return psk


def decrypt_packet(key: bytes, packet_id: int, sender: int, encrypted: bytes) -> bytes:
    nonce = struct.pack("<QI", packet_id, sender) + b"\0" * 4
    return aes_ctr(key, nonce, encrypted)


def _selftest():
    # FIPS-197 appendix C vectors
    k128 = bytes(range(16))
    pt = bytes.fromhex("00112233445566778899aabbccddeeff")
    assert _encrypt_block(_expand(k128), pt).hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"
    k256 = bytes(range(32))
    assert _encrypt_block(_expand(k256), pt).hex() == "8ea2b7ca516745bfeafc49904b496089"
    # NIST SP800-38A F.5.1 CTR-AES128
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    ctr = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff")
    p = bytes.fromhex("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51")
    assert aes_ctr(key, ctr, p).hex() == "874d6191b620e3261bef6864990db6ce9806f66b7970fdff8617187bb9fffdff"
    assert base64.b64encode(expand_psk(b"\x01")).decode() == base64.b64encode(DEFAULT_KEY).decode()
    return True


if __name__ == "__main__":
    print("selftest", _selftest())


# ───────────────────────── hub-to-hub end-to-end encryption ─────────────────────────
# X25519 (RFC 7748) key agreement + HKDF-SHA256 + AES-256-CTR + HMAC-SHA256 (encrypt-then-MAC).
# The server only ever sees sealed boxes; it cannot read or change what hubs send each other.

import hashlib, hmac as _hmac, os as _os, time as _time

_P = 2 ** 255 - 19
_A24 = 121665


def _clamp(k: bytes) -> int:
    b = bytearray(k)
    b[0] &= 248
    b[31] &= 127
    b[31] |= 64
    return int.from_bytes(b, "little")


def x25519(k: bytes, u: bytes) -> bytes:
    """RFC 7748 X25519: scalar k times point u (both 32 bytes, little endian)."""
    k_int = _clamp(k)
    x1 = int.from_bytes(u, "little") & ((1 << 255) - 1)
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in reversed(range(255)):
        kt = (k_int >> t) & 1
        swap ^= kt
        if swap:
            x2, x3, z2, z3 = x3, x2, z3, z2
        swap = kt
        a, b = (x2 + z2) % _P, (x2 - z2) % _P
        aa, bb = a * a % _P, b * b % _P
        e = (aa - bb) % _P
        c, d = (x3 + z3) % _P, (x3 - z3) % _P
        da, cb = d * a % _P, c * b % _P
        x3 = (da + cb) ** 2 % _P
        z3 = x1 * (da - cb) ** 2 % _P
        x2 = aa * bb % _P
        z2 = e * (aa + _A24 * e) % _P
    if swap:
        x2, z2 = x3, z3
    return (x2 * pow(z2, _P - 2, _P) % _P).to_bytes(32, "little")


def x25519_public(private: bytes) -> bytes:
    return x25519(private, (9).to_bytes(32, "little"))


def new_private() -> bytes:
    return _os.urandom(32)


def hkdf(secret: bytes, info: bytes, length=64, salt=b"ura-link-v1") -> bytes:
    prk = _hmac.new(salt, secret, hashlib.sha256).digest()
    out, t, i = b"", b"", 1
    while len(out) < length:
        t = _hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        out += t
        i += 1
    return out[:length]


def link_keys(my_private: bytes, my_public: bytes, peer_public: bytes):
    """Both hubs derive the same 32-byte AES key + 32-byte MAC key for their link."""
    shared = x25519(my_private, peer_public)
    if shared == bytes(32):
        raise ValueError("bad peer key")
    a, b = sorted([my_public, peer_public])
    k = hkdf(shared, b"ura e2e " + a + b)
    return k[:32], k[32:]


def safety_code(pub_a: bytes, pub_b: bytes) -> str:
    """Short code both operators can compare (phone, chat). Same on both sides."""
    a, b = sorted([pub_a, pub_b])
    n = int.from_bytes(hashlib.sha256(b"ura safety " + a + b).digest()[:10], "big")
    digits = str(n % 10 ** 20).zfill(20)
    return " ".join(digits[i:i + 5] for i in range(0, 20, 5))


def seal(keys, plaintext: bytes) -> bytes:
    """box = version(1) | time(4) | nonce(16) | ciphertext | mac(16)"""
    enc, mac = keys
    head = b"\x01" + int(_time.time()).to_bytes(4, "big") + _os.urandom(16)
    ct = aes_ctr(enc, head[5:21], plaintext)
    tag = _hmac.new(mac, head + ct, hashlib.sha256).digest()[:16]
    return head + ct + tag


def open_box(keys, box: bytes, max_age=600):
    """Returns (plaintext, nonce) or raises ValueError (wrong key, changed, too old)."""
    enc, mac = keys
    if len(box) < 37 or box[0] != 1:
        raise ValueError("bad box")
    head, ct, tag = box[:21], box[21:-16], box[-16:]
    if not _hmac.compare_digest(_hmac.new(mac, head + ct, hashlib.sha256).digest()[:16], tag):
        raise ValueError("bad mac")
    if abs(_time.time() - int.from_bytes(head[1:5], "big")) > max_age:
        raise ValueError("too old")
    return aes_ctr(enc, head[5:21], ct), head[5:21]


def _selftest_e2e():
    # RFC 7748 section 5.2 vector 1 and section 6.1 Diffie-Hellman
    k = bytes.fromhex("a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4")
    u = bytes.fromhex("e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c")
    assert x25519(k, u).hex() == "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552"
    a = bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a")
    b = bytes.fromhex("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb")
    A, B = x25519_public(a), x25519_public(b)
    assert A.hex() == "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"
    assert B.hex() == "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"
    assert x25519(a, B).hex() == "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742" == x25519(b, A).hex()
    ka, kb = link_keys(a, A, B), link_keys(b, B, A)
    assert ka == kb and safety_code(A, B) == safety_code(B, A)
    box = seal(ka, b"hello mesh")
    assert open_box(kb, box)[0] == b"hello mesh"
    bad = bytearray(box); bad[25] ^= 1
    try:
        open_box(kb, bytes(bad)); raise AssertionError("tamper not detected")
    except ValueError:
        pass
    return True


if __name__ == "__main__":
    print("selftest e2e", _selftest_e2e())
