# Test-Driven Development (TDD) - 测试驱动开发

## 简介

Test-Driven Development (TDD) skill用于在实现任何功能或bug修复之前编写测试。核心原则：**如果你没有看到测试失败，你就不知道它是否测试了正确的东西。**

## 使用场景

**总是使用：**
- 新功能
- Bug修复
- 重构
- 行为更改

**例外（需要询问你的伙伴）：**
- 一次性原型
- 生成的代码
- 配置文件

## 红绿重构循环

### RED - 编写失败的测试

编写一个显示应该发生什么的极小测试。

**好的示例：**
```typescript
test('重试失败操作3次', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

**要求：**
- 一个行为
- 清楚的名称
- 真实代码（除非不可避免，否则没有mock）

### 验证RED - 看它失败

**强制性的。从不跳过。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试失败（不是错误）
- 失败消息是预期的
- 因为功能缺失而失败（不是拼写错误）

### GREEN - 最小代码

编写最简单的代码来通过测试。

**好的示例：**
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```

不要添加功能、重构其他代码或"改进"超出测试。

### 验证GREEN - 看它通过

**强制性的。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试通过
- 其他测试仍然通过
- 输出纯净（没有错误、警告）

### REFACTOR - 清理

只有在绿色之后：
- 删除重复
- 改进名称
- 提取辅助函数

保持测试绿色。不要添加行为。

## 铁律

```
没有失败测试的生产代码
否则 → 不是TDD
```

没有例外，除非你的伙伴明确允许。

## 常见合理化

| 借口 | 现实 |
|--------|---------|
| "太简单无法测试" | 简单代码会坏。测试需要30秒。 |
| "我稍后测试" | 立即通过的测试什么都不证明。 |
| "测试后达到相同目标" | 测试后 = "这做什么？" 测试先 = "这应该做什么？" |
| "我已经手动测试所有边缘情况" | 临时 ≠ 系统化。没有记录，无法重新运行。 |
| "删除X小时工作是浪费" | 沉没成本谬误。时间已经没了。你的选择：删除并用TDD重写（X更多小时，高信心）vs 保留并在之后添加测试（30分钟，低信心，可能bug） |
| "保留为参考，先写测试" | 你会适应它。那是测试后。删除意味着删除。 |
| "需要先探索" | 好的。丢弃探索，从TDD开始。 |
| "测试难 = 设计不清楚" | 听测试。难测试 = 难使用。 |
| "TDD会减慢我" | TDD比调试更快。实用 = 测试先。 |
| "手动测试更快" | 手动不证明边缘情况。你会在每次更改时重新测试。 |
| "现有代码没有测试" | 你在改进它。为现有代码添加测试。 |

## 验证检查表

在标记工作完成之前：

- [ ] 每个新函数/方法都有一个测试
- [ ] 在实现之前看了每个测试失败
- [ ] 每个测试都因为预期原因失败（功能缺失，不是拼写错误）
- [ ] 编写了最小代码来通过每个测试
- [ ] 所有测试通过
- [ ] 输出纯净（没有错误、警告）
- [ ] 测试使用真实代码（除非不可避免，否则没有mock）
- [ ] 边缘情况和错误被覆盖

无法检查所有框？你跳过了TDD。重新开始。

## Bug修复示例

**Bug：** 空邮箱被接受

**RED**
```typescript
test('拒绝空邮箱', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

**验证RED**
```bash
$ npm test
FAIL: expected 'Email required', got undefined
```

**GREEN**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

**验证GREEN**
```bash
$ npm test
PASS
```

**REFACTOR**
如果需要，提取多个字段的验证。
