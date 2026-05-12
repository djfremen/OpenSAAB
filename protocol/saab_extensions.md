# SAAB-specific GMLAN extensions

SAAB extends standard GMLAN with at least one wire-level pattern not
documented in the public GMW3110-2010 spec or the Jason Gaunt
`GMLAN_11bit.h` library. This page collects them.

## The `0xFE` functional broadcast prefix

**Pattern:** every SAAB Tech2 broadcast on `$0101` starts with the byte
`0xFE`, followed by the actual UDS service ID, followed by the standard
sub-function and data bytes.

```
TX $0101  FE 3E         → functional broadcast TesterPresent
TX $0101  FE 01 3E      → functional broadcast SecurityAccess level $01 (start of ECU sweep)
TX $0101  FE 1A 9A      → functional broadcast ReadDataByIdentifier DID 0x9A
TX $0101  FE 1A 90      → functional broadcast ReadDataByIdentifier DID 0x90 (VIN)
```

### What `0xFE` is

A SAAB-specific framing byte that means "this is a functional broadcast to
all ECUs on the bus, not a physically-addressed request". It's separate
from the ISO-TP PCI byte (which would normally be `0x0L` for a single-frame
of length L) — `0xFE` replaces the PCI for these broadcasts.

### How clients see it

Scapy's GMLAN dissector does NOT know about `0xFE` and parses the frame
as a generic "GMLAN" packet without a service layer. Custom decoders
should strip the `0xFE` prefix when present on `$0101` and dissect the
remaining bytes as a normal UDS request.

### Statistics

In OpenSAAB bench captures so far (5 shim logs, 476 frames):
- `0xFE` accounts for **123 frames** — the most-sent service prefix in the
  entire dataset, dwarfing every actual UDS SID.
- All 123 are on `$0101`. No `0xFE` frames on physical addresses.
- The most common payload is `FE 01 3E` (functional TesterPresent),
  fired in pairs every ~2 seconds when the session is idle.

## Mid-cycle TesterPresent cadence

Standard UDS spec says P3C (session timeout) is implementation-defined,
typically 5-10 seconds. SAAB Tech2 sends TesterPresent **every 2-2.5s
in pairs** (two frames ~80ms apart, then ~2.4s gap, then two more).
The reason for paired emission isn't documented but matches behavior of
all bench captures.

When idle in a connected session, this is the dominant traffic on the
bus. Any wire emulator that wants to act like Tech2 must reproduce this
cadence or the ECU will P3C-timeout the session.

## ResponsePending (`7F xx 78`) tolerance

Standard NRC. Worth flagging here because SAAB-specific flows emit it
heavily — the SAS unlock path (`$27 0B`) typically returns `7F 27 78`
once before the actual seed arrives ~150-200ms later. Implementations
that don't tolerate `0x78` will give up before the seed lands.

The Bojer-via-HTTP path doesn't see this because the round-trip is
mediated by their server; the bench Tech2 path always sees it.
