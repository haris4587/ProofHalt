# ProofHalt Architecture

## Goal

ProofHalt gives autonomous protocols a narrow emergency intervention path without handing an operator an unrestricted pause key. A protocol first registers a versioned security constitution. Evidence submitted to an incident is then evaluated through GenLayer validator consensus under that frozen constitution.

## Decision path

1. A protocol registers a target contract and Guardian adapter.
2. A constitution fixes protected targets, emergency conditions, exclusions, minimum independent source groups and review rules.
3. An incident is opened and evidence artifacts are submitted with content hashes. The contract accepts only the approved source URL itself or a source-native GitHub raw URL that matches the approved blob URL's repository, exact 40-hex commit and path.
4. GenLayer validators independently fetch the evidence inside nondeterministic execution, verify the exact adjudicated bytes, and independently evaluate the same structured decision schema.
5. Deterministic gates reject any decision that lacks the required target match, exploit condition, impact, source corroboration, evidence integrity or technical anchor.
6. A HALT authorization emits the narrow EVM Guardian action for the exact incident/revision.
7. The Guardian tracks incident-specific state and the protected target remains paused while any incident remains active.
8. RESTORE requires new remediation evidence, a later verdict revision and target-side remediation.
9. `confirm_target_state` proves that the Guardian applied the incident-bound HALT/RESTORE commitment; `close_incident` closes only a restored, Guardian-confirmed incident. Both actions are exposed in the reviewer console and fail closed in authorization-only Studio deployments.

## Binding model

A verdict revision is bound to the incident, parent revision, constitution version/hash, evidence-set hash, structured assessment, authorized action and reasoning digest. The evidence-set hash commits both source and artifact URLs. Evidence and verdict history are append-only.

## Overlapping incidents

Global pause state is insufficient to prove that a specific incident was enforced. ProofHalt therefore verifies incident-specific Guardian views (`isIncidentActive`, `isIncidentRestored`). Partial recovery of one incident cannot clear another incident's halt.

## Trust boundaries

- Web evidence is untrusted input and may contain prompt injection.
- LLM output is advisory until it passes deterministic schema and safety gates.
- The Guardian cannot choose a verdict and cannot execute arbitrary calls.
- The web app keeps all public reads wallet-free and uses MetaMask only for explicit, named zero-value writes. It shows wallet confirmation, submission, consensus, finality, leader execution verification and contract readback.
