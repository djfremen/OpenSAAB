# GMLAN 11-bit Arbitration IDs

Standard GM Local Area Network 11-bit CAN IDs used by GM and SAAB vehicles
~2007+. Map below is sourced from Jason Gaunt's 2013 `GMLAN_11bit.h` library
([Afterglow/arduino-gmlan](https://github.com/Afterglow/arduino-gmlan),
[maxpfeif/GMLAN](https://github.com/maxpfeif/GMLAN),
[mattatcha/gmlan](https://github.com/mattatcha/gmlan) — all derivative of
the same Jason Gaunt original, Apache 2.0).

## Broadcast / wake-up

| CAN ID | Name | Use |
|---|---|---|
| `0x100` | InitialWakeUpRequest | First frame on the bus to start a session |
| `0x101` | RequestToAllNodes | Functional broadcast (TesterPresent, mass DID reads) |
| `0x102` | DiagnosticRequest | Older diag broadcast |

## Per-ECU diagnostic requests (Tester → ECU)

| CAN ID | Module | Notes |
|---|---|---|
| `0x240` | ReservedRequest | |
| `0x241` | BCM (stock GM) / **engine + CIM diag gateway** on SAAB 9-3 | See platform notes |
| `0x242` | TDM (Transmission Diagnostic Module) | |
| `0x243` | EBCM (Electronic Brake Control Module / ABS) | |
| `0x244` | EHU (Entertainment / Head Unit) | |
| `0x246` | SIC (Steering / Inflatable Restraint Controller) | |
| `0x247` | SDC | |
| `0x248` | (varies by platform) | |
| `0x24A` | (varies) | |
| `0x24B` | (varies) | |
| `0x24C` | IPC (Instrument Panel Cluster) | |
| `0x251` | HVAC | |
| `0x257` | (varies) | |
| `0x258` | RFA (Remote Function Actuator / keyless) | |

## Per-ECU diagnostic responses (ECU → Tester)

Single-frame responses use `0x540 + ECU_offset`; multi-frame responses use
`0x640 + ECU_offset`.

| CAN ID range | Use |
|---|---|
| `0x540 - 0x55F` | Single-frame responses (1-byte PCI, ≤7 bytes data) |
| `0x640 - 0x65F` | Multi-frame responses (ISO-TP First-Frame / Consecutive-Frame) |

Example pairs:
- `0x241` (TX) ↔ `0x541` (RX SF) / `0x641` (RX MF)
- `0x244` (TX) ↔ `0x544` (RX SF) / `0x644` (RX MF)

## OBD-II compliance addresses

| CAN ID | Use |
|---|---|
| `0x7DF` | OBD-II functional request (broadcast to all OBD-II ECUs) |
| `0x7E0` | OBD-II physical to ECM |
| `0x7E1` | OBD-II physical to TCM |
| `0x7E8` | OBD-II physical from ECM |
| `0x7E9` | OBD-II physical from TCM |

## Platform notes

**SAAB 9-3 (2003-2011, T8/E78/ME9.6):** `0x241/0x641` is the diag entry
point for the engine ECM AND for CIM-related identification fields. The
labeling differs from stock GM because SAAB's body/engine diag gateway
is consolidated.

**SAAB 9-5 (T7/T8 platforms):** uses the same `0x241/0x641` for engine
on the older T7. T8/T8.5 platforms vary.

Most SAAB SecurityAccess (UDS `$27 0B` SAS) is on `0x241`. Other ECUs
(transmission, ABS) use the standard `$27 01` on their own diag pair.
