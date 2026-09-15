# Security Model

## Fail-closed properties

ProofHalt is designed so uncertainty blocks autonomous intervention rather than expanding authority. A malformed consensus result, missing technical anchor, insufficient source independence, hash mismatch, stale revision, target mismatch or Guardian-state mismatch causes the action to fail closed.

## Evidence integrity

Each evidence record carries a submitted SHA-256 digest. Validators fetch the selected origin/snapshot and compare the fetched bytes to that digest before the content can count toward the deterministic authorization gates. Recovery provenance is calculated from remediation evidence rather than recycling original exploit evidence.

## Prompt-injection resistance

The GenLayer prompts explicitly classify evidence content as untrusted data. Instructions embedded in webpages, reports, comments or metadata cannot change the constitution or output schema. Validator code independently reruns the evaluation and checks decision-critical fields.

## Guardian authority

`ProofHaltGuardian.sol` binds immutable ProofHalt authority and immutable protected target addresses. It exposes only incident-scoped pause/restore methods. It rejects stale/equal-conflicting revisions, replay conflicts, unauthorized callers, target-binding inconsistencies and restored-incident re-halts.

## Target safety

`DemoVault.sol` is deliberately testnet-only. Its bounded exploit exists solely for the demonstration. The exploit is disabled while paused, the remediation patch is one-way, and final restore is refused until the patch is applied.

## Non-claims

The public GenLayer Intelligent Contract and Netlify demo are part of the release. The repository does not claim that the Guardian/DemoVault pair is funded or publicly deployed on Bradbury/EVM. Their source is compiler-gated and lifecycle-tested separately.
