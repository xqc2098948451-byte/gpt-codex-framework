# Framework 工作入口

默认使用简体中文，依据用户公开需求、Git 候选和实际测试证据工作。

- 日常流程与全新会话启动：[codex-only/README.md](codex-only/README.md)。
- CLI、测试入口与角色约束：[codex-only/AGENTS.md](codex-only/AGENTS.md)。
- 合成试点验收、证据和边界：[codex-only/ACCEPTANCE.md](codex-only/ACCEPTANCE.md)。
- 用户拥有六部分需求；一次任务授权覆盖范围内的实现、修复和复评，无额外内部人工批准。
- Implementer 与 Reviewer 使用独立工作目录、全新原生会话；不得向 Reviewer 恢复、派生或导入 Implementer 历史。
- 旧资产保留；原入口见基线 `300dfd48167954e1179f821f23157d6a917cd47b:AGENTS.md`。本试点不改 `.gpt-codex/`、`VERSION`、`STATE`，不迁移真实 Consumer，不推送、发布或合并 main。
