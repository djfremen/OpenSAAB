# Feedback from Michał Bojarski (Bojer), 2026-05-12

Bojer is the operator of [sas.mysaab.info](https://sas.mysaab.info) and has
been working with SAAB GMLAN / SAS for many years. After the initial
OpenSAAB push he reviewed the protocol docs and pointed out three
specific errors plus structural advice. This page records the feedback
verbatim (paraphrased to respect the Messenger context) and the
corrections applied.

## Three concrete errors he flagged

### 1. `baud_rates.md` — fabricated SAAB-web-client claim and wrong URL

We had written:
> `GMLAN_BAUD_LS_FAST  | 83,333  | … Same constant used by the SAAB web
> client (`sas.mysaab.info/commands.js`).`

His critique:
> *"Address wrong and even if you look at correct one:
> https://sas.mysaab.info/js/commands.js — this does not make sense."*

Verification: the local `commands.js` source we have under
`wiki/sources/` has **no occurrence of `83333`**. The connection between
the GMLAN `LS_FAST` constant and the SAAB web client was an
unsupported inference. The URL `sas.mysaab.info/commands.js` was also
wrong — the actual path is `/js/commands.js`.

**Fix applied:** removed the SAAB-web-client claim and the bad URL from
`protocol/baud_rates.md`. The 83,333 entry now reads only what
`mattatcha/gmlan` actually documents: a single-wire CAN download-mode
constant. SAAB-specific usage requires its own citation if asserted.

### 2. `protocol/gmlan_11bit_ids.md` — "$0241 = engine ECM" is wrong

We had written:
> `0x241  |  BCM (stock GM) / **engine + CIM diag gateway** on SAAB 9-3`

His critique:
> *"Here you identify 241 as ecm."*
> *"Here you mix everything up."*

Verification: the Jason Gaunt 2013 canonical label is simply `TO_BCM`
(Body Control Module). Our editorial extension "engine + CIM diag
gateway on SAAB 9-3" was an unsupported inference based on bench
captures — Tech2Win uses `$0241` for several operations, but that does
not establish what physical module sits at that address.

**Fix applied:** stripped editorial from the canonical table.
`gmlan_11bit_ids.md` now lists only the Jason Gaunt 2013 names without
SAAB-specific interpretation. Added a "don't conflate canonical labels
with SAAB observations" caveat. SAAB-specific bench observations were
removed from `protocol/` and live only in `commands/` going forward.

### 3. Bojer-API mentions in OpenSAAB

His statement, separately:
> *"my api has nothing to do with gmlan/can. It only provides keys
> based on seeds."*

Verification: every `Bojer` mention in OpenSAAB describes his service
correctly — as a seed → key oracle. Specifically:
- `engine_sas_unlock.yaml`: "validated 9/9 against Bojer roundtrip"
  (seed→key cross-check, correct).
- `security_access_sweep_l01.yaml`: "Bojer fills these slots into the
  SSA post-auth blob" (correct — his API returns filled SSA tuples).
- `audit_trionic_2026-05-12.md`: "matches Bojer 9/9" (seed→key).
- `README.md`: "use Bojer's hosted service" (in the "if you need the
  seed/key engine" section, correct).

**Fix applied:** none required; existing mentions accurately describe
the API surface. Keeping them as-is.

## Strategic direction he gave

> *"Start small — send messages using Chipsoft DLL — log everything —
> start building command list. Start building gmlan lib. With modularity
> in mind. So you can swap later slcan to another implementation (like
> j2534). With gmlan you will get to see whats going on."*

This validates the direction OpenSAAB is already heading but emphasizes
a clean transport-abstracted GMLAN library. Recorded in the project
roadmap; future entries should keep transport (slcan / J2534 /
chipsoft USB) separable from the GMLAN protocol layer.

## Editorial principle going forward

`protocol/` files describe **canonical sources** — Jason Gaunt 2013,
Trionic, GMW3110, published standards. Each claim cites a source.

`commands/` files describe **bench observations** — what specific bytes
flowed on specific addresses during specific Tech2Win actions. These
don't claim canonical identity; they record what happened.

No editorial bridging between the two layers in `protocol/`. If a bench
observation suggests a routing or aliasing not in any canonical source,
flag it as an open question in the relevant `commands/` entry rather
than smuggling it into the protocol reference.

## Attribution

Thanks to Bojer for the direct review. Errors above were ours;
corrections applied promptly.
