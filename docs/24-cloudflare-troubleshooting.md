# Cloudflare Troubleshooting - Cloudflare故障排除

## 简介

Cloudflare Troubleshooting skill用于使用API驱动的证据收集来调查和解决Cloudflare配置问题。专注于使用Cloudflare API检查实际配置而不是做假设的系统化调查方法。

## 核心原则

**基于证据的调查，而不是假设。** 总是查询Cloudflare API来检查实际配置，然后再诊断问题。skill的价值是系统化调查方法，而不是预定的解决方案。

## 调查方法

### 1. 收集凭据

从用户请求：
- 域名
- Cloudflare账户邮箱
- Cloudflare全局API密钥（或API令牌）

全局API密钥位置：Cloudflare仪表板 → 我的个人资料 → API令牌 → 查看全局API密钥

### 2. 获取区域信息

任何Cloudflare故障排除的第一步 - 获取区域ID：

```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=<domain>" \
  -H "X-Auth-Email: <email>" \
  -H "X-Auth-Key: <api_key>" | jq '.'
```

从`result[0].id`提取`zone_id`用于后续API调用。

### 3. 系统化调查

对于每个问题，在做出结论之前收集证据。使用Cloudflare API来检查：
- 当前配置状态
- 最近的更改（如果审计日志可用）
- 可能相互的相关设置

## 常见调查模式

### 重定向循环（ERR_TOO_MANY_REDIRECTS）

**证据收集序列：**

1. **检查SSL/TLS模式：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

   查找：`result.value` - 告诉当前SSL模式

2. **检查始终使用HTTPS设置：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

3. **检查页面规则的转发：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/pagerules" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

   查找：`forwarding_url`或`always_use_https`动作

4. **直接测试源服务器（如可能）：**
   ```bash
   curl -I -H "Host: <domain>" https://<origin_ip>
   ```

**诊断逻辑：**
- SSL模式"flexible" + 源强制HTTPS = 重定向循环
- 多个重定向规则可能冲突
- 检查浏览器vs curl行为差异

**修复：**
```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl" \
  -H "X-Auth-Email: email" \
  -H "X-Auth-Key: key" \
  -H "Content-Type: application/json" \
  --data '{"value":"full"}'
```

修复后清除缓存：
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "X-Auth-Email: email" \
  -H "X-Auth-Key: key" \
  -d '{"purge_everything":true}'
```

### DNS问题

**证据收集：**

1. **列出DNS记录：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

2. **检查外部DNS解析：**
   ```bash
   dig <domain>
   dig @8.8.8.8 <domain>
   ```

3. **检查DNSSEC状态：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/dnssec" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

**查找：**
- 缺失的A/AAAA/CNAME记录
- 不正确的代理状态（代理 vs DNS-only）
- TTL值
- 冲突的记录

### SSL证书错误

**证据收集：**

1. **检查SSL证书状态：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/ssl/certificate_packs" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

2. **检查源证书（如果使用Full Strict）：**
   ```bash
   openssl s_client -connect <origin_ip>:443 -servername <domain>
   ```

3. **检查SSL设置：**
   - 最低TLS版本
   - TLS 1.3状态
   - 机会性加密

**常见问题：**
- 错误526：SSL模式是"strict"但源证书无效
- 错误525：源处的SSL握手失败
- 配置延迟：等待15-30分钟以进行Universal SSL

### 源服务器错误（502/503/504）

**证据收集：**

1. **检查源是否可达：**
   ```bash
   curl -I -H "Host: <domain>" https://<origin_ip>
   ```

2. **检查DNS记录指向正确的源：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

3. **审查负载均衡器配置（如适用）：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/load_balancers" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

4. **检查防火墙规则：**
   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/rules" \
     -H "X-Auth-Email: email" \
     -H "X-Auth-Key: key"
   ```

## 学习新API

遇到未涵盖的问题时，请查阅Cloudflare API文档：

1. **浏览API参考：** https://developers.cloudflare.com/api/
2. **使用问题关键词搜索相关端点**
3. **检查API schema**以了解可用操作
4. **首先使用GET请求**来理解数据结构
5. **在确认方法后使用PATCH/POST**进行更改

**探索新API的模式：**
```bash
# 列出区域的所有可用设置
curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings" \
  -H "X-Auth-Email: email" \
  -H "X-Auth-Key: key"
```

## API参考概述

请参阅：
- `references/api_overview.md` - 按类别组织的常见端点
- `references/ssl_modes.md` - 详细的SSL/TLS模式解释
- `references/common_issues.md` - 问题模式和症状、调查检查表、平台特定说明

## 最佳实践

### 基于证据的调查

1. **查询前假设** - 使用API来检查实际状态
2. **收集多个数据点** - 交叉引用设置
3. **检查相关配置** - 设置经常交互
4. **外部验证** - 使用dig/curl来确认
5. **增量测试** - 一次一个更改

### API使用

1. **解析JSON响应** - 使用`jq`或python以提高可读性
2. **检查成功字段** - 响应中的`"success": true/false`
3. **优雅地处理错误** - 响应中的`errors`数组
4. **尊重速率限制** - Cloudflare API有限制
5. **使用适当的方法：**
   - GET：检索信息
   - PATCH：更新设置
   - POST：创建资源 / 触发动作
   - DELETE：移除资源

### 进行更改

1. **先收集证据** - 理解当前状态
2. **识别根本原因** - 不要猜测
3. **应用目标修复** - 仅更改需要的内容
4. **如需要，清除缓存** - 特别是对于SSL/重定向更改
5. **验证修复** - 通过API重新查询以确认
6. **告知用户等待时间：**
   - 边缘服务器传播：30-60秒
   - DNS传播：最多48小时
   - 浏览器缓存：需要手动清除

### 安全

- 从不在输出中记录API密钥
- 如果用户在公共上下文中共享凭据，则警告
- 推荐使用带范围权限的API令牌而不是全局API密钥
- 使用只读操作进行调查

## 工作流模板

```
1. 收集：域名、邮箱、API密钥
2. 通过zones API获取zone_id
3. 调查：
   - 查询相关API以获取证据
   - 检查多个相关设置
   - 用外部工具（dig、curl）验证
4. 分析证据以确定根本原因
5. 通过适当的API端点应用修复
6. 如果配置更改影响交付，则清除缓存
7. 通过API查询和外部测试验证修复
8. 向用户报告解决方案和任何所需操作
```

## 示例：完整调查

当用户报告"站点显示ERR_TOO_MANY_REDIRECTS"时：

```bash
# 1. 获取zone ID
curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=example.com" \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: abc123" | jq '.result[0].id'

# 2. 检查SSL模式（重定向循环的主要嫌疑）
curl -s -X GET "https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings/ssl" \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: abc123" | jq '.result.value'

# 如果返回"flexible"并且源是GitHub Pages/Netlify/Vercel：

# 3. 通过更改为"full"来修复
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/ZONE_ID/settings/ssl" \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: abc123" \
  -H "Content-Type: application/json" \
  --data '{"value":"full"}'

# 4. 清除缓存
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: abc123" \
  -d '{"purge_everything":true}'

# 5. 告知用户：等待60秒，清除浏览器缓存，重试
```

## 脚本何时有用

捆绑的脚本（`scripts/check_cloudflare_config.py`、`scripts/fix_ssl_mode.py`）作为：
- **参考实现** - 调查模式
- **快速诊断工具** - Python可用时
- **示例** - 程序化API使用

然而，**首选通过Bash/curl的直接API调用**以获得灵活性和透明度。当方便时使用脚本，但对于以下情况需要原始API调用：
- 不熟悉的场景
- 边缘情况
- 学习/调试
- 脚本未覆盖的操作

调查方法和API知识是核心技能，而不是脚本。
