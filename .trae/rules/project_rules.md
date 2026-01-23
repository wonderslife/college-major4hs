<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.
# OpenSpec 项目规则
 
## 通用准则 (Guardrails)
 
- 优先采用简单、最小化的实现方案，只在明确需要时才增加复杂度
- 保持变更范围紧密聚焦于请求的目标
- 如需了解 OpenSpec 的额外约定或说明，请参考 `openspec/AGENTS.md`（位于 `openspec/` 目录下，可运行 `ls openspec` 或 `openspec update` 查看）
 
## 代码风格
 
- 实现应当最小化且聚焦
- 在编辑文件时保持变更范围紧凑
- 完成所有工作后再更新状态
 
## OpenSpec CLI 命令参考
 
常用命令：
- `openspec list` - 列出所有变更
- `openspec list --specs` - 列出所有规格文档
- `openspec show <id>` - 显示指定变更详情
- `openspec show <id> --json --deltas-only` - 以 JSON 格式显示变更增量
- `openspec show <spec> --type spec` - 显示规格文档
- `openspec validate <id> --strict` - 严格验证变更
- `openspec archive <id> --yes` - 归档变更
 
## 搜索与探索
 
- 使用 `rg <keyword>` 搜索代码库
- 使用 `rg -n "Requirement:|Scenario:" openspec/specs` 搜索现有需求
- 使用 `ls` 或直接读取文件了解当前实现
<!-- OPENSPEC:END -->