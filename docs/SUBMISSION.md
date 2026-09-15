# Hackathon Submission Copy

## Project name
ProofHalt — Evidence-Bound Emergency Governance

## One-liner
ProofHalt lets GenLayer validators independently verify security evidence and authorize narrowly bound HALT/RESTORE actions for autonomous protocols.

## Overview
ProofHalt is an evidence-bound emergency governor for autonomous protocols. A protocol registers a versioned security constitution that fixes the target, evidence requirements and recovery rules. When an incident is reported, GenLayer validators independently retrieve hash-bound evidence, reassess it, and reach consensus over a strict decision schema. Deterministic gates prevent model confidence from bypassing missing corroboration, source independence, evidence integrity or a technical anchor. A minimal EVM Guardian can enforce only the finalized incident/revision action and safely composes overlapping incidents. Recovery is separately adjudicated and requires independent remediation evidence plus a permanent target-side patch. The public release includes the finalized GenLayer contract, a MetaMask-connected Netlify reviewer console, reproducible tests and preserved audit evidence.

## Reviewer links

- Demo: https://proofhalt.netlify.app
- GitHub: https://github.com/haris4587/ProofHalt
- GenLayer contract: https://explorer-studio.genlayer.com/address/0x9E43C93Dae87C32eEadbD8E733FAb4e54cF06767
- Deploy transaction: https://explorer-studio.genlayer.com/tx/0x1e4d126a9f8880f259a7e6eb983b7a949110d7e18631b691f0abf9e54fee53d7

## Exact reviewer path

1. Open the ProofHalt website and click **Connect MetaMask**.
2. Approve the wallet connection and allow MetaMask to switch/add **GenLayer Studionet (chain 61999)**.
3. Wait for the reviewer console to read `get_global_constitution` from the deployed ProofHalt contract. Confirm the UI shows the deployed address as verified and the global safety floor as loaded.
4. Use **Begin evidence scan** and **Advance lifecycle** to walk the transparent incident simulation through EVIDENCE → HALT AUTHORIZED → HALTED → PATCHED → RESTORE AUTHORIZED → RECOVERED.
5. Open the GenLayer Explorer contract link and the GitHub repository to verify the finalized deployment, source, tests and release gate.

## Expected verification outcome

The reviewer should be able to connect MetaMask to GenLayer Studionet and read ProofHalt's finalized global constitution directly from the deployed Intelligent Contract. The site should clearly distinguish that live wallet/contract verification from the staged incident lifecycle walkthrough. The walkthrough should progress to RECOVERED, while the Explorer and GitHub repository provide the finalized contract, deployment transaction, source code and reproducible validation evidence.

## Important scope note
Do not describe the Solidity Guardian/DemoVault as publicly deployed on Bradbury unless a later deployment record is added. The public deployment claim in this release is the GenLayer Intelligent Contract above. The external Guardian lifecycle shown on the website remains an explicit reviewer simulation because the current Studionet deployment does not execute that EVM integration path.
