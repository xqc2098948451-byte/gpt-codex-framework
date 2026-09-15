import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/".gpt-codex/scripts"))
from instruction_envelope import render_minimal_codex_task
class MinimalTaskProtocolTests(unittest.TestCase):
 def test_sections_refs_and_default_transfer(self):
  text=render_minimal_codex_task({"instruction_id":"i","instruction_type":"EXECUTION_INSTRUCTION","target_work_unit":"WU","expected_base_sha":"a"*40},goal="Go",scope=["a"],constraints=["b"],done=["c"],refs={"STRATEGY_PROFILE":"P"})
  for key in ("GOAL:","SCOPE:","CONSTRAINTS:","DONE:","BASE_SHA:","STRATEGY_PROFILE:"):self.assertIn(key,text)
  self.assertTrue(text.startswith("是否需要你上传内容：不需要"))
 def test_invalid_inputs_and_upload_transfer(self):
  with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task({},goal="",scope=["a"],constraints=["b"],done=["c"])
  text=render_minimal_codex_task({},goal="g",scope=["a"],constraints=["b"],done=["c"],transfer={"upload_required":True,"items":["f"],"source":"attachment"})
  self.assertTrue(text.startswith("是否需要你上传内容：需要"))
 def test_lists_refs_and_transfer_fail_closed(self):
  base={"instruction_id":"i","instruction_type":"t","target_work_unit":"w"}
  for kwargs in ({"scope":[]},{"constraints":[""]},{"done":"x"},{"scope":["x"]*101}):
   values={"goal":"g","scope":["a"],"constraints":["b"],"done":["c"]};values.update(kwargs)
   with self.subTest(kwargs=kwargs):
    with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,**values)
  for refs in ({"UNKNOWN":"x"},{"PLAN_REF":" "}):
   with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,goal="g",scope=["a"],constraints=["b"],done=["c"],refs=refs)
  for transfer in ({"upload_required":True,"source":"x"},{"upload_required":True,"items":[],"source":"x"},{"upload_required":False,"source":" ","items":[]},{"upload_required":"yes","source":"x"}):
   with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,goal="g",scope=["a"],constraints=["b"],done=["c"],transfer=transfer)
if __name__=="__main__":unittest.main()
