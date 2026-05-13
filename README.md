# OpenSAAB

Open-protocol reference for SAAB GMLAN/UDS diagnostic communication: a labeled
command catalog, the protocol primitives behind it, and the tools to grow the
catalog from real bench captures.

> Not affiliated with SAAB, GM, or Tech2Win. All entries are derived from
> non-destructive observation of dealer-tool traffic against owner-operated
> vehicles. See `LICENSE` (Apache 2.0).

## What's here

```
commands/   Catalog of named Tech2 operations: each YAML names a menu path,
            the target ECU, the UDS service IDs it uses, and the expected
            response shape. Drop-in playbook for any client that talks GMLAN.

protocol/   Vendor-neutral protocol references — 11-bit and 29-bit GMLAN ID
            maps, UDS service-ID table, NRC table, baud rates, SAAB-specific
            extensions like the 0xFE functional-broadcast prefix.

workflows/  operator_api-format JSON workflows. Same data as commands/ but in
            a machine-driveable state-machine schema. Auto-generated from
            commands/<name>.yaml + a bench capture; do not hand-edit.

tools/      Small scripts that don't depend on copyleft libraries.

docs/       Bench capture workflow, vehicle profiles, glossary.
```

## Editorial principle

`protocol/` describes **canonical sources** with citations (Jason Gaunt
2013, Trionic, GMW3110, etc.). `commands/` describes **bench
observations** — what bytes flowed when. We don't editorially bridge the
two: if a bench observation suggests routing or aliasing not in any
canonical source, that goes in the relevant `commands/` entry as an
open question, not smuggled into the protocol reference. See
[`docs/feedback_bojer_2026-05-12.md`](docs/feedback_bojer_2026-05-12.md)
for what prompted this.

Architecturally, the design direction is a transport-abstracted GMLAN
library — the protocol layer should not care whether bytes flow over
slcan, J2534, Chipsoft USB, or anything else. Per Bojer's framing:
*"With gmlan you will get to see whats going on."*

## What's NOT here

By design, this repo doesn't ship:
- Reverse-engineered cryptographic engines (SAAB seed/key NativeVM tables) —
  copyright-encumbered, kept private.
- Captured shim logs containing customer VINs.
- Proprietary scan-tool DLLs, J2534 vendor SDKs, or anything you can't
  legally redistribute.
- GPL-licensed code (scapy etc.) — kept out so this repo stays usable for
  both open-source and proprietary downstream projects.

If you need the seed/key engine, you have to RE it yourself (`dllsecurity.dll`
documentation is available elsewhere) or use Bojer's hosted service.

## Currently catalogued

| Entry | Status |
|---|---|
| `commands/saab/cim_info_read.yaml` | captured (9 ECU identification DIDs) |
| `commands/saab/security_access_sweep_l01.yaml` | captured (9-ECU SKA tuple harvest, full canonical slot order) |
| `commands/saab/security_access_l01_unlock.yaml` | captured (full seed/key/ack cycle for 5 ECUs — body-module unlock) |
| `commands/saab/engine_sas_unlock.yaml` | captured to seed; send-key bench-validated externally |
| `commands/saab/engine_program_unlock_fd.yaml` | spec-only, Trionic-cited (level $FD for engine flashing) |
| `commands/saab/module_pair_write.yaml` | captured (4-DID write of VIN + security-code prefix per module) |
| `commands/saab/vin_read_did_3f.yaml` | captured (SAAB-extended VIN read on engine-diag gateway) |
| `commands/saab/check_ignition_key_status.yaml` | captured (DeviceControl + DPID 0x0B read; bit layout TBD) |
| `workflows/saab/body_module_add.yaml` | end-to-end: unlock + pair-write loop for 5 ECUs (level $01, works offline) |
| `workflows/saab/door_module_add_prerequisites.yaml` | end-to-end chain (1→7) for the SecurityAccess preflight that body-module operations require |

**SAAB has four documented SecurityAccess levels** (see [`docs/audit_trionic_2026-05-12.md`](docs/audit_trionic_2026-05-12.md) for cross-validation against Trionic):

| Level | Send-key | Purpose | Algorithm source |
|---|---|---|---|
| `$01` | `$02` | Body-module unlock (door, IPC, RFA, transmission) | NativeVM, per-ECU |
| `$0B` | `$0C` | SAAB SAS / IMMO-specific (Tech2Win-only path) | Private NativeVM tape |
| `$FB` | `$FC` | Mid-tier engine access | Hardcoded formula (Trionic) |
| `$FD` | `$FE` | Engine reprogramming / flashing | Hardcoded formula (Trionic) |

Engine ECU operations split: SAS/IMMO uses `$0B` at SAAB-manufacturer alias `$0241`; engine flashing uses `$FD` at OBD-II `$7E0`.

## Quick start — read a captured command

```yaml
# commands/saab/cim_info_read.yaml — excerpt
menu: "Diagnostic → Get ECM Information → CIM Info"
target_ecu: $0241/$0641
service: 0x1A  # ReadDataByIdentifier
dids:
  0xC2: { name: "boot_software_version", example: "00 c3 53 f3" }
  0xD2: { name: "field_d2",             example: "41 42" }
  0x9A: { name: "sas_algo_tape_head",   example: "03 04" }
```

## Contributing a new command

1. Run Tech2Win (or any J2534 dealer tool) on the bench with the
   CSTech2Win shim attached. Click ONE menu, then stop.
2. Pull the shim log: `cstech2win_shim_<timestamp>.log` from
   `%TEMP%`.
3. Run `tools/shim_log_decode.py` against it.
4. Write `commands/saab/<your_action>.yaml` with the menu path, ECU
   address, service IDs you saw, and a sample TX/RX pair.
5. PR with the YAML + a short note in `docs/`. Do NOT include the raw
   shim log if it contains a customer VIN — redact or skip.

## License

Apache 2.0 — see `LICENSE`.
