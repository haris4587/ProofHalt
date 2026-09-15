#!/usr/bin/env python3
"""Create a canonical, hashable ProofHalt evidence snapshot JSON.

This formats evidence; it does NOT make an origin independent. Two snapshots of
the same underlying source still belong to one provenance group.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
TX_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=["incident", "remediation"], required=True)
    p.add_argument("--chain-id", type=int, default=4221)
    p.add_argument("--target", required=True)
    p.add_argument("--tx-hash", required=True)
    p.add_argument("--origin-url", required=True, help="Original explorer/monitor/source URL")
    p.add_argument("--origin-name", required=True, help="Actual origin, e.g. GenLayer Chain explorer or independent monitor")
    p.add_argument("--summary", required=True)
    p.add_argument("--facts-json", default="{}", help='Additional JSON object, e.g. {"victim_balance_before":"3000000000000"}')
    p.add_argument("--out", required=True)
    a = p.parse_args()
    if not ADDR_RE.fullmatch(a.target): raise SystemExit("invalid target")
    if not TX_RE.fullmatch(a.tx_hash): raise SystemExit("invalid tx hash")
    try:
        facts = json.loads(a.facts_json)
    except json.JSONDecodeError as e:
        raise SystemExit(f"invalid --facts-json: {e}")
    if not isinstance(facts, dict): raise SystemExit("--facts-json must be an object")
    obj = {
        "schema": "proofhalt-evidence-snapshot/v1",
        "kind": a.kind,
        "chain_id": a.chain_id,
        "target_contract": a.target,
        "transaction_hash": a.tx_hash,
        "origin_name": a.origin_name,
        "origin_url": a.origin_url,
        "summary": a.summary,
        "facts": facts,
    }
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    Path(a.out).write_bytes(text.encode("utf-8"))
    print(f"file={a.out}")
    print(f"sha256={hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    print("IMPORTANT: upload these exact bytes to a stable immutable URL; do not edit after hashing.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
