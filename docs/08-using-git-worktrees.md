# Using Git Worktrees - 使用Git工作树

## 简介

Using Git Worktrees skill用于在需要与当前工作空间隔离的功能工作开始时，创建隔离的git工作树。

## 使用场景

- 开始需要与当前工作空间隔离的功能工作
- 在执行实施计划之前
- 需要在多个分支上同时工作
- 需要独立的工作环境

## 核心流程

### 目录选择过程

按此优先级顺序遵循：

#### 1. 检查现有目录

```bash
# 按优先级顺序检查
ls -d .worktrees 2>/dev/null     # 首选（隐藏）
ls -d worktrees 2>/dev/null      # 替代
```

**如果找到：** 使用该目录。如果两者都存在，`.worktrees`获胜。

#### 2. 检查CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**如果指定了偏好：** 使用它而不询问。

#### 3. 询问用户

如果不存在目录且没有CLAUDE.md偏好：

```
没有找到worktree目录。我应该在哪里创建worktrees？

1. .worktrees/（项目本地，隐藏）
2. ~/.config/superpowers/worktrees/<project-name>/（全局位置）

你更喜欢哪个？
```

### 安全验证

#### 对于项目本地目录（.worktrees或worktrees）

**必须在创建worktree之前验证目录被忽略：**

```bash
# 检查目录是否被忽略（尊重本地、全局和系统gitignore）
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果未被忽略：**

根据Jesse的规则"立即修复坏东西"：
1. 在.gitignore中添加适当的行
2. 提交更改
3. 继续worktree创建

**为什么关键：** 防止意外将worktree内容提交到仓库。

#### 对于全局目录（~/.config/superpowers/worktrees）

不需要.gitignore验证 - 完全在项目之外。

### 创建步骤

#### 1. 检测项目名称

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
```

#### 2. 创建Worktree

```bash
# 确定完整路径
case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME"
    ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"
    ;;
esac

# 使用新分支创建worktree
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

#### 3. 运行项目设置

自动检测并运行适当的设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

#### 4. 验证清洁基线

运行测试以确保worktree以清洁状态开始：

```bash
# 示例 - 使用适当的命令
npm test
cargo test
pytest
go test ./...
```

**如果测试失败：** 报告失败，询问是否继续或调查。

**如果测试通过：** 报告准备就绪。

#### 5. 报告位置

```
Worktree准备就绪在<full-path>
测试通过（<N>次测试，0次失败）
准备实现<feature-name>
```

## 快速参考

| 情况 | 操作 |
|-----------|--------|
| `.worktrees/`存在 | 使用它（验证被忽略）|
| `worktrees/`存在 | 使用它（验证被忽略）|
| 两者都存在 | 使用`.worktrees/`|
| 都不存在 | 检查CLAUDE.md → 询问用户|
| 目录未被忽略 | 添加到.gitignore + 提交|
| 基线测试失败 | 报告失败 + 询问|
| 没有package.json/Cargo.toml | 跳过依赖安装 |

## 常见错误

### 跳过忽略验证
- **问题：** Worktree内容被跟踪，污染git状态
- **修复：** 在创建项目本地worktree之前总是使用`git check-ignore`

### 假设目录位置
- **问题：** 创建不一致，违反项目约定
- **修复：** 遵循优先级：现有 > CLAUDE.md > 询问

### 用失败的测试继续
- **问题：** 无法区分新bug和预先存在的问题
- **修复：** 报告失败，获取明确许可以继续

### 硬编码设置命令
- **问题： 在使用不同工具的项目上中断
- **修复：** 从项目文件自动检测（package.json等）

## 示例工作流

```
你：我正在使用using-git-worktrees skill来设置隔离的工作空间。

[检查.worktrees/ - 存在]
[验证被忽略 - git check-ignore确认.worktrees/被忽略]
[创建worktree: git worktree add .worktrees/auth -b feature/auth]
[运行npm install]
[运行npm test - 47次通过]

Worktree准备就绪在/Users/jesse/myproject/.worktrees/auth
测试通过（47次测试，0次失败）
准备实现auth功能
```
