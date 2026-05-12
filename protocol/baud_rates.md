# GMLAN baud rates

Constants from the GM-spec layer. Match the values in J2534 dealer-tool
configurations and SAAB Tech2/web-client code. Verified against
`mattatcha/gmlan` and bench captures.

| Constant | Value (bit/s) | Use |
|---|---|---|
| `GMLAN_BAUD_LS_NORMAL` | 33,333 | Single-wire CAN (SWCAN), body bus, normal mode. Pin 1 only. |
| `GMLAN_BAUD_LS_FAST` | 83,333 | Single-wire CAN, download / programming mode. Same constant used by the SAAB web client (`sas.mysaab.info/commands.js`). |
| `GMLAN_BAUD_MS` | 95,200 | Mid-speed CAN (less common on SAAB). |
| `GMLAN_BAUD_HS` | 500,000 | High-speed dual-wire CAN. Pins 6 + 14. Engine ECM, transmission, ABS, OBD-II. |

## Which bus is the engine ECM on?

**SAAB 9-3 (2003-2011): HS-CAN 500k, pins 6 + 14.** Address `$0241/$0641`.
SWCAN at 33k on pin 1 is the body bus — engine ECM does NOT live there.

A common debugging trap: connect on SWCAN 33k pin 1 and wonder why
`$27 0B` to `$0241` is silent. The bus you're talking on doesn't reach
the engine ECM. Switch to HSCAN 500k pins 6/14 and the response appears.
