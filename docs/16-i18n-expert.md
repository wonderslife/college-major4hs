# I18n Expert - 国际化专家

## 简介

I18n Expert skill用于为UI代码库（React/TS、i18next或类似、JSON locales）设置、审计或强制国际化/本地化，包括安装/配置i18n框架、替换硬编码字符串、确保en-US/zh-CN覆盖、将错误代码映射到本地化消息，以及验证键奇偶性、复数化和格式化。

## 使用场景

- 设置、审计或强制UI代码库的i18n/l10n
- 安装/配置i18n框架
- 替换硬编码字符串
- 确保en-US/zh-CN覆盖
- 将错误代码映射到本地化消息
- 验证键奇偶性、复数化和格式化

## 核心能力

- 库选择和设置（React、Next.js、Vue）
- 键架构和locale文件组织
- 翻译生成和质量策略（AI、专业、手动）
- 路由和语言检测/切换
- SEO和元数据本地化（如适用）
- RTL支持（仅当RTL locales在范围内时）

## 范围输入（如不清楚则询问）

- 框架和路由风格
- 现有i18n状态（无、部分、遗留）
- 目标locales（默认：en-US + zh-CN）
- 翻译质量需求（AI vs 专业 vs 手动）
- Locale格式（JSON、YAML、PO、XLIFF）
- 正式性/文化要求（如有）

## 工作流（审计 → 修复 → 验证）

1) **确认范围和locale目标**
- 识别i18n框架和locale位置
- 确认locales；默认为en-US + zh-CN（如指定）

2) **设置i18n基线（如缺失）**
- 选择框架适当的库（例如，React：react-i18next；Next.js：next-intl；Vue：vue-i18n）
- 安装包并创建i18n入口/配置文件
- 在app根目录连接provider并加载locale资源
- 添加语言切换器和持久化（路由/param/localStorage），如适当
- 建立locale文件布局和键命名空间
- 如路由是locale感知的，早期定义locale段策略（子路径、子域、查询参数）
- 如元数据是用户面向的，包含标题/描述的翻译

3) **审计键使用和locale奇偶性**
- 运行：
  ```bash
  python scripts/i18n_audit.py --src <src-root> --locale <path/to/en-US.json> --locale <path/to/zh-CN.json>
  ```
- 将缺失键/奇偶性缺口视为阻塞器
- 手动验证动态键（`t(var)`）

4) **查找原始用户面向字符串**
- 搜索：
  ```bash
  rg -n --glob '<src>/**/*.{ts,tsx,js,jsx}' "<[^>]+>[^<{]*[A-Za-z][^<{]*<"
  rg -n --glob '<src>/**/*.{ts,tsx,js,jsx}' "aria-label=\"[^\"]+\"|title=\"[^\"]+\"|placeholder=\"[^\"]+\""
  ```
- 本地化可访问性标签

5) **替换字符串为键**
- 使用`t('namespace.key')`表示UI文本
- 对于复数使用`t('key', { count })` + `_one/_other`键
- 使用Intl/app格式化器表示时间/日期/数字

6) **本地化错误处理（关键）**
- 将错误代码映射到本地化键；仅显示本地化UI
- 仅记录原始错误详情
- 为未知代码提供本地化回退

7) **更新locale文件**
- 在两个locales中添加缺失键
- 保持占位符一致；除非要求否则避免重命名
- 使用商定的方法生成翻译；保留占位符和复数规则

8) **验证**
- 重新运行审计直到缺失/奇偶性问题为零
- 验证JSON（例如，`python -m json.tool <file>`）
- 更新断言可见文本的测试

## 守护栏

- 从不向UI暴露原始`error.message`；仅显示本地化字符串
- 不要添加额外locales，除非明确请求
- 优先结构化命名空间（例如，`errors.*`、`buttons.*`、`workspace.*`）
- 保持翻译简洁和一致
- 某些技术/品牌术语应保持未翻译（例如，产品名称、API、MCP、Bash）

## 可交付成果（预期输出）

- i18n配置/provider连接
- 每个目标语言的locale文件
- 用稳定键替换的UI字符串
- 语言切换器和持久化（如适用）
- 更新可见文本的测试

## 架构指导（保持简洁）

- **键结构**：优先按区域嵌套命名空间（例如，`common.buttons.save`、`pricing.tier.pro`）
- **文件布局**：每个locale一个文件或每个locale命名空间；在locales之间保持键同步
- **占位符**：精确保留`{name}`/`{{name}}`；按locale规则验证复数
- **格式化**：对日期、时间、数字和列表格式化使用Intl/app辅助函数
- **SEO/元数据**：如果app暴露它们，本地化标题和描述
- **RTL**：仅需要RTL locales；使用逻辑CSS属性并测试布局
- **非web表面**（Electron主进程对话框、CLI提示、本地菜单）也需要本地化

## 性能说明（简短）

- 当app支持时延迟加载locale bundles
- 按命名空间拆分大locale文件

## 失败模式（监视列表）

- 缺失翻译：回退到默认locale并记录警告
- RTL布局问题：验证逻辑CSS并测试页面
- SEO缺失：确保alternates和元数据在适用时本地化

## 验证检查表（简短）

- 没有缺失键和没有原始UI字符串
- Locale切换工作并持久化
- 在两个locales中验证复数和格式化
- 配置回退locale
