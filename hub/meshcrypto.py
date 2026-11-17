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
