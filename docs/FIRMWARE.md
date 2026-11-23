# Hub radio firmware

The **hub radio** (the one connected to the ura-hub) needs Meshtastic firmware with one
small Ura patch. **All other radios — your phone's radio, everybody else's — stay
unchanged.**

## Why the patch

A Meshtastic radio can only accept another node's packet from a connected program through its
MQTT path. The stock firmware marks such packets *via MQTT* in the LoRa header when it sends
them on air, and every node with **Ignore MQTT** switched on throws them away. Remote nodes
then never appear for those users.

The patch changes one thing: packets handed in by the hub go on air **without** the *via MQTT*
flag, like normal LoRa packets. Inside the hub radio they keep their internal mark, so they are
never sent back into the bridge (no loops). Packets the radio hears over LoRa that already
carry the flag keep it.

File: [`firmware/meshtastic-2.7.26-ura-no-mqtt-flag-on-air.patch`](../firmware/meshtastic-2.7.26-ura-no-mqtt-flag-on-air.patch)
(5 lines in `src/mesh/RadioInterface.cpp`).

> Some people turn on *Ignore MQTT* on purpose because they do not want internet traffic on
> their radio. With this patch they receive Ura traffic anyway. Keep that in mind, and use the
> hub's rules and airtime limit to keep the load reasonable.

## Build

On any Linux PC (not on the radio):

```bash
python3 -m venv ~/pio && ~/pio/bin/pip install platformio
git clone --depth 1 --branch v2.7.26.54e0d8d --recurse-submodules --shallow-submodules \
    https://github.com/meshtastic/firmware.git
cd firmware
git apply /path/to/Ura-mesh/firmware/meshtastic-2.7.26-ura-no-mqtt-flag-on-air.patch
~/pio/bin/pio run -e heltec-v3                    # your board's environment, see below
```

The first build downloads the ESP32 tool chain (~1–2 GB) and takes a while. The result is
`.pio/build/<env>/firmware-<env>-2.7.26.54e0d8d.bin`.

Board environments: look in `variants/` for your board, e.g. `heltec-v3`,
`heltec-wireless-tracker`, `tbeam`, `rak4631` (nRF52), `station-g2`. The patch is not
board-specific.

## Flash (ESP32 boards) — keeps all settings

Write only the application part at `0x10000`; the radio's settings (channels, keys, name,
LoRa) stay as they are. Use [esptool](https://github.com/espressif/esptool) (pip or the
standalone release):

```bash
esptool --chip esp32s3 --port /dev/ttyUSB0 --baud 921600 write_flash 0x10000 firmware-heltec-v3-2.7.26.54e0d8d.bin
```

(`--chip esp32` for classic ESP32 boards.) Stop the ura-hub first (`sudo systemctl stop
ura-hub`) — only one program can use the USB port.

**If esptool cannot connect** ("No serial data received") the board does not enter flashing
mode by itself (common on boards with native USB, e.g. the Heltec Wireless Tracker): hold the
**BOOT/USER** button, tap **RST**, release BOOT — the screen goes dark — then flash with
`--before no_reset`, and tap **RST** afterwards to start the new firmware.

**Virtual machines:** USB pass-through often cannot reset the board into flashing mode. Detach
the radio from the VM and flash on the host. Pass radios through **by USB vendor/device ID**,
not by port — ESP32 boards re-enumerate when they restart and port-based pass-through loses
them.

nRF52 boards (RAK4631 etc.): copy the `.uf2` from the build to the board's USB drive (double-tap
reset to get the drive).

Upgrading from 2.6.x to 2.7.x with an application-only flash worked in our tests (same flash
layout, settings kept). Save the settings first anyway (`meshtastic --export-config`).

## Check

In the hub's website, **Meshtastic → Radio** shows the firmware version and **Ready for Ura**. The patch
itself cannot be detected remotely; a quick test: a phone on a radio with *Ignore MQTT* on, near
the hub, should see remote nodes.

## Going back

Flash the stock Meshtastic release for your board the same way (web flasher or esptool). Your
settings stay.
