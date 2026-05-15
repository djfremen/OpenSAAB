# SAAB CAN-ID → ECU function map

**Date:** 2026-05-13
**Sources:**
- Bench captures from `commands/saab/check_codes_read_dtcs.yaml` (T8 bench, VIN `YS3FD49YX41012017`)
- Bench captures from `commands/saab/engine_me96_read_codes.yaml` + `clear_codes_clear_dtcs.yaml` (ME9.6 field car, VIN prefix `YS3FH46U…`)
- [`mattiasclaesson/Trionic`](https://github.com/mattiasclaesson/Trionic) — `Trionic8.cs:42-44` `FilterIdECU` / `FilterIdCIM`
- [z90.pl SAAB DTC catalog](https://z90.pl/saab/dtc/) — model 9-3 9440 MY 2009 ECU index
- [`protocol/gmlan_11bit_ids.md`](../protocol/gmlan_11bit_ids.md) — Jason Gaunt 2013 canonical labels

This document **infers** the physical module sitting at each CAN-ID by
cross-referencing observed DTCs with z90's per-ECU sections and
Trionic's hardcoded address constants. It is not a canonical claim —
it's the strongest hypothesis the available evidence supports for each
address.

## Address-to-module table

| TX | SF reply | MF reply | Inferred module | Confidence | Evidence |
|---|---|---|---|---|---|
| `$0241` | `$0541` | `$0641` | Engine ECM (T8) — Tech2Win manufacturer alias | High | Bench unlock w/ seed `f6 31` → key `de 40` (engine SAS); Tech2Win uses this for engine read; canonical Jason Gaunt is `TO_BCM`, but Tech2Win re-uses it as engine-diag entry |
| `$0242` | `$0542` | `$0642` | **BCM** (Body Control Module) | High | DTCs `B0092-05` "Passenger Seat Sensor circuit" + `B1001` "Control Module not Added" + lost-comm with multiple modules — z90 attributes both to BCM(#817) |
| `$0243` | `$0543` | `$0643` | **Door module** (DDM/PDM/RLDM/RRDM — specific role TBD) | High | `B3832-45` "Information: Anti Pinch Not Learned" — z90 attributes only to DDM(#819), PDM(#825), RLDM(#827), RRDM(#828). Same code seen on $0243/$0248/$024A/$024B → all four are doors |
| `$0245` | `$0545` | `$0645` | **ACC / Heated Seats / Climate** (NOT CIM as Trionic claims) | Medium-High | z90 attributes captured `B1928-05` "Seat Temperature Sensor Left" + `B2429-06` "Seat Heating Left" to ACC(#814). **Conflicts** with Trionic's `FilterIdCIM = { 0x245 }` — see ambiguity note below |
| `$0246` | `$0546` | `$0646` | **TO_SIC** (Steering Integration Control — canonical) | Medium | 2026-05-14 1367 capture: 6 DIDs respond on $0646 (02, 03, 90, 9A, B9, BA). Real populated ECU. DID 9A=`04 09`, BA=`7C CF 35 50` (calibration). No DTCs yet to cross-reference vs z90 |
| `$0247` | `$0547` | `$0647` | TO_SDC (canonical) — bench evidence pending | Low | Jason Gaunt label only |
| `$0248` | `$0548` | `$0648` | **Door module** (DDM/PDM/RLDM/RRDM) | High | Same `B3832-45` as $0243; z90 door-module exclusive |
| `$0249` | `$0549` | `$0649` | **TCS/ESP** (Anti-Skid / Electronic Stability) | Medium | DTCs `U2105-00` "ECM Missing on Bus", `U2143-00` "Steering Angle Sensor Missing", `U2108-00` "TCS/ESP Missing" — z90 attributes to TCS/ESP(#831) more often than other candidates |
| `$024A` | `$054A` | `$064A` | **Door module** (DDM/PDM/RLDM/RRDM) | High | `B3832-45` shared |
| `$024B` | `$054B` | `$064B` | **Door module** (DDM/PDM/RLDM/RRDM) | High | `B3832-45` + `B3205-06` "Power Window Down" + `B3210-06` "Power Window Up" — z90 attributes window codes to DDM/PDM/RLDM |
| `$024D` | `$054D` | `$064D` | unknown — empty DTC list this run | None | No DTCs returned (terminator only) |
| `$024F` | `$054F` | `$064F` | **UEC** (User Equipment Center / front lighting controller) | High | All 5 unique DTCs (`B2575/B2698/B2699/B2525` low-beam + fog-light circuits, `B3810-06` headlamp washer relay) z90-attributed exclusively to UEC(#832) |
| `$0253` | `$0553` | `$0653` | unknown body module — bench evidence pending | None | Cleared in clear-codes sweep but no DTCs read |
| `$0257` | `$0557` | `$0657` | unknown — possibly RFA (Remote Function Actuator) | Low | Jason Gaunt has TO_RFA at $0258, this is adjacent; involved in L01 SecurityAccess sweep |
| `$025B` | `$055B` | `$065B` | unknown body module — bench evidence pending | None | |
| `$025C` | `$055C` | `$065C` | unknown body module — bench evidence pending | None | |
| `$025D` | `$055D` | `$065D` | **TBD — confirmed ASCII `"1A9"` signature** | Medium | 2026-05-14 1367 capture: DID 81 returns `5A 81 31 41 39` = ASCII `"1A9"` (verifies the 2026-05-13 note). Also DID B2 = `A1 00 00 00 00 00`. Needs Tech2Win Module Description screen to put a SAAB name on `"1A9"` |
| `$025F` | `$055F` | `$065F` | unknown body module — bench evidence pending | None | |
| `$07E0` | `$05E8` | `$07E8` | **Engine ECM (OBD-II)** — ME9.6 on the field car | High | Trionic `FilterIdECU = { 0x7E0, 0x7E8, 0x5E8 }`; all 21 captured DTCs are engine codes z90-attributed to ME9(#840) and T8(#821) |
| `$07E1` | `$05E9` | `$07E9` | **TCM (OBD-II)** — Transmission | High | Jason Gaunt canonical `OBD-II physical to TCM`; bench L01 SecurityAccess captures show $0257/$07E1 returning 67 01 d2 dc |

## Ambiguity: $0245 — ACC vs CIM

Trionic's `FilterIdCIM = { 0x245, 0x545, 0x645 }` says **CIM** (Column
Integration Module) is at $0245. But our bench DTCs at $0245 are
exclusively heated-seat related (`B1928-05` Seat Temperature Sensor
Left, `B2429-06` Seat Heating Left, `B0260-06` likely seat-related),
which z90 attributes to ACC(#814) — Air Conditioning Control / climate
module.

Three possible reconciliations:

1. **Tech2Win routes both ACC and CIM through $0245.** SAAB's
   diagnostic gateway may proxy multiple physical modules through one
   alias. The seat heater is part of the climate package and CIM
   handles ignition / column functions; both could land at $0245 with
   the gateway disambiguating internally.
2. **Trionic's CIM constant was correct for older platforms, ACC took
   over $0245 on later models.** The 9-3 9440 platform may have
   re-assigned addresses vs the 9-3 9400 / Trionic7-era cars Trionic
   originally targeted.
3. **z90 mis-attributes these DTCs to ACC** when they're actually CIM
   or BCM codes. Less likely given z90 has per-ECU sections that match
   Tech2Win menu structure.

To disambiguate: send `$1A 9A` to $0245 and check the algorithm-tape
prefix against known CIM vs ACC tape signatures. Also send `$1A 90`
(VIN read) — only certain modules carry VIN.

## Door module disambiguation ($0243 / $0248 / $024A / $024B)

All four return `B3832-45 Information: Anti Pinch Not Learned`. z90
attributes this code identically to DDM(#819), PDM(#825), RLDM(#827),
RRDM(#828) — one entry per door module. So all four CAN-IDs are door
modules, but **which door is which is not yet determined from this
data**.

Likely mapping by canonical SAAB address discipline (untested):

| CAN-ID | Likely door | Reasoning |
|---|---|---|
| `$0243` | Driver | Lowest in the door range, often master |
| `$0248` | Passenger | Adjacent body-control range |
| `$024A` | Rear left | Higher addresses often rear |
| `$024B` | Rear right | Adjacent |

Bench test to resolve: actuate one window at a time and observe which
ECU's DPID stream changes. Or read DID 0x90 (VIN/identity) — each door
module ought to identify itself.

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

## What's NOT inferred yet

- Which physical module sits at `$0247`, `$0253`, `$025B`,
  `$025C`, `$025F` — silent on `$1A` in this capture; need targeted
  re-query.
- `$025D` answers ASCII `"1A9"` but the SAAB name behind that tag is
  unknown — best resolved by reading Tech2Win's Module Description
  screen which displays canonical names.
- Whether `$0244` (Jason Gaunt `TO_EHU`) corresponds to the actual
  Entertainment Head Unit on this platform — silent on `$1A` here.

## How to grow this map

For each unidentified address:
1. Run `commands/saab/cim_info_read.yaml` against it (`$1A 9A` plus the
   identification DIDs) — many modules return readable identification
   strings under DIDs 0x81, 0x82, 0x90.
2. Trigger an action you suspect that module owns (e.g. cycle the
   washer pump and see which ECU emits codes).
3. Cross-reference resulting DTCs against z90's ECU index pages.
4. Update this file with the new evidence.
