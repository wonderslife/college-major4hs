# Skill Creator - Skill创建器

## 简介

Skill Creator skill提供创建有效skill的指导。Skills是模块化、自包含的包，通过提供专业化知识、工作流和工具来扩展Claude的能力。

## 什么是Skill

### Skills提供什么

1. **专业化工作流** - 特定领域的多步程序
2. **工具集成** - 使用特定文件格式或API的说明
3. **领域专业知识** - 公司特定知识、schema、业务逻辑
4. **捆绑资源** - 脚本、引用和复杂重复任务的资产

### Skill的解剖

每个skill由必需的SKILL.md文件和可选的捆绑资源组成：

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter元数据（必需）
│   │   ├── name: (必需）
│   │   └── description: (必需）
│   └── Markdown说明（必需）
└── 捆绑资源（可选）
    ├── scripts/          - 可执行代码（Python/Bash/etc.）
    ├── references/       - 文档，按需加载到上下文中
    └── assets/           - 输出中使用的文件（模板、图标、字体等）
```

## Skill创建流程

### 步骤1：用具体示例理解Skill

跳过此步骤仅当skill的使用模式已经清楚理解时。

要创建有效的skill，清楚地理解skill如何使用的具体示例。这种理解可以来自直接的用户示例或用用户反馈验证的生成示例。

### 步骤2：规划可重用的Skill内容

要将具体示例转化为有效的skill，通过以下方式分析每个示例：

1. 考虑如何从 scratch执行示例
2. 确定Claude的适当自由度级别
3. 识别什么脚本、引用和资产在重复执行这些工作流时会有帮助

**将特异性与任务风险匹配：**
- **高自由度（文本说明）**：存在多个有效方法；上下文确定最佳路径（例如，代码审查、故障排除、内容分析）
- **中等自由度（带参数的伪代码）**：存在首选模式，有可接受的变体（例如，API集成模式、数据处理工作流）
- **低自由度（精确脚本）**：操作脆弱，一致性关键，顺序重要（例如，PDF旋转、数据库迁移、表单验证）

### 步骤3：初始化Skill

此时，是实际创建skill的时候。

跳过此步骤仅当正在开发的skill已经存在，并且需要迭代或打包时。在这种情况下，继续到下一步。

当从 scratch创建新skill时，总是运行`init_skill.py`脚本。脚本方便地生成新的模板skill目录，自动包含skill所需的一切，使skill创建过程更加高效和可靠。

**用法：**

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

脚本：
- 在指定路径创建skill目录
- 生成带有适当frontmatter和TODO占位符的SKILL.md模板
- 创建示例资源目录：`scripts/`、`references/`和`assets/`
- 在每个目录中添加可以自定义或删除的示例文件

初始化后，根据需要自定义或删除生成的SKILL.md和示例文件。

### 步骤4：编辑Skill

当编辑（新生成的或现有）skill时，记住skill是为另一个Claude实例使用而创建的。专注于包含对另一个Claude实例有效执行这些任务有益且非显而易见的信息。考虑什么程序知识、领域特定细节或可重用资产将帮助另一个Claude实例更有效地执行这些任务。

#### 从可重用的Skill内容开始

要开始实现，从上面识别的可重用资源开始：`scripts/`、`references/`和`assets/`文件。注意此步骤可能需要用户输入。

**当更新现有skill时：** 扫描所有现有引用文件以检查它们是否需要相应的更新。新功能通常需要对架构、工作流或其他现有文档进行更新以保持一致性。

#### 引用文件命名

文件名必须在不阅读内容的情况下自我解释。

**模式：** `<content-type>_<specificity>.md`

**示例：**
- ❌ `commands.md`、`cli_usage.md`、`reference.md`
- ✅ `script_parameters.md`、`api_endpoints.md`、`database_schema.md`

**测试：** 有人可以仅从名称理解文件的内容吗？

#### 更新SKILL.md

**写作风格：** 使用**祈使/不定式形式**（动词优先的说明），而不是第二人称。使用客观、指导性语言（例如，"要完成X，做Y"而不是"你应该做X"或"如果你需要做X"）。这为AI消费保持了一致性和清晰度。

要完成SKILL.md，回答以下问题：

1. skill的目的是什么，用几句话？
2. 什么时候应该使用skill？
3. 在实践中，Claude应该如何使用skill？上面开发的所有可重用skill内容应该被引用，以便Claude知道如何使用它们。

### 步骤5：安全审查

在打包或分发skill之前，运行安全扫描器以检测硬编码的机密和个人信息：

```bash
# 打包前必需
python scripts/security_scan.py <path/to/skill-folder>

# 详细模式包括对路径、电子邮件和代码模式的额外检查
python scripts/security_scan.py <path/to/skill-folder> --verbose
```

**检测覆盖：**
- 硬编码机密（API密钥、密码、令牌）通过gitleaks
- 详细模式中的个人信息（用户名、电子邮件、公司名称）
- 详细模式中的不安全代码模式（命令注入风险）

**首次设置：** 如果不存在，安装gitleaks：

```bash
# macOS
brew install gitleaks

# Linux/Windows - 见脚本输出以获取安装说明
```

**退出代码：**
- `0` - 清洁（可以安全打包）
- `1` - 高严重性问题
- `2` - 关键问题（分发前必须修复）
- `3` - gitleaks未安装
- `4` - 扫描错误

**检测到的机密的补救：**

1. 从所有文件中删除硬编码机密
2. 使用环境变量：`os.environ.get("API_KEY")`
3. 如果之前提交到git，轮换凭据
4. 重新运行扫描以在打包前验证修复

### 步骤6：打包Skill

一旦skill准备好，它应该被打包成可分发的zip文件，与用户共享。打包过程自动验证skill首先以确保它满足所有要求：

```bash
scripts/package_skill.py <path/to/skill-folder>
```

可选输出目录规范：

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

打包脚本将：

1. **自动验证** skill，检查：
   - YAML frontmatter格式和必需字段
   - Skill命名约定和目录结构
   - 描述完整性和质量
   - **路径引用完整性** - SKILL.md中提到的所有`scripts/`、`references/`和`assets/`路径必须存在

2. **打包** skill如果验证通过，创建以skill命名的zip文件（例如，`my-skill.zip`），包含所有文件并保持用于分发的适当目录结构。

**常见验证失败：** 如果SKILL.md引用`scripts/my_script.py`但文件不存在，验证将失败并显示"缺少引用的文件：scripts/my_script.py"。确保所有捆绑资源在打包前存在。

如果验证失败，脚本将报告错误并在不创建包的情况下退出。修复任何验证错误并再次运行打包命令。

### 步骤7：更新Marketplace

打包后，更新marketplace注册表以包含新的或更新的skill。

**对于新skill**，在`.claude-plugin/marketplace.json`中添加条目：

```json
{
  "name": "skill-name",
  "description": "从SKILL.md frontmatter description复制",
  "source": "./",
  "strict": false,
  "version": "1.0.0",
  "category": "developer-tools",
  "keywords": ["relevant", "keywords"],
  "skills": ["./skill-name"]
}
```

**对于更新的skill**，在`plugins[].version`中遵循semver进行版本升级：
- 补丁（1.0.x）：Bug修复、拼写错误更正
- 次要（1.x.0）：新功能、额外引用
- 主要（x.0.0）：破坏性更改、重构工作流

**同时更新** `metadata.version`和`metadata.description`如果整体插件集合显著更改。

### 步骤8：迭代

测试skill后，用户可能请求改进。通常这在使用skill后立即发生，具有skill如何执行的上下文。

**迭代工作流：**
1. 在真实任务上使用skill
2. 注意挣扎或低效
3. 识别SKILL.md或捆绑资源应该如何更新
4. 实施更改并再次测试

**细化过滤器：** 仅添加解决观察到的问题的内容。如果最佳实践已经覆盖它，不要重复。

## 关键原则

### 渐进式披露设计原则

Skills使用三级加载系统来高效管理上下文：

1. **元数据（名称 + 描述）** - 总是在上下文中（~100词）
2. **SKILL.md主体** - 当skill触发时（<5k词）
3. **捆绑资源** - 根据Claude需要（无限*）

*无限是因为脚本可以在不读取到上下文窗口的情况下执行。

### ⚠️ 关键：在源位置编辑Skills

**从不编辑`~/.claude/plugins/cache/`中的skills** —— 那是一个只读缓存目录。那里的所有更改是：
- 当缓存刷新时丢失
- 不同步到源控制
- 浪费需要手动重新合并的工作

**总是验证你正在编辑源仓库：**
```bash
# 错误 - 缓存位置（只读副本）
~/.claude/plugins/cache/daymade-skills/my-skill/1.0.0/my-skill/SKILL.md

# 正确 - 源仓库
/path/to/your/claude-code-skills/my-skill/SKILL.md
```

**在任何编辑之前**，确认文件路径不包含`/cache/`或`/plugins/cache/`。

## 资源类型

### Scripts（`scripts/`）

可执行代码（Python/Bash/etc.）对于需要确定性可靠性或重复重写的任务。

- **何时包括：** 当相同代码被重复重写或需要确定性可靠性时
- **示例：** 用于PDF旋转任务的`scripts/rotate_pdf.py`
- **好处：** Token高效，确定性，可以在不加载到上下文的情况下执行
- **注意：** 脚本可能仍需要由Claude读取以进行修补或环境特定调整

### References（`references/`）

文档和参考材料，旨在按需加载到上下文中以告知Claude的过程和思考。

- **何时包括：** 用于Claude在工作时应该引用的文档
- **示例：** 用于财务schema的`references/finance.md`、用于公司NDA模板的`references/mnda.md`、用于公司策略的`references/policies.md`、用于API规范的`references/api_docs.md`
- **用例：** 数据库schema、API文档、领域知识、公司策略、详细工作流指南
- **好处：** 保持SKILL.md精简，仅在Claude确定需要时加载
- **最佳实践：** 如果文件很大（>10k词），在SKILL.md中包含grep搜索模式
- **避免重复：** 信息应该存在于SKILL.md或引用文件中，而不是两者中。优先使用引用文件来获取详细信息，除非它对skill真正核心——这保持SKILL.md精简，同时使信息可发现而不会占用上下文窗口。仅在SKILL.md中保留必要的程序说明和工作流指导；将详细参考材料、schema和示例移动到引用文件。

### Assets（`assets/`）

不打算加载到上下文中的文件，而是在Claude产生的输出中使用。

- **何时包括：** 当skill需要在最终输出中使用的文件时
- **示例：** 用于品牌资产的`assets/logo.png`、用于PowerPoint模板的`assets/slides.pptx`、用于HTML/React样板代码的`assets/frontend-template/`、用于排版的`assets/font.ttf`、用于示例文档的`assets/sample-document.pdf`
- **用例：** 模板、图像、图标、样板代码、字体、被复制或修改的示例文档
- **好处：** 将输出资源与文档分离，使Claude能够使用文件而不加载它们到上下文

### 隐私和路径引用

**关键：** 打算公开分发的skills不得包含用户特定或公司特定信息：

- **禁止：** 用户目录的绝对路径（`/home/username/`、`/Users/username/`、`/mnt/c/Users/username/`）
- **禁止：** 个人用户名、公司名称、部门名称、产品名称
- **禁止：** OneDrive路径、云存储路径或任何环境特定的绝对路径
- **禁止：** 像`~/.claude/skills/`或`/Users/username/Workspace/claude-code-skills/`这样的硬编码skill安装路径
- **允许：** skill包内的相对路径（`scripts/example.py`、`references/guide.md`）
- **允许：** 标准占位符（`~/workspace/project`、`username`、`your-company`）
- **最佳实践：** 使用像`scripts/script_name.py`这样的简单相对路径来引用捆绑脚本 - Claude将解析实际位置

### 版本控制

**关键：** Skills不应在SKILL.md中包含版本历史或版本号：

- **禁止：** SKILL.md中的版本部分（`## Version`、`## Changelog`、`## Release History`）
- **禁止：** SKILL.md主体内容中的版本号
- **正确位置：** Skill版本在marketplace.json的`plugins[].version`中跟踪
- **理由：** Marketplace基础设施管理版本控制；SKILL.md应该是专注于功能的无时间内容
- **示例：** 不在SKILL.md中记录v1.0.0 → v1.1.0的更改，仅在marketplace.json中更新版本
