# Requesting Code Review - 请求代码审查

## 简介

Requesting Code Review skill用于在完成任务、实现主要功能或合并之前，通过分派superpowers:code-reviewer子代理来在问题级联之前捕获问题。

## 使用场景

**强制性：**
- subagent-driven development中的每个任务后
- 完成主要功能后
- 合并到main之前

**可选但有价值：**
- 当卡住时（新视角）
- 重构之前（基线检查）
- 修复复杂bug后

## 核心流程

### 1. 获取git SHA

```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或 origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

### 2. 分派code-reviewer子代理

使用Task工具与superpowers:code-reviewer类型，填写`requesting-code-review/code-reviewer.md`中的模板

**占位符：**
- `{WHAT_WAS_IMPLEMENTED}` - 你刚刚构建了什么
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交
- `{DESCRIPTION}` - 简要摘要

### 3. 对反馈采取行动

- 立即修复关键问题
- 在继续之前修复重要问题
- 注意次要问题以备后用
- 如审查者错误，用推理推回

## 示例

```
[刚完成Task 2: 添加验证函数]

你：让我在继续之前请求代码审查。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[分派superpowers:code-reviewer子代理]
  WHAT_WAS_IMPLEMENTED: 对话索引的验证和修复函数
  PLAN_OR_REQUIREMENTS: docs/plans/deployment-plan.md中的Task 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: 添加了verifyIndex()和repairIndex()，包含4个问题类型

[子代理返回]：
  优势：清洁的架构，真实测试
  问题：
    重要：缺少进度指示器
    次要：魔法数字（100）用于报告间隔
  评估：准备继续

你：[修复进度指示器]
[继续到Task 3]
```

## 与工作流集成

### Subagent-Driven Development
- 每个任务后审查
- 在问题级联之前捕获
- 在移到下一个任务之前修复

### Executing Plans
- 每批次后审查（3个任务）
- 获取反馈，应用，继续

### 临时开发
- 合并前审查
- 卡住时审查

## 红旗

**从不：**
- 因为"它简单"而跳过审查
- 忽略关键问题
- 用未修复的重要问题继续
- 用有效的技术反馈争论

**如果审查者错误：**
- 用技术推理推回
- 展示证明它工作的代码/测试
- 请求澄清

## 模板位置

参见：`requesting-code-review/code-reviewer.md`
