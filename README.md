# Yuanxin Insight Codex 插件（内部试用）

## 原心项目管理插件 测试版

测试标签：`v1.2.0-lite-preview.2`。在现有日历市场中新增项目洞察，日历插件仍为1.1.0。项目洞察连接 `https://projects.yuanxininsight.com/mcp`，同事无需在本机运行服务。

首次安装，在已安装Codex CLI的终端依次执行：

```bash
codex plugin marketplace add chenhebuaa/zhijian-calendar-plugin --ref v1.2.0-lite-preview.2
codex plugin add feishu-project-insights-lite@yuanxin-insight
codex mcp login feishu-project-insights-lite
```

已有旧版yuanxin-insight市场时，先执行 `codex plugin marketplace remove yuanxin-insight`，再执行上面的安装命令；日历包没有改动。如果此前安装了本机Lite预览，先执行 `codex plugin remove feishu-project-insights-lite@feishu-project-insights-lite-local`，避免两个Lite连接同时启用。按浏览器提示使用本人飞书账号登录，然后新建Codex对话。

试用成员须在此飞书应用的可用范围内，并由管理员以该应用的open_id加入服务准入。未准入时请联系管理员，不要借用他人账号。准入只允许使用插件，文档和群聊仍按本人飞书权限读取；普通成员不能保存项目配置。

依次验证：

1. “用原心项目管理插件列出可查询的项目。”
2. “分析幻师COMMUNE的最新进展、客户尚未解决的问题和风险。”核对可读文档来源及读取缺口。
3. 使用本人确实无权的已配置资料验证权限提示，不应出现正文。若暂无这样的资料，记录为未验收。

群聊参与分析，但回答不罗列消息ID或单列群聊证据。当前不是增量分析，PDF、图片、附件等读取有限，序列结束不代表资料全部覆盖。当前仅完成部署和连接准备，同事本人权限及连续试用仍须实际验收。

后续更新固定到发布者提供的新标签，重新添加市场并安装Lite；不要移动既有标签。回退也使用已验收的固定标签。安装包只包含Skill和公开连接信息，项目绑定、账号令牌和服务配置均不在此仓库。

## 指尖日程

这是供组织同事个人 Codex/ChatGPT 账号安装的公开安装包。插件只包含查询 Skill 和生产 MCP 的公开 HTTPS 地址；飞书 tenant、白名单、共享源凭证、缓存和服务代码均不进入分发仓库。任何人都可以下载安装包，但只有通过飞书组织身份和服务端白名单校验的成员才能访问日程。

## 发布者构建

1. 将 `distribution/` 的内容复制为一个独立公开 Git 仓库的根目录，排除 `.pytest_cache`、`__pycache__`、`.env` 和服务代码。
2. 确认 `.mcp.json` 只包含生产 `https://calendar.yuanxininsight.com/mcp` 地址，不包含账号级 App ID 或凭证。
3. 验证发布树：

```bash
python /path/to/validate_plugin.py plugins/zhijian-calendar
python -m pytest -q
```

以不可移动的 release tag（如 `v1.1.0`）发布。

## 同事安装

```bash
codex plugin marketplace add chenhebuaa/zhijian-calendar-plugin --ref v1.1.0 && codex plugin add zhijian-calendar@yuanxin-insight && codex mcp login zhijian_calendar
```

在 Codex/ChatGPT 桌面端打开 `/plugins`，连接“指尖日程”，按提示用飞书登录，然后新建会话。服务端每次调用都会重新检查飞书租户和白名单；移出白名单后现有会话也会立即失效。

旧 marketplace 固定在旧标签时，先删除本地插件和 marketplace，再添加新标签、安装插件并新建会话。回滚时将 marketplace ref 固定到上一个已验收的签名 tag；不要移动已有 tag。

## 本地门禁

```bash
service/.venv/bin/python -m pytest distribution/tests -q
service/.venv/bin/python /path/to/quick_validate.py distribution/plugins/zhijian-calendar/skills/schedule-query
service/.venv/bin/python /path/to/validate_plugin.py distribution/plugins/zhijian-calendar
```

插件通过 `.mcp.json` 直接连接生产 MCP，不引用任何个人账号创建的 `.app.json`。
