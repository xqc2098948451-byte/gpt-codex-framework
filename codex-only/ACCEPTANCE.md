# 合成试点验收与 Framework 接入

这是 synthetic / test-only 验收，只涉及合成 Consumer，不代表真实业务规则验收或生产迁移。Framework 接入基线为 `300dfd48167954e1179f821f23157d6a917cd47b`，专用分支为 `refactor/codex-only-pilot-20261012`。本目录接入已有验收原型；本次 Framework 候选的独立 Reviewer 结论须在提交后另外绑定精确 SHA，本文件不预先声明该候选 PASS。

## 公开依据与原型结果

以下路径均相对于本次试点目录 `D:/通用开发框架管理/codex-only-pilot-20261013/`，不是通用部署依赖。文档仅引用客观记录，不嵌入私有会话文本。

- 接入需求：`public/FRAMEWORK_INTEGRATION_SPEC.md`；原型六部分需求：`public/FRAMEWORK_SPEC.md`。需求由用户拥有。
- 冻结代码：`public/accepted-prototype/`；验收记录：`public/accepted-e2e.json`（status `PASS`）。
- 已接受原型 SHA：`be6b5f9bad186f02256a5349990a2c6369cbbf30`。
- 已接受合成 Consumer SHA：`4c4e6def06358db2630ec2941d7415959dd431a7`，项目 UUID `4bd3bd8d-18f7-45ab-b40f-8f9db87d8e4f`。
- 实际 gate 与交付记录：`evidence/consumer-independent-gate.json`、`evidence/consumer-real-delivery.json`。这里引用公开验收索引中的路径，不声称本次重新执行了 Consumer 交付。

公开验收记录提供以下不同的原生会话标识；新运行也必须从自身 JSON 事件 `thread.started.thread_id` 获取真实 ID，不能用角色名或测试夹具字符串替代。

| 客观记录 | 原生会话 ID | 结果 |
| --- | --- | --- |
| 原型独立 Reviewer | `01a130fc-d3d1-7861-acd9-d6d25ea3792b` | 精确原型 SHA，PASS |
| Consumer 修复后独立 Reviewer | `01a130fa-c4b0-7880-bf56-63ab55dd846b` | 精确 Consumer SHA，PASS，findings 为空 |
| 冷恢复新会话 | `01a13102-4483-7c71-95b2-adec50161514` | 精确 Consumer SHA，PASS |

Consumer Reviewer 使用独立目录 `consumer-fault-B2`，独立测试证据为 `sessions/consumer-fault-B2/tests.json`。公开索引未提供 Implementer 的原生 ID，本文件不补造；上述历史 ID 也不能复用于本次 Framework 候选。模型为 `gpt-6-astra`，CLI 为 `0.154.0`，同一账号、逻辑隔离且关闭共享记忆，没有强制 OS 或加密身份边界。Reviewer 不得 resume/fork/import Implementer 历史；启动参数见 README。

自然发现 `B1-R1` 为 branch/tag 歧义，已修复并独立复评。另一次明确标记的故障注入 `F1` 为 duplicate-key hook injection，已拒绝、修复并独立复评；不得把人工注入计作自然发现。

公开 `negative_cases` 记录的是实际命令拒绝，以下 11 项均退出 1，错误标识符合预期，且各项 `main_before == main_after`；每项原始命令证据路径均在该 JSON 内：

| 实际负向场景 | 错误标识 |
| --- | --- |
| 无授权 | `AUTHORIZATION_MISSING` |
| 候选与 HEAD 不一致 | `CANDIDATE_MISMATCH` |
| 外来项目 | `WRONG_PROJECT` |
| 越界文件 | `OUTSIDE_SCOPE` |
| 非快进历史 | `NON_FAST_FORWARD` |
| 目标基线过期 | `STALE_BASELINE` |
| 评审失败 | `REVIEW_FAILED` |
| 缺少评审 | `REVIEW_MISSING` |
| 同会话评审 | `SELF_REVIEW` |
| Reviewer 候选变化 | `REVIEWER_CHANGED` |
| 实际测试失败 | `TEST_FAILED` |

这些是逻辑检测，不是 OS 拒写。单元集成测试中的 review JSON 仅为协议夹具，不冒充 Codex 独立评审。冷恢复依据真实 Git 和公开任务/证据；恢复命令只读，交付已合并而完成记录缺失时可按原任务安全重试，详见 README 和原型测试。

## 实测复杂度与保留边界

测量来源：`evidence/legacy-complexity.json`，基线同上。

| 指标 | 旧入口依赖 | 新日常入口 |
| --- | --- | --- |
| Python 运行脚本 | 20 个文件 / 10,357 行 | 1 个 CLI 文件 |
| CLI 入口 | 6 个 | 1 个，7 个命令：init / authorize / check / test / gate / deliver / recover |
| 根 AGENTS | 160 行 | 短入口索引 |
| 任务授权 | 旧日常人工批准次数未测量 | 本合成任务 1 次，额外内部人工批准 0 次 |

这是日常依赖移除，不是物理删除。旧文件保留在当前树中；被替换的根 AGENTS 原文可从基线 Git 历史取得。没有正式 STATE/VERSION 变更，没有真实 Consumer 迁移。首次接入还需 `init + authorize`、显式原生 Git A/B 目录设置及独立会话启动，不能把操作步骤数混同于批准次数，也不能编造旧/新批准次数对比。

## 本次接入验证与交接

CLI 与测试从冻结导出逐字节复制，不修改行为。SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `codex_only.py` | `de78fbd597370fbef7ac6cc2ad75e90ccd9a415e6b3100936e7af4a7d86e4ba3` |
| `tests/test_codex_only.py` | `a54997248628113c9f1dc9ac4e79501e051ccd8e189d39e4b5afd81ab3690a8d` |

实际集成测试命令为 `C:/Python313/python.exe -B -m unittest discover -s tests -v`，cwd 为 `framework-A/codex-only`。22 项真实 Git 集成测试通过，退出码 0。外部记录 `sessions/framework-A1/green-tests.json` 保存完整 argv、cwd、exit_code、stdout/stderr 与时间。Reviewer 应在自己的目录重新测试精确候选并生成独立记录。

允许差异仅为根 `AGENTS.md` 和 `codex-only/{codex_only.py,tests/test_codex_only.py,README.md,AGENTS.md,.gitignore,ACCEPTANCE.md}`。候选交接前核对实际 Git diff 路径、复制字节、工作树干净状态和单一提交父节点；`.gpt-codex/`、`VERSION`、`STATE` 不变。原保护 checkout 不作读写；不 push、release、cleanup 或合并 main，不修改账号、ACL、VM。接入只交付一个本地候选，后续全新 Reviewer 的客观结论单独保存。
