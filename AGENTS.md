# Framework 工作入口

默认使用简体中文，依据用户公开需求、Git 候选和实际测试证据工作。

- 日常流程与全新会话启动：[codex-only/README.md](codex-only/README.md)。
- CLI、测试入口与角色约束：[codex-only/AGENTS.md](codex-only/AGENTS.md)。
- 合成试点验收、证据和边界：[codex-only/ACCEPTANCE.md](codex-only/ACCEPTANCE.md)。
- 用户拥有六部分需求；一次任务授权覆盖范围内的实现、修复和复评，无额外内部人工批准。
- Implementer 与 Reviewer 使用独立工作目录、全新原生会话；不得向 Reviewer 恢复、派生或导入 Implementer 历史。
- 临时工作树和测试目录优先使用合适的本地工作空间；Windows 上优先使用非 C 盘，不将具体盘符硬编码为跨平台要求。临时产物放在源码树外或已忽略目录。
- 交付前在真实或有代表性的运行环境执行任务规定的测试，以实际退出码、Git SHA、测试日志和客观证据验收；AI 文字结论不能代替实际执行。
- 正式发布前核对源码结构、入口链接、无关临时文件、Git SHA 版本标识及发行范围，确认发行物绑定最终源码提交。
- 对最终 ZIP 实际解压，核对完整文件集合、逐文件哈希、入口及必要测试；源码测试通过不能代替发行物验证。
- **正式日常入口已切换为 Codex-only**；新任务以实际 Git SHA 确认代码版本，使用 `init / authorize / gate / deliver` 管理本任务的授权与交付，不读取旧 `STATE@48` 作为新任务许可。
- 旧 Consumer 兼容源与 `VERSION=2.13.0` 暂保留；旧管理 STATE、证据与文档从本候选当前树移除，原文保留在 Git 历史中，均仅为旧 GPT–Codex 框架的回退依据，不是新 Codex-only 的当前版本或权威状态；旧入口见基线 `300dfd48167954e1179f821f23157d6a917cd47b:AGENTS.md`。
- Issue #19 本地修复、Stage6、历史证据与其他 Consumer 保留，不自动迁移或删除；正式 Release、跨项目变更、危险操作及旧资产清理须另获用户明确授权。README 中的试点高权限启动参数不作为所有项目的默认运行权限。
