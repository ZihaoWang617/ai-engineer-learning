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