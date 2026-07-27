# Longest Repeating Character Replacement (Medium)

**Pattern**: Sliding Window
**日期**: 2026-07-23 (Day 65)
**独立/视频/答案**: 视频(NeetCode)
**下次重做日期**: 2026-07-26(3 天后)

## 题目

给一个字符串 `s` 和一个整数 `k`,你可以把字符串中任意 `k` 个字符替换成任意其他字符。问替换之后,最长的**由同一个字符组成的连续子串**长度是多少。

Example: s = "AABABBA", k = 1 → 输出 4(把中间那个 B 换成 A,得到 "AABABBA" → "AAAABBA" 中的 "AAAA")

## 解法思路

Sliding window + 记录窗口内出现最多的字符的频率。

关键洞察:窗口合法的条件是 `window_length - max_frequency <= k`。也就是说,窗口内除了"最多的那个字符",其他字符的数量之和 ≤ k(这些"其他字符"都可以被替换)。

**窗口伸缩逻辑**:
- 每次 right 右移,更新频率表,更新 max_freq
- 如果 `(right - left + 1) - max_freq > k`,left 右移,更新频率表
- 记录 `max_length = max(max_length, right - left + 1)`

## 代码

```python
def characterReplacement(s: str, k: int) -> int:
    count = {}
    max_freq = 0
    left = 0
    max_length = 0

    for right in range(len(s)):
        count[s[right]] = count.get(s[right], 0) + 1
        max_freq = max(max_freq, count[s[right]])

        if (right - left + 1) - max_freq > k:
            count[s[left]] -= 1
            left += 1

        max_length = max(max_length, right - left + 1)

    return max_length
```

## 复杂度

- Time: O(n)
- Space: O(26) = O(1)(只处理大写字母)

## 踩坑 / 关键点

1. **max_freq 不需要重新计算**:即使 left 右移,窗口内 max_freq 可能变小,但**答案不受影响**。原因:max_length 只在窗口"合法"时更新,而窗口收缩到合法后,max_freq 就算是"过时"的,也只会让 max_length 偏保守,不会让答案变大。写代码时不需要维护 max_freq 精确值。

2. **为什么用 if 不用 while**:每次 right 右移最多增加 1,所以 left 每次最多右移 1 次窗口就重新合法。用 while 也对,但 if 更简洁且更快。