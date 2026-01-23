# Markdown Tools - Markdown工具

## 简介

Markdown Tools skill用于将文档转换为markdown，带有图像提取和Windows/WSL路径处理。支持PDF、Word文档、PowerPoint、Confluence导出等的转换。

## 快速开始

### 安装带有PDF支持的markitdown

```bash
# 重要：使用[pdf] extra以获得PDF支持
uv tool install "markitdown[pdf]"

# 或通过pip
pip install "markitdown[pdf]"
```

### 基本转换

```bash
markitdown "document.pdf" -o output.md
# 或重定向：markitdown "document.pdf" > output.md
```

## 带图像的PDF转换

markitdown仅提取文本。对于带有图像的PDF，使用此工作流：

### 步骤1：转换文本

```bash
markitdown "document.pdf" -o output.md
```

### 步骤2：提取图像

```bash
# 在markdown旁边创建assets目录
mkdir -p assets

# 使用PyMuPDF提取图像
uv run --with pymupdf python scripts/extract_pdf_images.py "document.pdf" ./assets
```

### 步骤3：添加图像引用

在markdown中需要的地方插入图像引用：

```markdown
![描述](assets/img_page1_1.png)
```

### 步骤4：格式清理

markitdown输出通常需要手动修复：
- 添加适当的标题级别（`#`、`##`、`###`）
- 以markdown格式重构表格
- 修复坏的换行
- 恢复缩进结构

## 路径转换（Windows/WSL）

```bash
# Windows → WSL转换
C:\Users\name\file.pdf → /mnt/c/Users/name/file.pdf

# 使用辅助脚本
python scripts/convert_path.py "C:\Users\name\Documents\file.pdf"
```

## 常见问题

**"dependencies needed to read .pdf files"**
```bash
# 安装带有PDF支持
uv tool install "markitdown[pdf]" --force
```

**PDF转换期间的FontBBox警告**
- 这些是无害的字体解析警告，输出仍然正确

**输出中缺失图像**
- 使用`scripts/extract_pdf_images.py`单独提取图像

## 资源

- `scripts/extract_pdf_images.py` - 使用PyMuPDF从PDF提取图像
- `scripts/convert_path.py` - Windows到WSL路径转换器
- `references/conversion-examples.md` - 批量操作的详细示例
