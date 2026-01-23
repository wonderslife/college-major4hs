# Finishing a Development Branch - 完成开发分支

## 简介

Finishing a Development Branch skill用于当实施完成、所有测试通过时，通过展示清晰选项并处理所选工作流来指导开发工作的完成。

## 使用场景

- 实施完成
- 所有测试通过
- 需要决定如何集成工作
- 准备合并、PR或清理

## 核心流程

### 步骤1：验证测试

**在展示选项之前，验证测试通过：**

```bash
# 运行项目的测试套件
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
测试失败（<N>次失败）。必须在完成之前修复：

[展示失败]

无法继续合并/PR，直到测试通过。
```

停止。不要继续到步骤2。

**如果测试通过：** 继续到步骤2。

### 步骤2：确定基础分支

```bash
# 尝试常见的基础分支
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或询问："此分支从main分出 - 这正确吗？"

### 步骤3：展示选项

准确展示这4个选项：

```
实施完成。你想做什么？

1. 本地合并回<base-branch>
2. 推送并创建Pull Request
3. 保持分支原样（我稍后处理）
4. 丢弃此工作

哪个选项？
```

**不要添加解释** - 保持选项简洁。

### 步骤4：执行选择

#### 选项1：本地合并

```bash
# 切换到基础分支
git checkout <base-branch>

# 拉取最新
git pull

# 合并功能分支
git merge <feature-branch>

# 在合并结果上验证测试
<test command>

# 如果测试通过
git branch -d <feature-branch>
```

然后：清理worktree（步骤5）

#### 选项2：推送并创建PR

```bash
# 推送分支
git push -u origin <feature-branch>

# 创建PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## 摘述
[更改了什么的2-3个要点]

## 测试计划
- [ ] [验证步骤]
EOF
)"
```

然后：清理worktree（步骤5）

#### 选项3：保持原样

报告："保持分支<name>。Worktree保存在<path>。"

**不要清理worktree。**

#### 选项4：丢弃

**先确认：**
```
这将永久删除：
- 分支<name>
- 所有提交：<commit-list>
- <path>的worktree

输入'discard'以确认。
```

等待确切确认。

如果确认：
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

然后：清理worktree（步骤5）

### 步骤5：清理Worktree

**对于选项1、2、4：**

检查是否在worktree中：
```bash
git worktree list | grep $(git branch --show-current)
```

如果是：
```bash
git worktree remove <worktree-path>
```

**对于选项3：** 保持worktree。

## 快速参考

| 选项 | 合并 | 推送 | 保持Worktree | 清理分支 |
|--------|-------|------|---------------|----------------|
| 1. 本地合并 | ✓ | - | - | ✓ |
| 2. 创建PR | - | ✓ | ✓ | - |
| 3. 保持原样 | - | - | ✓ | - |
| 4. 丢弃 | - | - | - | ✓（强制）|

## 常见错误

**跳过测试验证**
- **问题：** 合并坏代码，创建失败的PR
- **修复：** 在提供选项之前总是验证测试

**开放式问题**
- **问题：** "接下来我该做什么？" → 模糊
- **修复：** 展示准确的4个结构化选项

**自动worktree清理**
- **问题：** 移除worktree当可能需要它（选项2、3）
- **修复：** 仅对选项1和4清理

**没有确认的丢弃**
- **问题：** 意外删除工作
- **修复：** 要求输入'discard'确认

## 红旗

**从不：**
- 用失败的测试继续
- 在验证测试结果的情况下合并
- 在没有确认的情况下删除工作
- 在没有明确请求的情况下强制推送

**总是：**
- 在提供选项之前验证测试
- 展示准确的4个选项
- 为选项4要求输入的'discard'确认
- 仅对选项1和4清理worktree
