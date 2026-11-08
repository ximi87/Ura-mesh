# 📡 Ura

*Every mesh, one world.*

**Ura** (Albanian for *bridge*) links LoRa mesh networks — **Meshtastic** and **MeshCore** — across
cities and countries over the internet, without flooding the local radio channels.

> 🚧 Early development. Not ready for use yet.

## The idea

```
   Tirana   Germany   USA   France   …
      \        |       |      /
       \       |       |     /
        ──── ura-mesh-server ────
```

- **ura-mesh-client** runs next to your repeater/radios (Meshtastic and/or MeshCore) and connects *out* to a Hub.
  No port forwarding needed at home.
- **ura-mesh-server** is the central server: it passes messages between bridges and shows a public
  directory and world map of all bridges.

> The agreed specification is in [SPEC.md](SPEC.md).

## Principles

- **Opt-in channels.** Only a dedicated channel such as "Global" is linked. The default local
  public channel is never sent to the internet.
- **Protect the airwaves.** Each bridge owner sets how many linked messages may go out over their
  radio. Extra messages stay on the web/Telegram side.
- **Control.** The Hub owner approves, limits and blocks bridges. Every bridge has its own key.
- **One bridge per area.** The Hub flags (or, in strict mode, refuses) a new bridge closer than a set distance
  (default 20 km) to an approved one, so one city is not connected twice.
- **Nodes & positions.** Off by default. When both point owners and the server owner switch it on, the nodes a
  point hears are passed on unchanged (name, id, the position each node's owner shares).
- **Clearly labelled.** Messages that came over the internet are marked with where they came from.
- **Private messages** go only to the bridge where the recipient is.

## Layout

- `server/` — ura-mesh-server (`server.py`, public page + admin page)
- `client/` — ura-mesh-client (`client.py`, one per point: radios + server link + statistics dashboard + admin page)
- `PROTOCOL.md` — how bridges and the hub talk
- `contrib/` — systemd service files

## Plan

1. Hub + bridge link, test Tirana ↔ Germany on a private network — *code done, tested with two bridges without radios*
2. Hub admin page (approve / block / limits) and public directory + map — *first version done*
3. HTTPS and public internet access, first outside bridges
4. Public release

## License

MIT, see [LICENSE](LICENSE).
