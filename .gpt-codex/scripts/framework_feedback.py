from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence
_POLICY_FIELDS={"strategy_profile_id","gpt_orchestrator_strategy","codex_implementer_strategy","codex_reviewer_strategy","task_splitting","review_policy","instruction_policy","result_return_policy"}
_COUNTERS=("codex_tasks","codex_retries","gpt_interventions","review_rounds","remediation_rounds","handoffs","handoff_failures")
_FEEDBACK_FIELDS={"problem","reason","local_solution","result","framework_change_recommended","evidence_refs"}
_AUTHORITY_FIELDS={"authorized_actions","framework_mutation","policy_update","release_authority","adoption_authority"}
_PROCESS_EVIDENCE_FIELDS={"source","project_context_id","work_unit_id","state_revision","result_ref","evidence_refs","source_record_refs","completeness","redactions","content","process_record"}
_PROCESS_EVIDENCE_IDENTITY="evidence_identity"
_UNSAFE_EVIDENCE_FIELDS={"raw_prompt","prompt","private_reasoning","reasoning","chain_of_thought","chat_transcript","tool_payload","diff","raw_diff","credential","token","secret","authority","instruction","work_unit","release_authority"}
_EVIDENCE_COMPLETENESS={"COMPLETE","PARTIAL","LOW_CONFIDENCE"}
_FEEDBACK_KINDS={"OBSERVED_GAP","FRICTION","WORKAROUND","ORCHESTRATION_OR_RECOVERY_FAILURE","RELEASE_OR_SYNC_FAILURE","VALIDATOR_FALSE_POSITIVE","CAPABILITY_REUSE_SUCCESS","PRESERVATION_EVIDENCE"}
_WORK_UNIT_RECORD_FIELDS={"work_unit_id","final_result","codex_retries","gpt_interventions","review_rounds","remediation_rounds","handoff_result","usage","git_sha","result_ref"}
@dataclass(frozen=True, slots=True)
class ProcessReview:
    strategy_profile: str; codex_tasks: int; codex_retries: int; gpt_interventions: int; review_rounds: int; remediation_rounds: int; handoffs: int; handoff_failures: int; project_result: str; usage: Mapping[str, Any] | str; work_unit_ids: tuple[str, ...]=(); result_refs: tuple[str, ...]=(); success_observations: tuple[str, ...]=(); failure_observations: tuple[str, ...]=(); evidence_refs: tuple[str, ...]=()
@dataclass(frozen=True, slots=True)
class FrameworkFeedback:
    problem: str; reason: str; local_solution: str; result: str; framework_change_recommended: bool; evidence_refs: tuple[str, ...]
def validate_execution_policy(policy: Mapping[str, Any] | None) -> list[str]:
    if policy is None:return []
    strings=_POLICY_FIELDS-{"task_splitting","review_policy","instruction_policy","result_return_policy"}
    if not isinstance(policy,Mapping) or set(policy)!=_POLICY_FIELDS or any(not isinstance(policy.get(k),str) or not policy[k].strip() or len(policy[k])>128 for k in strings) or policy.get("task_splitting")!="PROJECT_DETERMINED" or policy.get("instruction_policy")!="REFERENCE_FIRST" or policy.get("result_return_policy")!="DURABLE_REF_FIRST" or policy.get("review_policy") not in {"RISK_OR_MILESTONE","EXPLICIT"}:return ["EXECUTION_POLICY_INVALID"]
    return []

def validate_project_strategy_lifecycle(policy: Mapping[str, Any] | None, work_units: Sequence[Mapping[str, Any]], *, governed_strategy_change: Mapping[str, Any] | None=None) -> list[str]:
    """Keep adopted Strategy authority at the Project, never a local Work Unit."""
    if policy is None:
        return []
    if validate_execution_policy(policy) or not isinstance(work_units, Sequence):
        return ["RECONCILIATION_REQUIRED"]
    profile = policy["strategy_profile_id"]
    if governed_strategy_change is not None and (
        not isinstance(governed_strategy_change, Mapping)
        or set(governed_strategy_change) != {"requirement_ref", "accepted_strategy_profile_id"}
        or not all(isinstance(governed_strategy_change.get(key), str) and governed_strategy_change[key].strip() for key in governed_strategy_change)
        or governed_strategy_change["accepted_strategy_profile_id"] != profile
    ):
        return ["RECONCILIATION_REQUIRED"]
    for work_unit in work_units:
        if not isinstance(work_unit, Mapping) or not isinstance(work_unit.get("work_unit_id"), str) or not work_unit["work_unit_id"].strip() or work_unit.get("strategy_profile_id") != profile:
            return ["RECONCILIATION_REQUIRED"]
    return []

def validate_work_unit_process_record(record: Mapping[str, Any]) -> list[str]:
    if not isinstance(record, Mapping) or set(record) != _WORK_UNIT_RECORD_FIELDS:
        return ["PROCESS_REVIEW_INVALID"]
    text_fields = _WORK_UNIT_RECORD_FIELDS-{"codex_retries","gpt_interventions","review_rounds","remediation_rounds","usage"}
    if any(not isinstance(record.get(key), str) or not record[key].strip() for key in text_fields):
        return ["PROCESS_REVIEW_INVALID"]
    if any(not isinstance(record.get(key), int) or isinstance(record[key], bool) or record[key] < 0 for key in ("codex_retries","gpt_interventions","review_rounds","remediation_rounds")):
        return ["PROCESS_REVIEW_INVALID"]
    usage = record.get("usage")
    if usage != "UNKNOWN" and not isinstance(usage, Mapping):
        return ["PROCESS_REVIEW_INVALID"]
    return []

def build_process_review(records: Sequence[Mapping[str, Any]], strategy_profile: str, usage: Mapping[str, Any] | None=None) -> ProcessReview:
    totals={k:0 for k in _COUNTERS}; result="UNKNOWN"; work_unit_ids=[]; result_refs=[]; record_usage=[]
    for record in records:
        if not isinstance(record,Mapping):raise ValueError("PROCESS_REVIEW_INVALID")
        if "work_unit_id" in record:
            if validate_work_unit_process_record(record):raise ValueError("PROCESS_REVIEW_INVALID")
            work_unit_ids.append(record["work_unit_id"]); result_refs.append(record["result_ref"])
            totals["codex_tasks"]+=1
            if isinstance(record["usage"], Mapping): record_usage.append(record["usage"])
        for key in _COUNTERS:
            value=record.get(key,0)
            if not isinstance(value,int) or isinstance(value,bool) or value<0:raise ValueError("PROCESS_REVIEW_INVALID")
            totals[key]+=value
        final = record.get("final_result", record.get("project_result"))
        if isinstance(final,str) and final.strip():result=final
    resolved_usage = dict(usage) if isinstance(usage, Mapping) else _aggregate_record_usage(record_usage)
    return ProcessReview(strategy_profile,**totals,project_result=result,usage=resolved_usage,work_unit_ids=tuple(work_unit_ids),result_refs=tuple(result_refs))

def _aggregate_record_usage(values: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | str:
    if not values or not all(set(value) == set(values[0]) and value for value in values): return "UNKNOWN"
    if any(any(not isinstance(amount, int) or isinstance(amount, bool) or amount < 0 for amount in value.values()) for value in values): return "UNKNOWN"
    return {key: sum(value[key] for value in values) for key in values[0]}

def _canonical_identity(prefix: str, value: Mapping[str, Any]) -> str:
    payload=json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=list).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(payload).hexdigest()}"

def _safe_refs(value: object) -> bool:
    return isinstance(value,list) and bool(value) and len(value)<=32 and all(isinstance(item,str) and item.strip() and len(item)<=256 for item in value)

def _bounded_process_record(record: Mapping[str, Any]) -> bool:
    """Apply C1 serialization and size limits to the legacy process-record shape."""
    if any(not isinstance(record.get(key),str) or len(record[key])>256 for key in ("work_unit_id","final_result","handoff_result","git_sha","result_ref")):
        return False
    usage=record.get("usage")
    return usage == "UNKNOWN" or (
        isinstance(usage,Mapping) and bool(usage) and len(usage)<=32
        and all(isinstance(key,str) and key and len(key)<=64 and isinstance(value,int) and not isinstance(value,bool) and value>=0 for key,value in usage.items())
    )

def validate_process_evidence(record: Mapping[str, Any]) -> list[str]:
    """Validate bounded, observable evidence without granting any authority."""
    if not isinstance(record,Mapping): return ["PROCESS_EVIDENCE_INVALID"]
    keys=set(record)
    if keys-{*_PROCESS_EVIDENCE_FIELDS,_PROCESS_EVIDENCE_IDENTITY} or not _PROCESS_EVIDENCE_FIELDS.issubset(keys): return ["PROCESS_EVIDENCE_INVALID"]
    if _UNSAFE_EVIDENCE_FIELDS.intersection(keys): return ["PROCESS_EVIDENCE_INVALID"]
    if any(not isinstance(record.get(key),str) or not record[key].strip() or len(record[key])>256 for key in ("source","project_context_id","work_unit_id","result_ref")): return ["PROCESS_EVIDENCE_INVALID"]
    if not isinstance(record.get("state_revision"),int) or isinstance(record["state_revision"],bool) or record["state_revision"]<0: return ["PROCESS_EVIDENCE_INVALID"]
    if record.get("completeness") not in _EVIDENCE_COMPLETENESS or not _safe_refs(record.get("evidence_refs")) or not _safe_refs(record.get("source_record_refs")): return ["PROCESS_EVIDENCE_INVALID"]
    if not isinstance(record.get("redactions"),list) or len(record["redactions"])>32 or not all(isinstance(item,str) and item.strip() and len(item)<=64 for item in record["redactions"]): return ["PROCESS_EVIDENCE_INVALID"]
    content=record.get("content")
    if not isinstance(content,Mapping) or not content or len(content)>16 or any(not isinstance(key,str) or not key or len(key)>64 or key.lower() in _UNSAFE_EVIDENCE_FIELDS or not isinstance(value,str) or len(value)>512 for key,value in content.items()): return ["PROCESS_EVIDENCE_INVALID"]
    process=record.get("process_record")
    if process is not None and (validate_work_unit_process_record(process) or not _bounded_process_record(process)): return ["PROCESS_EVIDENCE_INVALID"]
    identity=record.get(_PROCESS_EVIDENCE_IDENTITY)
    base={key:record[key] for key in _PROCESS_EVIDENCE_FIELDS}
    if identity is not None and (not isinstance(identity,str) or identity!=_canonical_identity("process-evidence",base)): return ["PROCESS_EVIDENCE_INVALID"]
    return []

def normalize_process_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    if validate_process_evidence(record): raise ValueError("PROCESS_EVIDENCE_INVALID")
    normalized={key:record[key] for key in _PROCESS_EVIDENCE_FIELDS}
    normalized["evidence_refs"]=list(dict.fromkeys(normalized["evidence_refs"]))
    normalized["source_record_refs"]=list(dict.fromkeys(normalized["source_record_refs"]))
    normalized["redactions"]=list(dict.fromkeys(normalized["redactions"]))
    normalized["content"]={key:normalized["content"][key] for key in sorted(normalized["content"])}
    normalized[_PROCESS_EVIDENCE_IDENTITY]=_canonical_identity("process-evidence",normalized)
    return normalized

def build_process_review_from_evidence(evidence: Sequence[Mapping[str, Any]], strategy_profile: str) -> ProcessReview:
    """Connect only complete, unique bounded evidence to the existing review owner."""
    seen=set(); records=[]; successes=[]; failures=[]; refs=[]
    for item in evidence:
        if validate_process_evidence(item): raise ValueError("PROCESS_EVIDENCE_INVALID")
        identity=item.get(_PROCESS_EVIDENCE_IDENTITY) or normalize_process_evidence(item)[_PROCESS_EVIDENCE_IDENTITY]
        if identity in seen: continue
        seen.add(identity)
        if item["completeness"] != "COMPLETE": continue
        refs.append(identity)
        observation=item["content"].get("observation")
        outcome=item["content"].get("outcome", "")
        if observation:
            (successes if outcome.upper() in {"PASS","SUCCESS"} else failures).append(observation)
        if item["process_record"] is not None: records.append(item["process_record"])
    review=build_process_review(records,strategy_profile)
    return ProcessReview(review.strategy_profile,review.codex_tasks,review.codex_retries,review.gpt_interventions,review.review_rounds,review.remediation_rounds,review.handoffs,review.handoff_failures,review.project_result,review.usage,review.work_unit_ids,review.result_refs,tuple(successes),tuple(failures),tuple(refs))

def _process_review_ref(review: ProcessReview) -> str:
    return _canonical_identity("process-review", {"work_unit_ids":list(review.work_unit_ids),"result_refs":list(review.result_refs),"evidence_refs":list(review.evidence_refs),"result":review.project_result})

def derive_framework_feedback(review: ProcessReview, evidence: Sequence[Mapping[str, Any]], *, kind: str) -> dict[str, Any]:
    if kind not in _FEEDBACK_KINDS or not isinstance(review,ProcessReview): raise ValueError("FRAMEWORK_FEEDBACK_INVALID")
    normalized=[normalize_process_evidence(item) for item in evidence]
    if not normalized or any(item["completeness"] == "LOW_CONFIDENCE" for item in normalized): raise ValueError("FRAMEWORK_FEEDBACK_INVALID")
    refs=list(dict.fromkeys([_process_review_ref(review),*[item[_PROCESS_EVIDENCE_IDENTITY] for item in normalized]]))
    observations=[item["content"].get("observation",kind) for item in normalized]
    record={"problem":kind,"reason":"; ".join(observations)[:512],"local_solution":"Management review only; no mutation is authorized.","result":review.project_result,"framework_change_recommended":kind not in {"CAPABILITY_REUSE_SUCCESS","PRESERVATION_EVIDENCE"},"evidence_refs":refs}
    if validate_framework_feedback(record): raise ValueError("FRAMEWORK_FEEDBACK_INVALID")
    return record

def build_improvement_candidate(feedback: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]], *, problem_class: str, management_question: str) -> dict[str, Any]:
    if validate_framework_feedback(feedback) or problem_class not in _FEEDBACK_KINDS or not isinstance(management_question,str) or not management_question.strip() or len(management_question)>512: raise ValueError("IMPROVEMENT_CANDIDATE_INVALID")
    normalized=[normalize_process_evidence(item) for item in evidence]
    if not normalized: raise ValueError("IMPROVEMENT_CANDIDATE_INVALID")
    base={"feedback_refs":list(feedback["evidence_refs"]),"evidence_refs":[item[_PROCESS_EVIDENCE_IDENTITY] for item in normalized],"problem_class":problem_class,"current_relevance":"UNASSESSED","existing_capability_facts":[item["content"].get("observation","") for item in normalized],"preservation_constraints":["NO_MUTATION","EXISTING_OWNER_ONLY"],"management_question":management_question,"status":"OBSERVATION_ONLY"}
    return {"candidate_identity":_canonical_identity("improvement-candidate",base),**base}

def classify_recurrence_relevance(evidence: Sequence[Mapping[str, Any]], *, resolution: str | None=None, preservation: bool=False, authoritative_source: bool=False) -> dict[str, Any]:
    if authoritative_source: raise ValueError("NON_AUTHORITY_BOUNDARY")
    normalized=[normalize_process_evidence(item) for item in evidence]
    if not normalized: raise ValueError("PROCESS_EVIDENCE_INVALID")
    if any(item["completeness"] != "COMPLETE" for item in normalized): raise ValueError("INCOMPLETE_PROCESS_EVIDENCE")
    correlation_outcomes={}
    for item in normalized:
        outcome=item["content"].get("outcome")
        for ref in item["source_record_refs"]:
            previous=correlation_outcomes.setdefault(ref,outcome)
            if previous != outcome: raise ValueError("CORRELATION_CONFLICT")
    if resolution == "RETRACTED": classification="INVALIDATED_OR_RETRACTED"
    elif resolution == "SUPERSEDED": classification="SUPERSEDED"
    elif resolution == "RESOLVED": classification="ALREADY_RESOLVED"
    elif preservation: classification="PRESERVATION_EVIDENCE"
    else: classification="REPEATED_CURRENT" if len({item[_PROCESS_EVIDENCE_IDENTITY] for item in normalized})>1 else "SINGLE_CURRENT"
    return {"classification":classification,"source_refs":list(dict.fromkeys(item[_PROCESS_EVIDENCE_IDENTITY] for item in normalized))}

def classify_harvest_relation(candidate: Mapping[str, Any]) -> dict[str, Any]:
    route=candidate.get("existing_harvest_route") if isinstance(candidate,Mapping) else None
    classification="NO_HARVEST_RELATION" if route is None else ("HARVEST_REFERENCE_ELIGIBLE" if isinstance(route,str) and route.startswith("harvest:") else "HARVEST_RELATION_AMBIGUOUS")
    return {"classification":classification,"candidate_identity":candidate.get("candidate_identity") if isinstance(candidate,Mapping) else None,"harvest_route_ref":route if classification=="HARVEST_REFERENCE_ELIGIBLE" else None}

def build_framework_management_review_input(review: ProcessReview, feedback: Mapping[str, Any], candidate: Mapping[str, Any], evidence: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(review,ProcessReview) or validate_framework_feedback(feedback) or not isinstance(candidate,Mapping) or not isinstance(candidate.get("candidate_identity"),str): raise ValueError("MANAGEMENT_REVIEW_INPUT_INVALID")
    relevance=classify_recurrence_relevance(evidence)
    return {"evidence_refs":relevance["source_refs"],"feedback_refs":list(feedback["evidence_refs"]),"candidate_identity":candidate["candidate_identity"],"recurrence_relevance":relevance,"existing_capability_facts":list(candidate.get("existing_capability_facts",[])),"preservation_constraints":list(candidate.get("preservation_constraints",[])),"management_question":candidate.get("management_question"),"decision":"NO_DECISION","mutation":"NO_MUTATION"}
def validate_framework_feedback(record: Mapping[str, Any]) -> list[str]:
    if not isinstance(record,Mapping) or set(record)!=_FEEDBACK_FIELDS or _AUTHORITY_FIELDS & set(record) or any(not isinstance(record.get(k),str) or not record[k].strip() for k in ("problem","reason","local_solution","result")) or not isinstance(record.get("framework_change_recommended"),bool) or not isinstance(record.get("evidence_refs"),list) or not record["evidence_refs"] or not all(isinstance(ref,str) and ref.strip() for ref in record["evidence_refs"]):return ["FRAMEWORK_FEEDBACK_INVALID"]
    return []

def validate_framework_evolution_boundary(project_control: Mapping[str, Any], feedback: Mapping[str, Any]) -> list[str]:
    errors = validate_framework_feedback(feedback)
    if errors:
        return errors
    if not isinstance(project_control, Mapping):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    if project_control.get("framework_management_only") is True:
        return []
    roots = project_control.get("roots")
    if not isinstance(roots, Mapping):
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    if roots.get("project_role") != "AUTHORITATIVE" or roots.get("framework_role") != "ADVISORY":
        return ["PROJECT_AUTHORITY_BOUNDARY_VIOLATION"]
    return []

def framework_feedback_authorizes_mutation(project_control: Mapping[str, Any], feedback: Mapping[str, Any]) -> bool:
    return False

def evaluate_structure_change(before_capabilities: set[str], after_capabilities: set[str], evidence: Mapping[str, Any]) -> str:
    if not before_capabilities.issubset(after_capabilities):
        return "CAPABILITY_REGRESSION"
    benefits = (
        evidence.get("complexity_decreased") is True,
        evidence.get("responsibility_clearer") is True,
        evidence.get("deployment_maintenance_testing_improved") is True,
    )
    return "ALLOW" if any(benefits) else "NO_BENEFIT"
