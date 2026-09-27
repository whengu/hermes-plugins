# hermes-plugins

Hermes 自建插件统一项目（单一 git 仓库）。

## 插件清单

| 插件 | 目录 | 说明 |
|---|---|---|
| write-guard | plugins/write-guard/ | 工具调用前置守卫（终端命令/配置/记忆审批） |
| toast-notify | plugins/toast-notify/ | 桌面通知 |
| firecrawl-selfhosted | plugins/firecrawl-selfhosted/ | 本地 Firecrawl 搜索/提取 |
| searchapi | plugins/searchapi/ | SearchAPI 搜索 |

## 目录结构

```
hermes-plugins/
├── .git/              # 主仓库（原 write-guard 历史）
├── README.md
└── plugins/
    ├── write-guard/
    ├── toast-notify/
    ├── firecrawl-selfhosted/
    └── searchapi/
```

## 部署

直接复制 plugins/<插件名>/ 到 D:\myagent\.hermes\plugins\<插件名>\（每个插件含 __init__.py、handler.py、plugin.yaml）。

## 已移除

- review_guard、review_guard_v2（2026-09-27 移除，备份在 D:\myagent\workspace\plugins-removed-20260927\）
- 各插件的 deploy.py（不再需要）