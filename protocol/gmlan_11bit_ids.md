# GMLAN 11-bit Arbitration IDs

Standard GM Local Area Network 11-bit CAN IDs documented by Jason Gaunt
(2013) in the public `GMLAN_11bit.h` library
([Afterglow/arduino-gmlan](https://github.com/Afterglow/arduino-gmlan),
[maxpfeif/GMLAN](https://github.com/maxpfeif/GMLAN),
[mattatcha/gmlan](https://github.com/mattatcha/gmlan) — all derivatives,
Apache 2.0).

This document is a **canonical reference** — the labels here come from
that public library. SAAB-specific *observations* of which physical
module answers at which CAN ID belong in `commands/` entries, not here.

## Broadcast / wake-up

| CAN ID | Canonical name |
|---|---|
| `0x100` | InitialWakeUpRequest |
| `0x101` | RequestToAllNodes (functional broadcast) |
| `0x102` | DiagnosticRequest |

## Per-ECU diagnostic requests (Tester → ECU)

Canonical Jason Gaunt 2013 mapping:

| CAN ID | Canonical name |
|---|---|
| `0x240` | ReservedRequest |
| `0x241` | TO_BCM |
| `0x242` | TO_TDM |
| `0x243` | TO_EBCM |
| `0x244` | TO_EHU |
| `0x246` | TO_SIC |
| `0x247` | TO_SDC |
| `0x24C` | TO_IPC |
| `0x251` | TO_HVAC |
| `0x258` | TO_RFA |

These names describe which module is being addressed in the original GM
GMLAN scheme. SAAB platforms may route operations to specific modules
differently than the canonical mapping implies — see the **caveat**
section below.

## Per-ECU diagnostic responses (ECU → Tester)

| CAN ID range | Use |
|---|---|
| `0x540 – 0x55F` | Single-frame responses (1-byte PCI, ≤7 bytes data) |
| `0x640 – 0x65F` | Multi-frame responses (ISO-TP First-Frame / Consecutive-Frame) |

Per-module response IDs follow the offset pattern: TX `0x24x` ↔ RX SF
`0x54x` / MF `0x64x`.

## OBD-II compliance addresses

| CAN ID | Use |
|---|---|
| `0x7DF` | OBD-II functional request (broadcast to all OBD-II ECUs) |
| `0x7E0` | OBD-II physical to ECM |
| `0x7E1` | OBD-II physical to TCM |
| `0x7E8` | OBD-II physical from ECM |
| `0x7E9` | OBD-II physical from TCM |

## Important caveat — don't conflate canonical labels with SAAB observations

The canonical names above are the *original GMLAN library* labels. On
SAAB platforms they may NOT describe what physically responds at a
given address — multiple operations can be routed through manufacturer-
specific gateways. **If you're trying to reach a specific physical
module, look at the relevant `commands/` entry, not at this canonical
table.**

For the OBD-II addressing layer used by open-source SAAB tools, see
[`mattiasclaesson/Trionic`](https://github.com/mattiasclaesson/Trionic),
which authoritatively maps:
```csharp
FilterIdECU = { 0x7E0, 0x7E8, 0x5E8 };  // engine ECU on OBD-II
FilterIdCIM = { 0x245, 0x545, 0x645 };  // CIM
```

OpenSAAB bench captures show Tech2Win sending SecurityAccess and
identification reads to addresses in the `$024X` range; the specific
routing (which physical module answers, which gateway proxies) is an
operational detail captured in the per-command YAMLs and is not
asserted here as canonical.
