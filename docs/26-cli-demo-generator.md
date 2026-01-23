# CLI Demo Generator - CLI演示生成器

## 简介

CLI Demo Generator skill用于创建专业的动画CLI演示。此skill支持从命令描述的自动生成和用于自定义演示的手动控制。

## 使用场景

当用户请求时触发此skill：
- "创建一个演示来展示如何安装我的包"
- "为这些命令生成CLI演示"
- "制作我的终端工作流的动画GIF"
- "录制终端会话并转换为GIF"
- "从配置批量生成演示"
- "创建交互式打字演示"

## 核心能力

### 1. 自动演示生成（推荐）

使用`auto_generate_demo.py`脚本进行快速、自动的演示创建。这是最简单和最常用的方法。

**基本用法：**
```bash
scripts/auto_generate_demo.py \
  -c "npm install my-package" \
  -c "npm run build" \
  -o demo.gif
```

**带选项：**
```bash
scripts/auto_generate_demo.py \
  -c "command1" \
  -c "command2" \
  -o output.gif \
  --title "Installation Demo" \
  --theme "Dracula" \
  --width 1400 \
  --height 700
```

**脚本参数：**
- `-c, --command`：要包含的命令（可以指定多次）
- `-o, --output`：输出GIF文件路径（必需）
- `--title`：演示标题（可选，在开始时显示）
- `--theme`：VHS主题（默认：Dracula）
- `--font-size`：字体大小（默认：16）
- `--width`：终端宽度（默认：1400）
- `--height`：终端高度（默认：700）
- `--no-execute`：仅生成tape文件，不执行VHS

**智能功能：**
- 基于命令复杂性的自动时序
- 优化的睡眠持续时间（根据操作1-3秒）
- 命令之间的适当间距
- 专业的默认值

### 2. 批量演示生成

使用`batch_generate.py`从配置文件创建多个演示。

**配置文件（YAML）：**
```yaml
demos:
  - name: "Install Demo"
    output: "install.gif"
    title: "Installation"
    theme: "Dracula"
    commands:
      - "npm install my-package"
      - "npm run build"

  - name: "Usage Demo"
    output: "usage.gif"
    commands:
      - "my-package --help"
      - "my-package run"
```

**用法：**
```bash
scripts/batch_generate.py config.yaml --output-dir ./demos
```

**何时使用批量生成：**
- 创建一系列相关的演示
- 为教程或文档记录多个功能
- 为教程或文档生成演示
- 维护一致的演示系列

### 3. 交互式录制

使用`record_interactive.sh`录制实时终端会话。

**用法：**
```bash
scripts/record_interactive.sh output.gif \
  --theme "Dracula" \
  --width 1400
```

**录制过程：**
1. 脚本启动asciinema录制
2. 在终端中自然地输入命令
3. 完成时按Ctrl+D
4. 脚本通过VHS自动转换为GIF

**何时使用交互式录制：**
- 演示复杂的工作流
- 展示真实的命令输出
- 捕获实时交互
- 录制调试会话

### 4. 手动Tape文件创建

为了最大控制，使用模板手动创建VHS tape文件。

**可用模板：**
- `assets/templates/basic.tape` - 简单的命令演示
- `assets/templates/interactive.tape` - 打字模拟

**示例工作流：**
1. 复制模板：`cp assets/templates/basic.tape my-demo.tape`
2. 编辑命令和时序
3. 生成GIF：`vhs < my-demo.tape`

有关完整的VHS语法参考，请参阅`references/vhs_syntax.md`。

## 工作流指导

### 对于简单演示（1-3个命令）

使用自动生成以快速获得结果：

```bash
scripts/auto_generate_demo.py \
  -c "echo 'Hello World'" \
  -c "ls -la" \
  -o hello-demo.gif \
  --title "Hello Demo"
```

### 对于多个相关演示

创建批量配置文件并使用批量生成：

1. 创建`demos-config.yaml`，包含所有演示定义
2. 运行：`scripts/batch_generate.py demos-config.yaml --output-dir ./output`
3. 所有演示自动生成，具有一致的设置

### 对于交互式/复杂工作流

使用交互式录制以捕获真实行为：

```bash
scripts/record_interactive.sh my-workflow.gif
# 自然地输入命令
# 完成时按Ctrl+D
```

### 对于自定义时序/布局

创建手动tape文件，具有精确控制：

1. 从模板开始或使用`--no-execute`生成基础tape
2. 编辑时序、添加注释、自定义布局
3. 生成：`vhs < custom-demo.tape`

## 最佳实践

有关全面的指南，请参阅`references/best_practices.md`。关键推荐：

**时序：**
- 快速命令（ls、pwd）：1秒睡眠
- 标准命令（grep、cat）：2秒睡眠
- 重型操作（install、build）：3秒+睡眠

**尺寸：**
- 标准：1400×700（推荐）
- 紧凑：1200×600
- 演示文稿：1800×900

**主题：**
- 文档：Nord、GitHub Dark
- 代码演示：Dracula、Monokai
- 演示文稿：高对比度主题

**持续时间：**
- 目标：15-30秒
- 最大：60秒
- 为复杂主题创建系列

## 故障排除

### VHS未安装

```bash
# macOS
brew install vhs

# Linux（通过Go）
go install github.com/charmbracelet/vhs@latest
```

### Asciinema未安装

```bash
# macOS
brew install asciinema

# Linux
sudo apt install asciinema
```

### 演示文件太大

**解决方案：**
1. 减少持续时间（更短的睡眠时间）
2. 使用更小的尺寸（1200×600）
3. 考虑MP4格式：`Output demo.mp4`
4. 拆分为多个更短的演示

### 输出不可读

**解决方案：**
1. 增加字体大小：`--font-size 18`
2. 使用更宽的终端：`--width 1600`
3. 选择高对比度主题：`--theme "Dracula"`
4. 在目标显示设备上测试

## 示例

### 示例1：快速安装演示

用户请求："创建一个展示npm install的演示"

```bash
scripts/auto_generate_demo.py \
  -c "npm install my-package" \
  -o install-demo.gif \
  --title "Package Installation"
```

### 示例2：多步教程

用户请求："创建一个展示项目设置的演示，带有git clone、install和run"

```bash
scripts/auto_generate_demo.py \
  -c "git clone https://github.com/user/repo.git" \
  -c "cd repo" \
  -c "npm install" \
  -c "npm start" \
  -o setup-demo.gif \
  --title "Project Setup" \
  --theme "Nord"
```

### 示例3：批量生成

用户请求："为我的CLI工具的所有功能生成演示"

1. 创建`features-demos.yaml`：
```yaml
demos:
  - name: "Help Command"
    output: "help.gif"
    commands: ["my-tool --help"]

  - name: "Init Command"
    output: "init.gif"
    commands: ["my-tool init", "ls -la"]

  - name: "Run Command"
    output: "run.gif"
    commands: ["my-tool run --verbose"]
```

2. 生成所有：
```bash
scripts/batch_generate.py features-demos.yaml --output-dir ./demos
```

### 示例4：交互式会话

用户请求："录制我使用CLI工具的交互式会话"

```bash
scripts/record_interactive.sh my-session.gif --theme "Tokyo Night"
# 用户自然地输入命令
# 完成时按Ctrl+D
```

## 捆绑资源

### scripts/
- **`auto_generate_demo.py`** - 从命令列表进行自动演示生成
- **`batch_generate.py`** - 从YAML/JSON配置生成多个演示
- **`record_interactive.sh`** - 录制和转换交互式终端会话

### references/
- **`vhs_syntax.md`** - 完整的VHS tape文件语法参考
- **`best_practices.md`** - 演示创建指南和最佳实践

### assets/
- **`templates/basic.tape`** - 基本命令演示模板
- **`templates/interactive.tape`** - 交互式打字演示模板
- **`examples/batch-config.yaml`** - 示例批量配置文件

## 依赖项

**必需：**
- VHS（https://github.com/charmbracelet/vhs）

**可选：**
- asciinema（用于交互式录制）
- PyYAML（用于批量YAML配置）：`pip install pyyaml`

## 输出格式

VHS支持多种输出格式：

```tape
Output demo.gif     # GIF（默认，最适合文档）
Output demo.mp4     # MP4（对于长演示更好的压缩）
Output demo.webm    # WebM（更小的文件大小）
```

根据用例选择：
- **GIF**：文档、README文件、易于嵌入
- **MP4**：更长的演示、更好的质量、更小的尺寸
- **WebM**：Web优化、最小的文件大小

## 摘要

此skill提供三种主要方法：

1. **自动**（`auto_generate_demo.py`）- 快速、简单、智能的默认值
2. **批量**（`batch_generate.py`）- 多个演示、一致的设置
3. **交互式**（`record_interactive.sh`）- 实时录制、真实输出

选择最适合用户需求的方法。对于大多数情况，自动生成是最快和最方便的选项。
