# Steward Response — ProofHalt v1.2

## Source/artifact binding

`contracts/proofhalt.py` now rejects evidence with `PH_SOURCE_SNAPSHOT_MISMATCH` unless:

1. `source_url == snapshot_uri`, in which case validators hash and adjudicate the single response fetched from the constitution-approved URL; or
2. the source is a GitHub blob URL and the artifact is a `raw.githubusercontent.com` URL with the same owner, repository, exact 40-hex commit, and file path.

The old global snapshot-host allowlist is therefore only an additional host restriction; it can no longer turn an unrelated claimant-selected snapshot into admissible evidence. This rule applies to incident, recheck, periodic-review, and remediation evidence.

Contract regression `test_26_source_snapshot_mismatch_is_rejected_at_contract_boundary` proves that mismatched source/artifact paths are rejected without recording evidence. `test_27` covers valid and invalid GitHub source-native mappings.

## Recovery lifecycle UI

The transaction console now exposes both `confirm_target_state` and `close_incident`, with finalized state readback. The UI explicitly explains that these Guardian-backed calls fail closed with `PH_ENFORCEMENT_UNAVAILABLE` on the current authorization-only Studio deployment.

## Constitution tooling

`tools/generate_demo_constitution.py` now emits canonical `proofhalt-protocol-constitution/v2` data with the required `evidence_sources` and `snapshot_hosts` fields. Regression `test_28_constitution_generator_emits_contract_accepted_v2` runs the CLI and registers its exact output through the contract validator.

## Verification

- Behavioral/model suites: 64/64 pass
- Security invariants: 62/62 pass
- Static site checks: 44/44 pass
- `npm test`: `PROOFHALT_RELEASE_GATE_PASS`
