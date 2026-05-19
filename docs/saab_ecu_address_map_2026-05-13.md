# SAAB CAN-ID → ECU function map

**Date:** 2026-05-13 (last update: 2026-05-15)
**Sources:**
- Bench captures from `commands/saab/check_codes_read_dtcs.yaml` (T8 bench, VIN `YS3FD49YX41012017`)
- Bench captures from `commands/saab/engine_me96_read_codes.yaml` + `clear_codes_clear_dtcs.yaml` (ME9.6 field car, VIN prefix `YS3FH46U…`)
- [`commands/saab/captures/2026-05-14_190004_ys3fh46u_tech2win_boot_scan.json`](../commands/saab/captures/2026-05-14_190004_ys3fh46u_tech2win_boot_scan.json) — shim-decoded boot scan of VIN `YS3FH46U68110137` (2008 9-3 SportCombi)
- Workspace-only T8 ECM walk analysis: `saab_security_project/tech2_video_analysis/2026-05-15_ecm_walk_t8/README.md` — Collector uploads around 2026-05-15 08:47 HST; Tech2Win `$1A 97` Module Description DIDs for VIN `YS3FD49YX41012017`
- Workspace-only ME9.6 ECM walk analysis: `saab_security_project/tech2_video_analysis/2026-05-15_ecm_walk_me96/README.md` — Collector upload around 2026-05-15 09:15 HST; Tech2Win `$1A 97` Module Description DIDs for VIN `YS3FH46U681101367`
- [`mattiasclaesson/Trionic`](https://github.com/mattiasclaesson/Trionic) — `Trionic8.cs:42-44` `FilterIdECU` / `FilterIdCIM`
- [z90.pl SAAB DTC catalog](https://z90.pl/saab/dtc/) — model 9-3 9440 MY 2009 ECU index
- [`protocol/gmlan_11bit_ids.md`](../protocol/gmlan_11bit_ids.md) — Jason Gaunt 2013 canonical labels

This document **infers** the module/logical function reachable at each CAN-ID by
cross-referencing observed DTCs, Tech2Win `$1A 97` Module Description
strings, z90's per-ECU sections, and Trionic's hardcoded address constants.
It is not a canonical claim — it's the strongest hypothesis the available
evidence supports for each address.

Important 2026-05-15 correction: the map is **not strictly one
CAN-ID-to-one-physical-module**. Tech2Win appears to route multiple logical
modules through the same transport address depending on menu context. Examples:
`$0243` can report both `DRIVER DOOR ECU` and ESP (`ESP EBC430` / `ESP 430 NG`);
`$0249` can report both `REC` and `AFL-Epsilon`. Model rows as
`transport address + Tech2Win menu context + platform/powertrain evidence`, not
as immutable physical ownership.

## Address-to-module table

| TX | SF reply | MF reply | Inferred module | Confidence | Evidence |
|---|---|---|---|---|---|
| `$0241` | `$0541` | `$0641` | **CIM** (Column Integration Module) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `CIM`. Earlier engine/SAS behavior is a Tech2Win service-routing alias, not the module identity. |
| `$0242` | `$0542` | `$0642` | **BCM** (Body Control Module) | High | DTCs `B0092-05` "Passenger Seat Sensor circuit" + `B1001` "Control Module not Added" + lost-comm with multiple modules — z90 attributes both to BCM(#817) |
| `$0243` | `$0543` | `$0643` | **Driver Door ECU** + ESP logical route | High | T8 and ME9.6 walks both show `$1A 97` `DRIVER DOOR ECU`; DTC evidence (`B3832-45`) supports door. T8 also shows `ESP EBC430`; ME9.6 shows `ESP 430 NG` at the same transport address, so this is context/proxy-routed. |
| `$0244` | `$0544` | `$0644` | **DSM** (Driver Seat Module) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `DSM`. |
| `$0245` | `$0545` | `$0645` | **ACC** (climate / heated seats) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `ACC`; prior seat-heater DTC evidence also pointed to ACC. This resolves the old Trionic CIM-address conflict for 9-3 9440. |
| `$0246` | `$0546` | `$0646` | **IPC** (Instrument Panel Cluster) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `IPC`; prior DIDs 02/03/90/9A/B9/BA are IPC identity/calibration reads. |
| `$0247` | `$0547` | `$0647` | **ICM 2** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `ICM 2`. |
| `$0248` | `$0548` | `$0648` | **Passenger Door ECU** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns `PASSENGER DOOR ECU`; `$1A 01: C9 34` matches `$0243` as the front-door pair. |
| `$0249` | `$0549` | `$0649` | **REC** + AFL logical route | High | T8 and ME9.6 walks show `$1A 97` `REC`; ME9.6 also shows `AFL-Epsilon` at `$0249`, so this transport address is context/proxy-routed. Prior TCS/ESP inference from DTC attribution is superseded for this address. |
| `$024A` | `$054A` | `$064A` | **Rear Left Door ECU** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns `REAR LEFT DOOR ECU`; shares door DTC evidence. |
| `$024B` | `$054B` | `$064B` | **Rear Right Door ECU** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns `REAR RIGHT DOOR ECU`; shares door/window DTC evidence. |
| `$024D` | `$054D` | `$064D` | **SRM** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `SRM`. |
| `$024F` | `$054F` | `$064F` | **UEC** (User Equipment Center / front lighting controller) | High | All 5 unique DTCs (`B2575/B2698/B2699/B2525` low-beam + fog-light circuits, `B3810-06` headlamp washer relay) z90-attributed exclusively to UEC(#832) |
| `$0251` | `$0551` | `$0651` | **EHU** (Entertainment Head Unit) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `EHU`. |
| `$0253` | `$0553` | `$0653` | unknown body module | Low | Present in sweeps; no `$1A 97` name captured yet. |
| `$0257` | `$0557` | `$0657` | **SDM** (Sensing Diagnostic Module / airbag) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `SDM`. |
| `$025B` | `$055B` | `$065B` | **PAS** (Parking Assistance System) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `PAS`. |
| `$025C` | `$055C` | `$065C` | **SLM** | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `SLM`. |
| `$025D` | `$055D` | `$065D` | **TBD — confirmed ASCII `"1A9"` signature** | Medium | 2026-05-14 1367 capture: DID 81 returns `5A 81 31 41 39` = ASCII `"1A9"` (verifies the 2026-05-13 note). Also DID B2 = `A1 00 00 00 00 00`. **2026-05-14 YS3FH46U68110137 capture**: identical `$81 = "1A9"` and `$B2 = A1 00 00 00 00 00` — same role across two different 9440-platform cars (cross-vehicle confirmation). Still needs Tech2Win Module Description screen to put a SAAB name on `"1A9"` |
| `$025F` | `$055F` | `$065F` | **TPMS_WAL01** on ME9.6; unnamed on T8 | Medium-High | 2026-05-15 ME9.6 walk: `$1A 97` returns `TPMS_WAL01`. T8 had `$025F` responses but no readable `$1A 97` name captured. |
| `$07E0` | `$05E8` | `$07E8` | **Engine ECM** (`ECM` on T8, `BOSCH_ME96` on ME9.6) | High | T8 walk: `$1A 97` returns `ECM`; ME9.6 walk: `$1A 97` returns `BOSCH_ME96`; Trionic `FilterIdECU = { 0x7E0, 0x7E8, 0x5E8 }`. |
| `$07E1` | `$05E9` | `$07E9` | **TCM** (Transmission Control Module) | High | 2026-05-15 T8 ECM walk: `$1A 97` returns ASCII `TCM`; Jason Gaunt canonical OBD-II physical-to-TCM address. |

## Resolved: `$0245` ACC vs CIM

Earlier evidence conflicted: Trionic's `FilterIdCIM = { 0x245, 0x545,
0x645 }` suggested **CIM** at `$0245`, while the captured DTCs were
seat-heater/climate DTCs attributed to **ACC**.

The 2026-05-15 T8 ECM walk resolves this for the 9-3 9440 platform:
`$0245 $1A 97` returns ASCII **`ACC`**. `$0241 $1A 97` returns **`CIM`**.
So Trionic's `$0245` CIM mapping is either older-platform-specific or a
service-routing alias, not the module identity on this bench car.

## Resolved: door module disambiguation (`$0243 / $0248 / $024A / $024B`)

The same T8 ECM walk resolves the four door modules by `$1A 97`:

| CAN-ID | Door module |
|---|---|
| `$0243` | Driver Door ECU |
| `$0248` | Passenger Door ECU |
| `$024A` | Rear Left Door ECU |
| `$024B` | Rear Right Door ECU |

Caution: one split-capture context shows `ESP EBC430` on `$0243`; treat
that as a Tech2Win context/proxy ambiguity until the two video halves are
time-aligned against the log. The Check-Codes DTC evidence and first T8
Module Description half both support `$0243` as Driver Door ECU.

## 2026-05-14 update — `$1A` ID sweep from 1367 ME9.6 capture

Bench shim log `cstech2win_1778807278859.log.gz` (599 frames / 110.5 s,
VIN `YS3FH46U681101367`) ran a full Check-Codes + Clear-Codes flow that
included `$1A` reads on every body module. 12 ECUs answered; 8 stayed
silent. Confirmed responders and their DIDs are catalogued in
[`commands/saab/ecu_id_sweep.yaml`](../commands/saab/ecu_id_sweep.yaml).

Key takeaways:

- `$0646` (TO_SIC canonical) now has bench evidence — responds to **6
  DIDs** (02, 03, 90, 9A, B9, BA). Was previously "Low confidence".
- `$0643` and `$0648` both return DID 01 = `C9 34` — **same door-module
  hardware revision**, helps disambiguate which-door-is-which later.
- `$065D` ASCII `"1A9"` confirmed from DID 81. Still no SAAB-canonical
  name — Tech2Win's Module Description menu screen would resolve this.
- Bus-wide consistency: every responder returned the **same VIN** on
  DID 90 — confirms the SAAB diagnostic gateway broadcasts VIN to all
  modules at boot.

The eight silent targets (`$0244, $0247, $024D, $0253, $0257, $025B,
$025F, $0657`) need a dedicated re-query to disambiguate "no module at
this address" vs "module present but doesn't carry $1A". Use the
`ecu_id_sweep.yaml` workflow.


## 2026-05-15 update — T8 ECM walk / Module Description DIDs

Chris ran the intended Tech2Win **All → F1 ECU Information** walk on the
T8 bench car (`YS3FD49YX41012017`). The useful Collector uploads are
`cstech2win_1778870835332.log.gz` and `cstech2win_1778870836516.log.gz`;
local analysis lives at
`saab_security_project/tech2_video_analysis/2026-05-15_ecm_walk_t8/`.

The decisive signal is `$1A 97`, which returns Tech2Win's module
description string. This resolves most of the prior DTC-only hypotheses:

- `$0241` = **CIM**
- `$0242` = **BCM**
- `$0243` = **Driver Door ECU** in the first T8 half, but one split-capture
  context also shows **ESP EBC430** at `$0243`; keep this ambiguity until the
  video split is time-aligned.
- `$0244` = **DSM**
- `$0245` = **ACC** (old ACC-vs-CIM conflict resolved)
- `$0246` = **IPC**
- `$0247` = **ICM 2**
- `$0248` = **Passenger Door ECU**
- `$0249` = **REC**
- `$024A` = **Rear Left Door ECU**
- `$024B` = **Rear Right Door ECU**
- `$024D` = **SRM**
- `$024F` = **UEC**
- `$0251` = **EHU**
- `$0257` = **SDM**
- `$025B` = **PAS**
- `$025C` = **SLM**
- `$07E0` = **ECM**
- `$07E1` = **TCM**

Still unresolved: `$025D` (stable `DID 81 = "1A9"`, `DID B2 = A1 00 00 00 00 00`)
and `$025F` (responds in sweeps, no readable `$1A 97` name captured).


## 2026-05-15 update — ME9.6 ECM walk / Module Description DIDs

Chris then ran the same walk on the ME9.6 car (`YS3FH46U681101367`). The
primary useful Collector upload is `cstech2win_1778872510392.log.gz`; local
analysis lives at
`saab_security_project/tech2_video_analysis/2026-05-15_ecm_walk_me96/`.

Confirmed ME9.6 `$1A 97` labels:

- `$0241` = **CIM**
- `$0242` = **BCM**
- `$0243` = **Driver Door ECU** and **ESP 430 NG** depending context
- `$0244` = **DSM**
- `$0245` = **ACC**
- `$0246` = **IPC**
- `$0248` = **Passenger Door ECU**
- `$0249` = **AFL-Epsilon** and **REC** depending context
- `$024A` = **Rear Left Door ECU**
- `$024B` = **Rear Right Door ECU**
- `$024D` = **SRM**
- `$024F` = **UEC**
- `$0257` = **SDM**
- `$025B` = **PAS**
- `$025F` = **TPMS_WAL01**
- `$07E0` = **BOSCH_ME96**

Observed ME9.6 deltas vs T8: `$07E0` identifies specifically as
`BOSCH_ME96`; `$025F` is now named TPMS; `$0249` exposes an AFL logical module
route in addition to REC; `$0247`/ICM 2, `$0251`/EHU, `$025C`/SLM, and
`$07E1`/TCM were not observed in the primary ME9.6 combined walk.

## What's NOT inferred yet

- `$025D` answers ASCII `"1A9"` and DID B2 = `A1 00 00 00 00 00`, but no
  `$1A 97` Module Description string was captured. It remains the main
  unnamed stable responder.
- `$0253` still responds in sweeps but lacks a readable module description in
  the current captures. `$025F` is named `TPMS_WAL01` on ME9.6 but remains
  unnamed in the T8 capture.
- The split-capture `$0243` / `ESP EBC430` ambiguity needs video time
  alignment before we treat it as either a true alternate address context
  or a log/video ordering artifact.

## How to grow this map

For each unidentified address:
1. Run `commands/saab/cim_info_read.yaml` against it (`$1A 9A` plus the
   identification DIDs) — many modules return readable identification
   strings under DIDs 0x81, 0x82, 0x90.
2. Trigger an action you suspect that module owns (e.g. cycle the
   washer pump and see which ECU emits codes).
3. Cross-reference resulting DTCs against z90's ECU index pages.
4. Update this file with the new evidence.
