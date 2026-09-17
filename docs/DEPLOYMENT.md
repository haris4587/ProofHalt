# Deployment Record

## GenLayer

- Network: GenLayer Studionet / Studio explorer
- Intelligent Contract: `0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB`
- Deployment transaction: `0xea7579b31f5461adccfc83065a166097b88b2e002b88f032d5c3feb2c42dc68c`
- Recorded release status: FINALIZED

Explorer links:

- https://explorer-studio.genlayer.com/address/0x02E5Ac4D8E718e15EdF6c52C48908d45a1A628bB
- https://explorer-studio.genlayer.com/tx/0xea7579b31f5461adccfc83065a166097b88b2e002b88f032d5c3feb2c42dc68c
- Public lifecycle: [`STUDIONET_PUBLIC_RECORD.md`](STUDIONET_PUBLIC_RECORD.md)

## Netlify

- Site: `proofhalt`
- Site ID: `e6791f4a-0842-4e5c-905a-a39e53de9261`
- Production URL: https://proofhalt.netlify.app
- Production branch: `main`
- Build command: `npm run build`
- Publish directory: `site`

The stable production URL resolves to the latest ready deploy recorded in the
Netlify dashboard; deploy-specific IDs are intentionally not pinned here.

## EVM Guardian/Vault

The Guardian/Vault integration remains explicitly separate from the public GenLayer deployment claim. The repository contains the exact Solidity source, compile gate and lifecycle tests. No public funded Bradbury deployment is asserted.
