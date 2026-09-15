# ProofHalt Architecture

## Goal

ProofHalt gives autonomous protocols a narrow emergency intervention path without handing an operator an unrestricted pause key. A protocol first registers a versioned security constitution. Evidence submitted to an incident is then evaluated through GenLayer validator consensus under that frozen constitution.

## Decision path

1. A protocol registers a target contract and Guardian adapter.
2. A constitution fixes protected targets, emergency conditions, exclusions, minimum independent source groups and review rules.
3. An incident is opened and evidence artifacts are submitted with content hashes.
4. GenLayer validators independently fetch the evidence inside nondeterministic execution and independently evaluate the same structured decision schema.
5. Deterministic gates reject any decision that lacks the required target match, exploit condition, impact, source corroboration, evidence integrity or technical anchor.
6. A HALT authorization emits the narrow EVM Guardian action for the exact incident/revision.
7. The Guardian tracks incident-specific state and the protected target remains paused while any incident remains active.
8. RESTORE requires new remediation evidence, a later verdict revision and target-side remediation.

## Binding model

A verdict revision is bound to the incident, parent revision, constitution version/hash, evidence-set hash, structured assessment, authorized action and reasoning digest. Evidence and verdict history are append-only.

## Overlapping incidents

Global pause state is insufficient to prove that a specific incident was enforced. ProofHalt therefore verifies incident-specific Guardian views (`isIncidentActive`, `isIncidentRestored`). Partial recovery of one incident cannot clear another incident's halt.

## Trust boundaries

- Web evidence is untrusted input and may contain prompt injection.
- LLM output is advisory until it passes deterministic schema and safety gates.
- The Guardian cannot choose a verdict and cannot execute arbitrary calls.
- The demo web app is a read-only reviewer interface; its live contract read is wallet-free and its optional MetaMask path cannot sign or submit transactions.
