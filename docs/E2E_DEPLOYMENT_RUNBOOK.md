# ProofHalt Stage 9 — Exact Deployment & End-to-End Test Runbook

**Status:** deployment procedure frozen; actual live deployment is intentionally deferred until the Solidity compile gate and GenVM semantic-lint gate pass.

## 0. Network and evidence rules

Use the same test environment for the integrated demo:

- GenLayer network: **Testnet Bradbury**
- GenLayer RPC: `https://rpc-bradbury.genlayer.com`
- GenLayer Chain / EVM RPC: `https://rpc.testnet-chain.genlayer.com`
- EVM chain ID: **4221**
- Native test currency: **GEN**

ProofHalt external EVM actions are not considered executed when a GenLayer transaction is merely accepted. The demo must wait for **FINALIZED** before expecting Guardian `pauseFromProofHalt` or `restoreFromProofHalt` to execute.

### Evidence rule — do not fake independence

A HALT and a RESTORE each require at least **two independent evidence-origin groups**, including a strong technical anchor. Two mirrors, screenshots, or GitHub copies of the same underlying claim are **one origin**, not two.

For every evidence record:

- `source_url` = the constitution-approved explorer/monitor/research artifact URL.
- `snapshot_uri` = exactly `source_url`, or a `raw.githubusercontent.com` URL naming the same repository, file path and exact 40-hex commit as an approved GitHub blob URL.
- `content_hash` = SHA-256 of the exact bytes returned by that contract-bound artifact.

Do not pair an approved source page with a separately hosted claimant snapshot; the contract rejects that mismatch. Prefer a source-native stable JSON/text artifact at the approved origin. For GitHub, pin the blob and raw URLs to the same commit. `generate_evidence_snapshot.py` creates canonical bytes and a hash, but the result counts only after the artifact is published at a constitution-approved source and does **not** make the source independent.

---

## 1. Pre-deployment gates

Do not deploy until all are true:

1. `proofhalt.py` passes the official GenVM linter / semantic validation.
2. `ProofHaltGuardian.sol` and `DemoVault.sol` compile with **solc 0.8.36** with zero severity `error` diagnostics.
3. `verify_solc_output.py` passes.
4. All offline suites pass: 28 ProofHalt regression + 21 Guardian/Vault model + 6 cross-layer overlap + 9 exploit/patch lifecycle = **64/64**.
5. Source hashes match `SHA256SUMS_STAGE9.txt`.

### Exact Solidity compile

From `proofhalt_stage9/` with solc 0.8.36 installed:

```bash
./compile_with_solc.sh
```

The script runs the pinned Standard JSON input and then `verify_solc_output.py`.

---

## 2. Deploy ProofHalt Intelligent Contract first

Deploy the Stage 9 `proofhalt.py` to **Testnet Bradbury**, not a local-only simulation.

Record:

- ProofHalt IC address: `PROOFHALT_IC`
- deployment transaction hash
- finalized status
- source SHA-256

The EVM ghost contract uses the **same address** as the GenLayer Intelligent Contract, so `PROOFHALT_IC` is the value passed into the Guardian constructor.

**Do not continue until the ProofHalt deployment is FINALIZED.**

---

## 3. Deploy DemoVault on GenLayer Chain

Compile with the Stage 9 settings:

- solc: `0.8.36`
- EVM target: `paris`
- optimizer: enabled, 200 runs
- via IR: false

Deploy `DemoVault.sol:DemoVault` to chain ID 4221.

Record:

- `DEMOVAULT`
- deployment transaction hash

Immediately verify:

```text
configurationAuthority() == deployment wallet
demoExploitEnabled() == true
paused() == false
isProofHaltConfigured() == false
DEMO_MAX_EXPLOIT_PER_CALL() == 1000000000000
```

This vault is deliberately **testnet-only** and contains a bounded demo exploit. Never fund it with valuable assets.

---

## 4. Deploy ProofHaltGuardian

Deploy `ProofHaltGuardian.sol:ProofHaltGuardian` with constructor arguments:

```text
proofHaltAuthority_ = PROOFHALT_IC
protectedTarget_    = DEMOVAULT
```

Record Guardian address as `GUARDIAN` and its deployment transaction.

Verify:

```text
proofHaltAuthority() == PROOFHALT_IC
protectedTarget() == DEMOVAULT
activeHaltCount() == 0
isPaused() == false
```

---

## 5. Permanently bind DemoVault to Guardian

From the DemoVault deployment wallet, call exactly once:

```text
DemoVault.configureProofHaltGuardian(GUARDIAN)
```

Verify after the transaction:

```text
proofHaltGuardian() == GUARDIAN
isProofHaltConfigured() == true
configurationAuthority() == 0x0000000000000000000000000000000000000000
Guardian.proofHaltAuthority() == PROOFHALT_IC
Guardian.protectedTarget() == DEMOVAULT
Guardian.activeHaltCount() == 0
Guardian.isPaused() == false
```

The zeroed `configurationAuthority` proves the temporary setup privilege is gone.

---

## 6. Generate the live Security Constitution

Do **not** reuse the old placeholder constitution.

Run:

```bash
python tools/generate_demo_constitution.py \
  --target DEMOVAULT \
  --protocol-id proofhalt-demovault-v1 \
  --out demo_constitution_live.json
```

The script prints `sha256=...`. Preserve:

```text
PROTOCOL_ID = proofhalt-demovault-v1
CONSTITUTION_HASH = printed SHA-256
CONSTITUTION_TEXT = exact file contents, no edits
CONSTITUTION_URI = stable public URL serving those exact bytes
```

Before registration, independently verify:

```bash
sha256sum demo_constitution_live.json
```

It must equal `CONSTITUTION_HASH`.

---

## 7. Register and activate the protocol in ProofHalt

Call:

```text
register_protocol(
  protocol_id="proofhalt-demovault-v1",
  target_contract=DEMOVAULT,
  guardian_adapter=GUARDIAN,
  metadata_uri=<public project/demo metadata URL>,
  initial_constitution_text=<exact canonical demo_constitution_live.json text>,
  initial_constitution_hash=CONSTITUTION_HASH,
  initial_constitution_uri=CONSTITUTION_URI
)
```

Expected status:

```text
INTEGRATION_PENDING = 1
```

Then call:

```text
activate_protocol("proofhalt-demovault-v1")
```

ProofHalt must verify the Guardian authority, target, target binding, `activeHaltCount == 0`, and unpaused state.

Expected status:

```text
PROTECTED = 2
```

Only now should the frontend/demo claim **Protected by ProofHalt**.

---

## 8. Create a real bounded exploit transaction

Use two different test wallets:

- Account A = victim
- Account B = attacker

### 8.1 Victim funds DemoVault

Account A calls `deposit()` with exactly:

```text
0.000003 GEN
= 3,000,000,000,000 wei
```

Verify:

```text
balanceOf(AccountA) == 3000000000000
totalManagedAssets() == 3000000000000
```

Record the deposit transaction.

### 8.2 Attacker executes the deliberate demo exploit

Account B calls:

```text
demoExploitWithdrawFrom(
  AccountA,
  1000000000000
)
```

This is the maximum bounded demo exploit amount: `0.000001 GEN`.

Verify:

```text
DemoExploitExecuted event emitted
balanceOf(AccountA) == 2000000000000
totalManagedAssets() == 2000000000000
Account B received the withdrawn test GEN
```

Record the exploit transaction hash as `EXPLOIT_TX`.

This is the genuine technical event used by the demo. Do not substitute a fake claim.

---

## 9. Prepare two genuinely independent incident evidence records

At minimum, prepare:

### Evidence A — technical anchor

Origin example: GenLayer Chain explorer/onchain transaction record for `EXPLOIT_TX`.

Snapshot should include:

```text
chain_id = 4221
target_contract = DEMOVAULT
transaction_hash = EXPLOIT_TX
victim = Account A
attacker = Account B
amount_wei = 1000000000000
victim_balance_before = 3000000000000
victim_balance_after = 2000000000000
DemoExploitExecuted event details
origin explorer URL
```

Create canonical bytes with `generate_evidence_snapshot.py`, publish them unchanged, and preserve the hash.

### Evidence B — independent corroboration

Use a **genuinely separate origin** such as an independently operated monitor/security observer that derives and publishes its own observation of the transaction/state change. It must not simply copy Evidence A.

If no independent second origin is available yet, **stop here**. The correct ProofHalt result is not HALT because the Global Constitution requires two independent groups. Do not fabricate a second group for the demo.

---

## 10. Open the incident and submit evidence

Call:

```text
open_incident(
  "proofhalt-demovault-v1",
  "Unauthorized bounded withdrawal from another account was executed through the registered DemoVault testnet exploit path."
)
```

Record returned incident ID as `INCIDENT_ID` (expected form `PH-000001`).

Submit technical evidence:

```text
submit_evidence(
  incident_id=INCIDENT_ID,
  origin_id=<constitution-approved technical origin ID>,
  source_url=<approved technical artifact URL>,
  snapshot_uri=<same URL or matching commit-pinned GitHub raw URL>,
  content_hash=<Evidence A SHA-256>,
  phase=0,                 # ORIGINAL
  note="Bounded unauthorized withdrawal transaction and state-change evidence."
)
```

Submit independent corroboration:

```text
submit_evidence(
  incident_id=INCIDENT_ID,
  origin_id=<constitution-approved independent origin ID>,
  source_url=<independent origin URL>,
  snapshot_uri=<same URL or matching commit-pinned GitHub raw URL>,
  content_hash=<Evidence B SHA-256>,
  phase=1,                 # SUPPORTING
  note="Independent observation corroborating the active unauthorized withdrawal."
)
```

Verify `get_incident_evidence(INCIDENT_ID)` contains both immutable records.

---

## 11. Run full-consensus adjudication and wait for FINALITY

Call:

```text
adjudicate_incident(INCIDENT_ID)
```

Use normal/full consensus, not simulation, for the hackathon evidence run.

Expected qualifying verdict:

```text
finding = ACTIVE_CRITICAL_EXPLOIT (5)
authorized_action = HALT (2)
incident status = HALT_AUTHORIZED (4)
```

The verdict must satisfy all five deterministic gates; confidence alone is irrelevant.

**Wait until the GenLayer transaction is FINALIZED.** Only then should the finality-only external message execute:

```text
Guardian.pauseFromProofHalt(INCIDENT_ID, REVISION)
```

Verify EVM state:

```text
Guardian.isIncidentActive(INCIDENT_ID) == true
Guardian.isIncidentRestored(INCIDENT_ID) == false
Guardian.activeHaltCount() == 1
Guardian.isPaused() == true
DemoVault.paused() == true
```

Then call:

```text
confirm_target_state(INCIDENT_ID)
```

Expected ProofHalt incident status:

```text
HALTED = 5
```

---

## 12. Prove the halt is real

While halted, attempt each of the following and preserve the reverted transaction/result evidence:

```text
Account B: demoExploitWithdrawFrom(AccountA, 1)
Account A: deposit() with tiny GEN
Account A: withdraw(1)
```

All must revert because the vault is paused.

This is strong judge evidence: ProofHalt did not merely write `HALTED` to its own state; the external protected protocol actually stopped operating.

---

## 13. Apply the one-way remediation patch

While the target is still paused, call:

```text
DemoVault.applyDemoPatch()
```

Verify:

```text
demoExploitEnabled() == false
DemoPatchApplied event emitted
DemoVault.paused() == true
```

Record `PATCH_TX`.

`applyDemoPatch()` cannot re-enable the vulnerability, and `proofHaltRestore()` itself rejects restoration until the patch is applied.

---

## 14. Prepare remediation evidence

Again require two independent origin groups, including technical evidence.

Technical remediation evidence should record:

```text
PATCH_TX
DemoPatchApplied event
demoExploitEnabled == false
DemoVault still paused
original exploit transaction reference
```

Independent corroboration must come from a separate origin/observer, not a copy of the first artifact.

Create source-native, contract-bound artifacts and SHA-256 hashes exactly as in the incident stage.

---

## 15. Submit remediation and adjudicate

For each remediation source call:

```text
submit_remediation(
  incident_id=INCIDENT_ID,
  origin_id=<constitution-approved origin ID>,
  source_url=<approved remediation artifact URL>,
  snapshot_uri=<same URL or matching commit-pinned GitHub raw URL>,
  content_hash=<exact SHA-256>,
  note=<concise remediation evidence note>
)
```

Then call:

```text
adjudicate_remediation(INCIDENT_ID)
```

Expected qualifying verdict:

```text
finding = REMEDIATED (7)
authorized_action = RESTORE (4)
incident status = RESTORE_AUTHORIZED (9)
```

Wait for **FINALIZED**. Only then should:

```text
Guardian.restoreFromProofHalt(INCIDENT_ID, REVISION)
```

execute.

For a single active incident, verify:

```text
Guardian.isIncidentActive(INCIDENT_ID) == false
Guardian.isIncidentRestored(INCIDENT_ID) == true
Guardian.activeHaltCount() == 0
Guardian.isPaused() == false
DemoVault.paused() == false
```

Call:

```text
confirm_target_state(INCIDENT_ID)
```

Expected status:

```text
RESTORED = 10
```

Then:

```text
close_incident(INCIDENT_ID)
```

Expected:

```text
CLOSED = 11
```

---

## 16. Prove recovery did not reintroduce the exploit

After restoration:

1. Normal `deposit()` succeeds.
2. Normal owner `withdraw()` succeeds.
3. `demoExploitWithdrawFrom(...)` still reverts because `demoExploitEnabled == false`.

Preserve these transactions/results as demo evidence.

---

## 17. Required overlapping-incident safety test

Run this on a **fresh DemoVault deployment** or create both incidents before applying the global demo patch.

1. Open `PH-A` and `PH-B` against the same target.
2. Get both independently adjudicated and finalized as HALT.
3. Verify:

```text
activeHaltCount == 2
DemoVault.paused == true
isIncidentActive(PH-A) == true
isIncidentActive(PH-B) == true
```

4. Remediate/restore `PH-A` first.
5. Verify:

```text
isIncidentRestored(PH-A) == true
isIncidentActive(PH-B) == true
activeHaltCount == 1
DemoVault.paused == true
```

`confirm_target_state(PH-A)` must succeed and `PH-A` may be closed even though the target remains globally paused for `PH-B`.

6. Restore `PH-B`.
7. Verify:

```text
activeHaltCount == 0
DemoVault.paused == false
```

This is the proof that one remediated incident cannot accidentally reopen a target while another critical halt is still active.

---

## 18. Evidence package to save for the hackathon

Preserve all of these:

- `proofhalt.py` source hash and deployment transaction
- DemoVault source hash/address/deployment transaction
- Guardian source hash/address/deployment transaction
- Guardian binding transaction
- live Constitution file + SHA-256 + immutable URI
- `register_protocol` transaction
- `activate_protocol` transaction
- victim deposit transaction
- real bounded exploit transaction
- both independent incident evidence URLs/hashes
- incident adjudication transaction + finalized verdict
- Guardian `HaltActivated` event
- blocked exploit attempt while paused
- patch transaction + `DemoPatchApplied` event
- both independent remediation evidence URLs/hashes
- remediation adjudication transaction + finalized verdict
- Guardian `RestoreActivated` event
- ProofHalt `confirm_target_state` and `close_incident` transactions
- post-restore normal withdrawal success
- post-restore exploit-path rejection
- overlapping-incident test evidence

Fill `deployment_record_template.json` as each item is completed. Never enter a transaction as finalized until the explorer/network shows finality.

---

## 19. Stage 9 go/no-go rules

### GO to live integrated deployment only if

- official GenVM semantic lint passes `proofhalt.py`;
- real solc 0.8.36 compile passes;
- verifier reports both bytecodes/ABIs valid;
- source hashes match;
- all offline tests remain green.

### NO-GO / stop immediately if

- compiler emits any severity `error`;
- Guardian authority does not equal the ProofHalt IC/ghost address;
- target/Guardian binding differs;
- `configurationAuthority` is not zero after binding;
- ProofHalt activates while Guardian already has an active halt;
- evidence snapshot bytes do not match the submitted SHA-256;
- there are fewer than two genuinely independent evidence origins;
- a HALT/RESTORE action is assumed from ACCEPTED rather than FINALIZED;
- partial restoration unpauses a target with another active incident;
- DemoVault can restore while `demoExploitEnabled == true`.

The frontend should only be built around state/actions that pass these checks.
