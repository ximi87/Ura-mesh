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
        ───────  Ura Hub  ───────
```

- **Ura Bridge** runs next to your radios (Meshtastic and/or MeshCore) and connects *out* to a Hub.
  No port forwarding needed at home.
- **Ura Hub** is the central server: it passes messages between bridges and shows a public
  directory and world map of all bridges.

## Principles

- **Opt-in channels.** Only a dedicated channel such as "Global" is linked. The default local
  public channel is never sent to the internet.
- **Protect the airwaves.** Each bridge owner sets how many linked messages may go out over their
  radio. Extra messages stay on the web/Telegram side.
- **Control.** The Hub owner approves, limits and blocks bridges. Every bridge has its own key.
- **Privacy.** Bridge locations are shown at city level. Node positions are off by default and
  rounded when shared.
- **Clearly labelled.** Messages that came over the internet are marked with where they came from.
- **Private messages** go only to the bridge where the recipient is.

## Plan

1. Hub + bridge link, test Tirana ↔ Germany on a private network
2. Hub admin page (approve / block / limits) and public directory + map
3. HTTPS and public internet access, first outside bridges
4. Public release

## License

MIT, see [LICENSE](LICENSE).
