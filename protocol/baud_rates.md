# GMLAN baud rates

Constants from `mattatcha/gmlan` (derived from Jason Gaunt 2013), matching
J2534 dealer-tool configurations.

| Constant | Value (bit/s) | Use |
|---|---|---|
| `GMLAN_BAUD_LS_NORMAL` | 33,333 | Single-wire CAN (SWCAN), body bus, normal mode. Pin 1 only. |
| `GMLAN_BAUD_LS_FAST` | 83,333 | Single-wire CAN, download / programming mode (per the GMLAN library; specific SAAB usage not documented here — needs citation if claimed). |
| `GMLAN_BAUD_MS` | 95,200 | Mid-speed CAN. |
| `GMLAN_BAUD_HS` | 500,000 | High-speed dual-wire CAN. Pins 6 + 14. OBD-II + many manufacturer-specific diagnostic addresses. |

## Bench observation note

Bench captures on a SAAB 9-3 (2003-2011 era) show Tech2Win using HS-CAN
500 kbps on pins 6 + 14 to reach diagnostic addresses in the `$024X`
range. SWCAN at 33 kbps pin 1 does NOT carry traffic to those addresses
in our captures — connecting on the wrong bus produces silent timeouts.

This is an empirical observation from `cstech2win_shim_*` captures, not
a claim about which physical module any specific address routes to.
For module → address mapping see `gmlan_11bit_ids.md` and the relevant
entries under `commands/`.
