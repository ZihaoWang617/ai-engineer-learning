# 76. Minimum Window Substring

**Difficulty**: Hard
**Pattern**: Sliding Window
**Date**: 2026-08-14 (Day 74)
**Independence**: video-assisted
**Time**: 30 min

---

## Insight

双 counter + 右扩到 have==need + while 左缩到条件破坏 = 最小窗口。

`have/need` 用两个 int 追踪"满足的字符类别数"，避免每步做 O(k) 字典比较。

---

## Solution

```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if t == "": return ""
        
        countT, window = {}, {}
        for c in t:
            countT[c] = 1 + countT.get(c, 0)
        
        have, need = 0, len(countT)
        res, resLen = [-1, -1], float("infinity")
        l = 0
        
        for r in range(len(s)):
            c = s[r]
            window[c] = 1 + window.get(c, 0)
            
            # 只在"恰好达标"那一刻 +1, 避免重复计数
            if c in countT and window[c] == countT[c]:
                have += 1
            
            # while: 缩到条件破坏为止, 才能得到最小窗口
            while have == need:
                if (r - l + 1) < resLen:
                    res = [l, r]
                    resLen = r - l + 1
                
                window[s[l]] -= 1
                if s[l] in countT and window[s[l]] < countT[s[l]]:
                    have -= 1
                l += 1
        
        l, r = res
        return s[l:r+1] if resLen != float("infinity") else ""
```

---

## Complexity

- **Time**: O(|s| + |t|) — 每个字符最多进出 window 一次
- **Space**: O(|s| + |t|) — 两个字典

---

## Mistakes / Confusions

1. **Q2 while vs if 没答清楚**: 说了 "recurring" 但没抓到关键——**缩到条件破坏才能得到最小窗口**, if 只缩一步会漏掉更小解. 例: s="AAABC" t="ABC", if 只缩到 "AABC", while 才能缩到 "ABC".

2. **Q1 O(1) vs O(k) 没意识到**: 用 have/need 两个 int 的真正理由是"每步比较 O(1)", 不是"字母顺序不一致". 面试官问 "为什么不直接 window == countT" 要答出复杂度差异.

3. **`== countT[c]` 而非 `>= countT[c]`**: 只在"恰好达标"那一刻 have +=1, 之后该字符再进 window 时 window[c] > countT[c] 条件不满足, 避免 have 被重复递增.

---

## Framework: Sliding Window "缩" 阶段通用骨架

```python
for r in range(n):
    # 1. 扩窗口 (右边加入 s[r])
    add(s[r])
    
    # 2. 收窗口 (while 条件成立就缩)
    while condition_satisfied():
        update_result()   # 每次缩之前 update
        remove(s[l])
        l += 1
```

所有 SW 题 (Longest Substring Without Repeating / Permutation in String / Sliding Window Maximum) 都是这个骨架, 只有 `condition_satisfied()` 和 `update_result()` 不同.

---

## Review Dates

- [ ] 2026-08-16 (+2 days)
- [ ] 2026-08-21 (+7 days)
- [ ] 2026-08-28 (+14 days)

Review 时: 遮住 Solution, 只看 Insight, 15 min 内独立重写. 卡住看 Framework 提示, 不看 Solution.