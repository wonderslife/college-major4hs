# Skills 文档索引

本目录包含项目中所有29个skills的介绍和使用方法文档。

## Skills 列表

### 核心开发流程

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 1 | [brainstorming](01-brainstorming.md) | [01-brainstorming.md](01-brainstorming.md) | 创意生成 - 在进行任何创造性工作之前探索用户意图、需求并设计实现方案 |
| 2 | [systematic-debugging](02-systematic-debugging.md) | [02-systematic-debugging.md](02-systematic-debugging.md) | 系统化调试 - 在遇到任何bug、测试失败或意外行为时，通过系统化方法找到根本原因后再进行修复 |
| 3 | [test-driven-development](03-test-driven-development.md) | [03-test-driven-development.md](03-test-driven-development.md) | 测试驱动开发 - 在实现任何功能或bug修复之前编写测试 |
| 4 | [writing-plans](04-writing-plans.md) | [04-writing-plans.md](04-writing-plans.md) | 编写计划 - 在开始实现之前，将spec或需求转化为详细的、可执行的实施计划 |
| 5 | [executing-plans](05-executing-plans.md) | [05-executing-plans.md](05-executing-plans.md) | 执行计划 - 在单独的会话中执行已编写的实施计划，带有审查检查点 |
| 6 | [subagent-driven-development](06-subagent-driven-development.md) | [06-subagent-driven-development.md](06-subagent-driven-development.md) | 子代理驱动开发 - 在当前会话中通过为每个任务分派新的子代理来执行实施计划 |
| 7 | [finishing-a-development-branch](07-finishing-a-development-branch.md) | [07-finishing-a-development-branch.md](07-finishing-a-development-branch.md) | 完成开发分支 - 当实施完成、所有测试通过时，通过展示清晰选项并处理所选工作流来指导开发工作的完成 |
| 8 | [using-git-worktrees](08-using-git-worktrees.md) | [08-using-git-worktrees.md](08-using-git-worktrees.md) | 使用Git工作树 - 在需要与当前工作空间隔离的功能工作开始时，创建隔离的git工作树 |
| 9 | [verification-before-completion](09-verification-before-completion.md) | [09-verification-before-completion.md](09-verification-before-completion.md) | 完成前验证 - 在声称工作完成、修复或通过之前，要求运行验证命令并确认输出后再做出任何成功声明 |

### 代码审查和质量保证

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 10 | [requesting-code-review](10-requesting-code-review.md) | [10-requesting-code-review.md](10-requesting-code-review.md) | 请求代码审查 - 在完成任务、实现主要功能或合并之前，通过分派code-reviewer子代理来在问题级联之前捕获问题 |
| 11 | [receiving-code-review](11-receiving-code-review.md) | [11-receiving-code-review.md](11-receiving-code-review.md) | 接收代码审查 - 在接收代码审查反馈时，在实施建议之前，特别是在反馈不清楚或技术上可疑时 |
| 12 | [qa-expert](21-qa-expert.md) | [21-qa-expert.md](21-qa-expert.md) | QA专家 - 为任何软件项目建立世界级的QA测试流程，使用来自Google测试标准和OWASP安全最佳实践的验证方法 |

### 技能创建和管理

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 13 | [skill-creator](12-skill-creator.md) | [12-skill-creator.md](12-skill-creator.md) | Skill创建器 - 创建有效的Claude Code skills，提供专业化知识、工作流和工具 |
| 14 | [skills-search](13-skills-search.md) | [13-skills-search.md](13-skills-search.md) | Skills搜索 - 搜索、发现、安装和管理来自CCPM注册表的Claude Code skills |
| 15 | [claude-skills-troubleshooting](29-claude-skills-troubleshooting.md) | [29-claude-skills-troubleshooting.md](29-claude-skills-troubleshooting.md) | Claude Skills故障排除 - 诊断和解决Claude Code插件和skill配置问题 |

### 文档和内容工具

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 16 | [markdown-tools](17-markdown-tools.md) | [17-markdown-tools.md](17-markdown-tools.md) | Markdown工具 - 将文档转换为markdown，带有图像提取和Windows/WSL路径处理 |
| 17 | [mermaid-tools](18-mermaid-tools.md) | [18-mermaid-tools.md](18-mermaid-tools.md) | Mermaid工具 - 从markdown文件中提取Mermaid图并使用捆绑脚本生成高质量PNG图像 |
| 18 | [pdf-creator](19-pdf-creator.md) | [19-pdf-creator.md](19-pdf-creator.md) | PDF创建器 - 使用weasyprint从markdown创建专业的PDF文档，带有适当的中文字体支持 |
| 19 | [ppt-creator](20-ppt-creator.md) | [20-ppt-creator.md](20-ppt-creator.md) | PPT创建器 - 从主题或文档创建专业的幻灯片，生成结构化内容，带有数据驱动的图表、演讲者笔记和完整的PPTX文件 |
| 20 | [docs-cleaner](23-docs-cleaner.md) | [23-docs-cleaner.md](23-docs-cleaner.md) | 文档清理器 - 在保留100%有价值内容的同时整合冗余文档 |
| 21 | [fact-checker](15-fact-checker.md) | [15-fact-checker.md](15-fact-checker.md) | 事实检查器 - 使用网络搜索和官方来源验证文档中的事实声明，然后提出更正并等待用户确认 |
| 22 | [prompt-optimizer](14-prompt-optimizer.md) | [14-prompt-optimizer.md](14-prompt-optimizer.md) | 提示优化器 - 将模糊的提示转化为精确、可操作的规范，使用EARS方法学 |
| 23 | [claude-md-progressive-discloser](28-claude-md-progressive-discloser.md) | [28-claude-md-progressive-discloser.md](28-claude-md-progressive-discloser.md) | CLAUDE.md渐进式披露优化器 - 通过应用渐进式披露原则来分析和优化用户CLAUDE.md文件，以减少上下文开销同时保留功能性 |

### 开发工具和实用程序

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 24 | [developing-ios-apps](25-developing-ios-apps.md) | [25-developing-ios-apps.md](25-developing-ios-apps.md) | 开发iOS应用 - 使用XcodeGen、SwiftUI和SPM构建、配置和部署iOS应用 |
| 25 | [cli-demo-generator](26-cli-demo-generator.md) | [26-cli-demo-generator.md](26-cli-demo-generator.md) | CLI演示生成器 - 创建专业的动画CLI演示，支持从命令描述的自动生成和用于自定义演示的手动控制 |
| 26 | [cloudflare-troubleshooting](24-cloudflare-troubleshooting.md) | [24-cloudflare-troubleshooting.md](24-cloudflare-troubleshooting.md) | Cloudflare故障排除 - 使用API驱动的证据收集来调查和解决Cloudflare配置问题 |
| 27 | [i18n-expert](16-i18n-expert.md) | [16-i18n-expert.md](16-i18n-expert.md) | 国际化专家 - 为UI代码库设置、审计或强制国际化/本地化，包括安装/配置i18n框架、替换硬编码字符串、确保en-US/zh-CN覆盖 |
| 28 | [ui-designer](ui-designer.md) | [ui-designer.md](ui-designer.md) | UI设计器 - 从参考UI图像中提取设计系统并生成实现就绪的UI设计提示 |
| 29 | [ui-ux-pro-max](ui-ux-pro-max.md) | [ui-ux-pro-max.md](ui-ux-pro-max.md) | UI/UX设计智能 - 带有可搜索数据库 |

### 历史和会话管理

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 30 | [claude-code-history-files-finder](27-claude-code-history-files-finder.md) | [27-claude-code-history-files-finder.md](27-claude-code-history-files-finder.md) | Claude Code历史文件查找器 - 从Claude Code会话历史文件中提取和恢复内容 |
| 31 | [video-comparer](video-comparer.md) | [video-comparer.md](video-comparer.md) | 视频比较器 - 比较两个视频以分析压缩结果或质量差异，生成带有质量指标（PSNR、SSIM）和逐帧视觉比较的交互式HTML报告 |

### 并行处理

| # | Skill | 文档 | 描述 |
|---|-------|------|------|
| 32 | [dispatching-parallel-agents](22-dispatching-parallel-agents.md) | [22-dispatching-parallel-agents.md](22-dispatching-parallel-agents.md) | 调度并行代理 - 在面临2+个可以在没有共享状态或顺序依赖的情况下工作的独立任务时使用 |

## 使用指南

### 如何使用这些文档

1. **浏览索引** - 使用上表找到您需要的skill
2. **阅读文档** - 点击链接查看详细的介绍和使用方法
3. **应用技能** - 根据文档中的指导在您的项目中应用相应的skill

### 按场景查找

- **开始新功能开发** → brainstorming → writing-plans → using-git-worktrees → executing-plans / subagent-driven-development
- **修复bug** → systematic-debugging → test-driven-development → verification-before-completion
- **代码审查** → requesting-code-review / receiving-code-review
- **完成开发** → finishing-a-development-branch
- **创建文档** → markdown-tools → pdf-creator / ppt-creator
- **测试和质量保证** → qa-expert → test-driven-development
- **国际化** → i18n-expert

### 技能分类

#### 核心工作流技能
这些skills定义了Claude Code的核心开发方法论：
- brainstorming - 创意生成
- systematic-debugging - 系统化调试
- test-driven-development - 测试驱动开发
- writing-plans - 编写计划
- executing-plans - 执行计划
- subagent-driven-development - 子代理驱动开发
- finishing-a-development-branch - 完成开发分支
- using-git-worktrees - 使用Git工作树
- verification-before-completion - 完成前验证

#### 质量保证技能
确保代码质量和可靠性：
- requesting-code-review - 请求代码审查
- receiving-code-review - 接收代码审查
- qa-expert - QA专家
- test-driven-development - 测试驱动开发

#### 文档和内容技能
创建和管理各种类型的文档：
- markdown-tools - Markdown工具
- mermaid-tools - Mermaid工具
- pdf-creator - PDF创建器
- ppt-creator - PPT创建器
- docs-cleaner - 文档清理器
- fact-checker - 事实检查器
- prompt-optimizer - 提示优化器
- claude-md-progressive-discloser - CLAUDE.md渐进式披露优化器

#### 开发工具技能
特定技术栈和工具的专用技能：
- developing-ios-apps - 开发iOS应用
- cli-demo-generator - CLI演示生成器
- cloudflare-troubleshooting - Cloudflare故障排除
- i18n-expert - 国际化专家
- ui-designer - UI设计器
- ui-ux-pro-max - UI/UX设计智能

#### 管理和维护技能
技能和会话的管理工具：
- skill-creator - Skill创建器
- skills-search - Skills搜索
- claude-skills-troubleshooting - Claude Skills故障排除
- claude-code-history-files-finder - Claude Code历史文件查找器

#### 高级技能
处理复杂场景：
- dispatching-parallel-agents - 调度并行代理
- video-comparer - 视频比较器

## 快速参考

### 必读核心技能

如果您是Claude Code的新用户，建议首先阅读以下核心技能文档：

1. [brainstorming](01-brainstorming.md) - 了解如何开始新功能
2. [systematic-debugging](02-systematic-debugging.md) - 学习系统化调试方法
3. [test-driven-development](03-test-driven-development.md) - 掌握TDD流程
4. [verification-before-completion](09-verification-before-completion.md) - 理解验证的重要性

### 常用技能组合

#### 完整功能开发流程
```
brainstorming → writing-plans → using-git-worktrees → subagent-driven-development
→ test-driven-development → requesting-code-review → finishing-a-development-branch
```

#### Bug修复流程
```
systematic-debugging → test-driven-development → verification-before-completion
```

#### 文档创建流程
```
markdown-tools → mermaid-tools → pdf-creator / ppt-creator → fact-checker
```

## 更新日志

- **2026-01-23** - 初始版本，包含所有29个skills的完整文档
