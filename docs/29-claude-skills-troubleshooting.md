# Claude Skills Troubleshooting - Claude Skills故障排除

## 简介

Claude Skills Troubleshooting skill用于诊断和解决Claude Code插件和skill配置问题。此skill提供插件安装、启用和激活问题的系统化调试工作流。

## 快速诊断

运行诊断脚本以识别常见问题：

```bash
python3 scripts/diagnose_plugins.py
```

脚本检查：
- 已安装 vs 已启用插件不匹配
- settings.json中缺失的enabledPlugins条目
- 陈旧的marketplace缓存
- 无效的插件配置

## 常见问题

### 问题1：插件已安装但未在可用skills列表中显示

**症状：**
- `/plugin`显示插件为已安装
- Skill未出现在Skill工具的可用列表中
- `installed_plugins.json`中存在插件元数据

**根本原因：** 已知bug（[GitHub #17832](https://github.com/anthropics/claude-code/issues/17832)）- 插件被添加到`installed_plugins.json`但**未**自动添加到`settings.json`中的`enabledPlugins`。

**诊断：**
```bash
# 检查插件是否在installed_plugins.json中
cat ~/.claude/plugins/installed_plugins.json | grep "plugin-name"

# 检查插件是否在settings.json中启用
cat ~/.claude/settings.json | grep "plugin-name"
```

**解决方案：**
```bash
# 选项1：使用CLI启用
claude plugin enable plugin-name@marketplace-name

# 选项2：手动编辑settings.json
# 添加到enabledPlugins部分：
# "plugin-name@marketplace-name": true
```

### 问题2：理解插件状态架构

**关键文件：**

| 文件 | 目的 |
|------|---------|
| `~/.claude/plugins/installed_plugins.json` | 所有插件的注册表（已安装 + 已禁用） |
| `~/.claude/settings.json` → `enabledPlugins` | 控制哪些插件是**活跃**的 |
| `~/.claude/plugins/known_marketplaces.json` | 注册的marketplace来源 |
| `~/.claude/plugins/cache/` | 实际的插件文件 |

**插件活跃仅当：**
1. 存在于`installed_plugins.json`中（已注册）
2. 列在`settings.json` → `enabledPlugins`中，值为`true`

### 问题3：Marketplace缓存陈旧

**症状：**
- GitHub有最新更改
- 安装找到插件但获取旧版本
- 新添加的插件不可见

**解决方案：**
```bash
# 更新marketplace缓存
claude plugin marketplace update marketplace-name

# 或清除并重新获取
rm -rf ~/.claude/plugins/cache/marketplace-name
claude plugin marketplace update marketplace-name
```

### 问题4：在Marketplace中找不到插件

**常见原因（按可能性排序）：**

1. **本地更改未推送到GitHub** - 最常见！
   ```bash
   git status
   git push
   claude plugin marketplace update marketplace-name
   ```

2. **marketplace.json配置错误**
   ```bash
   python3 -m json.tool .claude-plugin/marketplace.json
   ```

3. **Skill目录缺失**
   ```bash
   ls -la skill-name/SKILL.md
   ```

## 诊断命令参考

| 目的 | 命令 |
|---------|---------|
| 列出marketplaces | `claude plugin marketplace list` |
| 更新marketplace | `claude plugin marketplace update {name}` |
| 安装插件 | `claude plugin install {plugin}@{marketplace}` |
| 启用插件 | `claude plugin enable {plugin}@{marketplace}` |
| 禁用插件 | `claude plugin disable {plugin}@{marketplace}` |
| 卸载插件 | `claude plugin uninstall {plugin}@{marketplace}` |
| 检查已安装 | `cat ~/.claude/plugins/installed_plugins.json \| jq '.plugins \| keys'` |
| 检查已启用 | `cat ~/.claude/settings.json \| jq '.enabledPlugins'` |

## 批量启用缺失的插件

要从marketplace启用所有已安装但已禁用的插件：

```bash
python3 scripts/enable_all_plugins.py marketplace-name
```

## Skills vs Commands架构

Claude Code有两种类型的用户可调用扩展：

1. **Skills**（在`skills/`目录中）
   - 基于描述匹配自动激活
   - 当用户请求匹配skill描述时加载

2. **Commands**（在`commands/`目录中）
   - 通过`/command-name`显式调用
   - 出现在Skill工具的可用列表中
   - 需要命令文件（例如，`commands/seer.md`）

如果skill应该显式可调用，添加相应的命令文件。

## 参考

- 见`references/known_issues.md`以获取GitHub问题跟踪
- 见`references/architecture.md`以获取详细的插件架构
