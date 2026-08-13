## [2026-07-23, Day 65] verbatim copying — 同日两次触发

**触发场景 1(无意识层)—— DEPLOYMENT.md v1 写作阶段**

在写 DEPLOYMENT.md 第一版时,把 Claude 上一轮对话中带方括号的措辞直接抄进文档。当时的主观感受是"写完了",完全没意识到这是抄的。发现是 Claude 指出之后。

**触发场景 2(有意识层)—— Issue 1 editable install 口头复述阶段**

Claude 明确要求"用你自己的话讲一遍 editable install 的意义,不许抄"。我的回答几乎逐字复制 Claude 上一轮的原话,只改了标点、少了几个词、缩了一个连接词。在被明确禁止抄的情况下依然发生了。

**根因**

不是意志力问题,是**认知资源耗尽时大脑的默认路径**。Day 65 早上 6:50 CS6120 起床 + 10 点 LeetCode 2 题(视频版)+ 下午 Render 三次部署失败调试(高强度)+ 傍晚写文档 —— 5 小时以上 deep + mid work 叠加。到 Issue 1 复述时,大脑找的是"最省力路径" = 复述最近读过的内容,而不是"重新组织语言"。

**特别危险的是第二次**:被明确指出后依然发生,说明"抄一次没事"的路径已经在被强化。如果不记进 anti-patterns,下次会更容易触发。

**下次触发前的自检问题**

1. 我现在要写下的这段话,是"我脑子里已经有的知识"还是"我刚才刚从对话里读到的"?如果是后者,合上对话窗口再写。
2. 如果一个概念我讲出来的时候句式和 Claude 一模一样,是不是意味着我根本没消化过?消化过的东西讲出来会是我自己的句式。

---

## [2026-07-23, Day 65] predict-before-run 缺失 —— Render 三连败

**触发场景**

Pinecone cutover 部署 Render 时,连续三次失败:

- 第 1 次:Build Command 只写 `pip install -r requirements.txt`,没写 `pip install -e .` → build 阶段 `from rag_basics import ...` ImportError
- 第 2 次:没设 `PYTHON_VERSION`,Render 默认 3.14 → `langchain-pinecone` / `pinecone-client` pip install 阶段 fail
- 第 3 次:`PINECONE_API_KEY` 和 `COHERE_API_KEY` 没配 → runtime 首次查询才报错

每次都是"改完直接推 → 等 Render log → 看到报错 → 再改"。三次失败之间没有做过一次"推之前先在脑子里预测这次会不会成功、如果会 fail,fail 点应该在哪个阶段"。

**根因**

即时反馈的诱惑。改完直接推有一个心理上的错觉:感觉"在推进"。而预测需要停下来想,主观上感觉"没动"。但实际上:预测 3 分钟能避免 10 分钟的 Render build 等待 + 状态切换成本。

三次连续失败之后加起来浪费的时间,远超"每次改完先预测 30 秒"的成本。

**下次触发前的自检问题**

1. 我要推的这个改动,如果失败,失败点应该在哪个阶段(build / config / runtime)?如果我答不出这个问题,说明我没预测,不要推。
2. 上次我这么改的时候,是一次就成的吗?如果不是,当时踩的坑现在解决了吗?
---

## Day 72 (2026-08-11)

### Anti-pattern: 假设 schema 全局一致而不 verify

**触发场景**  
Day 72 处理 evaluate.py 之前, memory 一直记 "三层元数据 schema (category_l1/l2/l3 + resource_type) 全程强制执行"。跑 dump-all-inventory 才发现: 71 个 link chunk 有完整 9 字段, 7 个 content chunk 只有 4 字段, 差 5 个 category 相关字段。schema 从 Day 60+ 就一直是 drift 状态, 无人 verify。

**根因**  
"三层元数据 schema 全程强制执行" 是**期望**, 不是**观察**。ingest 代码里 link 和 content 走两个函数 (load_content_chunks / load_link_chunks), 双方独立演化, 没有一个中央 constraint 强制 schema 一致。心理上以为 "我在两处都写了 metadata" == "两处 metadata 结构相同", 实际上没有类型检查 / test 来 enforce。

**下次触发前的自检问题**  
1. 我说 "KB 有 X 特征", 这是从代码里读出来的 (grep / dump), 还是我记得应该有?
2. 至少每 2 周跑一次 `list_docs_by_category.py`, dump 出的 category / metadata 结构和上次 dump 一致吗? 如果不一致, 什么时候变的, 为什么变的?
3. 有没有一个 assertion / test 在 ingest 时强制 content 和 link 的 metadata keys 集合相同? 没有的话, drift 只是时间问题。

---

### Anti-pattern: 只 audit metadata 不 audit page_content

**触发场景**  
Day 72 修完 metadata schema 后跑 dry-run, 才发现 chunk_size=800 让 content chunk 语义严重污染: chunk_0 是 "EE 提前体检 + 拒签信备注" 两条政策混合, chunk_3/4/5 全是 TEER NOC 代码列表 (纯英文代码 + 职业名, 对任何自然语言 query 都是低 relevance)。修 metadata 花了 20 分钟, 修 chunking 又花了 20 分钟, 本可以一次做完。

**根因**  
Metadata 是显式字段, 可以直接 assert; page_content 是自由文本, 需要打开每个 chunk 读一遍才能判断语义质量。心理上默认 "chunking 是 splitter 自动的, 应该没问题", 但 splitter 不懂语义, 只按 token 数硬切。fixed-size splitter 对 markdown / 时间线 / 数据表格类内容天然不适配, 但 Day 30-71 从没被系统性 challenge 过。

**下次触发前的自检问题**  
1. audit KB 要至少 3 层: (1) vector 数量 (2) metadata schema (3) 每个 chunk 的 page_content 独立语义。缺一层, evaluate 数字都不可信。
2. splitter 配置 (chunk_size / chunk_overlap / separator) 和我的内容结构 (markdown headers / 时间戳 / 数据条目) 有没有明确 alignment? 没有的话, 到 evaluate 阶段就会撞见语义污染。
3. dry-run 输出的 chunk length 分布如果有异常小值 (200 chars 残片) 或异常大值 (>1500 chars 无法 embedding 有效捕捉), 就是 splitter 不适配的信号。

---

### Anti-pattern: KB 认知盲区 - 数据存在但看不见

**触发场景**  
Day 72 chunking migration 后 dry-run 输出 10 个 chunk, 我第一次看见 "2024.11.15 — 转学必须重新申请学签" 这条政策。这条政策一直在 knowledge_base.txt 里, 但之前 chunk_size=800 时被埋在某个 chunk 的中间部分, 从 memory 到 Day 71 review 都没意识到 KB 里有这条。这意味着: 从 Day 30 到 Day 71 之间, 只要客户问 "转学要不要重新申请学签", 系统本可以答对但我不知道系统能答对, 也无从设计相关 test case。

**根因**  
把 "KB 里有多少条内容" 等价于 "我脑子里记得的多少条", 但两者从来不相等。fixed-size chunking 把语义单元 (一条政策) 切散到多个 chunk 中间, 单独看每个 chunk 只能看到部分政策的部分内容, 谁都拼不出全貌 —— 包括开发者自己。开发者以为自己了解 KB, 实际上不了解。

**下次触发前的自检问题**  
1. 每次 KB 更新后, 必须至少跑一次 dry-run 输出所有 chunk 的 title / 前 200 chars, 当作 KB 内容 self-audit —— 不是为了 debug 系统, 是为了让我自己知道 KB 里到底有什么。
2. 如果一个 chunk 的 title 是通用词 (如 "IRCC 政策更新时间线"), 说明 metadata 无法帮我识别这个 chunk 的内容 —— 需要更细粒度的 resource_title (如具体政策名称 + 日期)。
3. 如果 chunking 让一个语义单元被切散, 我永远也不会 "看到" 这个语义单元, 除非某天正好搜到相关 query。**Semantic-aware chunking 不只是检索质量问题, 是开发者对自己 KB 的可见性问题。**

---

## Day 73 (2026-08-12)

### Anti-pattern: Hybrid merge 用 union + dedup 而非 RRF, semantic 因 list 拼接顺序隐式优先

**触发场景**  
Day 73 抽 retrieve() 之前, 通过 `grep BM25` 回顾 `hybrid_retriever` 实现, 发现代码是 `for doc in semantic_docs + bm25_docs` 后按 `page_content` 去重, 不是 memory 里记的 RRF (Day 35 "RRF 合并原理" 是概念学习, 从没落地)。生产环境 Cohere rerank 抹掉了输入顺序偏差, 所以体感无问题, 但 Config 3 (hybrid no rerank) 会让 semantic 获得不公平位次优势。

**根因**  
"我学过 RRF" ≠ "我实现了 RRF"。Day 35 学 RRF 时是概念探讨, 但当时代码用 union-dedup 图快, 之后 memory 慢慢从 "实现了 union-dedup" 漂移成 "实现了 RRF"。没有一次实际打开代码 verify 实现方式和 memory 一致。silent drift 只有做 ablation 时才暴露。

**下次触发前的自检问题**  
1. 我说 "生产系统用了 X 策略", 这是我记得的还是我刚看过代码的? 如果超过 2 周没打开代码 verify, 默认 memory 已经 drift。
2. 面试前把系统架构自述 vs 代码实现做一次对齐 audit, 找出所有 "以为实现了但没实现" 的项。
3. Config 3 数字要**打折解读**, semantic 贡献被高估, 不能直接用 Config 3 - Config 1 得出 "semantic 比 BM25 强 X%" 结论。

**长期修复**: rank-based RRF (`score = Σ 1/(k + rank_i)`, k=60), tech debt Day 74+。

---

### Anti-pattern: 共享 retriever 单例被临时修改属性

**触发场景**  
Day 73 抽 retrieve() 时, dense-only 分支需要 `semantic_retriever.search_kwargs["k"] = intermediate_k`, 但 `semantic_retriever` 是模块顶层单例, 被多个函数共享。改完不还原, 下次调用 hybrid 分支时用的还是被污染的 k。BM25 同理。

**根因**  
模块顶层单例是**只读的心理暗示**, 但 Python 里 dict / attribute 全是可变的。retrieve() 内部临时改共享单例属性是 "省事", 但引入跨调用状态泄漏风险。

**当前 mitigation**: 每次分支前重置到默认值 (`bm25_retriever.k = 3`, `semantic_retriever.search_kwargs["k"] = 3`)。

**下次触发前的自检问题**  
1. 我要改的对象是模块顶层单例吗? 如果是, 改动会不会影响其他调用者?
2. 有没有更干净的替代 —— 每次调用创建新对象, 或者直接绕过共享层调更底层 API?

**长期修复**: retrieve() 内改用 `vectorstore.similarity_search(query, k=...)` 和 `BM25Okapi` 直接接口, 绕过共享 retriever, tech debt Day 74+。

---

### Anti-pattern: BM25 default whitespace tokenizer 对中文和混合术语 query 部分失效

**触发场景**  
Day 73 verify_retrieve.py 输出显示: 3 个语义完全不同的中文 query ("学签怎么办" / "BC PNP 分数" / "父母团聚担保要求") 在 Config 1 (BM25 only) 下返回**完全一致的 3 个 doc**。追加英文 identifier query ("OINP") 测试, 返回正确的 OINP 相关 doc。

**Anti-pattern**: BM25Retriever.from_documents 默认 tokenizer 按空白/标点切分:
- 纯英文 identifier (OINP, IRCC): ✅ 工作正常
- 混合术语 (BC PNP): ⚠️ 依赖 KB 术语拼写一致性, 拼写不统一时命中率低  
- 纯中文 query (学签怎么办): ❌ 整个 query 变 1 个 token, 除非 doc 逐字含该子串否则 score 为 0

**为什么是问题**: 生产 KB 中文为主, BM25 对约 90% query silent failure, 排序退化成插入顺序返回 corpus 前 N 个 doc。生产表现 OK 因为 rerank 层兜底, 但 ablation 数字里 Config 1 接近随机基线。**这是 silent failure —— 没有 alarm, 只有做 ablation 才发现**。

**当前状态**: 不修。生产依赖 dense + rerank two-stage, BM25 结果被 rerank 打分低刷掉。

**下次触发前的自检问题**  
1. 我用的第三方库默认配置是不是为我的场景优化的? tokenizer / analyzer 类的配置默认往往是英文 assumption。
2. 系统的 "hybrid" / "ensemble" 声明背后, 每一路是不是都在真正 contribute? 有没有做过独立 ablation?

**长期修复 (Day 74+)**: 两条路径任选或并行
1. jieba 中文分词: `BM25Retriever.from_documents(..., preprocess_func=jieba_tokenize)`
2. KB 术语标准化: 建立术语表, ingest 时统一拼写 (BC PNP / BC省提名 / BC Provincial Nominee → 统一)

**Interview articulation**: "Ablation 暴露 BM25 tokenizer 对中文 silent failure, 生产实际靠 dense + rerank two-stage. 修复归为 tech debt, 因为 8 月投递前引入新变量会破坏 evaluation attribution."
