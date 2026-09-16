import importlib.util
import unittest
import hashlib
import types

spec = importlib.util.spec_from_file_location('stage7tests', str(__import__('pathlib').Path(__file__).resolve().parent/'test_proofhalt_stage7.py'))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
ph = t.ph

class CrossLayerTests(unittest.TestCase):
    def setUp(self):
        t.gl.message.sender_address = t.OWNER
        t.gl.message.contract_address = t.Address('0x'+'99'*20)
        t.FakeGuardianInstance.paused = False
        t.FakeGuardianInstance.active_halts = 0
        t.FakeGuardianInstance.incident_active = {}
        t.FakeGuardianInstance.incident_restored = {}
        t.FakeGuardianInstance.incident_binding = {}
        ph.ProofHaltGuardianEVM = t.FakeGuardianInstance
        self.c = ph.ProofHalt('')
        self.clock = [1_800_000_000]
        self.c._now = lambda: self.clock[0]
        text, h = t.constitution()
        self.c.register_protocol('demovault-v1', t.TARGET, t.GUARDIAN, '', text, h, '')
        self.c.activate_protocol('demovault-v1')
        self.p = self.c.protocols['demovault-v1']

    def open_two(self):
        i1 = self.c.open_incident('demovault-v1', 'Incident one')
        i2 = self.c.open_incident('demovault-v1', 'Incident two')
        return i1, i2

    def halt(self, iid, revision=1):
        inc = self.c.incidents[iid]
        inc.status = ph.u8(ph.INCIDENT_HALT_AUTHORIZED)
        key=self.c._verdict_key(iid,revision)
        binding=hashlib.sha256(f'halt:{iid}:{revision}'.encode()).hexdigest()
        self.c.verdicts[key]=types.SimpleNamespace(decision_binding_hash=binding)
        inc.latest_revision_key=key
        self.c._emit_halt(self.p, iid, revision)
        self.c.confirm_target_state(iid)
        self.assertEqual(int(inc.status), ph.INCIDENT_HALTED)

    def restore(self, iid, revision=2):
        inc = self.c.incidents[iid]
        inc.status = ph.u8(ph.INCIDENT_RESTORE_AUTHORIZED)
        key=self.c._verdict_key(iid,revision)
        binding=hashlib.sha256(f'restore:{iid}:{revision}'.encode()).hexdigest()
        self.c.verdicts[key]=types.SimpleNamespace(decision_binding_hash=binding)
        inc.latest_revision_key=key
        self.c._emit_restore(self.p, iid, revision)
        self.c.confirm_target_state(iid)
        self.assertEqual(int(inc.status), ph.INCIDENT_RESTORED)

    def test_01_global_pause_cannot_false_confirm_second_incident(self):
        i1, i2 = self.open_two()
        self.halt(i1)
        self.assertTrue(t.FakeGuardianInstance.paused)
        self.c.incidents[i2].status = ph.u8(ph.INCIDENT_HALT_AUTHORIZED)
        with self.assertRaisesRegex(t.UserError, 'PH_TARGET_STATE_MISMATCH'):
            self.c.confirm_target_state(i2)
        self.assertEqual(int(self.c.incidents[i2].status), ph.INCIDENT_HALT_AUTHORIZED)

    def test_02_each_overlapping_halt_requires_incident_specific_guardian_state(self):
        i1, i2 = self.open_two()
        self.halt(i1)
        self.halt(i2)
        self.assertEqual(t.FakeGuardianInstance.active_halts, 2)
        self.assertTrue(t.FakeGuardianInstance.incident_active[i1])
        self.assertTrue(t.FakeGuardianInstance.incident_active[i2])
        self.assertTrue(t.FakeGuardianInstance.paused)

    def test_03_partial_restore_can_confirm_and_close_while_target_stays_paused(self):
        i1, i2 = self.open_two()
        self.halt(i1); self.halt(i2)
        self.restore(i1, 2)
        self.assertEqual(t.FakeGuardianInstance.active_halts, 1)
        self.assertTrue(t.FakeGuardianInstance.paused)
        self.assertFalse(t.FakeGuardianInstance.incident_active[i1])
        self.assertTrue(t.FakeGuardianInstance.incident_restored[i1])
        self.c.close_incident(i1)
        self.assertEqual(int(self.c.incidents[i1].status), ph.INCIDENT_CLOSED)
        self.assertEqual(int(self.c.incidents[i2].status), ph.INCIDENT_HALTED)

    def test_04_final_restore_unpauses_and_both_incidents_can_close(self):
        i1, i2 = self.open_two()
        self.halt(i1); self.halt(i2)
        self.restore(i1, 2); self.c.close_incident(i1)
        self.restore(i2, 2); self.c.close_incident(i2)
        self.assertEqual(t.FakeGuardianInstance.active_halts, 0)
        self.assertFalse(t.FakeGuardianInstance.paused)
        self.assertEqual(int(self.p.unresolved_incident_count), 0)

    def test_05_activation_rejects_nonzero_guardian_active_halt_count(self):
        # Fresh protocol, intentionally inconsistent adapter state: unpaused but count != 0.
        c2 = ph.ProofHalt('')
        c2._now = lambda: self.clock[0]
        text, h = t.constitution('vault-two')
        c2.register_protocol('vault-two', t.TARGET, t.GUARDIAN, '', text, h, '')
        t.FakeGuardianInstance.paused = False
        t.FakeGuardianInstance.active_halts = 1
        with self.assertRaisesRegex(t.UserError, 'PH_TARGET_ALREADY_PAUSED'):
            c2.activate_protocol('vault-two')

    def test_06_close_requires_guardian_incident_restore_proof(self):
        iid = self.c.open_incident('demovault-v1', 'Claim')
        self.c.incidents[iid].status = ph.u8(ph.INCIDENT_RESTORED)
        key=self.c._verdict_key(iid,1)
        binding=hashlib.sha256(b'close-proof').hexdigest()
        self.c.verdicts[key]=types.SimpleNamespace(decision_binding_hash=binding)
        self.c.incidents[iid].latest_revision_key=key
        t.FakeGuardianInstance.incident_active[iid] = False
        t.FakeGuardianInstance.incident_restored[iid] = False
        t.FakeGuardianInstance.incident_binding[iid] = bytes.fromhex(binding)
        with self.assertRaisesRegex(t.UserError, 'PH_TARGET_STATE_MISMATCH'):
            self.c.close_incident(iid)

if __name__ == '__main__':
    unittest.main(verbosity=2)
