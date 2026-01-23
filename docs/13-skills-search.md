# Skills Search - Skills搜索

## 简介

Skills Search skill用于搜索、发现、安装和管理来自CCPM（Claude Code Plugin Manager）注册表的Claude Code skills。此skill包装`ccpm` CLI以提供无缝的skill发现和安装。

## 快速开始

```bash
# 搜索skills
ccpm search <query>

# 安装skill
ccpm install <skill-name>

# 列出已安装的skills
ccpm list

# 获取skill详情
ccpm info <skill-name>
```

## 命令参考

### 搜索Skills

搜索CCPM注册表以查找匹配查询的skills。

```bash
ccpm search <query> [options]

选项：
  --limit <n>    最大结果数（默认：10）
  --json         输出为JSON
```

**示例：**
```bash
ccpm search pdf              # 查找PDF相关skills
ccpm search "code review"    # 查找代码审查skills
ccpm search cloudflare       # 查找Cloudflare工具
ccpm search --limit 20 react # 查找React skills，显示20个结果
```

### 安装Skills

安装skill以使其在Claude Code中可用。

```bash
ccpm install <skill-name> [options]

选项：
  --project      仅安装到当前项目（默认：用户级别）
  --force        即使已安装也强制重新安装
```

**示例：**
```bash
ccpm install pdf-processor                    # 安装pdf-processor skill
ccpm install @daymade/skill-creator           # 安装命名空间skill
ccpm install cloudflare-troubleshooting       # 安装故障排除skill
ccpm install react-component-builder --project # 仅为当前项目安装
```

**重要：** 安装skill后，必须重启Claude Code以使skill可用。

### 列出已安装的Skills

显示当前所有已安装的skills。

```bash
ccpm list [options]

选项：
  --json         输出为JSON
```

**输出包括：**
- Skill名称和版本
- 安装范围（用户/项目）
- 安装路径

### 获取Skill信息

显示来自注册表的skill的详细信息。

```bash
ccpm info <skill-name>
```

**输出包括：**
- 名称、描述、版本
- 作者和仓库
- 下载次数和标签
- 依赖项（如果有）

**示例：**
```bash
ccpm info skill-creator
```

### 卸载Skills

移除已安装的skill。

```bash
ccpm uninstall <skill-name> [options]

选项：
  --global       从用户级别安装卸载
  --project      从项目级别安装卸载
```

**示例：**
```bash
ccpm uninstall pdf-processor
```

## 工作流：查找和安装Skills

当用户需要可能作为skill可用的功能时：

1. **搜索** 相关skills：
   ```bash
   ccpm search <relevant-keywords>
   ```

2. **审阅** 搜索结果 - 检查下载次数和描述

3. **获取详情** 有前景的skills：
   ```bash
   ccpm info <skill-name>
   ```

4. **安装** 选择的skill：
   ```bash
   ccpm install <skill-name>
   ```

5. **通知用户** 重启Claude Code以使用新skill

## 热门Skills

用户可能需要的常见skills：

| Skill | 目的 |
|-------|---------|
| `skill-creator` | 创建新的Claude Code skills |
| `pdf-processor` | PDF操作和分析 |
| `docx` | Word文档处理 |
| `xlsx` | Excel电子表格操作 |
| `pptx` | PowerPoint演示文稿创建 |
| `cloudflare-troubleshooting` | 调试Cloudflare问题 |
| `prompt-optimizer` | 改进提示质量 |

## 故障排除

### "ccpm: command not found"

全局安装CCPM：
```bash
npm install -g @daymade/ccpm
```

更多信息，请访问[CCPM官方网站](https://ccpm.dev)。

### 安装后Skill不可用

重启Claude Code - skills在启动时加载。

### 权限错误

尝试使用用户范围安装（默认）或检查对`~/.claude/skills/`的写权限。
