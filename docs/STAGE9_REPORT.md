> **Historical validation record.** This report was produced before the later public GenLayer Studionet deployment and Netlify release. Its "Live deployment: NOT YET AUTHORIZED" line describes the Stage-9 checkpoint only. For the current release status, contract address, transaction, and live-site deployment record, see [`DEPLOYMENT.md`](DEPLOYMENT.md).

# ProofHalt Stage 9 — Compile/Audit/Deployment Readiness Report

## Result

**Stage 9 package: READY FOR EXTERNAL COMPILER + LIVE-NETWORK GATES**  
**Live deployment: NOT YET AUTHORIZED**

The Solidity/Python cross-layer audit uncovered and fixed important multi-incident state-synchronization issues before deployment. A real `solc 0.8.36` binary is not available in this runtime, so no compile success is claimed.

## Final Stage 9 architecture changes

- Solidity compiler pin upgraded to `0.8.36`.
- `ProofHaltGuardian` exposes incident-specific `isIncidentActive` and `isIncidentRestored` state.
- `proofhalt.py` v0.3.0 confirms a specific incident's Guardian state rather than inferring it from the global target pause flag.
- A resolved incident can close while another incident correctly keeps the target paused.
- Activation rejects a Guardian with non-zero `activeHaltCount`.
- DemoVault contains a clearly labeled **testnet-only, bounded** vulnerability so the hackathon demo can produce a genuine unauthorized withdrawal transaction.
- DemoVault adds a one-way remediation patch that only works while paused.
- DemoVault independently refuses restore until the demo vulnerability is patched.

## Validation performed

- Stage 9 static audit: **36/36 PASS**
- ProofHalt regression: **24/24 PASS**
- Guardian/Vault model: **21/21 PASS**
- Cross-layer overlap: **6/6 PASS**
- Exploit/patch lifecycle: **9/9 PASS**
- Aggregate offline checks: **60/60 PASS**

## Compiler gate

Prepared:

- `solc_standard_input.json`
- `compile_with_solc.sh`
- `verify_solc_output.py`
- `foundry.toml`

The compile helper requires exactly Solidity 0.8.36. The Standard JSON build uses optimizer 200, `viaIR=false`, and conservative `evmVersion=paris`.

Current runtime result is intentionally recorded in `compiler_attempt.txt` as `SOLC_UNAVAILABLE`; this is an environment limitation, not a claimed compiler pass.

## Live-network requirement

The integrated Guardian demo must run on Testnet Bradbury / GenLayer Chain. Studio cannot establish the final EVM-interface proof path. External EVM messages must be treated as executed only at GenLayer finality.

## Evidence integrity requirement

The demo must not fabricate source independence. HALT and RESTORE both need at least two genuinely independent origin groups and a technical anchor. Stable immutable snapshots are hash-bound; mirrors of the same origin still count as one provenance group.

## Deployment procedure

See `E2E_DEPLOYMENT_RUNBOOK.md` and fill `deployment_record_template.json` during the live run.
