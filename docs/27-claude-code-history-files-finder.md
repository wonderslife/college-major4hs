# Claude Code History Files Finder - Claude Code历史文件查找器

## 简介

Claude Code History Files Finder skill用于从`~/.claude/projects/`中存储的Claude Code会话历史文件中提取和恢复内容。

## 能力

- 从以前的会话中恢复删除或丢失的文件
- 跨会话历史搜索特定代码或内容
- 跨过去的会话分析文件修改
- 随时间跟踪工具使用和文件操作
- 查找包含特定关键词或主题的会话

## 会话文件位置

会话文件存储在`~/.claude/projects/<normalized-path>/<session-id>.jsonl`。

有关详细的JSONL结构和提取模式，请参阅`references/session_file_format.md`。

## 核心操作

### 1. 列出项目的会话

查找项目的所有会话文件：

```bash
python3 scripts/analyze_sessions.py list /path/to/project
```

显示带有时间戳和大小的最近会话。

可选：`--limit N`仅显示N个会话（默认：10）。

### 2. 搜索会话中的关键词

查找包含特定内容的会话：

```bash
python3 scripts/analyze_sessions.py search /path/to/project keyword1 keyword2
```

返回按关键词频率排序的会话，带有：
- 总提及计数
- 每个关键词细分
- 会话日期和路径

可选：`--case-sensitive`进行精确匹配。

### 3. 恢复删除的内容

从会话历史中提取文件：

```bash
python3 scripts/recover_content.py /path/to/session.jsonl
```

提取所有Write工具调用并将文件保存到`./recovered_content/`。

**按关键词过滤：**

```bash
python3 scripts/recover_content.py session.jsonl -k ModelLoading FRONTEND deleted
```

仅恢复其路径中匹配任何关键词的文件。

**自定义输出目录：**

```bash
python3 scripts/recover_content.py session.jsonl -o ./my_recovery/
```

### 4. 分析会话统计

获取详细的会话指标：

```bash
python3 scripts/analyze_sessions.py stats /path/to/session.jsonl
```

报告：
- 消息计数（用户/助手）
- 工具使用细分
- 文件操作计数（Write/Edit/Read）

可选：`--show-files`列出所有文件操作。

## 工作流示例

有关文件恢复、跟踪文件演变和批处理的详细工作流示例，请参阅`references/workflow_examples.md`。

## 恢复最佳实践

### 去重

`recover_content.py`自动仅保留每个文件的最新版本。如果文件在会话中被多次写入，仅保存最终版本。

### 关键词选择

选择出现在以下内容的独特关键词：
- 文件名或路径
- 函数/类名
- 代码中的唯一字符串
- 错误消息或注释

### 输出组织

创建描述性的输出目录：

```bash
# 坏
python3 scripts/recover_content.py session.jsonl -o ./output/

# 好
python3 scripts/recover_content.py session.jsonl -o ./recovered_deleted_docs/
python3 scripts/recover_content.py session.jsonl -o ./feature_xy_history/
```

### 验证

恢复后，始终验证内容：

```bash
# 检查文件列表
ls -lh ./recovered_content/

# 阅读恢复报告
cat ./recovered_content/recovery_report.txt

# 抽查内容
head -20 ./recovered_content/ImportantFile.jsx
```

## 限制

### 可以恢复什么

✅ 使用Write工具写入的文件
✅ 代码块中显示的代码（部分提取）
✅ 来自Edit/Read操作的文件路径

### 不能恢复什么

❌ 从未写入磁盘的文件（仅讨论）
❌ 会话开始前删除的文件
❌ 二进制文件（图像、PDF）- 仅路径可用
❌ 会话中未捕获的外部工具输出

### 文件版本

- 仅在调用Write工具时捕获状态
- Write调用之间的中间编辑丢失
- Edit操作显示增量，不是完整内容

## 故障排除

### 没有找到会话

```bash
# 验证项目路径规范化
ls ~/.claude/projects/ | grep -i "project-name"

# 检查实际项目目录
ls -la ~/.claude/projects/
```

### 恢复为空

可能原因：
- 文件被编辑（Edit工具）但从未写入（Write工具）
- 关键词不匹配会话中的文件路径
- 会话早于文件创建

解决方案：
- 尝试`--show-edits`标志以查看Edit操作
- 扩大关键词搜索
- 搜索相邻会话

### 大型会话文件

对于会话>100MB：
- 脚本使用流式（逐行处理）
- 内存使用保持不变
- 处理可能需要1-2分钟

## 安全和隐私

### 在共享恢复的内容之前

会话文件可能包含：
- 带有用户名的绝对路径
- API密钥或凭据
- 公司特定信息

共享前始终清理：

```bash
# 移除绝对路径
sed -i '' 's|/Users/[^/]*/|/Users/username/|g' file.js

# 验证没有凭据
grep -i "api_key\|password\|token" recovered_content/*
```

### 安全存储

恢复的内容继承自原始会话的敏感性。安全存储并遵循处理会话数据的组织策略。
