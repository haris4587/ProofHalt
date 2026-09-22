# Hackathon Submission Copy

## Project name

ProofHalt — Evidence-Bound Emergency Governance

## One-liner

ProofHalt lets GenLayer validators independently verify constitution-approved evidence and authorize narrowly bound HALT/RESTORE actions for autonomous protocols.

## Problem and solution

Autonomous protocols need to react to exploits without giving a model, reporter or multisig unchecked emergency power. ProofHalt freezes the target and evidence policy in a versioned constitution, retrieves source-bound and hash-bound evidence during GenLayer consensus, and applies deterministic gates after the model assessment. A claimant-selected source/snapshot mismatch, missing evidence, hash mismatch, insufficient provenance or an unavailable technical anchor blocks intervention.

The production frontend genuinely calls the Intelligent Contract. It supports protocol registration and activation, constitution publication, incident opening, evidence submission, validator adjudication, public verdict reads, remediation adjudication, `confirm_target_state`, and `close_incident`. Each write reports wallet confirmation, submission hash, accepted consensus, finalized receipt, execution result and authoritative readback. The last two calls are visibly marked as Guardian-dependent and fail closed on the authorization-only Studio deployment.

## Reviewer links

- Demo: https://proofhalt.netlify.app
- GitHub: https://github.com/haris4587/ProofHalt
- Contract: https://explorer-studio.genlayer.com/address/0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB
- Deploy transaction: https://explorer-studio.genlayer.com/tx/0xea7579b31f5461adccfc83065a166097b88b2e002b88f032d5c3feb2c42dc68c
- Public record: [`STUDIONET_PUBLIC_RECORD.md`](STUDIONET_PUBLIC_RECORD.md)
- Launch copy: [`LAUNCH_POST.md`](LAUNCH_POST.md)
- Latest steward response: [`STEWARD_RESPONSE_V1_2.md`](STEWARD_RESPONSE_V1_2.md)

## Exact reviewer path

1. Open the live app. It calls `get_global_constitution` and loads the preserved `proofhalt-studionet-demo` / `PH-000001` record without a wallet.
2. Inspect the public record cards and open the contract/transaction links in GenLayer Explorer.
3. If desired, connect MetaMask and approve only account access plus the add/switch to GenLayer Studionet (chain 61999).
4. Submit a named workflow form. Confirm the zero-value contract call in MetaMask and watch wallet → submitted → consensus accepted → finalized → execution verified → readback.
5. Run `npm ci && npm test` to reproduce the release gate.

## Preserved public outcome

The public case includes successful finalized writes for deployment, registration, activation, incident opening, four evidence submissions, initial adjudication and an evidence recheck. Every listed transaction has `FINALIZED`, `MAJORITY_AGREE`, leader `return`, and leader execution `SUCCESS`.

The latest verdict is deliberately not presented as a successful halt. Studionet validators reported that their nondeterministic web environment could not retrieve the four source/snapshot URLs, so the deterministic integrity gates returned `INSUFFICIENT_EVIDENCE` and authorized no action. This is the real trust property: a model cannot manufacture emergency authority when authoritative data is unavailable. Because no halt was authorized, remediation/restore are not valid transitions for this case; those methods remain implemented, tested and exposed for a supporting network state.

## Scope and security note

Studionet currently records authorization only; it does not execute the external EVM Guardian bridge. The repository therefore does not claim a public EVM pause or funded Bradbury deployment. The Netlify hostname has an outstanding MetaMask false-positive review. Reviewers should follow their wallet warning and never bypass a safety interstitial.
