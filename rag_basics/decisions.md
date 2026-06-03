# RAG 项目技术决策日志

## 🔧 Active TODOs

### P0 — 紧急（线上服务挂着）
- [ ] **Day 55**: Render Service #1 (FastAPI) 配置更新 — Root Directory `rag-basics` → `rag_basics`，验证 Start Command 路径
- [ ] **Day 55**: Render Service #2 (Streamlit) 配置同步更新

### P1 — 高优
- [ ] **Day 55**: `retrieve_with_reranking()` 重构 — 合并 langchain_query.py 中 3 处重复的 `rerank_docs()` 调用
- [ ] **Day 55**: Pinecone 启动 — 注册 + 创建 index + 第一次 upsert
- [ ] **Tool 覆盖度扩展** — `check_processing_time` 只覆盖 study/work/visitor permit + pr card 四类。未覆盖 BC PNP、OINP、Express Entry、Atlantic、PEQ。KB 有内容但 tool 不知道
- [ ] **retrieve_kb_context error message 升级** — 当前直接 expose `str(e)`，无 LLM 指令、无 fallback、可能泄露技术细节。与 `check_processing_time` graceful message 不一致。分层 catch (ConnectionError/TimeoutError + Exception 兜底)，隔离 dev print 和 LLM-facing message

### P2 — 中等
- [ ] **SqliteSaver migration for HITL** — `agent_graph_hitl.py` 当前用 InMemorySaver，演示不了跨进程 resume。`pip install langgraph-checkpoint-sqlite` + 替换 InMemorySaver → `SqliteSaver(conn)` + 写验证脚本（第一次 invoke 触发 interrupt → 退出 Python 进程 → 重新启动 + Command(resume=...) 用同 thread_id → 成功恢复 final answer）
- [ ] **HITL Pattern A → Pattern B refactor** — 把 `submit_application` 内部的 `interrupt()` 抽出来，graph 加独立 `approval_node` + conditional edge 路由 high-stakes tool calls。换来：approval 逻辑集中可配、per-tool approval policy、tool 实现纯净（pure function 不含 control flow）、audit log 易加
- [ ] **LLM single-attempt fallback graph node** — 实测：tool miss 后 LLM 不会主动用 `retrieve_kb_tool` 重新检索。修复方向：显式 fallback node 或 system prompt 教 LLM retry
- [ ] **`calculate` eval() 安全风险** — Prompt injection 攻击面（`__import__('os').system(...)`）。替换为 `ast.literal_eval` 或 `numexpr`/`sympy` parser

### P3 — 低优 / 待决策
- [ ] **HITL multi-tool integration** — 当前 `agent_graph_hitl.py` 只 bind submit_application。把它跟 `agent_graph_conditional.py` 的 retrieve_kb_tool / check_processing_time / calculate 合并到一个 graph，验证 multi-iteration + HITL gate 行为（agent 先 retrieve KB context、再 submit_application，只在 submit 阶段 interrupt）
- [ ] **HITL FastAPI + Streamlit integration** — 当前 driver 是 console `input()`。production 化：`/ask` endpoint 检测 result 里 `__interrupt__` 字段、返回 `{"status": "pending_approval", "interrupt_data": {...}, "session_id": "..."}`；Streamlit 渲染 approval card；用户点 approve/reject → `/resume` endpoint 用 `Command(resume=...)` + 同 thread_id 继续 graph 直到 final answer
- [ ] **File structure consolidation 决策** — 当前双文件并存：`agent_graph_minimal.py`（Day 43 static-edge archive）+ `agent_graph_conditional.py`（Day 44 current canonical）。选项 P 保留（演化痕迹做简历资产）vs 选项 Q 合并为单一 `agent_graph.py`（简洁但丢失演化可见性）。倾向 P，待最终确认后 git rename
- [ ] **验证 sync vs async ToolNode 行为** — Day 42 audit Q5 follow-up。实验：`def tool(): time.sleep(3)` vs `async def tool(): await asyncio.sleep(3)`，配 `.invoke()` 和 `.ainvoke()`，测 wall-clock。预期 sync sleep + ainvoke 仍 ~6s（event loop 阻塞），async sleep + ainvoke ~3s
- [ ] **迁 Pinecone 后**: 把 `chroma_db_lc/` 从 git 历史中清理（git filter-repo 或 BFG），并彻底加进 `.gitignore`

---

## 📐 Architectural Conventions

- **Truthy verification rule**: Python truthy/falsy 行为有疑问立刻 REPL 跑 `bool(...)` 验证；字符串 / config 值的判断**永远 explicit 比较**（`approval == "approve"`），永远不靠 truthy 检查。尤其 `bool("False") == True` 是反直觉陷阱——任何非空字符串都是 truthy。
- **Import discipline**: 拒绝 IDE auto-import；每个 import 必须 conscious、能 60 秒内说清来源 module 是什么、被 import 的 name 是干什么的；commit 前扫一眼 import block，删 dead imports。Day 45 踩坑：Pylance auto-import 把 `from pydantic import tools` 加进来，导致 `Annotated[tools, add_messages]` 语义完全错乱。
- **Save-before-run discipline**: terminal 跑 Python 脚本前确认 VS Code tab 没有 ● 未保存标记。"代码看起来对但 output 不对" 99% 是这个。Cmd+S 后再跑。
- **模块顶层零副作用** —— 顶层只允许 imports、class/function 定义、纯常量赋值。任何执行代码（API call、I/O、print、`graph.invoke()`）包进 `if __name__ == "__main__"` 或函数内部。例外：`load_dotenv()` 顶层 ok（配置加载且必须早于 ChatOpenAI 实例化）
- **Graph 构建工厂化** —— 复杂 graph 构建逻辑（含 LLM client、ToolNode、StateGraph 组装）封装成 `build_graph()` 工厂函数，return compiled graph。换来 import 安全 + 可独立调用 + 状态隔离
- **Decision function = 纯观察者** —— Conditional edge 的 routing 函数读 state、返回 string、不改 state。State 变更只在 node 内发生。换来 reasoning + debug 性：每个 state 变化可追溯到具体 node，edge 不背锅
- **Routing 用 isinstance，display/log 用 hasattr** —— Routing/控制流场景类型即语义（AIMessage = LLM 输出 = 唯一有资格代表"LLM 决定"的消息），isinstance 表达意图；display/log/debug 场景容错优先，hasattr/getattr 合适
- **State 字段名永远 `messages` 复数** —— typo `message` 单数会触发 silent bug（add_messages reducer 不绑到错的字段，state 表面正常但行为悄悄错）
- **Tool 内部 fail-soft** —— return LLM-actionable string，不 raise。LangGraph 当前默认 fail-loud，raise 会让整个 graph.invoke() 崩
- **Error message 三要素** —— 明确失败 + 指令 LLM 该做什么 + 提供 fallback（URL 或替代 tool）
- **Path hardening** —— 模块 load 时 resolve absolute path，不依赖 cwd（避免 sub-directory 启动 fail）
- **Prebuilt 使用姿势** —— 完全清楚它替你做什么的部分才用 prebuilt（如 ToolNode dispatch 已在 Day 42 手写过）；不清楚就先手写
- **Provider-agnostic 设计** —— 代码不预设 provider，LLM 实例化和 `.bind_tools()` 行为在 OpenAI/Anthropic 下保持一致
- **Package 化优于 sys.path hack**（Day 54 新增）—— 跨目录 import 用 `pyproject.toml` + editable install 显式声明 package，不用 `sys.path.insert`。后者只是"凑巧能用"，不是"正确配置"。`pyproject.toml` 必须在项目根目录才能统管所有 sub-package；Python package 名不能含连字符（会被解释为减号）。

---

## 📜 Decision Log

### 2026-06-03 (Day 54) — 项目工程化重构：散文件 → Proper Python Package

**背景**  
项目跑了几十天，`rag_basics` 和 `mcp_learning` 之间的跨目录 import 一直靠 `sys.path.insert` 维持。memory 里把这个记录为"editable install 技术债"——隐含的假设是"editable install 装过但装坏了"。今天诊断后发现这个假设本身就是错的：项目根目录从来没有 `pyproject.toml` 或 `setup.py`，editable install 从来没有发生过。`sys.path.insert` 不是 workaround，是当时能让 import 跑起来的唯一机制。

这个误诊之所以能存在这么久，是因为 `sys.path.insert` 确实能用——但"能用"和"正确配置"之间有一道沟。这道沟在小项目里不可见，等 Pinecone 模块进来、MCP 继续扩展，每新加一个文件就要多两行黑魔法，代价才会显现。

**决策**  
在项目根目录建 `pyproject.toml`，将整个 repo 注册为一个名为 `ai-engineer-learning` 的 editable package，用 `[tool.setuptools.packages.find]` 显式声明 `rag_basics` 和 `mcp_learning` 两个子 package，然后在根目录跑 `pip install -e .`。

同时把 `rag-basics/` 和 `mcp-learning/` 改名为 `rag_basics/` 和 `mcp_learning/`，两个目录各加 `__init__.py`，并清掉唯一剩余的 `sys.path.insert`（在 `mcp_learning/server_v3.py`），将 `from langchain_query import ...` 改为绝对 import `from rag_basics.langchain_query import ...`。

**备选方案**  
方案 A：在 site-packages 手放一个 `.pth` 文件，指向项目根目录。五分钟能搞定，但本质上还是 workaround——换了一种方式绕过问题而不是解决它，下次遇到类似场景还是不知道正确做法是什么。

方案 C：维持现状，继续用 `sys.path.insert`。等价于主动积累技术债，唯一的收益是今天省了一小时。

**为什么选 B**  
`pyproject.toml` 是 Python 生态的标准答案，面试能讲清楚"我们项目是怎么管理 package 的"，也是 Pinecone 和更多 MCP server 进来之后能继续扩展的前提。更重要的是，今天这次修复暴露了一个思维模式的问题：之前一直把"能跑"等同于"配置正确"。editable install 这件事让这个等式第一次被清楚地证伪——两个 package 在 `pip install -e .` 跑对之前就已经能 import，但原因是 setuptools 把根目录塞进了 `sys.path`，是副作用，不是意图。

**踩坑记录**  
重构过程中有一个中间态：`pyproject.toml` 被建在了 `rag_basics/` 子目录里，内容也错——`name = "rag-basics"`，用 `py-modules` 把模块当散文件注册而不是用 `packages.find`。这个配置让 `mcp_learning` 看起来也能 import，但原因是 setuptools 的副作用而不是显式声明，属于"凑巧能用"。子目录里的 `pyproject.toml` 只能管那个子目录自己，无法声明同级的其他 package；要统管整个项目的所有 package，`pyproject.toml` 必须在根目录。

改名也不是审美问题——Python package 名里的连字符会被解释器当减号处理，`rag-basics` 这个目录名从语法层面就不是合法的 package name。

**副作用 / 后续**  
Render 上的两个 service（FastAPI + Streamlit）在这次 push 之后会因为 Root Directory 和 Start Command 路径变化而部署失败。已知，推到 Day 55 集中修。`chroma_db_lc/` 的 git 历史清理也推到迁 Pinecone 之后再做。

---

### 2026-05-29 (Day 51) — MCP server 升级为 RAG-backed

**Decision 1: 跨目录 import 方案**
- 尝试 editable install (pyproject.toml + pip install -e .)
- 失败:macOS case-sensitivity 干扰 finder 注册,sys.meta_path 未触发
- 临时方案:sys.path.insert(0, absolute path),记入 TODO
- 周日 special block 回头修方案 B (验证 _EditableFinder + 大小写归一化)

> **Day 54 后注**：这条 "失败原因" 的诊断本身是错的。真相是项目根目录从未有过 `pyproject.toml`，editable install 从未发生。Day 54 用根目录 `pyproject.toml` + `packages.find` 彻底解决。

**Decision 2: Server tool 设计 (选项 B)**
- 两个 tool: get_immigration_program_summary (结构化) + retrieve_documents (通用)
- 拒绝设计 A (单一 ask wrapper) — 会绑死 LLM 和 prompt
- 拒绝设计 C (纯 retrieve, agent 自己 reason) — production 太不可控
- 选择 B = capability 边界清晰 + production-grade 可预测性

**Decision 3: Reranking 归属 (选项 α)**
- Reranking 留在 server 内,作为 retrieve_documents 的实现细节
- 拒绝 β (独立 tool) — 把检索内部决策错误暴露给 model
- 拒绝 γ (client 自己调) — 检索质量应该是 server 责任
- Punchline: "MCP-native ≠ expose every step. Hide implementation, expose capability."

**Known issue: RAG retrieval quality**
- 3 docs 太少,language requirement query 返回 BC PNP top1
- 解决: Phase 3 Week 1, Pinecone + 全量 ingest + 更细 chunking

**ask() 函数 deprecation**
- app.py 已切换到 agent + retrieve_kb_context 路径
- ask() 只剩 langchain_query.py __main__ 块在用 (CLI test)
- 标记为 deprecated, 未来重构时删除

---

### 2026-05-28 (Day 50) — MCP Adapter Integration

**Decision**: Use `langchain-mcp-adapters` with `MultiServerMCPClient` (unified client) instead of multiple independent MCP clients.

**Alternatives considered**:
- 3 个独立 client per server → boilerplate 爆炸,生命周期分散
- 手写 MCP JSON-RPC 协议 → 重复造轮子,production 太脆

**Why unified client**:
- Subprocess lifecycle 集中管理
- Tools 自动 merge 成单一 list,agent 不感知来源
- Async context 统一,error isolation 在 client 层做

**Trade-offs accepted**:
- 整条链路必须 async-to-async,sync agent 要重写为 async
- Tools 启动后是 immutable list,运行时加 server 需要重启 agent

**Production trap discovered**:
- ToolMessage.content 不是 string,是 list of dict
  (MCP structured content format: `[{"type": "text", "text": "...", "id": "..."}]`)
- 下游处理时要解构,不能直接当 str 用

**Cross-folder concern**:
- Server 在 mcp-learning/,agent 在 rag-basics/,用 absolute path 启动
- Day 51-58 进 Phase 3 时合并到统一 production repo

---

### 2026-05-20 (Day 46) — Agentic RAG

**Agentic RAG: 5-node graph with self-evaluation loop**  
`agentic_rag.py` 写新 graph：`query_analysis → [needs_retrieval? retrieve : generate]`，`retrieve → self_evaluate → [good? generate : iter<2? retrieve : generate]`。State 6 字段（question / retrieved_docs / answer / evaluation_score / iteration_count / needs_retrieval）。3 测试场景 pass：闲聊（"你好"，iter=0 直奔 generate）、命中（"BC PNP 要求"，1 次 retrieve → good → 详细 answer）、知识库 miss（"ABCXYZ123 移民项目"，retrieve 2 次都 bad → 优雅退出"我没有相关信息"，未编造）。架构差异 vs LangChain AgentExecutor：决策点显式分散到 graph nodes（query_analysis / self_evaluate），不是集中在 ReAct loop 的 LLM 内部 — graph 拓扑本身可审计、可控制流。

**Self-evaluate prompt = 评估 "docs vs question" 不评估 "answer 好不好"**  
LLM-as-judge 自评偏见：同一 LLM 评估自己产出会系统性偏 good（论文报告 +10-15pp）。Mitigation 四档按强度排序：(1) 评估对象切换为"客观相关性"而非"主观质量"，(2) Structured output 限定 good/bad 单词输出 + 容错先查 bad 后查 good（保守优先），(3) 不同 model 做 evaluation（如 retrieve gpt-4o-mini / eval claude），(4) Embedding similarity 替代 LLM judge。今天做 (1)(2)，(3)(4) 留 ticket → Day 36 RAG evaluation block 做。Default 解析失败 → "bad" 触发重试（fail-safe over fail-loud）。

**iteration_count 计数职责 = retrieve node（不是 self_evaluate）**  
计数 +1 放在产生检索副作用的 node 而非评估 node。理由：语义清晰（"retrieve 跑几次"= iteration_count 字面值），conditional edge `if iter < 2` 阅读即语义；若放 self_evaluate +1，会导致 retrieve 1 次 → eval 1 次 → count=2 → conditional 误判已重试，**实际只 retrieve 1 次但语义说 2 次**。架构原则 generalized：**state 字段的更新职责绑定到产生该字段对应副作用的 node**。

**Generate node 严格继承 simple RAG 的 "只根据文档" 原则**  
第一版 prompt 写"如果文档信息不足请基于一般知识回答"——和 simple RAG `langchain_query.py` 的"只根据提供的内容回答，不要编造"矛盾。Agentic RAG 作为 production 系统给同事用，更应严格。改为：保持 system message "只根据文档"，self_evaluate=bad 时（iter 达上限兜底场景）prompt 加 warning 强化"找不到就说找不到"。结果：测试场景 3 "ABCXYZ123" iter=2 退出后回答"我没有相关信息"，无 hallucination。**Production hallucination 是 user-visible failure，cost 是 system-visible failure；前者优先级 >> 后者。**

**State 字段单一职责 — needs_retrieval 不复用**  
self_evaluate 第一版误把"评估结果"压缩进 `needs_retrieval` 字段（已被 query_analysis 用过）。Refactor 后 self_evaluate 只 return `evaluation_score`，conditional edge 直接读 `evaluation_score` + `iteration_count` 做分支。原则：**每个 state 字段对应一个决策点，不复用**，conditional edge 直接消费多个 state 字段做 routing，不需要预先压缩成一个 boolean。

**Code smell logged：simple RAG retrieval 逻辑重复**  
`langchain_query.py` 的 `ask()` 和 `retrieve_kb_context()` 都直接写 `rerank_docs(question, hybrid_retriever(question, k=6), top_n=3)`——违反 DRY。Agentic RAG retrieve node 是第 3 处重复。**Decision**：Day 47 之后重构为 `retrieve_with_reranking(question, k=6, top_n=3)` 单一入口函数，三处都调它；改 k/top_n 时只动一处。面试 story：发现 simple RAG 的代码异味，做 Agentic RAG 时顺手清理，体现 production code quality awareness。

**Python 工程基础 bug 集中暴露 — Self-audit habit 强化**  
今天 5 nodes 共踩 6 类 Python 基础 bug：(1) Dead code（变量计算后未使用）×2 — query_analysis 的 iteration_count 第一次、self_evaluate 的 format_docs；(2) Operator chaining（`content == "yes" in content` 被解释为 `(content == "yes") and ("yes" in content)`）；(3) iteration_count 职责忘记（讲了两遍仍 +1 in self_evaluate）；(4) `is None` vs `not`（truthy/falsy 不一致，None / [] / missing 应该一律走 falsy 分支）；(5) if/else 共享逻辑被困一侧（`llm.invoke` 只在 else 分支，if 分支跑会 NameError）；(6) 凭印象编 LangGraph API（`add_state` / `add_transition` / `graph.run` 均不存在，正确是 `add_node` / `add_edge` / `app.invoke`）。
**Root cause**：累 + 赶进度时跳过 self-review
**Mitigation enforced**：每个 node 写完强制 30 秒 checklist —— (a) 所有计算变量都被 return 或使用？(b) return 字段是否只包含本 node 负责的？(c) 老师的问题都回答了？不确定的 API 直接翻已写过的 graph 文件（5 秒搞定）不凭印象编。

---

### 2026-05-15 (Day 45) — HITL Implementation

**HITL implementation via in-tool `interrupt()` (Pattern A) vs independent approval_node (Pattern B)**  
新 `submit_application` tool 在函数最前一行调 `interrupt({"action", "data_preview", "question"})`，接 user 的 `"approve"`/`"reject"` resume 值走 if/elif/else 分支。备选 Pattern B 用独立 `approval_node` + conditional edge 路由 high-stakes tool calls，graph-native 更适合 production（approval 逻辑集中、per-tool policy 可配、audit log 易加）。选 A 理由：今天 focus 是 `interrupt + Command + checkpointer` 三件套 mental model，不引入 graph 复杂度；A 嵌入式、单工具范围内可读性高。代价：approval 逻辑跟 tool 实现耦合。Day 46 重构候选。

**Checkpointer = InMemorySaver for development; SqliteSaver migration deferred**  
`builder.compile(checkpointer=InMemorySaver())`。SqliteSaver 需要额外 `pip install langgraph-checkpoint-sqlite` + sqlite3 connection 管理，今天 setup 开销不值；InMemorySaver Day 41 已用过 API 一致。Trade-off：进程退出 state 丢失，演示不了 HITL 的 superpower —— 用户关网页 30 分钟后服务器重启过仍能 resume。Day 46 升级时配验证脚本（第一次跑触发 interrupt → Ctrl+C 退出 Python → 重新跑 Command(resume=...) 用同 thread_id → 成功恢复）。

**should_continue returns `"tools"` / `END` to match conditional edge dict keys (Pattern A)**  
`return "tools"` / `return END` 匹配 `{"tools": "tools", END: END}`。导师推荐 Pattern B（returns `"use_tools"` / `"finish"`，dict `{"use_tools": "tools", "finish": END}`，把"router signal"跟"node name"语义解耦——前者是 routing 标签、后者是 graph 拓扑）。A 功能等价且代码量少，但 silently 选 A 没 articulate 理由，是 Day 44 zero-violation 续约的边界违反。下次类似 trade-off 必须 explicit 表达"我选 X 因为...."。

**Single-tool graph for HITL learning isolation**  
`agent_graph_hitl.py` 只 bind `submit_application` 单工具，不引入 `agent_graph_conditional.py` 的 `check_processing_time` / `retrieve_kb_tool` / `calculate`。今天 focus 是 HITL 控制流（interrupt / Command / resume / replay 行为），multi-tool 引入 multi-iteration 验证 noise 干扰单点 mental model 建立。Multi-tool + HITL 组合留 Day 46+。

**Interrupt-first ordering inside tool function (路 A)**  
`submit_application` 内部第一行就是 `approval = interrupt({...})`，所有 if/elif/else 内的 side effects 放后面。原因：LangGraph resume 时 node function 从头 replay —— interrupt 之前的代码会执行**两次**。如果把 `log_to_db()` 放 interrupt 之前，会写两条 log；把 `call_ircc_api()` 放前面会调两次 IRCC（不可逆灾难）。备选方案"路 B"是让所有副作用 idempotent（用 dedup key），工程复杂度高暂不采用。

**Pydantic auto-import disease**  
Day 45 踩坑：Pylance auto-import 把 `from pydantic import tools` 加进来，导致 `Annotated[tools, add_messages]` 语义错乱（`tools` 既不是合法类型也跟 `tools = [submit_application]` 后续赋值冲突）。Root cause 是接受 IDE auto-suggest 没 verify 来源 module。已加进 Architectural Conventions 区的 "Import discipline" 规则。

---

### 2026-05-14 (Day 44) — Conditional Edge Migration

**Conditional edge migration (static dual-llm → single llm with routing)**  
重写 agent graph 用 `add_conditional_edges` + `should_continue` decision function 替代 Day 43 的双 llm_node hack。结果：单一 `llm` node，conditional edge 根据 `state["messages"][-1]` 的 `tool_calls` 字段路由到 `tools` 或 `END`；`tools → llm` 是固定边形成 loop。可处理"无需 tool 的 query"（如"你好"，单步直奔 END）和"多步 tool 调用"（agent loop 从图拓扑涌现）。验证 query：「学签需要多久」→ 4 条消息（H/A_tool/T/A_final），「你好」→ 2 条消息（H/A）。

**isinstance over hasattr/getattr for routing logic**  
`should_continue` 判断"LLM 是否决定调工具"用 `isinstance(last, AIMessage) and last.tool_calls`。备选 hasattr/getattr 是 duck typing — 在 LangChain 强类型语义生态里会被无关属性骗（假设 HumanMessage 未来加 tool_calls 字段，duck typing 返回 use_tools，类型路径不会）。Routing/控制流场景 isinstance 表达意图（"我只信 AIMessage 的决定"）而不是机制（"这玩意儿有 tool_calls 属性"）。

**should_continue canonical location = production graph file**  
`should_continue` 住在 `agent_graph_conditional.py`，`decision_test.py` 改为消费者 (`from agent_graph_conditional import should_continue, AgentState`)。备选放 test 文件会导致 graph → test 反向依赖 + import 时副作用泄漏；备选独立 `routing.py` 当前项目规模过度工程。Future trigger：多 graph 共用同一决策逻辑、或 decision function 复杂到需独立 test suite 时再抽。

**LangGraph node 契约 = wrapper function，不直接传 Runnable**  
第一版 `add_node("llm", llm_with_tools)` 直接传 ChatOpenAI Runnable，runtime fail：LangGraph 把 state dict 喂给 `ChatOpenAI.invoke()`，但后者只接 `str | list[BaseMessage] | PromptValue`。修法恢复 `llm_node(state) -> {"messages": [response]}` 适配器，显式取 `state["messages"]` 喂 LLM、用 dict 包返回。LangGraph 故意把 state schema → LLM input 的映射责任留给开发者 — 换来 state 字段命名自由、前后插日志/错误处理的余地。配合 closure 嵌套：`llm_node` 定义在 `build_graph()` 内部，闭包捕获 `llm_with_tools`，外部不可见。

---

### 2026-05-13 (Day 43) — Static-Edge Graph

**Provider switch (Anthropic → OpenAI for `agent_graph_minimal.py`)**  
Anthropic 用尽 → gpt-4o-mini。教学内容（native LangGraph）无需续费，代码本来 provider-agnostic。

**双节点注册同函数 vs Conditional edge**  
今天 scope 是 static edge only。`add_node("llm_call", llm_node)` + `add_node("llm_final", llm_node)` dual-registration 暴露"node 名是 unique identifier、函数可复用"机制。代价：agent 只能处理 exactly-one-tool-call。Day 44 conditional edge 取代。

**Prebuilt ToolNode vs 手写 dispatch**  
用 prebuilt。Day 42 手写过整套（找 tool_call → lookup → 执行 → 包 ToolMessage），今天 cognitive load 留给 graph 编排本身。

**Toy tool vs 真 RAG retriever**  
hardcode `get_processing_time`（4 个 visa 类型 dict），不接 ChromaDB。隔离变量：今天观察 graph 机制，RAG 集成是 orthogonal complexity，混在一起调试时分不清是哪层 bug。Day 44-46 graph 稳定后接真 retriever。

---

### 2026-05-12 (Day 42) — Tool Error Handling

**Tool error handling 策略**  
所有 tool 内部不向 Agent raise，return LLM-actionable string。HOW 取决于 tool 类型：危险操作（`eval`）和外部调用必需 try/except；纯内存 dict lookup 用 default return 即可。

实验验证：故障注入对比 raise vs graceful return —— raise 让 graph.invoke() 直接崩（fail-loud），无 LLM fallback；graceful return 让 LLM 老实 acknowledge 失败 + 给 IRCC URL + 保留 partial answer (BC PNP 介绍)。

附加观察：modern LangGraph 默认支持 parallel tool calling，LLM 一次 AIMessage 可发多个 tool_call，节省 round trip。

**Path hardening (chroma_db_lc)**  
模块 load 时 `Path(__file__).parent / "chroma_db_lc"` resolve 绝对路径，替代依赖 cwd 的 `"./chroma_db_lc"`。Root-cause fix。从此 rag-basics 子目录之外启动也能找到 vector store。