# Command catalog

Each YAML in `commands/<vehicle>/<action>.yaml` names a single observable
Tech2 menu action and the bytes it produces on the bus. The schema is
deliberately small so the catalog stays human-editable.

## Schema

```yaml
menu:           # the Tech2Win menu path that triggers this command
                # e.g. "Diagnostic → Get ECM Information → CIM Info"
target_ecu:     # CAN ID pair: "$0241/$0641" means TX on 0x241, RX on 0x641
captured_from:  # path to shim log + timestamp range, for traceability
status:         # "captured" / "spec-only" / "deprecated"
services: []    # UDS service IDs invoked: [0x1A, 0x27, ...]

# For ReadDataByIdentifier ($1A) commands: list each DID seen
dids:
  0xC2:
    name: human_readable_name
    example: "00 c3 53 f3"           # raw bytes after SID+DID
    interpretation: optional decode  # if known
  0xC3:
    name: ...
    example_nrc: 0x22                # if it returned 7F 1A 22 (NRC) instead

# For multi-step flows (e.g. SecurityAccess): list each step
steps:
  - tx:     [0x27, 0x0B]
    rx_pos: [0x67, 0x0B, "SEED_HI", "SEED_LO"]
    rx_nrc: { 0x37: "RequiredTimeDelayNotExpired", 0x78: "ResponsePending" }
  - compute:
      input:  rx_step_0.SEED
      algo:   "saab_ska"
      output: KEY
  - tx:     [0x27, 0x0C, "KEY_HI", "KEY_LO"]
    rx_pos: [0x67, 0x0C]
    rx_nrc: { 0x35: "invalidKey" }

notes: |
  Free-form context, gotchas, known-quirks.
```

## Naming convention

`<verb>_<subject>` in `snake_case`. Examples:
- `cim_info_read`
- `engine_sas_unlock`
- `vin_read_obd`
- `dtc_clear`
- `programming_session_enter`

## What each entry MUST contain

- `menu` and `target_ecu` (so a tool can reproduce the action)
- `services` (so a tool can filter / pick a transport)
- At least one example TX/RX pair (so it's testable)

## What each entry SHOULD contain

- `captured_from` — bench-session traceability
- `notes` — known NRC patterns, timing quirks, vehicle profile dependencies

## Vendor-neutral DIDs

When a DID's meaning is known across multiple GM/SAAB platforms,
document it in `../protocol/dids.md` and reference by name from each
command entry, e.g. `name: ECU_SoftwarePartNumber`.
