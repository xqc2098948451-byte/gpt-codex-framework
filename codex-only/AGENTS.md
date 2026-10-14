# 工作索引

默认使用简体中文，依据实际代码与运行证据工作。

- 规范、一次授权语义、评审协议、恢复和边界见 [README.md](README.md)。
- 需求对应核对见 [授权前核对需求对应](README.md#授权前核对需求对应)：Implementer 在 authorize 前保留原文并逐条补齐 scope、完整 argv、场景预期与审查方式；独立 Reviewer 从实际 task、候选和客观证据重新核对，测试通过不等于需求覆盖。
- 授权后保持 task 原始字节不变；不得借对应表扩大权限。需求/范围变化由用户确认后用现有 authorize 创建新任务，新任务不自动撤销旧任务；范围内修复和复审沿用授权。
- CLI：`codex_only.py init / authorize / check / test / gate / deliver / recover`。
- 导航：`project_map.py build / locate / update`，先 locate 再读取所选文件；初建需要显式模块描述，update 只覆盖明确受影响模块。地图文件必须在原任务精确 scope 中，具体命令见 README 的 Project Map。
- 测试：在本目录运行 `C:/Python313/python.exe -B -m unittest discover -s tests -v`。
- Git：`C:/Program Files/Git/cmd/git.exe`，提交只用命令级作者配置。
- 实现者不创建独立评审 PASS，不推送，不修改系统、账号或 ACL。
- 原生会话启动和历史隔离见 README；试点证据与待评审状态见 [ACCEPTANCE.md](ACCEPTANCE.md)。
