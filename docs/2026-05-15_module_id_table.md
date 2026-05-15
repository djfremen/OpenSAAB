# SAAB 9-3 / 9440 module-ID table — merged T8 bench + ME9.6 field car

**Date:** 2026-05-15
**Source captures:**
- T8 bench (VIN `YS3FD49YX41012017`, ECU 2017) — `2026-05-15_ecm_walk_t8/raw/cstech2win_17788708{29013,31934,33390,34359,35332,36516}.log.gz`
- ME9.6 field car (VIN `YS3FH46U681101367`, ECU 1367) — `2026-05-15_ecm_walk_me96/raw/cstech2win_1778872510392.log.gz`
- Video evidence — `videos/2026-05-15_1142_pdt_ecm_walk_t8.mkv`, `videos/2026-05-15_1208_pdt_ecm_walk_me96.mkv`

**Method:** Tech2Win main menu → All → F1 ECU Information → step through each module page. Each page issues `$1A 97` Module Description DID; reply ASCII is the canonical name. Cross-checked with the address map at `OpenSAAB/docs/saab_ecu_address_map_2026-05-13.md`.

## Unified address ↔ name table

| TX | RX | T8 bench (2017) | ME9.6 field car (1367) | Confidence | Notes |
|---|---|---|---|---|---|
| `$0241` | `$0641` | CIM | CIM | High | Was previously labelled "engine ECM" via Tech2Win SAS routing; the module's own `$1A 97` reply is CIM. |
| `$0242` | `$0642` | BCM | BCM | High | |
| `$0243` | `$0643` | DRIVER DOOR ECU | DRIVER DOOR ECU **+ ESP 430 NG** | Mixed | Tech2Win returns two different module descriptions depending on menu context. Likely a diag-route alias, not a second physical module. |
| `$0244` | `$0644` | DSM | DSM | High | |
| `$0245` | `$0645` | ACC | ACC | High | Resolves the old Trionic `FilterIdCIM = 0x245` ambiguity for this platform. |
| `$0246` | `$0646` | IPC | IPC | High | |
| `$0247` | `$0647` | ICM 2 | — | High (T8) | Not observed on ME9.6 capture. |
| `$0248` | `$0648` | PASSENGER DOOR ECU | PASSENGER DOOR ECU | High | |
| `$0249` | `$0649` | REC | REC **+ AFL-Epsilon** | Mixed | Same context-aliasing pattern as `$0243`. |
| `$024A` | `$064A` | REAR LEFT DOOR ECU | REAR LEFT DOOR ECU | High | |
| `$024B` | `$064B` | REAR RIGHT DOOR ECU | REAR RIGHT DOOR ECU | High | |
| `$024D` | `$064D` | SRM | SRM | High | Steering-wheel reel module / clockspring. |
| `$024F` | `$064F` | UEC | UEC | High | Underhood Electrical Center (front fuse box ECU). |
| `$0251` | `$0651` | EHU | — | High (T8) | Entertainment Head Unit; ME9.6 capture didn't probe. |
| `$0257` | `$0657` | SDM | SDM | High | Sensing & Diagnostic Module (airbag). |
| `$025B` | `$065B` | PAS | PAS | High | Park-Assist module. |
| `$025C` | `$065C` | SLM | — | High (T8) | T8 only. |
| `$025D` | `$065D` | no `$1A 97` (DID 81 = `"1A9"`, DID B2 = `A1 00 00 00 00 00`) | — | Low | Real oddball; responds but does not expose a Module Description in these captures. |
| `$025F` | `$065F` | no `$1A 97` reply | **TPMS_WAL01** | High (ME9.6) | ME9.6 capture resolves the previously unnamed `$025F`. |
| `$07E0` | `$07E8` | **ECM** | **BOSCH_ME96** | High | Different engine ECM identity by platform. T8 bench reports generic `ECM`; ME9.6 reports the actual product string. |
| `$07E1` | `$07E9` | TCM | — | High (T8) | Transmission Control Module; ME9.6 capture didn't probe. |

## Reading specific DIDs from specific modules

Generic Tech2Win pattern observed for every named module:

```
TX  $02XX  1A 97        ; request Module Description DID
RX  $06XX  5A 97 <ascii> ; positive reply, ASCII module name
```

For other useful DIDs we see in these same captures (with TX `$02XX  1A <did>` and RX `$06XX  5A <did> ...`):

| DID | Meaning | Example |
|---|---|---|
| `90` | VIN (17 ASCII chars) | `$0241 1A 90` → `YS3FD49YX41012017` / `YS3FH46U681101367` |
| `97` | Module description (ASCII) | as above |
| `98` | Build/identification trailer (ASCII, often padded with `0x20`) | |
| `99` | 4-byte build date or similar | `20 04 02 23` |
| `9A` | Tape-head / hardware signature (2 bytes) | `03 04` / `03 09` |
| `9B` | (varies per ECU) | |
| `7B`, `7C` | Counter / odometer-like 4-byte values | |
| `C1`–`CC` | Various 4-byte ECU-internal counters | |
| `D1` | 2-byte status/region code | `41 44` (`"AD"`) |

A complete dump for any module is therefore: open `$1A 90` then iterate `$1A 91..FF` and accept positive (`$5A`) replies. The two `did_summary.txt` files in `2026-05-15_ecm_walk_t8/` and `2026-05-15_ecm_walk_me96/` are the per-walk rollups.

## Modeling correction (carried from ME9.6 README)

Do **not** treat the OpenSAAB address map as one address ↔ one physical module. The captures show Tech2Win uses diag routes / aliases — the same TX CAN-ID can return different logical module descriptions under different menu contexts (`$0243` Driver-Door / ESP 430 NG, `$0249` REC / AFL-Epsilon).

Best model going forward:

- **Transport address** (`$02XX`)
- **Tech2Win context/menu path** (ECU Information, DTC sweep, subsystem menu)
- **Logical module description** (`DRIVER DOOR ECU`, `ESP 430 NG`, …)
- **Powertrain/platform** (T8 bench vs ME9.6 field car)

## Open items

- `$025D` still has no `$1A 97` reply in either capture. Try `F1 ECU Information` while a specific menu (e.g. Steering Sensor or Tape-head) is open to force the proxy route.
- `$0243` Driver-Door vs ESP 430 NG aliasing on ME9.6 — re-walk with video time-alignment so we can correlate Tech2Win menu state to the wire reply.
- Re-walk the T8 with `$025F` and `$025D` deliberately probed; current T8 raw set didn't surface readable names for either.
