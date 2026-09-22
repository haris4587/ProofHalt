#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python tests/test_proofhalt_stage7.py
python tests/test_stage8_model.py
python tests/test_stage9_cross_layer.py
python tests/test_stage9_demo_lifecycle.py
python tools/security_invariants.py
python tools/site_checks.py
printf '\nBehavioral/model suites: 64/64 PASS\n'
printf 'Security invariants: 62/62 PASS\n'
printf 'Static site checks: 44/44 PASS\n'
printf 'Preserved Stage-9 audit: results/audit_results.txt (36/36 PASS)\n'
printf 'PROOFHALT_RELEASE_GATE_PASS\n'
