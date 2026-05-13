# OpenSAAB ↔ Trionic cross-validation audit

**Date:** 2026-05-12
**Sources:** OpenSAAB `commands/` + `protocol/` as of commit `8894b2b`,
audited against [`mattiasclaesson/Trionic`](https://github.com/mattiasclaesson/Trionic)
@ HEAD (2026-04-29).

Trionic is an established (53-star, ~13-year-old, actively maintained) C#
library for SAAB Trionic ECU diagnostics + flashing. Its `SeedKey/`,
`SeedToKey.cs`, and `Trionic8.cs` modules independently document the
seed/key engine and wire framing we've been deriving from shim captures.

## ✅ Confirmations

**NativeVM opcodes & structure.** Trionic's `SeedKey/Step.cs:Operation()`
implements the exact same opcode set we have in our private security_calc
engine (and that the v6 shim captures attest to). Same parameter
conventions, same 4-step algorithm structure, same 16-bit arithmetic.

Opcodes confirmed identical: `0x05`, `0x14`, `0x2A`, `0x37`, `0x4C`,
`0x52`, `0x6B`, `0x75`, `0x7E`, `0x98`, `0xF8`. (Our engine also handles
`0x0B`, `0x27`, `0x29` which Trionic does not cover — likely SAAB SAS
tape extensions.)

**Wire-level SecurityAccess pattern.** Trionic sends `02 27 <LEVEL>` for
request-seed and `04 27 <LEVEL+1> KK KK` for send-key. The level+1 rule
for send-key is universal UDS (GMW3110 §8.8.5.1) and matches our bench
captures verbatim:

| Request level | Send-key sub |
|---|---|
| `0x01` | `0x02` |
| `0x0B` | `0x0C` |
| `0xFB` | `0xFC` |
| `0xFD` | `0xFE` |

**ResponsePending tolerance.** Trionic handles `7F xx 78` the same way
our docs prescribe.

## ⚠️ Refinements needed in OpenSAAB

### 1. Address labeling: $0241 ≠ CIM in canonical SAAB

`Trionic8.cs:42-44`:
```csharp
static public List<uint> FilterIdECU = new List<uint> { 0x7E0, 0x7E8, 0x5E8 };
static public List<uint> FilterIdCIM = new List<uint> { 0x245, 0x545, 0x645 };
```

**Canonical SAAB addressing per Trionic:**
- Engine ECU (T8): `$7E0` (TX) / `$7E8` (RX) — OBD-II standardized
- CIM: `$245` (TX) / `$545` SF / `$645` MF
- ME9.6 engine ECU: `$11` (recovery) / OBD-II for normal

Our bench captures show Tech2Win using `$0241/$0641` for what menu labels
called "CIM Info". This is most likely a **Tech2Win-specific manufacturer
alias** that routes to the same physical CIM module via the SAAB
diagnostic gateway, separate from the OBD-II addressing scheme Trionic
uses.

Both addressing schemes are valid simultaneously on the bus; they target
the same physical modules. OpenSAAB should document both maps and not
imply they're mutually exclusive.

### 2. SecurityAccess level landscape — four levels, not two

We previously documented levels $01 (body modules) and $0B (engine SAS).
Trionic adds two more, and reframes "engine programming":

| Level | Send-key | Operation class | Algorithm source |
|---|---|---|---|
| `$01` | `$02` | Standard body-module unlock (door, IPC, RFA, etc.) | NativeVM, per-ECU `AlgorithmDictionary` |
| `$0B` | `$0C` | SAS / IMMO-specific (what we captured at $0241) | not in Trionic — likely SAAB-online SAS server |
| `$FB` | `$FC` | Mid-tier engine access | Hardcoded formula in `SeedToKey.calculateKey` |
| `$FD` | `$FE` | Highest engine access (Trionic's "AccessLevelFD = default") — used for flashing | Different hardcoded formula |

**Trionic's `$FD`, not `$0B`, is what enables engine reprogramming.**
Our prior characterization of `$0B` as "engine programming" is misleading.
`$0B` is the SAAB-specific SAS/IMMO unlock; engine programming proper
goes through `$FD` at OBD-II addressing.

### 3. ME9.6 has a custom (non-NativeVM) seed/key formula

`SeedToKey.cs:RetSeed()` — ME9.6 uses an arithmetic expression, not
the NativeVM bytecode. Important: not every SAAB ECU is bytecode-driven.
Worth flagging in `protocol/saab_extensions.md`.

### 4. Trionic publishes per-ECU NativeVM algorithm constants

`SeedKey/AlgorithmDictionary.cs` gives the exact 4-Step algorithm for:
- `TRIONIC8`: `Step(0x6B, 0x65, 0x07)` → `Step(0x4C, 0x0A, 0x77)` → `Step(0x7E, 0xF8, 0xDA)` → `Step(0x98, 0x3F, 0x52)`
- `MOTRONIC96`, `MOTRONIC961`, `EDC16C39`, `EDC17C19`

These are at level `$01` only. Comments reference tape offsets (e.g.
`// 39 000002E5 EC ...`) — these match the bytecode-tape layout we have
from `dllsecurity.dll`.

OpenSAAB doesn't ship these tape entries (kept private). Trionic does.
If a contributor wants offline level-$01 keys for engine ECUs without
RE'ing the DLL, Trionic's `AlgorithmDictionary.cs` is the published
source.

## ❓ Open mystery — bench `0xC4DC → 0x4EED` matches no Trionic algorithm

Bench-verified: seed `0xC4DC` + our algo `(table 1, idx 0x67)` → key
`0x4EED` (matches Bojer 9/9). Computing Trionic's published algos
against the same seed:

| Algorithm | Computed key | Match? |
|---|---|---|
| TRIONIC8 NativeVM (level $01) | `0x9FAE` | ❌ |
| MOTRONIC96 NativeVM (level $01) | `0x8E41` | ❌ |
| MOTRONIC961 NativeVM | (different) | ❌ |
| ME9.6 custom formula | `0x8E41` | ❌ |
| $FB hardcoded | `0x4E65` | close but no |
| $FD hardcoded | `0x5F03` | ❌ |
| CIM custom | `0x3371` | ❌ |

**None produce 0x4EED.** Most likely explanation: Tech2Win's `$27 0B`
at `$0241` is the SAS/IMMO path that uses an algorithm tape entry not
covered by Trionic. The algorithm matches our private NativeVM tape
position (idx 0x67) but Trionic doesn't publish that entry because
Trionic targets engine reflashing (`$FD`), not SAS (`$0B`).

This is independent corroboration that level `$0B` is a separate
universe of access from Trionic's scope.

## Action items applied in this commit

- `protocol/gmlan_11bit_ids.md` — added the Trionic-canonical addresses
  ($245 CIM, $7E0 engine OBD-II) alongside the Tech2Win manufacturer
  aliases.
- `protocol/service_ids.md` — expanded SecurityAccess section to cover
  all 4 levels ($01, $0B, $FB, $FD).
- `commands/saab/engine_sas_unlock.yaml` — clarified `$0B` is
  SAS/IMMO-specific, not engine programming.
- `commands/saab/cim_info_read.yaml` — flagged the $0241 vs $0245 routing
  question; added Trionic-canonical CIM address as alternate.
- `commands/saab/engine_program_unlock_fd.yaml` — NEW. Trionic-cited
  level $FD wire format + key formula. The level our engine programming
  flow should actually use.
- `README.md` — table of catalogued entries refreshed; link to this doc.
