# How to contribute a new command capture

The OpenSAAB command catalog grows one captured Tech2Win action at a time.
This page is the playbook.

## What you need

- A Windows machine with Tech2Win + a J2534-compatible scan-tool driver
  installed. The bench setup most contributors use is Chipsoft J2534 Pro,
  but anything that exposes the standard PassThru API works.
- A DLL shim that intercepts `CSTech2Win.dll` and logs every PDU API call
  including REQ-PDU and RSP-UDS bytes. (Not distributed here — write your
  own or use one off the shelf. The output format this catalog expects is
  documented in `tools/shim_log_format.md`.)
- Python 3 with `pyyaml`. Optionally `scapy` (kept out of the OpenSAAB
  repo for licensing reasons, but available if you want it for decoding).
- A vehicle on the bench. Don't capture from a customer's car without
  consent.

## Step by step

1. **Plug in the J2534 device + connect to the vehicle's OBD port.**
   Ignition on, wait 10s (avoid `$27 NRC 0x37`).

2. **Launch Tech2Win with the shim attached.** The shim begins writing
   to `%TEMP%\cstech2win_shim_<timestamp>.log`. Note that exact filename.

3. **Click ONE menu, wait for Tech2 to settle.** Don't click multiple
   menus in one capture — keeping each capture single-action makes the
   catalog clean.

4. **Stop the capture** (close Tech2Win, ignition off).

5. **Decode the log** with a UDS-aware dissector. The labeled timeline
   should show every TX/RX with service-ID names. Find the
   start and end timestamps of the action you triggered (skip any
   diag-session preamble — that goes in a separate entry, see step 7).

6. **Write the YAML.** Copy `commands/saab/cim_info_read.yaml` as a
   template. Fill in `menu`, `target_ecu`, `services`, and `dids` or
   `steps`. Add a representative `example` payload for each.

7. **Split common preambles.** If your action requires
   "DiagSessionEntry + ReadDataByPacketIdentifier setup" first, put
   those bytes in a separate entry (e.g. `diag_session_setup.yaml`) and
   reference it from your new entry's `notes:` instead of duplicating.

8. **PR.** Include:
   - The new YAML.
   - A brief mention in `docs/CHANGELOG.md`.
   - **Do NOT** include the raw shim log if it contains a customer's VIN.
     Redact the VIN or describe the action in prose if you can't share
     the raw bytes.

## What makes a good capture entry

- Single-action scope — one menu click per file.
- The `menu:` field reads exactly as Tech2Win shows it, with `→` between
  levels.
- An example payload for every DID / step. Without bytes the entry is
  useless to anyone trying to reproduce.
- A `notes:` block calling out NRCs, vehicle-profile dependencies, and
  preamble requirements.

## What gets rejected

- Captures with VINs / serial numbers that aren't yours.
- Multi-action captures (split into per-action entries before submitting).
- Entries lacking example bytes ("Tech2 talks to the ECM" isn't enough).
- DLL binaries, vendor SDK files, or anything you can't legally redistribute.
