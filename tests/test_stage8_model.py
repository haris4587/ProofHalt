from dataclasses import dataclass
from pathlib import Path
import re

AUTH='proofhalt'

class Err(Exception): pass

@dataclass
class Incident:
    latest: int = 0
    active: bool = False
    ever: bool = False
    restored: bool = False

class VaultModel:
    def __init__(self):
        self.guardian = None
        self.configured = False
        self.paused = False
        self.balances = {}
    def configure(self, guardian):
        if self.configured: raise Err('configured')
        self.guardian = guardian
        self.configured = True
    def halt(self, caller):
        if caller != self.guardian: raise Err('auth')
        self.paused = True
    def restore(self, caller):
        if caller != self.guardian: raise Err('auth')
        self.paused = False
    def deposit(self, who, amount):
        if self.paused: raise Err('paused')
        if amount <= 0: raise Err('zero')
        self.balances[who] = self.balances.get(who,0)+amount
    def withdraw(self, who, amount):
        if self.paused: raise Err('paused')
        if amount <= 0 or self.balances.get(who,0)<amount: raise Err('amount')
        self.balances[who] -= amount

class GuardianModel:
    def __init__(self, vault):
        self.vault=vault
        self.active=0
        self.states={}
        self.executed=set()
        self.bound=False
    def bind(self):
        self.vault.configure('guardian')
        self.bound=True
    def _check(self, caller, iid, rev):
        if caller != AUTH: raise Err('auth')
        if not iid or rev==0: raise Err('input')
        if not self.bound or self.vault.guardian!='guardian': raise Err('bound')
    def _consistent(self):
        if self.vault.paused != (self.active>0): raise Err('inconsistent')
    def pause(self, caller, iid, rev):
        self._check(caller,iid,rev)
        key=(iid,rev,'halt')
        if key in self.executed: return 'replay'
        st=self.states.setdefault(iid,Incident())
        if st.restored: raise Err('restored')
        if rev < st.latest: raise Err('stale')
        if st.latest and rev==st.latest: raise Err('conflict')
        self._consistent()
        self.executed.add(key); st.latest=rev; st.ever=True
        if not st.active:
            st.active=True; self.active +=1
        if not self.vault.paused:
            self.vault.halt('guardian')
        return 'ok'
    def restore(self, caller, iid, rev):
        self._check(caller,iid,rev)
        key=(iid,rev,'restore')
        if key in self.executed: return 'replay'
        st=self.states.setdefault(iid,Incident())
        if not st.active: raise Err('inactive')
        if rev < st.latest: raise Err('stale')
        if st.latest and rev==st.latest: raise Err('conflict')
        self._consistent()
        self.executed.add(key); st.latest=rev; st.active=False; st.restored=True
        self.active -=1
        if self.active==0:
            self.vault.restore('guardian')
        return 'ok'

def expect_err(fn, name):
    try: fn()
    except Err: return
    raise AssertionError(name)

def run():
    results=[]
    def ok(name, fn):
        fn(); results.append(name)

    # Source/API checks
    gsrc=(Path(__file__).resolve().parents[1]/'contracts/ProofHaltGuardian.sol').read_text()
    vsrc=(Path(__file__).resolve().parents[1]/'contracts/DemoVault.sol').read_text()
    pysrc=(Path(__file__).resolve().parents[1]/'contracts/proofhalt.py').read_text()

    ok('01 guardian ABI matches proofhalt.py', lambda: [
        (_ for _ in ()).throw(AssertionError(sig)) if sig not in gsrc or sig not in pysrc else None
        for sig in ['proofHaltAuthority','protectedTarget','isPaused','pauseFromProofHalt','restoreFromProofHalt']
    ])
    ok('02 no dangerous generic execution surface', lambda: (
        None if not re.search(r'\b(delegatecall|callcode|selfdestruct|suicide|arbitraryCall|executeCall)\b', gsrc) else (_ for _ in ()).throw(AssertionError('dangerous'))
    ))
    ok('03 target has no force-unpause admin', lambda: (
        None if not re.search(r'force(Unpause|Restore)|owner(Unpause|Restore)', vsrc, re.I) else (_ for _ in ()).throw(AssertionError('backdoor'))
    ))

    vault=VaultModel(); guard=GuardianModel(vault)
    ok('04 unbound guardian rejected', lambda: expect_err(lambda: guard.pause(AUTH,'PH-1',1),'unbound'))
    guard.bind()
    ok('05 unauthorized halt rejected', lambda: expect_err(lambda: guard.pause('attacker','PH-1',1),'auth'))
    ok('06 first halt pauses target', lambda: (guard.pause(AUTH,'PH-1',1), assert_state(guard,vault,1,True)))
    ok('07 exact halt replay is idempotent', lambda: (assert_eq(guard.pause(AUTH,'PH-1',1),'replay'), assert_state(guard,vault,1,True)))
    ok('08 conflicting equal revision rejected', lambda: expect_err(lambda: guard.restore(AUTH,'PH-1',1),'conflict'))
    ok('09 stale revision rejected', lambda: expect_err(lambda: guard.restore(AUTH,'PH-1',0),'stale/input'))
    ok('10 higher halt revision does not double-count incident', lambda: (guard.pause(AUTH,'PH-1',2), assert_state(guard,vault,1,True)))
    ok('11 second incident increments active set', lambda: (guard.pause(AUTH,'PH-2',1), assert_state(guard,vault,2,True)))
    ok('12 restoring one of two incidents keeps target paused', lambda: (guard.restore(AUTH,'PH-1',3), assert_state(guard,vault,1,True)))
    ok('13 restored incident cannot be re-halted', lambda: expect_err(lambda: guard.pause(AUTH,'PH-1',4),'rehalt'))
    ok('14 final active restore unpauses target', lambda: (guard.restore(AUTH,'PH-2',2), assert_state(guard,vault,0,False)))
    ok('15 exact restore replay harmless', lambda: (assert_eq(guard.restore(AUTH,'PH-2',2),'replay'), assert_state(guard,vault,0,False)))
    ok('16 restore without active halt rejected', lambda: expect_err(lambda: guard.restore(AUTH,'PH-3',1),'inactive'))

    # Target user-flow checks
    vault2=VaultModel(); guard2=GuardianModel(vault2); guard2.bind()
    vault2.deposit('alice',100)
    ok('17 normal withdraw works before halt', lambda: (vault2.withdraw('alice',10), assert_eq(vault2.balances['alice'],90)))
    guard2.pause(AUTH,'PH-X',1)
    ok('18 deposit blocked while paused', lambda: expect_err(lambda: vault2.deposit('alice',1),'deposit pause'))
    ok('19 withdraw blocked while paused', lambda: expect_err(lambda: vault2.withdraw('alice',1),'withdraw pause'))
    guard2.restore(AUTH,'PH-X',2)
    ok('20 withdraw works after finalized restore path', lambda: (vault2.withdraw('alice',10), assert_eq(vault2.balances['alice'],80)))

    # Deliberate target-state corruption should fail closed.
    vault3=VaultModel(); guard3=GuardianModel(vault3); guard3.bind(); vault3.paused=True
    ok('21 inconsistent target state fails closed', lambda: expect_err(lambda: guard3.pause(AUTH,'PH-Z',1),'inconsistent'))

    print(f'PASS {len(results)}/{len(results)}')
    for r in results: print('PASS',r)

def assert_state(g,v,count,paused):
    assert g.active==count, (g.active,count)
    assert v.paused==paused, (v.paused,paused)

def assert_eq(a,b):
    assert a==b,(a,b)

if __name__=='__main__': run()
