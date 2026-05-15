# 2026-05-15 ECM walk audit — T8 vs ME9.6

Cross-references the two OBS walk videos against the cstech2win shim logs to enumerate (a) every Tech2Win UDS command issued on the bus, (b) every distinct ECU reply, (c) the menu state visible on screen at each point in the video.

**Source files**
- Videos: `videos/2026-05-15_1142_pdt_ecm_walk_t8.mkv` (4m 14s, T8 bench), `videos/2026-05-15_1208_pdt_ecm_walk_me96.mkv` (6m 41s, ME9.6 field car)
- cstech2win logs: 13 gzipped log slices across `2026-05-15_ecm_walk_t8/raw/` and `2026-05-15_ecm_walk_me96/raw/`
- Decoded JSON: same dirs, `decoded/`

**Important data-grouping note:** the two `2026-05-15_ecm_walk_*` directories don't cleanly separate by car — the collector batched files from both cars across both upload directories. **Files are grouped here by VIN (the canonical car identifier), not by walk directory.**

| Group | VIN | Decoded files |
|---|---|---|
| T8 (VIN…2017) | YS3FD49YX41012017 | cstech2win_1778870835332.json, cstech2win_1778870836516.json, cstech2win_1778872508198.json, cstech2win_1778872509078.json |
| ME9.6 (VIN…1367) | YS3FH46U681101367 | cstech2win_1778870829013.json, cstech2win_1778870831934.json, cstech2win_1778872504286.json, cstech2win_1778872505412.json, cstech2win_1778872510392.json |

---

## 1. Master UDS command catalogue (Tech2Win → bus)

Across both walks combined, Tech2Win issued these distinct `(SID, sub)` pairs. Counts are the number of TX frames carrying that exact byte pair per car.

| SID | sub | T8 walk-dir count | ME9.6 walk-dir count | Purpose |
|---|---|---:|---:|---|
| `0x04` | `` | 20 | 20 | ClearDiagnosticInformation |
| `0x1a` | `01` | 14 | 14 | DID 01: manuf status |
| `0x1a` | `02` | 4 | 4 | DID 02: ? |
| `0x1a` | `03` | 2 | 2 | DID 03: ? |
| `0x1a` | `07` | 2 | 2 | DID 07: ? |
| `0x1a` | `08` | 4 | 4 | DID 08: ? |
| `0x1a` | `26` | 2 | 2 | DID 26: ? |
| `0x1a` | `41` | 4 | 4 | DID 41: UEC sub |
| `0x1a` | `42` | 2 | 2 | DID 42: ACC sub |
| `0x1a` | `7b` | 21 | 40 | DID 7b: counter |
| `0x1a` | `7c` | 21 | 40 | DID 7c: counter |
| `0x1a` | `81` | 9 | 9 | DID 81: ident |
| `0x1a` | `90` | 69 | 88 | DID 90: VIN (17 ASCII) |
| `0x1a` | `97` | 21 | 40 | DID 97: module description (ASCII) |
| `0x1a` | `98` | 21 | 40 | DID 98: part trailer |
| `0x1a` | `99` | 21 | 40 | DID 99: build date (4B) |
| `0x1a` | `9a` | 74 | 130 | DID 9a: tape-head signature (2B) |
| `0x1a` | `b2` | 9 | 9 | DID b2: IPC/SDM sub |
| `0x1a` | `b9` | 2 | 2 | DID b9: IPC sub |
| `0x1a` | `ba` | 11 | 11 | DID ba: IPC sub |
| `0x1a` | `c1` | 21 | 40 | DID c1: counter c1 |
| `0x1a` | `c2` | 20 | 39 | DID c2: counter c2 |
| `0x1a` | `c3` | 20 | 39 | DID c3: counter c3 |
| `0x1a` | `c4` | 21 | 40 | DID c4: counter c4 |
| `0x1a` | `cb` | 21 | 40 | DID cb: counter cb |
| `0x1a` | `cc` | 21 | 40 | DID cc: counter cc |
| `0x1a` | `d1` | 21 | 40 | DID d1: region code |
| `0x1a` | `d2` | 4 | 7 | DID d2: region code |
| `0x1a` | `d3` | 3 | 5 | DID d3: region code |
| `0x1a` | `d4` | 1 | 1 | DID d4: region code |
| `0x1a` | `db` | 21 | 40 | DID db: region code |
| `0x1a` | `dc` | 21 | 40 | DID dc: region code |
| `0x20` | `` | 15 | 15 | ReturnToNormalCommunication |
| `0x2c` | `f3` | 2 | 2 | DynamicallyDefineLocalID (sub=f3) |
| `0xa9` | `81` | 46 | 46 | ReadDiagnosticInformation (GM DTC) (sub=81) |
| `0xaa` | `01` | 68 | 92 | ReadDataByPID (DPID setup) (sub=01) |
| `0xfe` | `01` | 36 | 39 | TesterPresent / keep-alive (sub=01) |
| `0xfe` | `04` | 2 | 2 | TesterPresent / keep-alive (sub=04) |
| `0xfe` | `1a` | 18 | 18 | TesterPresent / keep-alive (sub=1a) |
| `0xfe` | `3e` | 486 | 792 | TesterPresent / keep-alive (sub=3e) |

**Totals:** T8 walk dir = 1201 TX frames, ME9.6 walk dir = 1880 TX frames. The same 40 distinct `(SID, sub)` pairs appear in both walks.

**Observation:** the command set is platform-agnostic. Tech2Win sends the same 40-pair UDS sweep regardless of car. Counts are by upload-batch directory (not by car VIN), because TX frames flow regardless of which ECU replies and which VIN is on the bus.

## 2. Per-CAN-ID reply diff

Full table at `2026-05-15_t8_vs_me96_reply_diff.md`. Headline numbers across all 22 CAN-IDs covered: **108 byte-identical DID slots, 136 differ, 111 only-in-one-car.**

Engine ECM `$07E0` — 18 of 19 DID slots differ:

| DID | T8 | ME9.6 | Δ |
|---|---|---|:-:|
| `97` | `ECM                 ` | **`BOSCH_ME96`** | ✗ |
| `98` | `PPCAN 210 ` | `O000006368` | ✗ |
| `99` | `FF FF FF FF` (unset) | `20 09 03 11` (~2009-03-11) | ✗ |
| `9A` | `01 06` | `03 0A` | ✗ |
| `C1` | `55556301` | `55566297` | ✗ |
| `C2` | `12799173` | `55571124` | ✗ |
| `C3` | `55353555` | `55566296` | ✗ |
| `D1..DC` | `20 20` (spaces) | `FF FF` (unset) | ✗ |

DID 97 alone cleanly fingerprints which engine ECM is on the wire. Tech2Win uses the same DID probe sequence; the engine's own firmware decides what to return.

## 3. Video menu timeline

OCR'd from each video at 1 fps, filtered for Tech2Win-menu signal (lines matching `F<digit>:`, ECU names, diagnostic-menu keywords). The shim debug pane that dominates each frame is intentionally excluded.

### 3a. T8 walk (4 min 14 s)

| Video t | Menu visible (selected lines) |
|---|---|
| 10s | 8: Diagnostics ee Sh / F2: Tool Options "OAM cesstoy 145.554 reset mark |
| 17s | | Diagnostics = | YES | G@ OFile C/Users/Elitebook/Desktop/bench-timecade-htm| 5: 3 Ro: |
| 18s | | Diagnostics = | YES | @ = OFile C/Users/Elitebook/Desktop/bench-timecade-htm| ov (OR Ro: |
| 21s | F@: Diagnostic Trouble Codes (DIC) SS Te |
| 22s | @: Diagnostic Trouble Codes (DIC =e) Sel |
| 23s | FQ: Diagnostic Trouble Codes (DIC) = |
| 24s | @: Diagnostic Trouble Codes (NIC) =e) Sel |
| 242s | Body Control Hodule — f |

### 3b. ME9.6 walk (6 min 41 s)

| Video t | Menu visible (selected lines) |
|---|---|
| 6s | F3: Diagnostic Strategy 3 | 4 | 5 i / F4: Release Notes «6 |_F7 | _F8 | |
| 7s | F3: Diagnostic Strategy r3 | 4 | 5 i / F4: Release Hotes * 6 | 7 | 8M |
| 11s | F2: chassis RC / F3: Bods ( 3 ie 5. i |
| 12s | Fiz ECU Information EXIT NO ' . . / F3: Bus ior =: > He 1778872098562 / F4: Vehicle Pouer Supply im O | 1 | 2 esston 4O: |
| 91s | Body Control Hodule ry i |
| 100s | Body Control Hodule = , |
| 124s | Body Control Hodule a , |
| 155–157s | Engine Control Hodule 2 , |
| 204s | Engine Control Hodule a q |

_Note: video OCR was dominated by the scrolling cstech2win shim-log pane in the left half of each frame; the actual Tech2Win UI occupies a smaller area. The filter retains the right signals but the rate is necessarily sparse. For deeper menu time-alignment we'd want to crop frames to the Tech2Win pane before OCR._

## 4. Video phases mapped to log activity

Bench observation correlated with what the wire shows:

1. **First ~10–15 s of either video** — Tech2Win initializing (`Diagnostics` / `Tool Options` menus visible, shim log shows `PDURegisterEventCallback` / `PDUIoCtl` setup). On the wire: `$FE 3E` keep-alive only.
2. **Tech2Win main menu → All → F1 ECU Information** (ME9.6 around t≈11–12 s, T8 implied around t≈8–18 s). On the wire: nothing yet — menu navigation alone doesn't transmit.
3. **ECU Information sweep begins** (ME9.6 t≈30 s onward, T8 implied t≈25 s onward). On the wire: cycle of `TX $02XX 1A 97` followed by the rest of the DID set (`90, 7B, 7C, 98, 99, 9A, C1..C4, CB, CC, D1, DB, DC`) — one address at a time, ~7 seconds per module.
3. **Per-module pages** — video shows e.g. `Body Control Module` (BCM) at ME9.6 t=91–124 s; `Engine Control Module` at ME9.6 t=155–204 s. Each page corresponds to a burst of the full DID probe set targeted at that one CAN-ID. On the engine ECM page is where `$07E0 1A 97 → BOSCH_ME96` is captured.
4. **DTC read sweep** — when video shows `Diagnostic Trouble Codes (DTC)` (T8 t=21–24 s, also in `non_keepalive_events.txt`), wire transmits `$A9 81` at every diag address.
5. **Clear DTCs** — `$04` at every diag address; ME9.6 walk did this 20 times across the bus.
6. **End of walk** — `$20` ReturnToNormalCommunication on multiple addresses (15 occurrences each walk), then drop back to `$FE 3E` keep-alive only.

## 5. Findings

1. **Tech2Win sends the same 40 distinct UDS command pairs to both cars.** The walk is platform-agnostic at the request level.
2. **Engine ECM identity is platform-distinct.** `$07E0 $1A 97` returns `ECM` (generic) for T8, `BOSCH_ME96` for ME9.6. 18 of 19 engine-ECM DID replies differ.
3. **Most body modules return identical part numbers across the two cars.** DSM, SRM, PAS, doors, TCM have 7–14 byte-identical DIDs each. These are the platform-shared parts.
4. **CIM, BCM, IPC, UEC differ in build counters but share module-name and structure.** Same physical part type, individual build IDs.
5. **Context aliasing visible in `$0249`:** T8 walk first-reply is `REC`, ME9.6 walk first-reply is `AFL-Epsilon`. Both Tech2Win menu states expose the same `$0249` transport address but route to a different logical module based on the current menu.
6. **`$025D` still has no readable `$1A 97` in either capture.** Open item — needs the steering / tape-head menu specifically open to force the proxy route.
7. **`$025F` resolves only on ME9.6 (`TPMS_WAL01`).** T8 capture didn't probe the TPMS address.

## 6. Open items

- Re-walk both cars on the same Tech2Win session in a single OBS recording to eliminate the file-grouping ambiguity in this dataset.
- Time-align frames to wire events at finer resolution — needs cropping the Tech2Win UI from the OBS frame before OCR.
- Force `$025D` Module Description by entering the relevant Tech2Win submenu and capturing again.
- Probe TCM (`$07E1`), EHU (`$0251`), ICM 2 (`$0247`), SLM (`$025C`), TPMS (`$025F`) on both cars in one session for symmetric data.
