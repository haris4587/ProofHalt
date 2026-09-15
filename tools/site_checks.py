#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'site/index.html').read_text(); c=(R/'site/assets/styles.css').read_text(); j=(R/'site/assets/app.js').read_text(); hd=(R/'site/_headers').read_text(); n=(R/'netlify.toml').read_text()
checks=[]
def ck(name, cond):
    if not cond: raise AssertionError(name)
    checks.append(name); print(f"PASS {len(checks):02d} {name}")
ck('HTML doctype', h.lower().startswith('<!doctype html>'))
ck('viewport metadata', 'name="viewport"' in h)
ck('meta description', 'name="description"' in h)
ck('ProofHalt title', '<title>ProofHalt' in h)
ck('local stylesheet', 'assets/styles.css' in h)
ck('module application script', 'type="module" src="assets/app.js"' in h)
ck('local SVG logo', 'assets/proofhalt-logo.svg' in h)
ck('GitHub release link', 'github.com/haris4587/ProofHalt' in h)
ck('GenLayer contract link', '0x9E43C93Dae87C32eEadbD8E733FAb4e54cF06767' in h)
ck('MetaMask connect control', 'Connect MetaMask' in h and 'eth_requestAccounts' in j)
ck('Studionet network binding', '61999' in j and 'wallet_switchEthereumChain' in j)
ck('GenLayer browser SDK', 'genlayer-js@1.1.8' in j and 'createClient' in j)
ck('live contract read', "functionName:'get_global_constitution'" in j)
ck('transparent simulation disclaimer', 'staged simulation' in h and 'external Guardian path' in h)
ck('RECOVERED terminal state', "status:'RECOVERED'" in j)
ck('responsive CSS', '@media' in c)
ck('wallet CSP allowlist', 'https://esm.sh' in hd and 'https://studio.genlayer.com' in hd)
ck('Netlify publish directory', 'publish = "site"' in n)
assert len(checks)==18
print('SUMMARY 18/18 PASS')
