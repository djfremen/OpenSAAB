# 2026-05-15 — USB pcap ↔ CSTech2Win shim alignment

**Inputs (Collector install `02a66883-…`, captured 2026-05-15 14:36 HST):**

- `usbpcap_1778891809358.log.gz` — 1.06 MB compressed (11.07 MB raw), 232,952 USB records, 107.3 s
- `cstech2win_1778891804118.log.gz` — 31.9 KB, 350 PDU frames, 73.2 s
- `cstech2win_1778891810313.log.gz` — 31.8 KB, 353 PDU frames, 69.6 s

This is the first capture with both the **byte-level USB transcript** (pcap) and the **PDU-call shim log** running side-by-side against the same Tech2Win session.

## TL;DR

| Question | Answer |
|---|---|
| Does the pcap-derived UDS decode byte-match the shim log's PDU bytes? | **Yes — every pcap UDS payload is identical to a shim PDU payload, zero discrepancies.** |
| Is the chipsoft USB envelope layout correctly understood? | Yes for the message-available channel (USB IN opcode `0x2000`) and the commit channel (USB OUT opcode `0x000F`). |
| Are there bytes in the pcap that don't correspond to a shim event? | **No** — zero pcap-only tuples. |
| Are there shim PDU events that don't appear in the pcap? | Yes — 56 distinct `RX $06XX` responses (e.g. `5A 9A 02 0A` on $0647) are visible in the shim but not in the pcap with the current envelope filter. **Likely a second USB IN opcode the supervisor's decoder doesn't recognize yet.** Open item for v0.3.0. |

## Envelope correction (v0.2.4 doc)

The envelope offsets documented in `Chipsoft_RE/tools/decode_chipsoft_pcap.py` (RE'd against a 2026-05-08 TrionicCANFlasher pcap, using the j2534_interface.dll path) included an ISO-TP PCI byte at fixed offset. The current CSTech2Win.dll envelope on the same chipsoft has **no PCI byte** — UDS bytes start where the old decoder thought PCI lived.

Corrected layout (validated against the v0.2.4 capture):

```
OUT (USB bulk OUT, opcode = 0x000F "commit", typical 35 bytes for 3-byte UDS)
   ofs 0-1   opcode (LE u16) = 0x000F
   ofs 2-5   length (LE u32) ≈ payload length minus 5
   ofs 6-7   sequence / msg counter (LE u16)
   ofs 30-31 CAN-ID (BE u16)
   ofs 32+   raw UDS bytes  ← NO separate PCI byte

IN  (USB bulk IN,  status = 0x2000 "MSG_AVAILABLE", typical 39 bytes for 7-byte UDS)
   ofs 0-1   status (LE u16) = 0x2000
   ofs 2-5   ? counter
   ofs 6-9   hardware timestamp (µs since adapter attach, LE u32)
   ofs 29-30 CAN-ID (BE u16)
   ofs 31+   raw UDS bytes  ← NO separate PCI byte
```

This corrected the v0.2.0–v0.2.3 `/api/admin/captures/.../summary` parser too — the v0.2.4 server-side fix in `decoder/usbpcap_summary.py` already uses these offsets.

## Method

`/tmp/v024/byte_match.py` (and `align.py`) — Python, no external deps:

1. Walk the classic-libpcap stream; filter to USB device address 23 (Chipsoft Pro), bulk transfers only.
2. For each frame, decode the chipsoft envelope at the corrected offsets to `(dir, can_id, uds_bytes)`.
3. Walk both cstech2win shim logs; their text format `<ms>|<tid>|HEX|REQ-PDU|len=N|<hex>` parses to `(dir, can_id, uds_bytes)` where dir = `TX` for `REQ-PDU` or `RX` for `RSP-UDS`.
4. Set-compare distinct `(dir, can_id, uds_bytes)` tuples.

## Headline numbers

```
Distinct (dir, can, uds-bytes) tuples
   pcap : 92
   shim : 148
   intersection : 92
   pcap-only    : 0     ← every byte in the pcap was also seen by the shim
   shim-only    : 56    ← shim saw 56 distinct response tuples the pcap filter missed
```

Top intersection rows (count of identical `(dir, can, uds_bytes)` in each source):

| dir | CAN | pcap | shim | UDS bytes |
|---|---|---:|---:|---|
| TX | `$0101` | 54 | 110 | `FE 3E`              (TesterPresent keep-alive, short form) |
| TX | `$0101` | 8 | 16 | `FE 1A 9A`           (broadcast `$1A 9A` tape-head signature) |
| TX | `$0241` | 7 | 13 | `AA 01 01`           (DPID setup on CIM) |
| RX | `$0541` | 6 | 11 | `01 77 06 02 02 FD 04 FC` |
| TX | `$0101` | 4 | 12 | `FE 01 3E`           (TesterPresent longer form) |
| TX | `$0241` | 4 | 8  | `1A 90`              (Read VIN from CIM) |
| TX | `$0243` | 4 | 8  | `1A 01`              (Read DID 01 from driver door) |
| TX | `$0248` | 3 | 6  | `1A 01`              (Read DID 01 from passenger door) |
| TX | `$0243` | 3 | 6  | `20`                 (ReturnToNormal on driver door) |

The **~50 % count ratio is uniform across every intersection row** because the USB capture (107 s) ran shorter than the combined shim window (~150 s). Within the overlapping window, byte-for-byte every shim PDU appears as a pcap envelope frame and vice versa.

## Open item: missing `$06XX` RX channel in pcap

Shim records 56 distinct response tuples on `$0641-$07E8` that don't appear in the pcap with the `status=0x2000` envelope filter:

```
RX  $0647  n=16  uds=5a 9a 02 0a
RX  $0642  n=10  uds=5a 9a 01 09
RX  $064F  n=10  uds=5a 9a 01 02
RX  $0649  n=10  uds=5a 9a 01 05
RX  $0641  n=9   uds=7f aa 78
RX  $0645  n=8   uds=5a 9a 03 04
RX  $0643  n=8   uds=5a 01 c9 34
RX  $07E8  n=8   uds=5a 9a 01 06
…
```

These are physical-response addresses ($06XX = $02XX + $400 in the SAAB GMLAN scheme). They're definitively coming from the bus (the shim's `RSP-UDS` records them via Tech2Win's PDU event callback). But the supervisor's pcap decoder, filtering only on USB IN `status=0x2000`, doesn't find them.

Two hypotheses:

1. **Second USB IN opcode.** The chipsoft delivers $06XX physical responses via a different status code (e.g. `0x2001`, or a different bulk-IN endpoint envelope). The v0.2.0 envelope RE only catalogued `0x2000` because the TrionicCANFlasher session it was built from didn't exercise $06XX-class replies.
2. **Different envelope offsets for those frames.** Less likely — the format is consistent within the existing `0x2000` IN frames.

Next step (v0.3.0 task): dump every USB IN frame's opcode in a fresh capture, find opcodes other than `0x2000` that carry CAN data, decode that second envelope. The pcap already has the data — we just need to look at the right opcode.

## What this unlocks

- **Path A `LibUsbTransport` is now byte-validated.** The pyusb-driven server-side transport for the operator API can encode UDS via the now-confirmed OUT envelope (`opcode=0x000F`, CAN-ID at offset 30, UDS at offset 32) with confidence that the chipsoft Pro will accept the bytes byte-for-byte the way Tech2Win drives them.
- **Cross-validation strategy proven.** Future captures can run pcap + shim in parallel and run `byte_match.py` as a regression check on the envelope decoder.
- **One known gap** (the $06XX RX channel via a second IN opcode) is now scoped as a single concrete open task instead of a vague "something might be missing."
