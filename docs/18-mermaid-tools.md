# Mermaid Tools - Mermaid工具

## 简介

Mermaid Tools skill用于从markdown文件中提取Mermaid图并使用捆绑脚本生成高质量PNG图像。skill在`scripts/`目录中捆绑所有必要的脚本（`extract-and-generate.sh`、`extract_diagrams.py`和`puppeteer-config.json`）以实现可移植性和可靠性。

## 核心工作流

### 标准图提取和生成

从markdown文件中提取Mermaid图并使用捆绑的`extract-and-generate.sh`脚本生成PNG图像：

```bash
cd ~/.claude/skills/mermaid-tools/scripts
./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**参数：**
- `<markdown_file>`：包含Mermaid图的markdown文件路径
- `<output_directory>`：（可选）输出文件的目录。默认为`<markdown_file_directory>/diagrams`

**示例：**
```bash
cd ~/.claude/skills/mermaid-tools/scripts
./extract-and-generate.sh "/path/to/document.md" "/path/to/output"
```

### 脚本做什么

1. **提取** markdown文件中的所有Mermaid代码块
2. **编号** 它们按出现顺序（01、02、03等）
3. **生成** 每个图的`.mmd`文件
4. **创建** 带有智能大小的高分辨率PNG图像
5. **验证** 所有生成的PNG文件

### 输出文件

对于每个图，脚本生成：
- `01-diagram-name.mmd` - 提取的Mermaid代码
- `01-diagram-name.png` - 高分辨率PNG图像

编号确保图从源文档中保持它们的顺序。

## 高级使用

### 自定义尺寸和缩放

使用环境变量覆盖默认尺寸：

```bash
cd ~/.claude/skills/mermaid-tools/scripts
MERMAID_WIDTH=1600 MERMAID_HEIGHT=1200 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**可用变量：**
- `MERMAID_WIDTH`（默认：1200）- 基础宽度（像素）
- `MERMAID_HEIGHT`（默认：800）- 基础高度（像素）
- `MERMAID_SCALE`（默认：2）- 高分辨率输出的缩放因子

### 演示文稿的高分辨率输出

```bash
cd ~/.claude/skills/mermaid-tools/scripts
MERMAID_WIDTH=2400 MERMAID_HEIGHT=1800 MERMAID_SCALE=4 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

### 打印质量输出

```bash
cd ~/.claude/skills/mermaid-tools/scripts
MERMAID_SCALE=5 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

## 智能大小功能

脚本根据从文件名检测到的图类型自动调整尺寸：

- **Timeline/Gantt**：2400×400（宽和短）
- **Architecture/System/Caching**：2400×1600（大和详细）
- **Monitoring/Workflow/Sequence/API**：2400×800（宽用于过程流）
- **默认**：1200×800（标准尺寸）

提取过程中的上下文感知命名有助于触发适当的智能大小。

## 重要原则

### 使用捆绑脚本

**关键：** 使用此skill的`scripts/`目录中的捆绑`extract-and-generate.sh`脚本。所有必要的依赖都捆绑在一起。

### 更改到脚本目录

从其自己的目录运行脚本以正确定位依赖项（`extract_diagrams.py`和`puppeteer-config.json`）：

```bash
cd ~/.claude/skills/mermaid-tools/scripts
./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

在不先更改到scripts目录的情况下运行脚本可能会因缺少依赖而失败。

## 前提条件验证

在运行脚本之前，验证依赖项已安装：

1. **mermaid-cli**：`mmdc --version`
2. **Google Chrome**：`google-chrome-stable --version`
3. **Python 3**：`python3 --version`

如果任何缺失，请参阅`references/setup_and_troubleshooting.md`以获取安装说明。

## 故障排除

对于详细的故障排除指导，请参阅`references/setup_and_troubleshooting.md`，涵盖：
- 浏览器启动失败
- 权限问题
- 没有找到图
- Python提取失败
- 输出质量问题
- 图特定的大小问题

常见问题的快速修复：

**权限被拒绝：**
```bash
chmod +x ~/.claude/skills/mermaid-tools/scripts/extract-and-generate.sh
```

**低质量输出：**
```bash
MERMAID_SCALE=3 ./extract-and-generate.sh "<markdown_file>" "<output_directory>"
```

**Chrome/Puppeteer错误：**
验证所有WSL2依赖项已安装（见参考资料以获取完整列表）。

## 捆绑资源

### scripts/

此skill捆绑所有必要的Mermaid图生成脚本：

- **extract-and-generate.sh** - 编排提取和PNG生成的主脚本
- **extract_diagrams.py** - 从markdown提取Mermaid代码块的Python脚本
- **puppeteer-config.json** - WSL2环境的Chrome/Puppeteer配置

所有脚本必须从`scripts/`目录运行以正确定位依赖项。

### references/setup_and_troubleshooting.md

综合参考文档，包括：
- 完整的前提条件安装说明
- 详细的环境变量参考
- 广泛的故障排除指南
- WSL2特定的Chrome依赖项设置
- 验证过程

在处理设置问题、安装问题或高级自定义需求时加载此参考。
