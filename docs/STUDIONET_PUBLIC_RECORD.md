# Studionet Public Record

ProofHalt's reproducible public case is `proofhalt-studionet-demo` / `PH-000001` on GenLayer Studionet (chain 61999).

## Contracts

- ProofHalt: [`0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB`](https://explorer-studio.genlayer.com/address/0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB)
- Non-financial demo target: [`0xB156762A2339174695C570e74295B6FBf7D1Ecd5`](https://explorer-studio.genlayer.com/address/0xB156762A2339174695C570e74295B6FBf7D1Ecd5)

The target explicitly accepts no assets. Its one-way incident switch exists only to make evidence and adjudication publicly reproducible.

## Finalized lifecycle

| Step | Transaction | Verified result |
|---|---|---|
| Deploy ProofHalt | [`0xea7579…c68c`](https://explorer-studio.genlayer.com/tx/0xea7579b31f5461adccfc83065a166097b88b2e002b88f032d5c3feb2c42dc68c) | FINALIZED / SUCCESS |
| Register protocol | [`0x1ad249…6a66`](https://explorer-studio.genlayer.com/tx/0x1ad24921a05d9c43a308c6fdfacf8997a2c34d0d63905b1b011586e8a0a26a66) | FINALIZED / SUCCESS |
| Activate protocol | [`0x8ccb47…2968`](https://explorer-studio.genlayer.com/tx/0x8ccb47accfc9f78d226f0fc37311e1493ea093dd18c98f680f4f810472d52968) | FINALIZED / SUCCESS |
| Open incident | [`0xa09bee…ba98`](https://explorer-studio.genlayer.com/tx/0xa09bee8b428780102d7cc6f93c6880681d8740a6901ba07c917c40c5b499ba98) | `PH-000001` |
| Submit evidence E001 | [`0x2fe3c6…8ddd`](https://explorer-studio.genlayer.com/tx/0x2fe3c696a258f63ed985d2d20b36306cc0107448a2029d5c1e93df9c79ea8ddd) | FINALIZED / SUCCESS |
| Submit evidence E002 | [`0x80f01d…325e`](https://explorer-studio.genlayer.com/tx/0x80f01d407598b3a7029d7019d83fd38e8d68be05f7541a76f522d12378d9325e) | FINALIZED / SUCCESS |
| Initial adjudication | [`0x855e00…b115`](https://explorer-studio.genlayer.com/tx/0x855e009ae9ec60abaff6fb20bd47fee4e70cfa27ec967e5af2bce737aefab115) | Revision R1 |
| Submit evidence E003 | [`0x35f844…7824`](https://explorer-studio.genlayer.com/tx/0x35f84419b56fb237ac5948af24220d272147a5f960156fa13e1b39954e747824) | FINALIZED / SUCCESS |
| Submit evidence E004 | [`0x3584ea…acdd`](https://explorer-studio.genlayer.com/tx/0x3584ea2bbbabdf85400b2598d091463e2db2121f62fa7b05e43578053d17acdd) | FINALIZED / SUCCESS |
| Consensus recheck | [`0x01a813…4d20`](https://explorer-studio.genlayer.com/tx/0x01a813218023e9653912c3d76b7af8446eaf4e5edc244bda1eb79795f1a14d20) | Revision R2 |

Every listed write was independently checked through `genlayer-js`: transaction status `FINALIZED`, consensus result `MAJORITY_AGREE`, leader result `return`, and leader execution result `SUCCESS`.

## Verdict and honest limitation

The latest consensus finding is `INSUFFICIENT_EVIDENCE`, with no authorized action. Studionet validators reported `source_fetch_ok=false` and `snapshot_fetch_ok=false` for all four evidence records even though the public URLs returned HTTP 200 and matching SHA-256 bytes outside the validator execution environment. ProofHalt therefore failed closed and did not authorize a halt.

This is useful public evidence of the trust boundary: a model cannot turn an unavailable source into emergency authority. Remediation and restore are not valid transitions because no halt was authorized. The frontend still exposes those transaction forms and their complete lifecycle for a network where validator web retrieval and external enforcement are available.

The machine-readable record is [`docs/evidence/studionet-final-record.json`](evidence/studionet-final-record.json).
