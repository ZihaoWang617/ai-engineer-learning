# RAG 项目技术决策日志

## 2026-05-12 (Day 42) — Tool Error Handling 策略

**决策**：所有 tool 内部保证不向 Agent raise 异常，return LLM-actionable error message。HOW 实现取决于 tool 操作类型——危险操作（eval）和外部调用必需 try/except；纯内存 dict lookup 用 default return 即可。

**考虑的备选**：
1. 让 tool raise 依赖框架 → 实测验证：LangGraph 现版本默认 fail-loud，异常直接 propagate 到 invoke() 调用者，整个调用崩溃
2. Tool 内部 catch 后 return generic "Error" 字符串 → LLM 可能 silent skip 或编造
3. (选用) Tool 内部 catch 后 return 包含"失败原因 + LLM 应对指令 + fallback"的字符串

**为什么选 3**：实测对比下，3 让 LLM 老实告知用户失败并给出 IRCC 官网替代方案；1 直接崩；2 易导致 silent skip。

**LLM-actionable error message 三要素**：
- 明确说明什么失败
- 指令 LLM 该做什么（"请用户稍后重试"）
- 提供 fallback 选项（URL 或替代查询）

---

## 2026-05-12 (Day 42) — 实验记录：故障注入

**实验设置**：将 check_processing_time 改造为强制 raise ConnectionError，对比 raise vs return graceful string 两种行为。

**关键发现 1**：LangGraph 现版本默认 fail-loud。Tool raise 后异常 propagate 到 agent.invoke()，整个调用崩溃，没有 LLM 优雅 fallback。与某些教程描述的"自动 catch 并 pass 给 LLM"不符。

**关键发现 2**：Tool 内部 try/except + LLM-actionable return 后，LLM 在最终回复中明确 acknowledge 失败、给出 IRCC fallback URL、保留 partial answer（BC PNP 介绍）。

**关键发现 3**：Parallel tool calling 在 modern LangGraph 中默认支持——LLM 在一次 AIMessage 里可发起多个 tool_call，节省 round trip。

**实验代码已恢复**。

---

## TODO — Tool 覆盖度 gap

check_processing_time 只覆盖 study/work/visitor permit + pr card 四类。未覆盖：BC PNP、OINP、Express Entry、Atlantic Immigration、PEQ 等省提名/联邦项目。KB 里有这些内容但 tool 不知道。

修复方向（不今天做）：
1. 扩展 processing_times dict 覆盖所有项目
2. 让 check_processing_time 在 miss 时返回 "请通过 retrieve_kb_tool 查询" 提示 LLM
3. 长期：接真实 IRCC API

---

## TODO — LLM single-attempt per tool 偏好

实测发现：check_processing_time 返回 "BC PNP not found" 后，LLM 没尝试用 retrieve_kb_tool("BC PNP 处理时间") 重新检索 KB。LLM 默认假设"已查过即查尽"。

修复方向（待 Day 43-46 LangGraph 块时实现）：
- 显式 fallback graph node：tool miss → 触发 retrieve_kb 兜底
- 或在 system prompt 里教 LLM 主动 retry with different query

---

## TODO — retrieve_kb_context error message 升级

当前 error message 直接 expose `str(e)` 给 LLM，无 LLM-instruction、无 fallback、可能泄露技术细节。对比 check_processing_time 的 graceful message 不一致。

未来重构方向：
- 分层 catch：(ConnectionError, TimeoutError) + Exception 兜底
- 隔离技术 detail（print 给 dev）和用户消息（return 给 LLM）
- 明确指令 LLM（"请告诉用户..."）

---

## TODO — calculate eval() 安全风险

calculate tool 使用 `eval()`，存在 prompt injection 攻击面（恶意输入诱导 `__import__('os').system(...)`）。

修复方向：用 `ast.literal_eval` 或 `numexpr`/`sympy` 数学表达式 parser 替代。