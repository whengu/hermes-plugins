# write-guard 第二轮复审上下文（2026-09-21）

## 对象
- 开发版：D:/myagent/workspace/write-guard/handler.py（约 880 行）
- 部署版：D:/myagent/.hermes/plugins/write-guard/handler.py（需 diff 验证一致）
- 测试：D:/myagent/workspace/write-guard/test_handler.py（python test_handler.py，
  当前 ALL PASS 29 scan + 4 hook + 153 new）
- 修订史：D:/myagent/workspace/write-guard/reviews/CHANGELOG-20260921.md
- 需求现行权威：requirements/requirement-20260921.md
- 第一轮审查报告：reviews/audit-20260921/（sa-0 安全审计脚本与输出）

## 第一轮审查后本轮已实施的全部变更（复审对象）
安全修复（sa-0 发现的 8 条绕过）：
- F-A1: open/Path/os.open/shutil/tool_call 6 条正则容忍 [rbfuRBFU]{0,2} 前缀
- F-A2: execute_code 内嵌 os.system/popen/subprocess 提取命令文本递归复用
  terminal 判定链；_NEST_DEPTH_LIMIT=3
- F-A3: plugins/ 下 .py/.yaml/.yml 纳入受保护（反缴械）
- F-A4: sed -i.bak / --in-place 形态
- F-A5: truncate；F-A6: Set-Content/Add-Content/Out-File
- F-A7: cp 目标为 home 目录本身 → 收集扩展 + approve（TC-A-46 边界翻转）
- C-cwd: terminal cwd 参数纳入 C 扫描
质量修复（sa-1 发现的 S/T/R 系列）：
- S-0 plugin.yaml 重写 version 1.2.0；S-1 注释考古外迁 CHANGELOG（AST 等价
  校验通过）；S-2 抽 _shown_path；T-3 _stub_guard 按 __name__ 定位；T-4 快照
  拆分；T-5 HOOK_N；R-7 deploy.py 双哈希；R-8 正则预编译 + _ENV_EXPAND_ROUNDS
过程事故（需重点复查该修复是否正确）：
- F-A7 首版误传作用域外变量 pipe_cwd → NameError 被异常隔离吞成 fail-open，
  11 用例捕获后已修为 cwd。请验证不再有同类"异常被隔离吞掉致保护静默失效"
  的残留（全文件扫 NameError/AttributeError 风险点）。

## 用户决策基准（需求红线，不得违反）
1. write_file/patch 写 HERMES_HOME 下配置 → block 截断（提示走 skill 流程）
2. terminal/execute_code 写配置：cp/copy 类 → approve 弹审批；其他写形态 → block
3. 改名/移动（mv/ren/shutil.move/os.rename/os.replace）→ 不拦截
4. 守卫 D：hermes gateway restart|run|start → block，消息逐字=
   "你违反了用户的规则, 必须使用skill指定的方式来访问hermes gateway"
   status/stop 放行
5. 记忆写 → approve；C：/tmp 拦截，5 读工具豁免（read_file/search_files/
   web_search/hindsight_recall/hindsight_reflect）
6. 不修改 Hermes 框架源码；approvals.mode 保持 manual；rm -r 类保持审批

## 审查纪律
- 只读被审文件，禁止修改；临时脚本写到指定目录
- 每条 finding：级别(CRITICAL/HIGH/MEDIUM/LOW) + 行号/代码证据 + 可操作修法
- 关键判定必须实测（import handler 调 on_pre_tool_call），不采信注释自述
- 输出中文，最后给 PASS 或 CHANGES REQUIRED
