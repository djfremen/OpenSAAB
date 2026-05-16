# Adapter coverage matrix

**Purpose:** track which OBD/diagnostic USB adapters the OpenSAAB pipeline can ingest from, which standardized APIs each adapter implements, and what shim/decoder work each one needs.

The strategic insight that shapes this table: **J2534 and D-PDU (ISO 22900-2) are standardized APIs**. One shim per *API* covers every adapter that implements it. We do not need a separate shim per physical adapter — we need a separate shim per *DLL surface* (proprietary or standard) that real client applications load.

## Current matrix (2026-05-15)

| Adapter | Native API surface(s) | Required shim(s) | Existing shim status | Captures |
|---|---|---|---|---|
| **Chipsoft Pro** | D-PDU-flavored via `CSTech2Win.dll` (Tech2Win-only proprietary), J2534 via `j2534_interface.dll` | Both | ✅ CSTech2Win shim built, ✅ j2534 shim built | 184 cstech2win, 3 usbpcap |
| **GM MDI** (ordered, in transit) | D-PDU via `mdi_api.dll` (canonical), J2534 backwards-compat | D-PDU shim (new) **or** existing j2534 shim if client supports it | ⚪ D-PDU shim scaffold in progress (`Chipsoft_RE/shim/dpdu/`); j2534 shim should work out-of-box for J2534 clients | 0 |
| **VX Nano / Bosch MDI 2** (ordered, in transit) | J2534 via `vxnano32.dll` (proprietary DLL name, **standard J2534 API underneath**) | Existing j2534 shim | ✅ j2534 shim should drop in unmodified | 0 |
| **OBDLink MX+ / SX** | ELM327 ASCII + J2534 driver | j2534 shim handles J2534 mode; ELM ASCII is a separate decoder (out of scope short term) | ⚪ Not prioritized | 0 |
| **DrewTech / Tactrix Openport / etc.** | J2534 (per-vendor DLL) | j2534 shim | ⚪ Not validated yet | 0 |

## Standardized APIs we shim

### J2534 (SAE J2534, "PassThru" API)

Standard API surface every J2534-compliant adapter must implement. Functions: `PassThruOpen`, `PassThruClose`, `PassThruConnect`, `PassThruDisconnect`, `PassThruReadMsgs`, `PassThruWriteMsgs`, `PassThruStartPeriodicMsg`, `PassThruStopPeriodicMsg`, `PassThruStartMsgFilter`, `PassThruStopMsgFilter`, `PassThruSetProgrammingVoltage`, `PassThruReadVersion`, `PassThruGetLastError`, `PassThruIoctl`.

Each adapter ships its OWN DLL implementing this surface (Chipsoft = `j2534_interface.dll`, MDI = `MDIPT32.dll`, VX Nano = `vxnano32.dll`, Tactrix = `Op20pt32.dll`, etc.). Our j2534 shim sits between any J2534 client (TrionicCANFlasher, ScanXL, GDS2-via-J2534, etc.) and the real DLL — same shim binary regardless of which adapter is on the USB bus.

### D-PDU (ISO 22900-2)

Standard "diagnostic protocol data unit" API used by GM (GDS2 native mode, Tech2Win on MDI/Chipsoft), Bosch ESI[tronic], and others. Functions: `PDUConstruct`, `PDUDestruct`, `PDUCreateModuleData`, `PDUDestroyModuleData`, `PDURegisterEventCallback`, `PDUStartComPrimitive`, `PDUCancelComPrimitive`, `PDUGetEventItem`, `PDUDestroyItem`, `PDUIoCtl`, `PDUGetLastError`, etc.

CSTech2Win.dll is Chipsoft's D-PDU-style DLL but with proprietary extensions, so our CSTech2Win shim is **specific to that DLL**, not generic D-PDU. The new D-PDU shim under construction will target the standard ISO22900 export table so it can drop into MDI (`mdi_api.dll`), Vetronix VX Tech 2 Flash, and other ISO22900-compliant adapters with one binary.

## Shim build process (template)

Same shape for every new shim, codified by the CSTech2Win and j2534 shims already in `Chipsoft_RE/shim/`:

1. **Identify the target DLL** — what does the real client application load? Run `Procmon` or `tasklist /m` against the client to find every loaded DLL containing the adapter's PnP signatures.
2. **Dump the export table** — `dumpbin /exports <target>.dll` → list of function names + ordinals.
3. **Generate trampolines** — one C function per export, signature lifted from the published API spec (J2534 SAE doc, ISO 22900-2 spec, or RE'd from public headers). Each trampoline logs `CALL func(args)` then forwards to the real DLL, then logs `RET func err=<rc>`.
4. **Build** — CMake or MSBuild, /MT static C runtime, /target:x86 or x64 depending on the client. Output goes alongside the original DLL.
5. **Install** — installer (Inno) renames the real DLL to `<dll>_real.dll`, drops our shim with the original name. On uninstall, restore.
6. **Test** — run the client, perform a known-good action, verify shim log file in `%TEMP%` shows the expected call sequence.

The OpenSAAB Collector installer already handles steps 5-6 generically — adding a new shim is a matter of writing the C source and chaining its build into the installer's `[Files]` section.

## Per-adapter open work

### GM MDI (D-PDU shim)

- [ ] Dump exports from a sample `mdi_api.dll` (ISO22900-2 compliant; GM publishes a header)
- [ ] Generate `dpdu_shim.c` with the canonical 28-function ISO22900 export table
- [ ] Build script in `Chipsoft_RE/shim/dpdu/` (mirror CSTech2Win's CMake)
- [ ] Decide install path — MDI installs to `%ProgramFiles%\General Motors\MDI`; installer needs an additional path-detect branch
- [ ] First capture target: GDS2 startup + Module Identification

### VX Nano

- [ ] Plug in, install Bosch-provided J2534 driver, find the DLL name
- [ ] Install the existing j2534 shim renamed to match VX Nano's DLL
- [ ] Run TrionicCANFlasher (or another J2534 client) against the SAAB bus, verify shim log captures the expected call sequence
- [ ] If shim works as-is: zero new code required. Log it and move on.

### Cross-adapter comparison

Once two or more adapters are capturing, run the same Tech2-style action through each, diff the resulting shim logs. Anything identical at the J2534 / D-PDU layer is **standard** (and our protocol catalogue can rely on it). Anything that differs is **adapter-specific** and gets documented per-adapter.

## API capacity for the projected load

Current Koyeb deployment: **free tier, single instance, ~256 MB RAM, ~0.1 vCPU shared, sleeps after 65 min idle.** R2 storage: 10 GB free, $0.015/GB after. Synchronous `/ingest` parsing on the request thread.

Projected steady state with multi-adapter community capture:

| Scenario | Captures/week | Bandwidth/month | CPU/month | R2 cost/month |
|---|---|---|---|---|
| Today (1 contributor, Chipsoft only) | ~50 (rolling) | < 0.5 GB | negligible | 0 (under 10 GB free) |
| 10 contributors × 3 adapters × 5 sessions/wk | ~1500 / wk | ~10-15 GB | ~30 min CPU | 0 |
| 100 contributors × same cadence | ~15,000 / wk | ~100-150 GB | ~5 hr CPU | $1-2 / mo |

**Bottlenecks before bandwidth:**

1. **Sync pcap parsing on the request thread.** Each USBPcap upload calls `_summarize_usbpcap_bytes` which walks the file in pure Python. On free-tier shared CPU, a 10 MB pcap takes ~1-2 s. Concurrent uploads will queue and a burst can starve the FastAPI worker.  
   **Mitigation:** move pcap summary to a background task (FastAPI `BackgroundTasks` or a queue) so `/ingest` returns immediately on successful body receive; summary backfills the sidecar async.
2. **Memory ceiling on free tier.** Reading a 50 MB pcap into bytes uses ~50 MB resident — fine alone, problematic if 4 uploads land simultaneously on a 256 MB instance.  
   **Mitigation:** streaming gunzip + pcap walk (no full file in memory). Code change scoped to `decoder/usbpcap_summary.py`.
3. **Cold starts after idle sleep.** First request after 65 min idle takes 10-30 s while Koyeb wakes the container. Annoying for users hitting the dashboard; harmless for Collector uploads (it retries with exp-backoff).  
   **Mitigation:** set `min instances: 1` ($5/mo) once we have >5 contributors.

**Triage when to upgrade:**

- < 20 active contributors → stay on free tier
- 20-50 contributors → bump to `nano` ($5/mo), `min: 1` (no cold-start)
- 50+ contributors → consider 2× instances behind Koyeb's autoscaler ($10-15/mo)

**Hard limits we're nowhere near:**

- R2 free tier: 10 GB storage, 10M Class-A ops/mo. Today's 250 MB is 2.5% of free quota.
- Koyeb free egress: 100 GB/mo. At 1500 captures × 2 MB = 3 GB/mo, we're at 3%.

Net: API can handle 10×-100× current volume on the current tier with the two `BackgroundTasks` + streaming-parse code changes. Beyond that the cost ramp is `nano` tier + R2 paid storage, both negligible.
