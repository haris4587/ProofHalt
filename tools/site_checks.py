#!/usr/bin/env python3
import json
import re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
h=(R/'site/index.html').read_text(); c=(R/'site/assets/styles.css').read_text(); j=(R/'site/assets/app.js').read_text(); s=(R/'site/src/genlayer-client.js').read_text(); b=(R/'site/assets/genlayer-client.js').read_text(); hd=(R/'site/_headers').read_text(); n=(R/'netlify.toml').read_text(); p=json.loads((R/'package.json').read_text())
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
ck('GenLayer SDK exactly pinned', p['dependencies'].get('genlayer-js')=='1.1.8')
ck('local GenLayer browser bundle', "from './genlayer-client.js'" in j and len(b)>1000)
ck('live contract read', "functionName: 'get_global_constitution'" in s and 'readGlobalConstitution' in j)
ck('public read without wallet', 'Verify live contract · no wallet' in h and 'verifyLiveContract();' in j and 'verifyContractBtn.disabled=false' in j)
requested_methods=set(re.findall(r"method:'([^']+)'",j))
allowed_methods={'eth_chainId','eth_requestAccounts','wallet_addEthereumChain','wallet_switchEthereumChain'}
ck('no Snap request', all(x not in j+s for x in ('wallet_getSnaps','wallet_requestSnaps','genlayer-wallet-plugin','walletClient.connect')))
ck('no signing or transaction request', requested_methods<=allowed_methods and all(x not in j+s for x in ('personal_sign','eth_sign','eth_sendTransaction','wallet_sendCalls','writeContract')))
ck('transparent simulation disclaimer', 'staged simulation' in h and 'external Guardian path' in h)
ck('RECOVERED terminal state', "status:'RECOVERED'" in j)
ck('responsive CSS', '@media' in c)
ck('restricted wallet CSP', "script-src 'self'" in hd and 'https://esm.sh' not in hd and 'https://studio.genlayer.com' in hd)
ck('Netlify production build', 'command = "npm run build"' in n and 'publish = "site"' in n)
assert len(checks)==22
print('SUMMARY 22/22 PASS')
