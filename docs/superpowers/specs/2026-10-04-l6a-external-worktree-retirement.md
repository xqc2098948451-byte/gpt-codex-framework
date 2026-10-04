# Exact R3 user retirement authority

执行 L6A_E015_E027_E029_EXTERNAL_WORKTREE_RETIREMENT。

GPT_DECISION：

R1 / R2 evidence accepted：

E170_EXECUTION = PASS
E170_POST = PASS

E015_SNAPSHOT = PASS
E027_SNAPSHOT = PASS
E029_SNAPSHOT = PASS

RECOVERY_SNAPSHOT_SELF_CONTAINED = PASS
BYTE_IDENTITY = PASS
GIT_STATE_CAPTURE = PASS
TRACKED_DELETION_PRESERVATION = PASS
UNIQUE_DATA_LOSS = 0

因此：

READY_FOR_E015_E027_E029_RETIREMENT = YES

目标：
安全退休 E015 / E027 / E029 的根外 registered worktree/source，
将：

PROVEN_PROJECT_PATH_ESCAPE = 3 -> 0

==================================================
1. Authority
==================================================

生成并持久化 exact：

- Work Unit
- Instruction
- source/worktree retirement matrix
- recovery snapshot locators/digests
- Native PRE

scope 仅限：
E015
E027
E029

如果 PRE 不通过：
停止，不执行任何 retirement。

==================================================
2. Immediate PRE
==================================================

对每个 registered worktree 在 mutation 紧邻前重新确认：

- exact source path
- Git common directory
- registry entry
- HEAD/ref
- dirty/staged/untracked state
- tracked deletion digest
- active process / handle / lease
- recovery snapshot exists
- recovery snapshot hash/inventory still matches captured source state
- no new unique source data appeared after R2
- main/repository identity unchanged

任何 drift：
该 storage unit KEEP，并返回 FINDING。

==================================================
3. E015 / E027 retirement
==================================================

它们不迁移成新的 active worktree。

使用 Git-native worktree retirement：

registered worktree
→ remove/deregister through Git-aware mechanism
→ verify registry entry absent
→ verify common-dir administrative entry cleaned
→ verify external source absent or safe-to-remove

因为原 worktree 含 tracked deletions / dirty state，
只有在 recovery snapshot freshness 再验证 PASS 后，
才允许使用必要的 force retirement。

禁止：
checkout
restore
reset
clean
stash
commit
merge

如果 Git-native remove 失败：
停止该项。
不得直接先 rm/rmdir worktree source。

==================================================
4. E029 composite retirement
==================================================

E029 含：
- 2 registered child worktrees
- 4 outer scripts
- admin-local data
- 373 tracked deletions

顺序必须：

A. fresh verify E029 recovery snapshot
B. child worktree #1 Git-native retirement
C. verify registry/admin cleanup
D. child worktree #2 Git-native retirement
E. verify registry/admin cleanup
F. verify 4 outer scripts + admin-local bytes
   remain identical to retained snapshot
G. only then remove external outer source tree
H. verify complete external E029 source absent

任一 child retirement 失败：
不得继续删除 E029 outer source。

==================================================
5. Recovery snapshots
==================================================

以下必须保留：

D:\通用开发框架管理\retained\worktree-recovery\E015
D:\通用开发框架管理\retained\worktree-recovery\E027
D:\通用开发框架管理\retained\worktree-recovery\E029

状态保持：

EXECUTION_AUTHORITY = NO
ACTIVE_WORKTREE = NO
AUTO_CLEANUP = DENY
SEMANTIC_RECLASSIFICATION_REQUIRED = YES

R3 不得删除或修改其内容，
除非仅追加 retirement provenance/manifest metadata 且 authority 明确授权。

==================================================
6. 83 UNKNOWN
==================================================

继续完全排除：

UNKNOWN_EXTERNAL_COUNT = 83
UNKNOWN_ACTION = KEEP

不得重新分类、移动或删除。

UNKNOWN != THIS_PROJECT。

==================================================
7. Integrity
==================================================

退休后重新验证：

- main checkout unchanged
- repository HEAD/source unchanged
- remaining valid worktrees intact
- worktree registry valid
- project binding unchanged
- recovery snapshots intact
- no project-exclusive known path remains outside CODEX_PROJECT_SOURCE_ROOT
- no unique data loss

==================================================
8. Closure condition
==================================================

只有全部成功才允许：

PROVEN_PROJECT_PATH_ESCAPE = 0
L6A_CONTAINMENT_OBJECTIVE = PASS

83 UNKNOWN 可以继续存在，
因为其 ownership 尚未证明属于当前项目。

它们不应被描述为当前项目 path escape。

==================================================
9. 本轮仍禁止
==================================================

- 修改 main source
- 修改 83 UNKNOWN
- 删除 recovery snapshots
- Documentation Canonicalization
- 启动 L7，直到 R3 POST 完成

==================================================
回传
==================================================

R3_AUTHORITY_MATERIALIZED = YES | NO
R3_NATIVE_PRE = PASS | FAIL

E015_RETIREMENT = PASS | KEEP | FAIL
E027_RETIREMENT = PASS | KEEP | FAIL
E029_CHILD_RETIREMENT = PASS_2_OF_2 | PARTIAL | FAIL
E029_OUTER_SOURCE_RETIREMENT = PASS | NOT_EXECUTED | FAIL

REGISTERED_WORKTREES_RETIRED = <n>
RECOVERY_SNAPSHOT_INTEGRITY = PASS | FAIL

PROVEN_PROJECT_PATH_ESCAPE = 3 -> <n>
UNKNOWN_EXTERNAL_COUNT = 83
UNKNOWN_CHANGED = NO

UNIQUE_DATA_LOSS = 0 | <n>
GIT_INTEGRITY = PASS | FAIL
WORKTREE_REGISTRY_INTEGRITY = PASS | FAIL
PROJECT_BINDING_INTEGRITY = PASS | FAIL

POST_REVIEW = PASS | FINDING

L6A_CONTAINMENT_OBJECTIVE = PASS | NOT_COMPLETE
READY_FOR_L6A_CLOSURE = YES | NO
L7_STARTED = NO

FINDINGS = [...]
BLOCKERS = [...]
RETURN_TO_GPT = YES