# Bug 1 UI Root Cause - Day 86 Fix

## Symptom (Day 85 curl output)
Backend `/ask` on "你好" returns:
{
  "answer": "你好! 我是移民咨询助手, 有什么可以帮你?",
  "sources": ["收费模版 - 服务费用", "收费模版 - 社交运营",
              "OINP 硕士第3阶段"],
  "links": []
}

Frontend displays sources → user sees irrelevant citations
on chit-chat.

## Two-field architecture
- `links` (empty ✅) — LLM cited_link_ids → deterministic URL
- `sources` (broken ❌) — retriever top-k titles

## Architecture decision needed (Day 86 morning)

Option 1: sources 完全绑 links
  chit-chat 时 sources 也为空
  Pro: 语义一致
  Con: 破坏"透明检索"debug 能力

Option 2: sources 保留 top-k,frontend gate
  Frontend: if links == []: hide sources section
  Pro: backend 不动
  Con: sources 语义仍然含糊

Option 3: 引入 branch metadata
  返回增加 "branch": "A" | "B" | "C1" | "C2" | "D"
  Frontend 根据 branch 决定显示
  Pro: 与 5-branch prompt rule 对齐
  Con: 工程量大

## Recommendation (待 Day 86 早晨确认)
倾向 Option 3 — 与已有 5-branch 架构对齐,
未来 debug + evaluation 都需要 branch tag。