import sys, unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from kernel_rules import *


class KernelConformanceTests(unittest.TestCase):
    def test_valid_lifecycle(self):
        self.assertTrue(can_transition('PROPOSED','AUTHORIZED'))
        self.assertTrue(can_transition('AUTHORIZED','ACTIVE'))
        self.assertTrue(can_transition('ACTIVE','VERIFYING'))
        self.assertTrue(can_transition('VERIFYING','COMPLETE'))

    def test_invalid_shortcut_to_complete(self):
        self.assertFalse(can_transition('PROPOSED','COMPLETE'))
        self.assertFalse(can_transition('AUTHORIZED','COMPLETE'))

    def test_complete_is_terminal(self):
        self.assertFalse(can_transition('COMPLETE','ACTIVE'))

    def test_revision_guard(self):
        self.assertTrue(revision_matches(7,7))
        self.assertFalse(revision_matches(8,7))

    def test_permission_can_narrow(self):
        self.assertTrue(permission_narrows('ALLOW','APPROVAL_REQUIRED'))
        self.assertTrue(permission_narrows('ALLOW','DENY'))
        self.assertTrue(permission_narrows('APPROVAL_REQUIRED','DENY'))

    def test_permission_cannot_expand(self):
        self.assertFalse(permission_narrows('DENY','ALLOW'))
        self.assertFalse(permission_narrows('APPROVAL_REQUIRED','ALLOW'))

    def test_model_inference_not_completion_evidence(self):
        self.assertFalse(evidence_can_authorize('MODEL_INFERRED', target_state='COMPLETE'))
        self.assertFalse(evidence_can_authorize('MODEL_INFERRED', high_impact=True))
        self.assertTrue(evidence_can_authorize('MODEL_INFERRED', target_state='ACTIVE'))

    def test_project_extension_requires_provenance(self):
        bad = {'maturity':'PROJECT_LOCAL','provenance':{'reason':'nice to have'}}
        self.assertFalse(project_extension_has_provenance(bad))
        good = {'maturity':'PROJECT_LOCAL','provenance':{'reason_type':'OBSERVED_EVIDENCE','reason':'real gap','evidence_refs':['E1'],'retire_when':'gap removed'}}
        self.assertTrue(project_extension_has_provenance(good))

    def test_harvest_candidate_is_not_builtin(self):
        good = {'maturity':'HARVEST_CANDIDATE','source_project_authoritative':True,'source_project_write_allowed':False,'promotion_status':'UNREVIEWED'}
        self.assertTrue(harvest_candidate_is_safe(good))
        bad = dict(good, promotion_status='BUILTIN')
        self.assertFalse(harvest_candidate_is_safe(bad))

    def test_complete_requires_authoritative_evidence(self):
        self.assertFalse(transition_has_sufficient_evidence('COMPLETE', []))
        self.assertFalse(transition_has_sufficient_evidence('COMPLETE', ['MODEL_INFERRED']))
        self.assertTrue(transition_has_sufficient_evidence('COMPLETE', ['TOOL_OBSERVED']))
        self.assertTrue(transition_has_sufficient_evidence('ACTIVE', []))

    def test_extension_reason_must_be_admissible(self):
        bad = {'maturity':'PROJECT_LOCAL','provenance':{'reason_type':'BEST_PRACTICE','reason':'nice','evidence_refs':['E1'],'retire_when':'never'}}
        self.assertFalse(project_extension_has_provenance(bad))

if __name__ == '__main__':
    unittest.main()
