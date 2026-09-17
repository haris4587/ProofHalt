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

## Reviewer wallet surface

The website's live `get_global_constitution` and public incident verification are public and require no wallet. The pinned `genlayer-js` dependency is bundled locally at build time, so the page does not execute code from a third-party module CDN. MetaMask connection is restricted to account access and the Studionet add/switch methods. A write is requested only after the user submits a named workflow form; it is a zero-value contract call and its wallet, submitted, consensus, finalized, execution and readback states are displayed. The application contains no token approval, arbitrary signature or Snap request.

The production hostname was submitted for MetaMask false-positive review after a phishing warning. The review remains pending; ProofHalt does not bypass or instruct users to bypass wallet/browser safety interstitials.

## Non-claims

The public GenLayer Intelligent Contract and Netlify demo are part of the release. The repository does not claim that the Guardian/DemoVault pair is funded or publicly deployed on Bradbury/EVM. Their source is compiler-gated and lifecycle-tested separately.
