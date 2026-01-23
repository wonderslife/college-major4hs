# PDF Creator - PDF创建器

## 简介

PDF Creator skill用于使用weasyprint从markdown创建专业的PDF文档，带有适当的中文字体支持。

## 快速开始

转换单个markdown文件：

```bash
uv run --with weasyprint --with markdown scripts/md_to_pdf.py input.md output.pdf
```

批量转换多个文件：

```bash
uv run --with weasyprint --with markdown scripts/batch_convert.py *.md --output-dir ./pdfs
```

## macOS环境设置

如果遇到库错误，先设置这些环境变量：

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
```

## 字体配置

脚本使用这些中文字体（带有回退）：

| 字体类型 | 主要 | 回退 |
|-----------|---------|--------|
| 正文 | 宋体 SC | SimSun、STSong、Noto Serif CJK SC |
| 标题 | 黑体 SC | SimHei、STHeiti、Noto Sans CJK SC |

## 输出规范

- **页面大小**：A4
- **边距**：上下2.5cm，左右2cm
- **正文字体**：12pt，1.8行高
- **最大文件大小**：设计保持在2MB以下以进行表单提交

## 常见用例

1. **法律文档**：商标备案、合同、证据列表
2. **报告**：业务报告、技术文档
3. **正式信函**：需要打印格式的官方通信

## 故障排除

**问题：** 中文字符显示为方框
**解决方案：** 确保系统上安装了宋体 SC或其他中文字体

**问题：** `weasyprint`导入错误
**解决方案：** 使用`uv run --with weasyprint --with markdown`运行以确保依赖项
