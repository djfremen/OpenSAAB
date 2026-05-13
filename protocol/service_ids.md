# UDS / GMLAN Service IDs

Vendor-neutral reference for the UDS service IDs seen on SAAB GMLAN buses.
Sourced from GMW3110-2010 (GM internal spec) and the public J2534 + UDS
literature. SID values match Jason Gaunt's 2013 GMLAN library and scapy's
`contrib/automotive/gm/gmlan` enums.

## Request SIDs (Tester → ECU)

| SID | Name | Notes |
|---|---|---|
| `0x04` | ClearDiagnosticInformation | Wipe DTCs |
| `0x10` | InitiateDiagnosticOperation | Enter / exit diag session. `$10 02` was historically thought to be SAAB SAS preamble — it's not (Tech2 doesn't send it). |
| `0x12` | ReadFailureRecordData | |
| `0x1A` | ReadDataByIdentifier | The big workhorse — read identification, calibration IDs, sensor snapshots. DID byte follows the SID. |
| `0x20` | ReturnToNormalOperation | |
| `0x22` | ReadDataByParameterIdentifier | |
| `0x23` | ReadMemoryByAddress | Used for SSA region reads on SAAB |
| `0x27` | SecurityAccess | Seed/key. SAAB uses at least 4 levels — see SecurityAccess levels table below |
| `0x28` | DisableNormalCommunication | |
| `0x2C` | DefineDPID | |
| `0x2D` | DefinePIDByAddress | |
| `0x34` | RequestDownload | Programming |
| `0x36` | TransferData | Programming payload chunks |
| `0x3B` | WriteDataByIdentifier | |
| `0x3E` | TesterPresent | Session keepalive. Cadence ~2-2.5s when idle, faster during active commands |
| `0xA2` | ReportProgrammingState | |
| `0xA5` | ProgrammingMode | |
| `0xA9` | ReadDiagnosticInformation | DTC read |
| `0xAA` | ReadDataByPacketIdentifier | Dynamic data ID setup. Used by Tech2 as preamble to many flows |
| `0xAE` | DeviceControl | |

## Response SIDs (positive)

Positive responses = request SID + `0x40`:
- `0x5A` = response to `0x1A`
- `0x67` = response to `0x27`
- `0x67 0B SS SS` = SAS seed; `0x67 0C` = SAS unlock ack
- `0x7E` = response to `0x3E`
- `0xE9` = response to `0xA9`
- `0xEA` = response to `0xAA`

## Negative Response Codes (NRC)

Negative response format: `7F <requested_sid> <nrc>`.

| NRC | Name | Common cause |
|---|---|---|
| `0x10` | generalReject | Driver / DLL refused — usually session-state issue |
| `0x11` | serviceNotSupported | ECU doesn't implement that SID |
| `0x12` | subFunctionNotSupported | Wrong sub-function for the SID |
| `0x21` | busyRepeatRequest | Try again in a moment |
| `0x22` | conditionsNotCorrect | Wrong session or DID not readable now |
| `0x31` | requestOutOfRange | DID not present on this ECU revision |
| `0x33` | securityAccessDenied | Need to do `$27` unlock first |
| `0x35` | invalidKey | Wrong key sent for `$27 0C` — burns one attempt |
| `0x36` | exceededNumberOfAttempts | ECM is locked out for cooldown period |
| `0x37` | requiredTimeDelayNotExpired | Wait 10s after power-on before first `$27` |
| `0x78` | responsePending | ECU is computing; keep polling, don't time out |
| `0x7E` | subFunctionNotSupportedInActiveSession | |
| `0x7F` | serviceNotSupportedInActiveSession | |

## SecurityAccess levels on SAAB

Cross-referenced against
[`mattiasclaesson/Trionic`](https://github.com/mattiasclaesson/Trionic)
(`SeedToKey.cs`, `SeedKey/AlgorithmDictionary.cs`). Wire format follows
GMW3110 §8.8.5.1 — request uses an odd subfunction; send-key uses the
next-even (level + 1).

| Request | Send-key | Routing | Purpose | Key algorithm |
|---|---|---|---|---|
| `$27 01` | `$27 02` | `$024X` (Tech2Win body bus) OR `$7E0` (OBD-II) | Body-module standard unlock (door, IPC, RFA, transmission, etc.) | NativeVM bytecode tape, per-ECU algorithm index. Trionic publishes constants in `AlgorithmDictionary.cs` for TRIONIC8 / MOTRONIC96 / EDC16C39 / EDC17C19. |
| `$27 0B` | `$27 0C` | `$0241` (SAAB manufacturer alias) | SAS / IMMO-specific unlock — what Tech2Win uses for module-pairing and immobiliser operations. Delegates to SAAB's online SAS server in stock Tech2Win. | Private NativeVM tape entry (not in Trionic). Bench-verified: seed `0xC4DC` + algo idx `0x67` → key `0x4EED`. |
| `$27 FB` | `$27 FC` | `$7E0` (OBD-II) | Mid-tier engine access | Hardcoded formula: `key = (((seed>>5)|(seed<<11)) + 0xB988) ^ 0x8749 + 0x06D3 ^ 0xCFDF` |
| `$27 FD` | `$27 FE` | `$7E0` (OBD-II) | Highest engine access — used for flashing/reprogramming the engine ECU. Trionic's default. | Hardcoded formula: `key = (((seed>>5)|(seed<<11)) + 0xB988) / 3 ^ 0x8749 + 0x0ACF ^ 0x81BF` |

**The two big distinctions:**
- `$01` is **universal** (all ECUs, all addressing schemes) and uses
  NativeVM bytecode with a per-ECU algorithm index.
- `$0B` is **Tech2Win/SAAB-online-specific** — narrow scope, mostly
  SAS/IMMO pairing. Engine REPROGRAMMING does NOT use `$0B`; it uses
  `$FD`.
- `$FB`/`$FD` are **hardcoded mathematical formulas** (not bytecode).
  Different from the NativeVM-based `$01`. These are bench-validated
  in Trionic's source.

ME9.6 engine ECUs have a custom non-NativeVM formula even at `$01` —
see `SeedToKey.calculateKeyForME96`. Not all SAAB ECUs are bytecode-driven.

## Tactical notes

- **`0x78` is not an error.** When you see `7F xx 78`, the ECU is working on
  the request — wait at least 200ms and re-read. Don't retry the original
  request; that wastes time and the ECU is already working.
- **`0x37` after power-on is universal.** All UDS-compliant ECUs require a
  10-second post-power-on delay before the first `$27` request. Don't burn
  attempts trying to skip it.
- **`0x35` is dangerous.** Each invalidKey response costs you one of the
  ECU's free attempts (usually 3-5). After exceeding, you hit `0x36`
  exceededNumberOfAttempts and the ECU locks for minutes-to-hours.
