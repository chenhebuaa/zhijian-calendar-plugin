# 指尖日程插件试点检查表

只记录 UTC 时间、服务构建 SHA、测试名称、通过/失败和 correlation ID。禁止记录 token、飞书 open_id、日程标题、备注或原始响应。

## 前置条件

- [ ] 预发布 HTTPS 服务已部署并完成数据库迁移。
- [ ] ChatGPT 开发者模式已注册预发布 MCP，OAuth discovery 成功。
- [ ] 测试租户中仅启用一个管理员、一个允许用户和一个拒绝用户。
- [ ] 预发布日历只含脱敏 fixture。
- [ ] E2E 环境变量仅注入当前 shell/CI secret，不写入文件。

## 自动检查

```bash
service/.venv/bin/python -m pytest distribution/tests/e2e/test_calendar_plugin.py -v
```

- [ ] 未登录访问返回 401/403，响应不含活动字段。
- [ ] 拒绝用户无法初始化或调用工具，错误不含活动字段。
- [ ] 允许用户可以执行三项只读工具。
- [ ] 31 天闭区间成功，32 天闭区间失败。
- [ ] 返回值明确包含 `data_as_of` 和 `stale`。
- [ ] 禁用允许用户后，下一次调用立即失败；测试最终恢复 fixture 用户。

## Codex 个人账号验收

- [ ] 从公开安装包 marketplace 的固定 release tag 安装插件。
- [ ] 插件安装树包含 `.mcp.json`，且不包含账号级 `.app.json`。
- [ ] 在 `/plugins` 中连接飞书，使用允许用户完成登录。
- [ ] 新建会话后查询今天、本周、关键词和同步状态。
- [ ] 相对日期按 Asia/Shanghai 解释，全日事件不虚构时间。
- [ ] 断开/撤销后显示通用重新连接提示，不泄露租户或白名单规则。

## 结果记录

| UTC 时间 | 构建 SHA | 测试/门禁 | 结果 | Correlation ID |
|---|---|---|---|---|
| 待执行 | 待部署 | 待执行 | 待执行 | 待执行 |

任一项目失败：停止发布、保留旧系统，不创建或移动发布 tag。
