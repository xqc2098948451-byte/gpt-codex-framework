# R3 Result/Evidence normalization authority

执行 L6A_R3_RESULT_EVIDENCE_NORMALIZATION_REMEDIATION。

问题已裁定：

L6A-R3-EXACT-RESULT-NATIVE-HANDOFF-001

根因：
原 R3 Result 的 evidence_refs 中包含 8 个绝对本地路径，
不符合 native durable handoff contract。

这不是 physical execution failure。

已接受且禁止重做的事实：

E015_RETIREMENT = PASS
E027_RETIREMENT = PASS
E029_CHILD_RETIREMENT = PASS_2_OF_2
E029_OUTER_SOURCE_RETIREMENT = PASS

REGISTERED_WORKTREES_RETIRED = 4
RECOVERY_SNAPSHOT_INTEGRITY = PASS
PROVEN_PROJECT_PATH_ESCAPE = 0
UNKNOWN_EXTERNAL_COUNT = 83
UNIQUE_DATA_LOSS = 0
GIT_INTEGRITY = PASS
WORKTREE_REGISTRY_INTEGRITY = PASS
PROJECT_BINDING_INTEGRITY = PASS

==================================================
1. Preserve original Result
==================================================

原本地 immutable Result：

f09fa950f590cd83dcbf1dbb401fa07e733101f7 /
.gpt-codex/evidence/results/RESULT-L6A-EXTERNAL-WORKTREE-RETIREMENT-001.json /
1ec236a741c5848f603e6eca9dddeb54d1266da8

保持不变。

不要：
- 改写该 blob
- 把它伪装成 native-valid Result
- 原样集成到 main 作为 canonical PASS Result

它作为：
SUPERSEDED_LOCAL_RESULT
保留历史 provenance。

==================================================
2. Inventory the 8 invalid evidence_refs
==================================================

逐项读取原 Result 的 8 个绝对 evidence_refs。

分类：

A. DURABLE_CLOSURE_EVIDENCE_REQUIRED
   对 R3 PASS / integrity / no-data-loss / retirement
   有实质证明作用。

B. LOCAL_PROCESS_DETAIL
   仅为 raw log、重复报告、派生展示或可重建过程材料。

禁止简单把绝对路径字符串替换成相对路径。

==================================================
3. Materialize repo-native durable Evidence
==================================================

对 A 类证据创建最小充分的 repo-native Evidence。

目标使用现有：

.gpt-codex/evidence/

或：

.gpt-codex/evidence/results/

不要创建新的 authority subsystem。

每个 durable Evidence 至少绑定：

- evidence_id
- project/context/repository identity
- R3 Work Unit / Instruction identity
- evidence purpose
- observed facts
- source artifact SHA-256
- source byte size
- relevant inventory/digest
- reviewer status
- no-data-loss / Git / registry / binding facts as applicable

如果多个本地文件证明同一事实，
允许合并成一个 bounded durable Evidence record，
但必须保存每个 source artifact 的 SHA-256 映射。

不要把原绝对本地路径作为 Result locator。

如确需 provenance，可使用非权威描述字段，
但 native evidence_refs 必须全部为 repo-relative durable paths。

==================================================
4. Generate a corrected R3 Result
==================================================

新建：

RESULT-L6A-EXTERNAL-WORKTREE-RETIREMENT-001-CORRECTED.json

或遵循现有 Result naming convention 的 exact 新 ID。

它必须明确：

supersedes_result =
original R3 Result identity

remediation_reason =
ABSOLUTE_LOCAL_EVIDENCE_REFS_NOT_NATIVE_DURABLE

physical_execution_replayed = NO

原 Result 与 corrected Result 的 execution facts 必须一致。

机械比较除以下字段外不得发生语义变化：

允许变化：
- result_id
- evidence_refs
- artifact_locator
- sync/publication continuity fields
- remediation/supersession metadata
- remote verification fields
- exact fields因新 integration SHA 必须变化者

禁止变化：
- execution outcome
- changed scope
- retirement counts
- worktree identities
- recovery snapshot conclusions
- path escape conclusion
- UNKNOWN83 conclusion
- data-loss conclusion
- Git/registry/project-binding conclusions

要求：

EXECUTION_FACTS_EQUIVALENT = PASS
PHYSICAL_EXECUTION_REPLAYED = NO

==================================================
5. Correct evidence_refs format
==================================================

corrected Result 的 evidence_refs：

只能引用 repo-relative durable Evidence，例如：

.gpt-codex/evidence/<...>.json
.gpt-codex/evidence/results/<...>.json
.gpt-codex/evidence/instructions/<...>.json
.gpt-codex/work-units/<...>.json

不得包含：

D:\
C:\
absolute filesystem path
file://
repo-external transient path

检查：

ABSOLUTE_EVIDENCE_REF_COUNT = 0
NON_DURABLE_EVIDENCE_REF_COUNT = 0

==================================================
6. New remediation authority
==================================================

不要使用旧 R3 Instruction 自行修改 Result。

生成独立：

- remediation Work Unit
- FIX/RECONCILIATION Instruction
- durable Evidence materialization
- corrected Result
- independent PRE/review

scope 仅限：

Result/Evidence normalization
+
durable integration

禁止 physical retirement mutation。

==================================================
7. Integration
==================================================

PRE PASS 后：

将以下内容按 native governance 集成到 main：

- valid R3 Work Unit / Instruction lineage as required
- remediation Work Unit / Instruction
- normalized durable Evidence
- corrected R3 Result

原 invalid local Result 不要求作为 canonical Result 集成。

集成后 remote verify：

- exact durable paths exist
- blobs match reviewed candidate
- evidence_refs resolve
- native result validation PASS
- native handoff no longer returns RECONCILIATION_REQUIRED

corrected Result 最终必须满足：

remote_verification = VERIFIED
publication_authority = CONFIRMED_PUBLICATION
sync_status = SYNCED

仅在真实 remote verification 后设置。

==================================================
8. Then L6A durable closure
==================================================

只有 corrected R3 Result native-valid 且 remote verified 后：

继续生成：

local-workspace-consolidation-l6a-durable-closure-001

L6A closure 继续记录：

CODEX_PROJECT_SOURCE_ROOT =
D:\通用开发框架管理

PROVEN_PROJECT_PATH_ESCAPE = 0

UNKNOWN_EXTERNAL_COUNT = 83

UNKNOWN semantics =
OWNERSHIP_NOT_PROVEN
NOT_COUNTED_AS_PROJECT_PATH_ESCAPE
KEEP_UNTIL_NEW_EVIDENCE

STATE 才允许从 revision 28 按 native contract 更新。

==================================================
9. Independent checks
==================================================

必须检查：

ORIGINAL_RESULT_BLOB_UNCHANGED = YES
CORRECTED_RESULT_EXECUTION_FACTS_EQUIVALENT = PASS
ABSOLUTE_EVIDENCE_REF_COUNT = 0
DURABLE_EVIDENCE_RESOLUTION = PASS
PHYSICAL_EXECUTION_REPLAYED = NO

R3_NATIVE_HANDOFF = PASS
R3_REMOTE_INTEGRATION = PASS

然后才允许：
L6A_DURABLE_CLOSURE = PASS

==================================================
回传
==================================================

R3_RESULT_REMEDIATION = PASS | FINDING

ORIGINAL_RESULT_BLOB_UNCHANGED = YES | NO
SOURCE_EVIDENCE_REF_COUNT = 8
DURABLE_EVIDENCE_CREATED = <n>
LOCAL_PROCESS_DETAIL_EXCLUDED = <n>

ABSOLUTE_EVIDENCE_REF_COUNT = 0 | <n>
DURABLE_EVIDENCE_RESOLUTION = PASS | FAIL
EXECUTION_FACTS_EQUIVALENT = PASS | FAIL
PHYSICAL_EXECUTION_REPLAYED = NO

REMEDIATION_WORK_UNIT_LOCATOR = <locator>
REMEDIATION_INSTRUCTION_LOCATOR = <locator>
CORRECTED_R3_RESULT_LOCATOR = <locator>

R3_NATIVE_HANDOFF = PASS | FAIL
R3_REMOTE_INTEGRATION = PASS | FAIL

L6A_DURABLE_CLOSURE = PASS | FAIL
L6A_CLOSURE_RESULT_LOCATOR = <locator | NOT_CREATED>

STATE_REVISION_BEFORE = 28
STATE_REVISION_AFTER = <n>
STATE_STATUS = PASS | FAIL

PROVEN_PROJECT_PATH_ESCAPE = 0
UNKNOWN_EXTERNAL_COUNT = 83

INDEPENDENT_POST = PASS | FINDING
READY_FOR_L7 = YES | NO
L7_STARTED = NO

FINDINGS = [...]
BLOCKERS = [...]
RETURN_TO_GPT = YES