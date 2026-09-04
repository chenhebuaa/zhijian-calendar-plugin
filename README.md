# 指尖日程 Codex Plugin（内部）

这是供组织同事个人 Codex/ChatGPT 账号安装的公开安装包。插件只包含查询 Skill 和已注册远程 MCP 的公开应用 ID；飞书 tenant、白名单、共享源凭证、缓存和服务代码均不进入分发仓库。任何人都可以下载安装包，但只有通过飞书组织身份和服务端白名单校验的成员才能访问日程。

## 发布者构建

1. 将 `distribution/` 的内容复制为一个独立公开 Git 仓库的根目录，排除 `.pytest_cache`、`__pycache__`、`.env` 和服务代码。
2. 在 ChatGPT 开发者模式中为生产 `https://<company-domain>/mcp` 注册远程 MCP 并启用 OAuth。
3. 在发布仓库的临时副本中绑定真实技术 ID：

```bash
export CALENDAR_PRODUCTION_MCP_APP_ID='asdk_app_<registered-id>'
python scripts/bind_registered_app.py plugins/zhijian-calendar/.app.json
python /path/to/validate_plugin.py plugins/zhijian-calendar
python -m pytest -q
```

绑定脚本会同时创建 `.app.json` 并在插件 manifest 中启用它；缺少或伪造 ID 时直接失败。只提交绑定后的发布副本，不把环境变量写入文件。以不可移动的 release tag（如 `v1.0.0`）发布。

## 同事安装

```bash
codex plugin marketplace add chenhebuaa/zhijian-calendar-plugin --ref v1.0.0 && codex plugin add zhijian-calendar@yuanxin-insight
```

在 Codex/ChatGPT 桌面端打开 `/plugins`，连接“指尖日程”，按提示用飞书登录，然后新建会话。服务端每次调用都会重新检查飞书租户和白名单；移出白名单后现有会话也会立即失效。

升级 marketplace 后重新安装/升级插件并新建会话。回滚时将 marketplace ref 固定到上一个已验收的签名 tag；不要移动已有 tag。

## 本地门禁

```bash
service/.venv/bin/python -m pytest distribution/tests -q
service/.venv/bin/python /path/to/quick_validate.py distribution/plugins/zhijian-calendar/skills/schedule-query
service/.venv/bin/python /path/to/validate_plugin.py distribution/plugins/zhijian-calendar
```

源码态 manifest 故意不包含 `apps`，因此可在没有假 ID 的情况下校验；只有发布副本完成真实应用绑定后才可安装。
