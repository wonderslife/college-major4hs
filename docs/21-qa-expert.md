# QA Expert - QA专家

## 简介

QA Expert skill用于为任何软件项目建立世界级的QA测试流程，使用来自Google测试标准和OWASP安全最佳实践的验证方法。包括通过master prompts的自主执行能力以及第三方QA团队交接的完整文档模板。

## 使用场景

触发此skill当：
- 为新或现有项目设置QA基础设施
- 编写标准化测试用例（AAA模式合规）
- 执行全面的测试计划并带有进度跟踪
- 实施安全测试（OWASP Top 10）
- 使用适当的严重性分类（P0-P4）提交bug
- 生成QA报告（每日摘要、每周进度）
- 计算质量指标（通过率、覆盖率、门控）
- 准备QA文档以进行第三方团队交接
- 启用LLM驱动的测试执行

## 快速开始

**一键初始化：**
```bash
python scripts/init_qa_project.py <project-name> [output-directory]
```

**创建内容：**
- 目录结构（`tests/docs/`、`tests/e2e/`、`tests/fixtures/`）
- 跟踪CSV（`TEST-EXECUTION-TRACKING.csv`、`BUG-TRACKING-TEMPLATE.csv`）
- 文档模板（`BASELINE-METRICS.md`、`WEEKLY-PROGRESS-REPORT.md`）
- QA master prompt用于自主执行
- 带有完整快速入门指南的README

**用于自主执行（推荐）：** 见`references/master_qa_prompt.md` - 用于100倍加速的单个复制粘贴命令。

## 核心能力

### 1. QA项目初始化

初始化带有所有模板的完整QA基础设施：

```bash
python scripts/init_qa_project.py <project-name> [output-directory]
```

创建目录结构、跟踪CSV、文档模板和用于自主执行的master prompt。

**使用场景：** 从scratch开始QA或迁移到结构化QA流程。

### 2. 测试用例编写

编写遵循AAA模式（Arrange-Act-Assert）的标准化、可重现的测试用例：

1. 阅读模板：`assets/templates/TEST-CASE-TEMPLATE.md`
2. 遵循结构：先决条件（Arrange）→ 测试步骤（Act）→ 预期结果（Assert）
3. 分配优先级：P0（阻塞器）→ P4（低）
4. 包含边缘情况和潜在bug

**测试用例格式：** TC-[CATEGORY]-[NUMBER]（例如，TC-CLI-001、TC-WEB-042、TC-SEC-007）

**参考：** 见`references/google_testing_standards.md`以获取完整的AAA模式指南和覆盖率阈值。

### 3. 测试执行和跟踪

**真值原则（关键）：**
- **测试用例文档**（例如，`02-CLI-TEST-CASES.md`）= **权威来源**用于测试步骤
- **跟踪CSV** = 仅执行状态（不要信任CSV用于测试规范）
- 见`references/ground_truth_principle.md`以防止文档/CSV同步问题

**手动执行：**
1. 从类别文档阅读测试用例（例如，`02-CLI-TEST-CASES.md`）← **总是从这里开始**
2. 按照文档精确执行测试步骤
3. **立即**在每次测试后更新`TEST-EXECUTION-TRACKING.csv`
4. 如果测试失败，在`BUG-TRACKING-TEMPLATE.csv`中提交bug

**自主执行（推荐）：**
1. 从`references/master_qa_prompt.md`复制master prompt
2. 粘贴到LLM会话
3. LLM自动执行、自动跟踪、自动提交bug、自动生成报告

**创新：** 比手动快100倍 + 零人工跟踪错误 + 自动恢复能力。

### 4. Bug报告

使用适当的严重性分类提交bug：

**必需字段：**
- Bug ID：顺序（BUG-001、BUG-002、...）
- 严重性：P0（24h修复）→ P4（可选）
- 重现步骤：编号、具体
- 环境：操作系统、版本、配置

**严重性分类：**
- **P0（阻塞器）**：安全漏洞、核心功能损坏、数据丢失
- **P1（关键）**：主要功能损坏，有变通方法
- **P2（高）**：次要功能问题、边缘情况
- **P3（中）**：美观问题
- **P4（低）**：文档拼写错误

**参考：** 见`BUG-TRACKING-TEMPLATE.csv`以获取完整模板及示例。

### 5. 质量指标计算

计算全面的QA指标和质量门控状态：

```bash
python scripts/calculate_metrics.py <path/to/TEST-EXECUTION-TRACKING.csv>
```

**指标仪表板包括：**
- 测试执行进度（X/Y测试，Z%完成）
- 通过率（已执行/通过%）
- Bug分析（唯一bug、P0/P1/P2细分）
- 质量门控状态（每个门控✅/❌）

**质量门控（所有必须通过以发布）：**
| 门控 | 目标 | 阻塞器 |
|------|--------|---------|
| 测试执行 | 100% | 是 |
| 通过率 | ≥80% | 是 |
| P0 Bug | 0 | 是 |
| P1 Bug | ≤5 | 是 |
| 代码覆盖率 | ≥80% | 是 |
| 安全 | 90% OWASP | 是 |

### 6. 进度报告

为利益相关者生成QA报告：

**每日摘要（每天结束时）：**
- 执行的测试、通过率、提交的bug
- 阻塞器（或无）
- 明天的计划

**每周报告（每周五）：**
- 使用模板：`WEEKLY-PROGRESS-REPORT.md`（由init脚本创建）
- 对照基线比较：`BASELINE-METRICS.md`
- 评估质量门控和趋势

**参考：** 见`references/llm_prompts_library.md`以获取30+个即用型报告提示。

### 7. 安全测试（OWASP）

实施OWASP Top 10安全测试：

**覆盖率目标：**
1. **A01：损坏的访问控制** - RLS绕过、权限提升
2. **A02：加密失败** - Token加密、密码哈希
3. **A03：注入** - SQL注入、XSS、命令注入
4. **A04：不安全设计** - 速率限制、异常检测
5. **A05：安全错误配置** - 详细错误、默认凭据
6. **A07：身份验证失败** - 会话劫持、CSRF
7. **其他**：数据完整性、日志记录、SSRF

**目标：** 90% OWASP覆盖率（9/10威胁已缓解）。

每个安全测试遵循带有特定攻击向量的AAA模式。

## 第1天入职

对于加入项目的新QA工程师，完成5小时入职指南：

**阅读：** `references/day1_onboarding.md`

**时间线：**
- 第1小时：环境设置（数据库、开发服务器、依赖项）
- 第2小时：文档审阅（测试策略、质量门控）
- 第3小时：测试数据设置（用户、CLI、DevTools）
- 第4小时：执行第一个测试用例
- 第5小时：团队入职和第1周规划

**检查点：** 到第1天结束时，环境运行、第一个测试已执行、准备好第1周。

## 自主执行（⭐ 推荐）

启用带有单个master prompt的LLM驱动的自主QA测试：

**阅读：** `references/master_qa_prompt.md`

**功能：**
- 自动从上次完成的测试恢复（读取跟踪CSV）
- 自动执行测试用例（第1-5周进度）
- 自动跟踪结果（每次测试后更新CSV）
- 自动提交bug（为失败创建bug报告）
- 自动生成报告（每日摘要、每周报告）
- 自动升级P0 bug（停止测试，通知利益相关者）

**好处：**
- 比手动快100倍执行
- 跟踪中零人工错误
- 一致的bug文档
- 立即的进度可见性

**用法：** 复制master prompt，粘贴到LLM，让它自主运行5周。

## 为你的项目调整

### 小型项目（50个测试）
- 时间线：2周
- 类别：2-3个（例如，前端、后端）
- 每天：5-7个测试
- 报告：仅每日摘要

### 中型项目（200个测试）
- 时间线：4周
- 类别：4-5个（CLI、Web、API、DB、安全）
- 每天：10-12个测试
- 报告：每日 + 每周

### 大型项目（500+个测试）
- 时间线：8-10周
- 类别：6-8个（多个组件）
- 每天：10-15个测试
- 报告：每日 + 每周 + 双周利益相关者

## 参考文档

访问来自捆绑参考的详细指南：

- **`references/day1_onboarding.md`** - 新QA工程师的5小时入职指南
- **`references/master_qa_prompt.md`** - 用于自主LLM执行的单个命令（100倍加速）
- **`references/llm_prompts_library.md`** - 30+个即用型提示用于特定QA任务
- **`references/google_testing_standards.md`** - AAA模式、覆盖率阈值、快速失败验证
- **`references/ground_truth_principle.md`** - 防止文档/CSV同步问题（对测试套件完整性至关重要）

## 资产和模板

测试用例模板和bug报告格式：

- **`assets/templates/TEST-CASE-TEMPLATE.md`** - 带有CLI和安全示例的完整模板

## 脚本

用于QA基础设施的自动化脚本：

- **`scripts/init_qa_project.py`** - 初始化QA基础设施（一键设置）
- **`scripts/calculate_metrics.py`** - 生成质量指标仪表板

## 常见模式

### 模式1：从零开始QA
```
1. python scripts/init_qa_project.py my-app ./
2. 填充BASELINE-METRICS.md（记录当前状态）
3. 使用assets/templates/TEST-CASE-TEMPLATE.md编写测试用例
4. 从references/master_qa_prompt.md复制master prompt
5. 粘贴到LLM → 自主执行开始
```

### 模式2：LLM驱动的测试（自主）
```
1. 阅读references/master_qa_prompt.md
2. 复制单个master prompt（一个段落）
3. 粘贴到LLM会话
4. LLM在5周内执行所有342个测试用例
5. LLM自动更新跟踪CSV
6. LLM自动生成每周报告
```

### 模式3：添加安全测试
```
1. 阅读references/google_testing_standards.md（OWASP部分）
2. 为每个OWASP威胁编写TC-SEC-XXX测试用例
3. 目标90%覆盖率（9/10威胁）
4. 在测试用例中记录缓解措施
```

### 模式4：第三方QA交接
```
1. 确保所有模板已填充
2. 验证BASELINE-METRICS.md完整
3. 打包tests/docs/文件夹
4. 包含references/master_qa_prompt.md以进行自主执行
5. QA团队可以立即开始（第1天入职 → 5周测试）
```

## 成功标准

此skill在以下情况下有效：
- ✅ 任何工程师都可以重现的测试用例
- ✅ 客观测量质量门控
- ✅ Bug完全记录并带有重现步骤
- ✅ 在CSV跟踪中实时可见进度
- ✅ 启用自主执行（LLM可以执行完整计划）
- ✅ 第三方QA团队可以立即开始测试
