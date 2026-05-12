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
| `0x27` | SecurityAccess | Seed/key. Level `$01` = standard; `$0B` = SAAB SAS (manufacturer-specific) |
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
