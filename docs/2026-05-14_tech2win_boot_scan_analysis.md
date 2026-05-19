# 2026-05-14 — Tech2Win boot-scan capture analysis (VIN YS3FH46U68110137)

**Source artifacts (EliteBook → workspace):**

- Video: `saab_security_project/tech2_video_analysis/2026-05-14_vehicle_id.mkv`
  (OBS, 1280×720, 116 s, recorded 18:59:43 local)
- Tech2Win HTML log: `saab_security_project/tech2_video_analysis/tech2win_185948.html`
- Tech2Win HTML log (prior session): `saab_security_project/tech2_video_analysis/tech2win_180517.html`
- Chipsoft shim log: `saab_security_project/tech2_video_analysis/shim_190004.log` (392 KB)
- Chipsoft shim log (prior session): `saab_security_project/tech2_video_analysis/shim_180523.log` (613 KB)
- Parsed fixtures:
  - `OpenSAAB/commands/saab/captures/2026-05-14_180523_ys3fh46u_tech2win_boot_scan.json`
  - `OpenSAAB/commands/saab/captures/2026-05-14_190004_ys3fh46u_tech2win_boot_scan.json`

## Headline finding

**The video does not reach the Vehicle Identification screen.** The 116-second
capture covers Tech2Win launch → Bus Check → Vehicle Specifics 90 % →
"Key Not in LOCK Position" prompt → the F0–F7 *All* main menu, then ends.
Tech2Win never navigates into **F1: ECU Information** (or
**F4: Vehicle Power Supply**, which on the 9440 also enumerates modules),
so the SAAB-name ↔ CAN-ID GUI mapping we were after isn't on screen.

What we *did* capture is two full **boot-time module scans** in the
shim logs. Tech2Win pings every module on the bus during the
"Checking Bus / Vehicle Specifics" stage. That gives a wire-confirmed
list of responding CAN-IDs for this car, plus a small set of identity
DIDs per module that can serve as fingerprints.

## Vehicle context

VIN echoed by every responding module on $1A 90:

```
59 53 33 46 48 34 36 55 36 38 31 31 30 31 33 36 37
 Y  S  3  F  H  4  6  U  6  8  1  1  0  1  3  6  7
```

**`YS3FH46U68110137`** — WMI `YS3FH46U6` = 2008 SAAB 9-3 sedan/SportCombi
(9440 platform). This is *not* the bench car
(`YS3FD49YX41012017`). It's a separate field car running ME9.6.

## Module response map — this car

Every CAN-ID below answered Tech2Win during the boot scan. The
"signature DIDs" column lists DID payloads we can use to fingerprint
the module across cars.

| CAN-ID | Responds to | Signature DIDs (this car) | Inferred role (per existing map) |
|---|---|---|---|
| `$0241` | `$1A 90` | VIN | Engine ECM alias (Tech2Win SAAB-side) |
| `$0242` | `$1A 90`, `$1A 07`, `$1A 08`, `$1A 9A`, `$1A 26` | `$07: 87 83 42` · `$08: 6F` · `$9A: 01 0E` · `$26: 00 00` | **BCM** |
| `$0243` | `$1A 90`, `$1A 01` | `$01: C9 34` | Door module |
| `$0245` | `$1A 90`, `$1A 42` | `$42:` 66-byte HVAC calibration table | **ACC** (climate) |
| `$0246` | `$1A 90`, `$1A 02`, `$1A 03`, `$1A 9A`, `$1A B9`, `$1A BA` | `$02: 1C A0 00` · `$03: FF 40` · `$9A: 04 09` · `$B9: 0F 00 00 00` · `$BA: 7C CF 35 50` | **TO_SIC** (Steering Integration) |
| `$0248` | `$1A 90`, `$1A 01` | `$01: C9 34` (matches $0243) | Door module |
| `$0249` | `$1A 90`, `$1A 9A` | `$9A: 01 05` | **TCS/ESP** |
| `$024A` | `$1A 90` | — | Door module |
| `$024B` | `$1A 90` | — | Door module |
| `$024F` | `$1A 90`, `$1A 41`, `$1A 9A` | `$41: 46 60 5A` · `$9A: 01 04` | **UEC** (front lighting) |
| `$025D` | `$1A 81`, `$1A B2` | `$81: 31 41 39` = ASCII `"1A9"` · `$B2: A1 00 00 00 00 00` | unknown (ASCII `"1A9"` signature) |
| `$02E0` | `$1A 90` (proxied to $07E8) | VIN via OBD-II $07E8 in 18:05 session; NRC $78 in 19:00 session | Powertrain functional group → ECM at `$07E0/$07E8` |

Doors `$0243 / $0248` returning **identical** `$1A 01: C9 34` is new
evidence — those two are running the same firmware build (left+right
front, most likely). `$024A / $024B` did not respond to `$1A 01` in
either session, suggesting they're a different (rear-door) firmware
variant.

`$025D` responding with ASCII `"1A9"` on `$1A 81` is the same
signature we logged on 2026-05-13 from the 1367 ME9.6 capture. So
this CAN-ID carries the same "1A9" identifier across two different
9440-platform cars — strong evidence `$025D` is a stable role
(candidate: TPM or TPMS controller — the `A1 00 00 00 00 00` on
`$1A B2` could be a "tire pressure status: OK / 0 / 0 / 0 / 0 / 0"
shape, worth verifying).

## What we cannot yet confirm from this capture

The video doesn't reach **F1: ECU Information** or the **Vehicle
Identification** screen, so we still don't have Tech2Win printing
SAAB names (BCM / CIM / ACC / UEC / etc.) next to addresses on
screen. The lexicon ↔ CAN-ID linkage in
`OpenSAAB/docs/saab_ecu_address_map_2026-05-13.md` remains an
inference, not a direct sighting.

## Recommended next capture

When Chris re-records, the screen we want is reached via:

1. Tech2Win main menu → **F0 / F1 / F2 / … (All)**
2. From the *All* menu → **F1: ECU Information**
3. That should iterate every responder and print
   "BCM (Body Control Module) — part number — software version"
   for each address, which closes the loop on every row in
   `saab_ecu_address_map_2026-05-13.md`.

Recording tips:

- Maximize the Tech2Win window so the recording isn't downsampled to
  a tiny pane; the current 1280×720 OBS capture left Tech2Win at
  ~280 px wide, which is below comfortable OCR resolution.
- Hold each module screen on the F1 list for ~2 s so a single frame
  catches the full text.
- The shim log will already be running in the background — no extra
  setup needed.

## Files added to the repo this session

- `OpenSAAB/commands/saab/captures/2026-05-14_180523_ys3fh46u_tech2win_boot_scan.json`
- `OpenSAAB/commands/saab/captures/2026-05-14_190004_ys3fh46u_tech2win_boot_scan.json`
- `OpenSAAB/docs/2026-05-14_tech2win_boot_scan_analysis.md` (this file)
