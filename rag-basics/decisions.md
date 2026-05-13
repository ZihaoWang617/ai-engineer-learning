# RAG 项目技术决策日志

## 🔧 Active TODOs

- [ ] **[P1] Tool 覆盖度扩展** — `check_processing_time` 只覆盖 study/work/visitor permit + pr card 四类。未覆盖 BC PNP、OINP、Express Entry、Atlantic、PEQ。KB 有内容但 tool 不知道
- [ ] **[P1] retrieve_kb_context error message 升级** — 当前直接 expose `str(e)`，无 LLM 指令、无 fallback、可能泄露技术细节。与 `check_processing_time` graceful message 不一致。分层 catch (ConnectionError/TimeoutError + Exception 兜底)，隔离 dev print 和 LLM-facing message
- [ ] **[P2] LLM single-attempt fallback graph node** — 实测：tool miss 后 LLM 不会主动用 `retrieve_kb_tool` 重新检索。修复方向：显式 fallback node 或 system prompt 教 LLM retry。等 Day 44-46 LangGraph block 学完
- [ ] **[P2] `calculate` eval() 安全风险** — Prompt injection 攻击面（`__import__('os').system(...)`）。替换为 `ast.literal_eval` 或 `numexpr`/`sympy` parser
- [ ] **[P3] 验证 sync vs async ToolNode 行为** — Day 42 audit Q5 follow-up。实验：`def tool(): time.sleep(3)` vs `async def tool(): await asyncio.sleep(3)`，配 `.invoke()` 和 `.ainvoke()`，测 wall-clock。预期 sync sleep + ainvoke 仍 ~6s（event loop 阻塞），async sleep + ainvoke ~3s

---

## 📐 Architectural Conventions

- **State 字段名永远 `messages` 复数** —— typo `message` 单数会触发 silent bug（add_messages reducer 不绑到错的字段，state 表面正常但行为悄悄错）
- **Tool 内部 fail-soft** —— return LLM-actionable string，不 raise。LangGraph 当前默认 fail-loud，raise 会让整个 graph.invoke() 崩
- **Error message 三要素** —— 明确失败 + 指令 LLM 该做什么 + 提供 fallback（URL 或替代 tool）
- **Path hardening** —— 模块 load 时 resolve absolute path，不依赖 cwd（避免 sub-directory 启动 fail）
- **Prebuilt 使用姿势** —— 完全清楚它替你做什么的部分才用 prebuilt（如 ToolNode dispatch 已在 Day 42 手写过）；不清楚就先手写
- **Provider-agnostic 设计** —— 代码不预设 provider，LLM 实例化和 `.bind_tools()` 行为在 OpenAI/Anthropic 下保持一致

---

## 📜 Decision Log

### Day 43 — 2026-05-13

**Provider switch (Anthropic → OpenAI for `agent_graph_minimal.py`)**  
Anthropic 用尽 → gpt-4o-mini。教学内容（native LangGraph）无需续费，代码本来 provider-agnostic。

**双节点注册同函数 vs Conditional edge**  
今天 scope 是 static edge only。`add_node("llm_call", llm_node)` + `add_node("llm_final", llm_node)` dual-registration 暴露"node 名是 unique identifier、函数可复用"机制。代价：agent 只能处理 exactly-one-tool-call。Day 44 conditional edge 取代。

**Prebuilt ToolNode vs 手写 dispatch**  
用 prebuilt。Day 42 手写过整套（找 tool_call → lookup → 执行 → 包 ToolMessage），今天 cognitive load 留给 graph 编排本身。

**Toy tool vs 真 RAG retriever**  
hardcode `get_processing_time`（4 个 visa 类型 dict），不接 ChromaDB。隔离变量：今天观察 graph 机制，RAG 集成是 orthogonal complexity，混在一起调试时分不清是哪层 bug。Day 44-46 graph 稳定后接真 retriever。

---

### Day 42 — 2026-05-12

**Tool error handling 策略**  
所有 tool 内部不向 Agent raise，return LLM-actionable string。HOW 取决于 tool 类型：危险操作（`eval`）和外部调用必需 try/except；纯内存 dict lookup 用 default return 即可。

实验验证：故障注入对比 raise vs graceful return —— raise 让 graph.invoke() 直接崩（fail-loud），无 LLM fallback；graceful return 让 LLM 老实 acknowledge 失败 + 给 IRCC URL + 保留 partial answer (BC PNP 介绍)。

附加观察：modern LangGraph 默认支持 parallel tool calling，LLM 一次 AIMessage 可发多个 tool_call，节省 round trip。

**Path hardening (chroma_db_lc)**  
模块 load 时 `Path(__file__).parent / "chroma_db_lc"` resolve 绝对路径，替代依赖 cwd 的 `"./chroma_db_lc"`。Root-cause fix。从此 rag-basics 子目录之外启动也能找到 vector store。