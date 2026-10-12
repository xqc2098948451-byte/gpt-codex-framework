# Codex-only 最小 Git 工作流

仅使用 Python 标准库和 Git，入口为 `codex_only.py`。这是一份非业务原型：实现者提交候选，另一独立、新会话的 Reviewer 运行测试并提供外部评审文件，随后按已授权任务快进交付。CLI 不创建评审 PASS，也不具有独立评审权。

本目录接入已验收原型，CLI 与测试按公开导出逐字节复制。验收来源、复杂度比较及本次 Framework 候选边界见 [ACCEPTANCE.md](ACCEPTANCE.md)。以下项目交付示例仅用于另行授权的合成项目；本次 Framework 集成只创建本地候选，不运行 `init`、`authorize` 或 `deliver` 修改 Framework 身份或 main。

## 运行与测试

本次环境使用 Python 3.13 和 Git for Windows。PowerShell 中运行全部真实 Git 集成测试：

```powershell
$env:PYTHONUTF8 = '1'
$env:CODEX_ONLY_GIT = 'C:/Program Files/Git/cmd/git.exe'
& 'C:/Python313/python.exe' -B -m unittest discover -s tests -v
```

临时仓库放在工作树内被忽略的 `.test-tmp/` 中，每项测试结束时删除自己的目录。测试实际创建仓库、提交、工作树和克隆，运行子进程，检查拒绝时目标 ref 未改变。评审 JSON 是协议测试夹具，**不是实际 Codex 独立评审证明**。

所有操作命令输出一个 JSON 对象；成功退出 0，拒绝退出 1，并给出稳定的 `error` 标识。`--help` 使用 argparse 的普通帮助输出。不依赖第三方软件包。可用 `CODEX_ONLY_GIT` 指定 Git，否则使用 PATH 或 Windows 标准安装位置。

## 一次授权与六部分需求

在目标分支已检出、工作树干净时执行一次 `authorize`，其含义是用户授权该任务、精确文件集合和测试命令。任务文件必须不存在且位于仓库外；CLI 后续不会修改它。重复授权到同一文件会拒绝。该命令不是加密身份认证，调用者负责确认需求已获用户批准。

需求文件为 UTF-8 文本，建议直接采用以下模板填写；CLI 保存全文和摘要，不自动判断自然语言需求的完整性：

```text
1. 目标：用户授权的具体结果。
2. 可观察行为：输入触发什么行为，如何判断完成。
3. 输入/输出：数据格式、文件、返回值。
4. 规则：身份、基线、允许文件、候选、测试和评审约束。
5. 错误/禁止事项：需要拒绝的条件和不得执行的动作。
6. Given/When/Then 验收：至少一个成功场景和必要失败场景。
```

任务保存 UUID、Git genesis、授权 baseline、目标分支、规范化 common directory、需求内容及 SHA-256、scope、可信测试 argv、`user:authorize-cli` 权威来源，以及外部完成记录路径 `<task.json>.completion.json`。身份保存在受 Git 跟踪的 `.codex-only/project.json`。空仓库初始化先创建 genesis 空提交，再提交身份；已有干净仓库只新增身份文件。初始化提交采用本地命令级作者参数，不改 Git 全局配置。

scope 中每一项是**精确的仓库相对文件路径**，使用 `/`；不支持目录前缀、通配符或 `..`。重命名的源、目标都必须授权。检查基线到候选的最终树差异，拒绝改变范围内的 Git symlink/submodule；不审计中间提交曾出现后又撤销的文件变化。

## 精确调用示例

以下是 Python 交互窗口或脚本中的调用，避免不同 PowerShell 版本对 JSON 引号的处理差异。路径是示例，需要换成实际路径。CLI 应位于候选工作树或其他可信位置。所有 `run()` 都是真实子进程调用，失败立即抛出异常。

```python
import json
import os
import subprocess

PY = 'C:/Python313/python.exe'
GIT = 'C:/Program Files/Git/cmd/git.exe'
CLI = 'D:/demo/framework/codex-only/codex_only.py'
DELIVERY = 'D:/demo/project'
IMPLEMENTER = 'D:/demo/implementer'
REVIEWER = 'D:/demo/reviewer'
TASK = 'D:/demo/public/task.json'
IMPL_TEST = 'D:/demo/public/implementer-tests.json'
REVIEW_TEST = 'D:/demo/public/reviewer-tests.json'
REVIEW = 'D:/demo/public/review.json'
os.environ['CODEX_ONLY_GIT'] = GIT
os.environ['PYTHONUTF8'] = '1'

def run(*args):
    return subprocess.run(args, check=True, text=True, encoding='utf-8',
                          capture_output=True).stdout.strip()

def workflow(command, root, *args):
    result = run(PY, CLI, command, '--root', root, *args)
    print(result)
    return json.loads(result)

# 新的合成项目首次执行；若 DELIVERY 已是干净 Git 仓库则省略此行。
run(GIT, 'init', '-b', 'main', DELIVERY)
workflow('init', DELIVERY)
workflow('authorize', DELIVERY, '--task', TASK,
         '--requirements', 'D:/demo/public/requirements.md',
         '--scope', 'app.py', '--scope', 'tests/test_app.py',
         '--test-command-json', json.dumps([
             PY, '-B', '-m', 'unittest', 'discover', '-s', '{root}/tests', '-v']),
         '--task-id', 'example-001')
run(GIT, '-C', DELIVERY, 'worktree', 'add', '-b', 'implementer/task', IMPLEMENTER)

# 此时用下文启动命令在 IMPLEMENTER 开始 A，会话中执行实现步骤。
# IMPL_SESSION 由启动者提供 A 的真实 thread.started.thread_id。

# 实现者现在修改授权文件并运行测试，再创建真实候选提交。
# run(GIT, '-C', IMPLEMENTER, 'add', '--', 'app.py', 'tests/test_app.py')
# run(GIT, '-C', IMPLEMENTER, '-c', 'user.name=Codex Pilot',
#     '-c', 'user.email=codex-pilot@example.invalid', 'commit', '-m', 'Implement task')
SHA = run(GIT, '-C', IMPLEMENTER, 'rev-parse', 'HEAD')
workflow('check', IMPLEMENTER, '--task', TASK, '--candidate', SHA)
workflow('test', IMPLEMENTER, '--task', TASK, '--candidate', SHA,
         '--session', IMPL_SESSION, '--output', IMPL_TEST)
```

`test` 只执行任务中保存的 argv，逐项替换 `{root}`，不经过 shell；cwd 是被测工作树，并设置 `PYTHONDONTWRITEBYTECODE=1`。输出必须位于被测仓库及 Git 元数据目录外且此前不存在。证据保存命令、cwd、起止时间、真实退出码、stdout/stderr、候选 SHA、项目 UUID、任务原始文件字节摘要、会话标识及测试后工作树检查结果。失败和工作树变化仍会保存证据，命令返回非零。修复后使用新证据文件名。

另一个全新 Reviewer 会话读取公开任务和候选，独立执行以下操作。可以使用同仓库的独立 worktree，也可使用不同 common directory 的完整克隆；不得采用 shallow clone 或复制身份到无关历史。下面继续使用上例中的变量和辅助函数，仅表示 Reviewer 应执行的命令：

```python
run(GIT, 'clone', '--no-local', DELIVERY, REVIEWER)
run(GIT, '-C', REVIEWER, 'checkout', '--detach', SHA)
# 此时用下文命令在 REVIEWER 开始全新 B；下行由 B 独立执行。
# REVIEW_SESSION 为 B 自己的真实 thread.started.thread_id。
workflow('test', REVIEWER, '--task', TASK, '--candidate', SHA,
         '--session', REVIEW_SESSION, '--output', REVIEW_TEST)
```

克隆的 `test` 通过 UUID、genesis、baseline 和候选历史验证身份，不要求 common directory 相同，也不以克隆内的目标分支位置代替授权仓库状态。`check`、`gate`、`deliver`、`recover` 均要求授权 common directory；gate 最终检查授权仓库目标 ref。Reviewer 工作树必须保持候选 HEAD 和干净状态。

Reviewer 自行完成代码审查后提供外部 JSON，格式如下；摘要和 SHA 必须是真实值，路径使用绝对路径。这里是格式说明，不是可用的评审结果：

```json
{
  "project_id": "task.json 中的 UUID",
  "task_digest": "task.json 原始字节的 SHA-256",
  "candidate": "完整候选 SHA",
  "verdict": "PASS 或 FAIL",
  "findings": [],
  "reviewer_session": "实际全新 Reviewer 会话标识",
  "reviewer_worktree": "D:/demo/reviewer",
  "test_evidence": "D:/demo/public/reviewer-tests.json"
}
```

有发现时使用 FAIL 和非空 findings。实现者修复、提交新 SHA 后，双方重新运行测试，Reviewer 重新审查并提供新候选绑定的评审。旧证据、旧评审不能用于新 SHA。框架没有 `approve` 命令，也不启动或模拟 Reviewer。

仅文档补充且运行代码、测试及相关运行输入未变时，源码候选审查只做必要的文档/结构与 Blob 一致性验证，不重复完整运行测试。已有有效测试记录须注明原 SHA，并作为补充依据；新 SHA 仍须独立复审，不能把旧记录改写为新 SHA 的运行测试 PASS。此规则不改变 CLI 的 `gate/deliver` 对当前候选测试证据的精确 SHA 绑定；通过 CLI 交付的任务仍须执行该任务已授权的测试命令。

实际独立评审就绪后，按原授权继续：

```python
workflow('gate', IMPLEMENTER, '--task', TASK, '--candidate', SHA,
         '--test-evidence', IMPL_TEST, '--review', REVIEW)
workflow('deliver', DELIVERY, '--source-root', IMPLEMENTER,
         '--task', TASK, '--candidate', SHA,
         '--test-evidence', IMPL_TEST, '--review', REVIEW)
workflow('recover', DELIVERY, '--task', TASK)
```

gate 要求实现者测试和 Reviewer 独立测试都退出 0 且绑定相同候选/任务/项目；Reviewer 会话不同，工作树也必须不同，评审 PASS 且 findings 为空。交付先 gate，再检查交付工作树、授权分支和基线，用 `git merge --ff-only`，重新检查候选和评审，写入唯一外部完成记录。完成记录包含候选、项目、任务摘要、评审与双方测试的路径和摘要。重复相同交付不再次 merge，也不重写已有正确记录。

## 恢复与错误

新会话只需 Git、公开任务文件、候选 SHA、测试/评审文件和相关干净工作树。`recover` 不运行测试、不写记录，只报告实际 `target_head`、`worktree_head`、`baseline`、`completion_missing` 及状态：

- `ACTIVE`：目标仍在授权基线，任务可继续。
- `DELIVERED`：完成记录匹配当前目标；或本任务交付的最新 Git reflog 标记确认 merge 已完成但记录缺失。
- `DIRTY`：当前工作树不干净。
- `STALE`：目标发生其他移动、当前工作树历史不继承授权基线，或完成记录不匹配。

若 merge 后记录写入中断，`recover` 如实报告 `DELIVERED` 和缺失记录；保留原候选、评审与证据后重试相同 `deliver`，重新验证并补写记录，不再 merge。完成记录原子替换；记录损坏时返回 `INVALID_JSON`，不会推断成功。若 reflog 被删除/过期且完成记录也缺失，恢复保守报告 `STALE`，自动重试也会拒绝，需要人工根据真实 Git 记录诊断。普通 merge 即使将目标移到了同一候选，也不会被接受为交付重试。`gate` 在交付后因 baseline 已移动而拒绝是正常行为，只有有交付记录支持的重试允许目标等于候选。

主要拒绝标识：`AUTHORIZATION_MISSING`、`WRONG_PROJECT`、`WRONG_COMMON_DIRECTORY`、`OUTSIDE_SCOPE`、`UNSAFE_PATH`、`DIRTY_WORKTREE`、`CANDIDATE_MISMATCH`、`STALE_BASELINE`、`NON_FAST_FORWARD`、`TEST_FAILED`、`TEST_WORKTREE_CHANGED`、`EVIDENCE_MISSING`、`EVIDENCE_BINDING_MISMATCH`、`REVIEW_MISSING`、`REVIEW_FAILED`、`REVIEW_BINDING_MISMATCH`、`SELF_REVIEW`、`REVIEWER_CHANGED`、`COMPLETION_MISMATCH`。Git 执行失败使用 `GIT_ERROR`，不解析本地化错误文本作为错误标识。

## 全新原生 Codex 会话

本试点使用 `gpt-6-astra`、`codex-cli 0.154.0`，同一账号、不同工作目录和逻辑隔离，没有强制 OS 边界。保留 CLI 原有正常认证，不读取或复制凭据文件，不另设账号、ACL、VM，也不迁移 `CODEX_HOME`。本机 `codex exec --help` 已核对以下开关；`--ignore-user-config` 和 `--ignore-rules` 属于 `exec` 参数。[官方 CLI 文档](https://learn.chatgpt.com/docs/developer-commands?surface=cli)说明前者跳过用户配置但继续使用现有认证，`--ephemeral` 不持久化会话文件，`--json` 输出事件。

以下参数对齐用户已授权、已由真实原生会话验证的同账号试点：`-s danger-full-access` 与 `-c approval_policy="never"` 显式选择本次执行和审批模式；关闭 chronicle、multi_agent 并跳过宿主技能发现，与其余禁用记忆及上下文导入的参数共同对齐已测试的上下文加载防护。Implementer 与 Reviewer 仍以不同工作目录和全新会话保持逻辑分离。这些是单次启动参数，不修改系统权限、持久配置或 ACL，也不引入新的权限框架。

启动者在前述原生 Git A/B 目录分别就绪后运行对应片段。A 的外部公开提示词写明 Implementer、六部分需求、授权路径、基线和测试命令；B 的提示词写明 Reviewer、精确候选 SHA、独立检查/测试要求和外部评审输出位置。两份提示词只引用公开任务、Git 和客观证据，不包含其他会话或项目私有上下文。因为 `project_doc_max_bytes=0`，需在各自提示词中明确允许读取的 README、需求和代码路径。

```powershell
$codexNative = 'C:/Users/xqc/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe'
$freshNative = @(
    'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral', '--json',
    '-m', 'gpt-6-astra',
    '-s', 'danger-full-access', '-c', 'approval_policy="never"',
    '-c', 'project_doc_max_bytes=0',
    '-c', 'features.chronicle=false',
    '-c', 'features.multi_agent=false',
    '-c', 'features.skip_host_skill_discovery=true',
    '-c', 'features.memories=false',
    '-c', 'memories.use_memories=false',
    '-c', 'memories.generate_memories=false',
    '-c', 'features.external_agent_memory_import=false',
    '-c', 'features.plugins=false', '-c', 'features.apps=false',
    '-c', 'features.hooks=false'
)
# 先启动 A；A 完成提交后，再按前文创建/检出 B 的精确候选。
New-Item -ItemType Directory -Force -Path 'D:/demo/sessions/A' | Out-Null
Get-Content -Raw -Encoding UTF8 'D:/demo/public/implementer-prompt.md' |
    & $codexNative @freshNative -C 'D:/demo/implementer' `
      -o 'D:/demo/sessions/A/result.md' - `
      1> 'D:/demo/sessions/A/events.jsonl' 2> 'D:/demo/sessions/A/stderr.txt'
if ($LASTEXITCODE -ne 0) { throw 'Implementer native session failed' }

# B 是另外一次全新 exec；不使用 resume、fork 或导入 A 的事件/输出。
New-Item -ItemType Directory -Force -Path 'D:/demo/sessions/B' | Out-Null
Get-Content -Raw -Encoding UTF8 'D:/demo/public/reviewer-prompt.md' |
    & $codexNative @freshNative -C 'D:/demo/reviewer' `
      -o 'D:/demo/sessions/B/result.md' - `
      1> 'D:/demo/sessions/B/events.jsonl' 2> 'D:/demo/sessions/B/stderr.txt'
if ($LASTEXITCODE -ne 0) { throw 'Reviewer native session failed' }

# 启动者仅提取各自 thread.started 的真实 ID，不把会话内容交给另一角色。
$implSession = (Get-Content 'D:/demo/sessions/A/events.jsonl' |
    ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object type -eq 'thread.started').thread_id
$reviewSession = (Get-Content 'D:/demo/sessions/B/events.jsonl' |
    ForEach-Object { $_ | ConvertFrom-Json } |
    Where-Object type -eq 'thread.started').thread_id
if (-not $implSession -or -not $reviewSession -or $implSession -eq $reviewSession) {
    throw 'Missing or non-distinct native session IDs'
}
```

`A`、`B` 只是目录标签，不是 session ID。启动者在各自 `thread.started` 出现后提取 ID（可在另一终端读取当前角色的事件文件），作为该角色 `test --session` 和评审 `reviewer_session` 的绑定值；不得编造名称代替 ID。上面展示的是启动与提取命令，不是本次 Framework Reviewer 已执行的证明。事件文件留在仓库外，不提交、不嵌入文档、不传给对方。已有原型的真实 ID 见 ACCEPTANCE。

首次项目接入需要 `init`、一次 `authorize`，还需要显式创建 A/B Git 目录和分别启动两次原生会话。七个 CLI 命令不会自动启动这些会话；范围内修复和复评沿用同一任务授权。

## 边界

这是同一 OS 账号下的逻辑约束，不是安全隔离。任务、证据、评审及其会话标识均为公开且可写数据，没有签名或不可伪造身份；摘要可检测意外变更，不能阻止恶意进程重写一整套数据。实际 Reviewer 独立性由用户安排全新会话保障。测试命令属于用户授权的可信代码，可以执行任意当前账号可执行操作；框架不沙箱化测试。

Git 的干净状态不包含忽略文件，也无法发现测试先修改后恢复的瞬间变化。工作流假设顺序操作，不为并发写入、恶意 hooks、replace refs、损坏仓库或恶意进程提供事务/隔离保证。测试无超时策略；调用者可中断挂起的测试，此时缺失证据必须重跑。初始化中断可能留下未提交身份文件，需检查后手动处理。目标分支基线在任务中固定并逐次核对，但不是不可改写的 Git ref 锁。

不读取私有上下文，不设置账号/ACL，不增加编排角色，不做 push、发布、清理旧资产或独立批准。原 Framework 接入候选仅修改根 AGENTS.md 和约定的六个 codex-only 文件；运行工作流生成的项目身份属于用户选定的测试/目标仓库。原接入时旧资产继续保留。后续源码收敛候选会把旧管理证据移至 Git 历史；新日常入口不依赖旧治理流程，不迁移真实 Consumer。


## 收敛候选与最小 ZIP

本轮源码候选保留兼容性尚未决定的旧 Consumer 导出、公开脚本/插件及必要依赖；这些不是新日常入口。8 文件最小 ZIP 仅面向新 Codex-only 项目，不包含旧 Consumer 运行时、VERSION、历史文档或 Git 数据，不适合作为旧框架的原地升级包。CLI 和 22 个测试保持基线字节及语义。

完整切换前树可在完整仓库中用 `git show 8839ce90f9f541b4b2fe5ac577ebdd0a26f8c194:<path>` 读取；旧根入口与完整旧治理使用 `git show 300dfd48167954e1179f821f23157d6a917cd47b:AGENTS.md`。仓库地址为 `https://github.com/xqc2098948451-byte/gpt-codex-framework`；仅持有 ZIP 时须另取得包含这些提交的完整 Git clone，ZIP 自身无法恢复历史。需要完整旧运行环境时，在独立目录检出对应历史提交，不把旧状态或入口混入新项目。历史原型的验收结果仅见 ACCEPTANCE 的历史说明，本轮测试与独立评审须重新绑定实际候选 SHA。
