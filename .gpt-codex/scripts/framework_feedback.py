from dataclasses import dataclass
from typing import Any, Mapping, Sequence
_POLICY_FIELDS={"strategy_profile_id","gpt_orchestrator_strategy","codex_implementer_strategy","codex_reviewer_strategy","task_splitting","review_policy","instruction_policy","result_return_policy"}
_COUNTERS=("codex_tasks","codex_retries","gpt_interventions","review_rounds","remediation_rounds","handoffs","handoff_failures")
_FEEDBACK_FIELDS={"problem","reason","local_solution","result","framework_change_recommended","evidence_refs"}
_AUTHORITY_FIELDS={"authorized_actions","framework_mutation","policy_update","release_authority","adoption_authority"}
@dataclass(frozen=True, slots=True)
class ProcessReview:
    strategy_profile: str; codex_tasks: int; codex_retries: int; gpt_interventions: int; review_rounds: int; remediation_rounds: int; handoffs: int; handoff_failures: int; project_result: str; usage: Mapping[str, Any] | str
@dataclass(frozen=True, slots=True)
class FrameworkFeedback:
    problem: str; reason: str; local_solution: str; result: str; framework_change_recommended: bool; evidence_refs: list[str]
def validate_execution_policy(policy: Mapping[str, Any] | None) -> list[str]:
    if policy is None:return []
    strings=_POLICY_FIELDS-{"task_splitting","review_policy","instruction_policy","result_return_policy"}
    if not isinstance(policy,Mapping) or set(policy)!=_POLICY_FIELDS or any(not isinstance(policy.get(k),str) or not policy[k].strip() or len(policy[k])>128 for k in strings) or policy.get("task_splitting")!="PROJECT_DETERMINED" or policy.get("instruction_policy")!="REFERENCE_FIRST" or policy.get("result_return_policy")!="DURABLE_REF_FIRST" or policy.get("review_policy") not in {"RISK_OR_MILESTONE","EXPLICIT"}:return ["EXECUTION_POLICY_INVALID"]
    return []
def build_process_review(records: Sequence[Mapping[str, Any]], strategy_profile: str, usage: Mapping[str, Any] | None=None) -> ProcessReview:
    totals={k:0 for k in _COUNTERS}; result="UNKNOWN"
    for record in records:
        if not isinstance(record,Mapping):raise ValueError("PROCESS_REVIEW_INVALID")
        for key in _COUNTERS:
            value=record.get(key,0)
            if not isinstance(value,int) or isinstance(value,bool) or value<0:raise ValueError("PROCESS_REVIEW_INVALID")
            totals[key]+=value
        if isinstance(record.get("project_result"),str) and record["project_result"].strip():result=record["project_result"]
    return ProcessReview(strategy_profile,**totals,project_result=result,usage=dict(usage) if isinstance(usage,Mapping) else "UNKNOWN")
def validate_framework_feedback(record: Mapping[str, Any]) -> list[str]:
    if not isinstance(record,Mapping) or set(record)!=_FEEDBACK_FIELDS or _AUTHORITY_FIELDS & set(record) or any(not isinstance(record.get(k),str) or not record[k].strip() for k in ("problem","reason","local_solution","result")) or not isinstance(record.get("framework_change_recommended"),bool) or not isinstance(record.get("evidence_refs"),list):return ["FRAMEWORK_FEEDBACK_INVALID"]
    return []
