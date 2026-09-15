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
  for kwargs in ({"scope":[]},{"constraints":[]},{"done":[]},{"constraints":[""]},{"done":"x"},{"scope":["x"]*101}):
   values={"goal":"g","scope":["a"],"constraints":["b"],"done":["c"]};values.update(kwargs)
   with self.subTest(kwargs=kwargs):
    with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,**values)
  for refs in ({"UNKNOWN":"x"},{"PLAN_REF":" "}):
   with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,goal="g",scope=["a"],constraints=["b"],done=["c"],refs=refs)
  for transfer in ({"upload_required":True,"source":"x"},{"upload_required":True,"items":[],"source":"x"},{"upload_required":False,"source":" ","items":[]},{"upload_required":"yes","source":"x"}):
   with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task(base,goal="g",scope=["a"],constraints=["b"],done=["c"],transfer=transfer)
 def test_no_upload_source_and_reference_order_are_frozen(self):
  envelope={"instruction_id":"i","instruction_type":"t","target_work_unit":"w","expected_base_sha":"a"*40}
  refs={"STRATEGY_PROFILE":"p","PLAN_REF":"plan","OPEN_FINDINGS":"NONE"}
  text=render_minimal_codex_task(envelope,goal="g",scope=["a"],constraints=["b"],done=["c"],refs=refs)
  self.assertLess(text.index("BASE_SHA:"),text.index("PLAN_REF:"))
  self.assertLess(text.index("PLAN_REF:"),text.index("OPEN_FINDINGS:"))
  self.assertLess(text.index("OPEN_FINDINGS:"),text.index("STRATEGY_PROFILE:"))
  for source in ("attachment","当前附件","other source"):
   with self.subTest(source=source):
    with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task({},goal="g",scope=["a"],constraints=["b"],done=["c"],transfer={"upload_required":False,"source":source})
 def test_complete_transfer_and_output_regression_lock(self):
  base={"instruction_id":"i","instruction_type":"t","target_work_unit":"w","expected_base_sha":"a"*40}
  text=render_minimal_codex_task(base,goal="g",scope=["a"],constraints=["b"],done=["c"],refs={"PLAN_REF":"p","STRATEGY_PROFILE":"s"},transfer={"upload_required":False,"source":"Git SHA:path"})
  self.assertEqual(text.splitlines()[:3],["是否需要你上传内容：不需要","需要上传的内容：无","读取来源：Git SHA:path"])
  for left,right in zip(("是否需要你上传内容","需要上传的内容","读取来源","INSTRUCTION_ID","INSTRUCTION_TYPE","TARGET_WORK_UNIT","BASE_SHA","PLAN_REF","STRATEGY_PROFILE","GOAL","SCOPE","CONSTRAINTS"),("需要上传的内容","读取来源","INSTRUCTION_ID","INSTRUCTION_TYPE","TARGET_WORK_UNIT","BASE_SHA","PLAN_REF","STRATEGY_PROFILE","GOAL","SCOPE","CONSTRAINTS","DONE")):self.assertLess(text.index(left),text.index(right))
  bad_transfers=[{"upload_required":False},{"upload_required":False,"source":"Git SHA:path","items":[]},{"upload_required":False,"source":"Git SHA:path","extra":"x"},{"upload_required":True,"items":[""],"source":"x"},{"upload_required":True,"items":[" "],"source":"x"},{"upload_required":True,"items":[123],"source":"x"},{"upload_required":True,"items":["x"]*101,"source":"x"},{"upload_required":True,"items":["x"]},{"upload_required":True,"items":["x"],"source":" "},{"upload_required":True,"items":["x"],"source":"x","extra":"x"},"invalid",[],123,{"upload_required":"yes","source":"Git SHA:path"}]
  for transfer in bad_transfers:
   with self.subTest(transfer=transfer):
    with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task({},goal="g",scope=["a"],constraints=["b"],done=["c"],transfer=transfer)
  with self.assertRaisesRegex(ValueError,"MINIMAL_TASK_INVALID"):render_minimal_codex_task({},goal="g",scope=["a"],constraints=["b"],done=["c"],refs={"PLAN_REF":123})
  upload=render_minimal_codex_task({},goal="g",scope=["a"],constraints=["b"],done=["c"],transfer={"upload_required":True,"items":["file-a","file-b"],"source":"当前附件"})
  self.assertIn("需要上传的内容：file-a、file-b",upload)
if __name__=="__main__":unittest.main()
