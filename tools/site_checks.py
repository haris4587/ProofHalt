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
ck('local script', 'assets/app.js' in h)
ck('local SVG logo', 'assets/proofhalt-logo.svg' in h)
ck('GitHub release link', 'github.com/haris4587/ProofHalt' in h)
ck('GenLayer contract link', '0x9E43C93Dae87C32eEadbD8E733FAb4e54cF06767' in h)
ck('reviewer demo disclaimer', 'No live wallet writes' in j or 'not represent a live wallet' in h)
ck('RECOVERED terminal state', "status:'RECOVERED'" in j)
ck('HALT state present', 'HALT AUTHORIZED' in j and 'HALTED' in j)
ck('RESTORE state present', 'RESTORE AUTHORIZED' in j)
ck('responsive CSS', '@media' in c)
ck('frame denial header', 'X-Frame-Options: DENY' in hd)
ck('CSP header', 'Content-Security-Policy:' in hd)
ck('no external JS dependencies', '<script src="http' not in h)
ck('Netlify publish directory', 'publish = "site"' in n)
assert len(checks)==18
print('SUMMARY 18/18 PASS')
