import copy
import unittest

CAP = 1_000_000_000_000

class Err(Exception): pass

class DemoVaultModel:
    def __init__(self):
        self.guardian = 'guardian'
        self.paused = False
        self.demo_exploit_enabled = True
        self.balances = {}
        self.total = 0
    def deposit(self, who, amount):
        if self.paused: raise Err('paused')
        if amount <= 0: raise Err('zero')
        self.balances[who] = self.balances.get(who, 0) + amount
        self.total += amount
    def exploit(self, attacker, victim, amount):
        if self.paused: raise Err('paused')
        if not self.demo_exploit_enabled: raise Err('patched')
        if amount <= 0 or amount > CAP: raise Err('amount')
        if self.balances.get(victim, 0) < amount: raise Err('balance')
        self.balances[victim] -= amount
        self.total -= amount
        self.balances[attacker] = self.balances.get(attacker, 0) + amount
    def halt(self, caller):
        if caller != self.guardian: raise Err('auth')
        self.paused = True
    def apply_patch(self):
        if not self.paused: raise Err('patch-needs-pause')
        self.demo_exploit_enabled = False
    def restore(self, caller):
        if caller != self.guardian: raise Err('auth')
        if self.demo_exploit_enabled: raise Err('patch-required')
        self.paused = False

class Incident:
    def __init__(self): self.latest=0; self.active=False; self.restored=False

class GuardianModel:
    def __init__(self, vault):
        self.vault=vault; self.active=0; self.states={}
    def halt(self, iid, rev):
        st=self.states.setdefault(iid,Incident())
        if st.restored or rev <= st.latest: raise Err('revision')
        if self.vault.paused != (self.active>0): raise Err('inconsistent')
        st.latest=rev
        if not st.active:
            st.active=True; self.active+=1
        if not self.vault.paused: self.vault.halt('guardian')
    def restore(self, iid, rev):
        # Model EVM atomic rollback around target call.
        snap=(self.active, copy.deepcopy(self.states), self.vault.paused)
        try:
            st=self.states.setdefault(iid,Incident())
            if not st.active or rev <= st.latest: raise Err('revision/inactive')
            if self.vault.paused != (self.active>0): raise Err('inconsistent')
            st.latest=rev; st.active=False; st.restored=True; self.active-=1
            if self.active==0: self.vault.restore('guardian')
            elif not self.vault.paused: raise Err('must-stay-paused')
        except Exception:
            self.active, self.states, self.vault.paused = snap
            raise

class Tests(unittest.TestCase):
    def setUp(self):
        self.v=DemoVaultModel(); self.g=GuardianModel(self.v)
        self.v.deposit('victim', CAP*2)
    def test_01_real_bounded_unauthorized_demo_withdrawal(self):
        self.g.vault.exploit('attacker','victim',CAP)
        self.assertEqual(self.v.balances['victim'],CAP)
        self.assertEqual(self.v.balances['attacker'],CAP)
    def test_02_demo_exploit_cap_enforced(self):
        with self.assertRaises(Err): self.v.exploit('attacker','victim',CAP+1)
    def test_03_patch_cannot_be_applied_before_halt(self):
        with self.assertRaises(Err): self.v.apply_patch()
    def test_04_finalized_halt_blocks_repeat_exploit(self):
        self.v.exploit('attacker','victim',1)
        self.g.halt('PH-1',1)
        with self.assertRaises(Err): self.v.exploit('attacker','victim',1)
    def test_05_restore_before_patch_fails_and_guardian_state_rolls_back(self):
        self.g.halt('PH-1',1)
        with self.assertRaises(Err): self.g.restore('PH-1',2)
        self.assertTrue(self.v.paused); self.assertEqual(self.g.active,1)
        self.assertTrue(self.g.states['PH-1'].active); self.assertFalse(self.g.states['PH-1'].restored)
    def test_06_patch_while_paused_is_one_way(self):
        self.g.halt('PH-1',1); self.v.apply_patch(); self.v.apply_patch()
        self.assertFalse(self.v.demo_exploit_enabled)
    def test_07_patch_then_restore_succeeds(self):
        self.g.halt('PH-1',1); self.v.apply_patch(); self.g.restore('PH-1',2)
        self.assertFalse(self.v.paused); self.assertEqual(self.g.active,0)
    def test_08_exploit_remains_disabled_after_restore(self):
        self.g.halt('PH-1',1); self.v.apply_patch(); self.g.restore('PH-1',2)
        with self.assertRaises(Err): self.v.exploit('attacker','victim',1)
    def test_09_overlapping_incident_partial_restore_keeps_pause(self):
        self.g.halt('PH-1',1); self.g.halt('PH-2',1); self.v.apply_patch()
        self.g.restore('PH-1',2)
        self.assertTrue(self.v.paused); self.assertEqual(self.g.active,1)
        self.g.restore('PH-2',2)
        self.assertFalse(self.v.paused); self.assertEqual(self.g.active,0)

if __name__=='__main__': unittest.main(verbosity=2)
