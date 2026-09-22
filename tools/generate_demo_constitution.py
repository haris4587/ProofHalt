#!/usr/bin/env python3
"""Generate a contract-accepted ProofHalt v2 DemoVault constitution and SHA-256.

Use only after DemoVault has a real deployed address. The output bytes are the
same canonical JSON representation proofhalt.py hashes internally.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from urllib.parse import unquote

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
PID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target", required=True, help="Deployed DemoVault 0x address")
    p.add_argument("--protocol-id", default="proofhalt-demovault-v1")
    p.add_argument("--review-period", type=int, default=86400)
    p.add_argument("--critical-loss-bps", type=int, default=1)
    p.add_argument(
        "--technical-source-host",
        default="explorer-studio.genlayer.com",
        help="Exact host for the technical source policy",
    )
    p.add_argument(
        "--technical-path-prefix",
        default="/address/",
        help="Slash-terminated path prefix for the technical source policy",
    )
    p.add_argument(
        "--corroborating-source-host",
        default="raw.githubusercontent.com",
        help="Exact host for the independent corroborating policy",
    )
    p.add_argument(
        "--corroborating-path-prefix",
        default="/haris4587/ProofHalt/",
        help="Slash-terminated path prefix for the corroborating source policy",
    )
    p.add_argument("--out", default="demo_constitution_live.json")
    a = p.parse_args()

    if not ADDR_RE.fullmatch(a.target):
        raise SystemExit("invalid --target; expected 20-byte 0x address")
    if not PID_RE.fullmatch(a.protocol_id):
        raise SystemExit("invalid --protocol-id")
    if not 3600 <= a.review_period <= 30 * 86400:
        raise SystemExit("--review-period must be 3600..2592000 seconds")
    if not 0 <= a.critical_loss_bps <= 10000:
        raise SystemExit("--critical-loss-bps must be 0..10000")
    host_re = re.compile(
        r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
    )
    for name, host in (
        ("--technical-source-host", a.technical_source_host),
        ("--corroborating-source-host", a.corroborating_source_host),
    ):
        if not host_re.fullmatch(host) or host.lower() != host:
            raise SystemExit(f"{name} must be a lowercase DNS host")
    if a.technical_source_host == a.corroborating_source_host:
        raise SystemExit("source policies must use distinct hosts")
    for name, prefix in (
        ("--technical-path-prefix", a.technical_path_prefix),
        ("--corroborating-path-prefix", a.corroborating_path_prefix),
    ):
        if (
            not prefix.startswith("/")
            or (prefix != "/" and not prefix.endswith("/"))
            or len(prefix) > 256
            or unquote(prefix) != prefix
            or "\\" in prefix
            or "//" in prefix
            or any(part == ".." for part in prefix.split("/"))
        ):
            raise SystemExit(f"{name} must start and end with /")

    obj = {
        "schema": "proofhalt-protocol-constitution/v2",
        "protocol_id": a.protocol_id,
        "protected_targets": [a.target],
        "dependencies": [],
        "halt_conditions": [
            {"id": "H1", "description": "Unauthorized withdrawal of assets tracked by the registered DemoVault."},
            {"id": "H2", "description": "Active ability for an unauthorized caller to withdraw assets attributed to another account."},
            {"id": "H3", "description": "Unauthorized acquisition or use of privileged control over the protected DemoVault."},
            {"id": "H4", "description": "Active exploitation of the intentionally bounded DemoVault testnet vulnerability producing unauthorized asset loss."},
        ],
        "exclusions": [
            "Token price volatility without protocol compromise.",
            "Social-media claims without independent technical corroboration.",
            "Historical or already-remediated vulnerabilities that are not currently exploitable.",
            "Authorized user withdrawals and normal DemoVault operations.",
        ],
        "minimum_independent_groups": 2,
        "requires_technical_anchor": True,
        "critical_loss_bps": a.critical_loss_bps,
        "review_period_seconds": a.review_period,
        "evidence_sources": [
            {
                "origin_id": "technical-source",
                "exact_host": a.technical_source_host,
                "path_prefix": a.technical_path_prefix,
                "source_type": 1,
                "technical_anchor": True,
            },
            {
                "origin_id": "independent-corroboration",
                "exact_host": a.corroborating_source_host,
                "path_prefix": a.corroborating_path_prefix,
                "source_type": 3,
                "technical_anchor": False,
            },
        ],
        # Direct-source artifacts use source_url == snapshot_uri. GitHub blob
        # pages may alternatively bind to raw.githubusercontent.com only when
        # both URLs name the same repository, 40-hex commit and file path.
        "snapshot_hosts": sorted({
            a.technical_source_host,
            a.corroborating_source_host,
            "raw.githubusercontent.com",
        }),
    }
    text = canonical(obj)
    out = Path(a.out)
    out.write_bytes(text.encode("utf-8"))  # deliberately no trailing newline
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"file={out}")
    print(f"sha256={digest}")
    print(f"protocol_id={a.protocol_id}")
    print(f"target={a.target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
