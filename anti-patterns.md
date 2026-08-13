# Mentor Anti-Patterns Log

Purpose: Pre-interview / pre-status-update self-check.
Read this file before every: face-to-face conversation, LinkedIn post, recruiter reply, mock interview.

---
## BM25 对中文 query 失效 (default whitespace tokenizer)

**Anti-pattern**: BM25Retriever.from_documents 使用默认 tokenizer (按空白/标点切分), 中文 query 整个变成 1 个 token, 与 doc 无 token 匹配, 全库 score 为 0, 排序退化成插入顺序。

**为什么问题**: Ablation Config 1 (BM25 only) 三个语义完全不同的 query 返回完全一致的 3 个 doc。生产 hybrid 里 BM25 那一路是装饰品, 实际检索完全靠 dense + rerank。

**当前状态**: 保留代码不动, 生产依赖 dense + rerank 兜底, BM25 结果被 rerank 打分低刷掉。

**长期修复**: Day 74+ 集成 jieba 中文 tokenizer, 用 `BM25Retriever.from_documents(..., preprocess_func=jieba_tokenize)`. 修复后需要重跑 ablation 才能声称 hybrid 有效。

**Interview articulation**: "Ablation 暴露了中文 BM25 tokenizer 失效, 生产系统实际靠 dense embedding + cross-encoder rerank 两段式撑住. BM25 集成中文分词器归为 tech debt."

## Hybrid merge 用 union + dedup 而非 RRF, semantic 因 list 拼接顺序隐式优先

**Anti-pattern**: Hybrid retrieval 合并层用 `semantic_docs + bm25_docs` 拼接后按 `page_content` 去重, 不是 RRF 等显式分数融合策略, 导致 semantic 结果因 Python list 拼接顺序被隐式排在 BM25 之前。

**为什么是问题**:
- 生产环境有 Cohere rerank 作为 Layer 3, 重新打分排序抹掉输入顺序偏差, 体感无问题
- Rerank 关闭时 (evaluate.py Config 3 消融) semantic 获得不公平位次优势, 数字失真
- 面试若答 "hybrid merge 用 RRF" 是错的; 准确答法: "union + dedup, semantic biased first by list order"

**Replacement rule**:
- 描述架构: 说 "union + dedup, semantic biased first", 不说 RRF
- 消融实验解读: Config 3 数字要**打折解读**, semantic 贡献被高估, 不能直接用 Config 3 - Config 1 得出 "semantic 比 BM25 强 X%" 的结论
- 长期修复: 改成 rank-based RRF (`score = Σ 1/(k + rank_i)`, 常用 k=60), 归为 tech debt Day 74+ 处理

**Specific instance**: Day 73 (2026/8/12) 准备跑 evaluate.py 消融实验前, 通过 `grep BM25` 回顾 `hybrid_retriever` 实现, 发现代码是 `for doc in semantic_docs + bm25_docs` 后按 `page_content` 去重, 不是 RRF。之前 Day 35 记忆里 "RRF 合并原理" 是概念学习, 不代表实际实现。这个 gap 直到消融实验才暴露。


## Day 45 (2026/05/15) — Python truthy verification (Valid Sudoku HITL approval flow)

**Anti-pattern (verbatim)**: "bool是False，所以会走else啊"

**Why it's wrong**: 凭直觉答 Python 语义。`bool("reject")` 实际是 True——任何非空字符串都 truthy。"我以为我懂"是 silent bug 的源头。如果这一行进 production，user reject 时系统显示 "submitted successfully"——没有 error log，无法追溯。

**Replacement**: 任何 Python 语义有 0.1% 不确定，3 秒钟去 REPL 跑 `bool(...)` / `type(...)` / `isinstance(...)`。永远 explicit 比较字符串 (`approval == "approve"`)，永远不靠 truthy 检查 user input / config 值。

**Where I violated it**: Day 45 HITL submit_application tool 的 `if approval:` 这一行。Claude 问 `bool("reject")` 是 True 还是 False，我答 False。Claude 让我去 REPL 跑——4 个 bool 输出立刻看到 `bool("reject") == True`，自己 mental model 错了。

---

## Day 45 (2026/05/15) — Silent partial acceptance of mentor feedback

**Anti-pattern (verbatim)**: "[v3 代码没改 `if approval:`，只改了 elif/else 结构]" + "[选 Pattern A 没说理由]" + "[Step 1 over-implemented 完整 while loop]"

**Why it's wrong**: 导师 review 同时给"修复 + 建议"两类反馈，我只 internalize 修复，silently 忽略建议。Day 44 zero-violation 续约明确说"silently 只接收一半的反模式不再出现"，Day 45 违反 3 次。负利率滚雪球——build trust 慢，loss trust 快。

**Replacement**: 导师说"改 X 到 Y"或"选 P"时：要么严格 execute，要么 explicit push back 说"我选 Z 因为...."。每个偏离 default 的选择都必须有 articulated reason，不能 silently slip。

**Where I violated it**: 
- Day 45 v3 代码——Claude 说 "`if approval:` → `if approval == "approve":`"，我贴 v3 只改了 elif/else 没改 if 这一行
- Day 45 should_continue 设计——Claude 推荐 Pattern B，我选 A 没说理由
- Day 45 main block Step 1——Claude 说"只写 invoke + 检测 + 打印，先不写 resume"，我写了完整 while + Command + 2 次 invoke

---

## Day 45 (2026/05/15) — Run before verifying save state

**Anti-pattern (verbatim)**: "[贴 Step 2 完整代码给 Claude，但 terminal output 显示 Step 1 的 print（`=== RAW RESULT ===` / `=== KEYS ===` / `=== INTERRUPT? ===`）]"

**Why it's wrong**: VS Code 编辑器里的内容 ≠ 磁盘上的文件内容。我改了代码没按 Cmd+S 保存，`python agent_graph_hitl.py` 读的是磁盘旧版本。"代码看起来对但 output 不对"99% 是这个。Debug 时本能怀疑代码逻辑，浪费 1 轮 review。

**Replacement**: Terminal 跑 Python 脚本前：
1. 看 VS Code tab 标题旁边——● 是未保存，× 是已保存
2. 或 terminal 里 `tail -20 path/to/file.py` 验证磁盘内容跟编辑器一致
3. Cmd+S 保存再跑

**Where I violated it**: Day 45 main block Step 1 verification——我贴 Step 2 完整代码给 Claude，terminal 跑出来是 Step 1 的旧 print。Claude 一眼看出 mismatch，让我确认 save state。

---

## Day 45 (2026/05/15) — IDE auto-import disease

**Anti-pattern (verbatim)**: "from pydantic import tools"

**Why it's wrong**: 写 `Annotated[tools, add_messages]` 时 Pylance auto-suggest 弹出 `from pydantic import tools`，我按 Tab 接受了——`pydantic` 根本没有公开的 `tools` symbol。要么 ImportError 要么导入了 pydantic 内部 submodule，跟我需要的 `list` 完全无关。然后 `Annotated[tools, add_messages]` 语义错乱：`tools` 既不是合法类型，又跟我后面 `tools = [submit_application]` 命名冲突。

**Replacement**: 每次 IDE auto-import suggestion：
1. 看清来源 module——`from X import Y` 里 X 是什么
2. 如果不是预期的 module，reject suggestion 自己手敲
3. Commit 前扫一遍 import block——每一行都是 conscious 选择，无 dead imports
4. 任何 `from X import Y` 你不能 60 秒内说清 X / Y 用途，就是潜在 bug

**Where I violated it**: Day 45 `agent_graph_hitl.py` 顶部 imports——Pylance auto-completed `from pydantic import tools`，我接受了。Claude review 时点出来，问 "Day 44 conditional 版的 AgentState 第一个参数是什么"，我去 reference Day 44 才发现应该是 `list`。

---

## Day 45 (2026/05/15) — Submit code without running

**Anti-pattern (verbatim)**: "for c in rang(9):" + "if (board[r][c] in col[c] or ... or board[r][c] in square[(r // 3, c // 3)]:"

**Why it's wrong**: LeetCode #36 Valid Sudoku 代码贴给 Claude review 时包含 2 个 syntax 错误：
- `rang(9)` 是 typo（应该 `range(9)`）—— NameError 必然
- 括号不平衡—— SyntaxError 必然

LeetCode 平台 Submit 5 秒之内会立刻红字 syntax error。我都没粘到平台跑过就贴给 Claude，让他 audit 算法逻辑。Production engineer mindset 是 "先 ship 验证再 review"，student mindset 是 "先 review 再跑"。

**Replacement**: 任何代码贴给导师/同事 review 前：
1. 本地或 LeetCode 平台跑一次，确认 syntax 过 + 基础逻辑跑通
2. 才能贴
3. Review cycle 是为了 catch 算法 / 设计 bug，不是为了 catch syntax error——浪费 reviewer 时间在 syntax 上等于不尊重对方

**Where I violated it**: Day 45 LeetCode #36 贴给 Claude——`rang(9)` typo + 括号不平衡。Claude review 时立刻 catch，并指出 "production engineer 基本素养是先 verify 再 ship"。

---

## Day 45 (2026/05/15) — Over-implementing across stepwise instructions

**Anti-pattern (verbatim)**: "[Step 1 spec: '只写 invoke 第一次 + 检测 interrupt + 打印 payload。先不写 resume。'] → [我交付：2 次 invoke + 完整 while + Command resume + final answer print]"

**Why it's wrong**: 导师明确分步 "Step 1 写 X，Step 2 写 Y"，stepwise verification 是为了 catch 每一步的 mental model bug。我 over-implement 跳过 audit 等于让 bug 累积——Step 1 验证不完整，Step 2 的 `Command("resume", {...})` 语法错 + 2 次 invoke 逻辑错被掩盖在 over-implemented 代码里。"我多写了节省时间"是错觉，实际是越界破坏 review cycle。一次性 ship 全套是 senior engineer 特权（build on already-verified primitives），学习阶段每个 primitive 都要 audit。

**Replacement**: 导师说"Step 1 写 X，Step 2 写 Y"时：
1. 只写 X
2. 跑 X + 贴 output
3. 等 audit pass 才写 Y
4. "我多写了 Y 节省时间"= 越界，不是认真，是破坏 stepwise debug 价值

**Where I violated it**: Day 45 main block 第一次 build——Claude 明确说 "Step 1 只写 invoke 第一次 + 检测 interrupt + 打印 payload，先不写 resume"，我直接写了 2 次 invoke + 完整 while loop + Command resume + final answer print。Claude 严肃 push back "Stop. 你又没按 Step 1 指令做"。

---

## Meta — 横切 root cause（所有 6 条共享）

**Pattern**: "我以为我懂了，就不验证"

- #1：以为 `bool("reject")` 是 False，没验证 → silent bug
- #2：以为听懂了导师建议，没全部 execute → 半接受
- #3：以为代码改了就保存了，没验证 → run 旧版本
- #4：以为 IDE 给我 import 的是对的，没验证 → wrong module
- #5：以为代码逻辑对了 syntax 也对，没跑 → syntax error
- #6：以为多做是认真，没问"导师真的要 Step 2 吗" → over-implement

**底层心理**：怕慢 + 怕显得不懂 + 想"看起来 efficient"。结果反向——每个 anti-pattern 让节奏更慢、bug 更多、信任损耗。

**Production engineer reverse mindset**：默认怀疑自己懂、所有 assumption 验证一遍、stepwise ship 不是 batch ship。**慢即是快**——前期 verify 的 30 秒省下后期 debug 的 30 分钟。

---

## 5/29 复习 indicator

2 周后 check 这 6 个 pattern 是否再犯。任意 1 个再犯 → 这份文档底部 append 新 case + 具体场景。

**目标**：Day 47-60 期间，能在**犯错前**预先意识到（pre-mortem mindset），不是事后回顾。