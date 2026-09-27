# write-guard 修改需求：终端命令审批（2026-09-27 用户最终口径）

## Python 环境前提
- **使用 Hermes 的 Python 环境**：`D:\Project\guwh\hermes-agent\venv\Scripts\python.exe`（Python 3.11.16）。
- 项目无独立虚拟环境；handler.py 仅依赖标准库，不安装任何第三方依赖。
- Python 代码检查一律使用 pyright（py_compile 被用户禁用）。

## 需求（一条：终端命令审批）
terminal 工具（command 参数）与 execute_code 工具（code 参数）的命令文本中，命中以下任一规则时按指定处置执行：

| 触发条件 | 处置 |
|---|---|
| 命令文本中**同时出现**这两类字样（无任何结构要求，本需求最核心的一条）：① `gateway` 字样；② `start` / `restart` / `run` / `install` / `stop` 中任意一个字样。**任意组合、任意顺序、任意间隔**——谁先谁后都算、相隔多远都算、不要求组成词组、中间夹任何内容都算（`restart gateway`、`gateway stop`、`run xxx gateway yyy start` 这类形态全部触发） | **approve（弹审批）**，未经用户批准不得执行 |
| 文本中出现 py_compile（如 python -m py_compile 等形态） | **block（直接阻止，不弹审批）**，此工具被用户禁用 |
| 文本中出现 codex（如 codex exec 等执行 codex CLI 的形态） | **approve（弹审批）**，未经用户批准不得执行 |

## 约束
- 现有守卫行为保持不变：hermes gateway restart/run/start 直接拦截（block）、临时目录拦截、配置写保护、记忆写保护。
- 实现方式由你自行决定；遇到项目内已有惯例遵循惯例（项目 requirements/、reviews/ 目录有历史文档）。

## 红线
- 只允许修改本项目（D:\myagent\workspace\write-guard）的 handler.py 与 plugin.yaml。
- 禁止修改生产目录 D:\myagent\.hermes\plugins\write-guard\ 下任何文件。
- 禁止 git commit / push；禁止运行 deploy.py。
- 禁止修改 __init__.py、deploy.py（测试用例可新增到 test_handler.py）。

## 验证
- 跑 test_handler.py 测试套件，新增守卫有对应测试用例覆盖，全部通过。
- pyright 检查通过。

## 交付
- 中文汇报：改动内容与验证结果。