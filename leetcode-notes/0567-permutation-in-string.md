# Permutation In String (Medium)

**Pattern**: Sliding Window (fixed size)
**日期**: 2026-07-23 (Day 65)
**独立/视频/答案**: 视频(NeetCode)
**下次重做日期**: 2026-07-26(3 天后)

## 题目

给两个字符串 `s1` 和 `s2`,判断 `s2` 是否包含 `s1` 的任意 permutation。也就是说,`s2` 中是否存在一个子串,是 `s1` 的字符重排。

Example: s1 = "ab", s2 = "eidbaooo" → True("ba" 在 s2 里)

## 解法思路

固定长度的 sliding window,窗口大小 = `len(s1)`。

用两个 26 位的数组分别记录 s1 和当前窗口的字符频率。如果两个数组完全相等,说明当前窗口是 s1 的 permutation。

**优化**:不需要每次都比较整个 26 位数组。维护一个 `matches` 计数,记录有多少个字符位置上两个数组相等。当 matches == 26 时,找到答案。

## 代码

```python
def checkInclusion(s1: str, s2: str) -> bool:
    if len(s1) > len(s2):
        return False

    s1_count = [0] * 26
    s2_count = [0] * 26

    for i in range(len(s1)):
        s1_count[ord(s1[i]) - ord('a')] += 1
        s2_count[ord(s2[i]) - ord('a')] += 1

    matches = sum(1 for i in range(26) if s1_count[i] == s2_count[i])

    left = 0
    for right in range(len(s1), len(s2)):
        if matches == 26:
            return True

        # 加入新字符
        idx = ord(s2[right]) - ord('a')
        s2_count[idx] += 1
        if s2_count[idx] == s1_count[idx]:
            matches += 1
        elif s2_count[idx] == s1_count[idx] + 1:
            matches -= 1

        # 移除左边字符
        idx = ord(s2[left]) - ord('a')
        s2_count[idx] -= 1
        if s2_count[idx] == s1_count[idx]:
            matches += 1
        elif s2_count[idx] == s1_count[idx] - 1:
            matches -= 1

        left += 1

    return matches == 26
```

## 复杂度

- Time: O(n),n = len(s2)。26 是常数
- Space: O(26) = O(1)

## 踩坑 / 关键点

1. **matches 增量维护是精髓**:朴素做法是每次窗口滑动都 O(26) 比较两个数组,总时间 O(26n)。用 matches 增量维护后,每次窗口滑动只更新 2 个位置的 matches(加入的字符 + 移除的字符),总时间 O(n) + O(26) 初始化。

2. **matches 更新逻辑**:每次一个字符的频率变化时,判断 3 种情况:
   - 变化前不等 → 变化后相等:matches +1
   - 变化前相等 → 变化后不等:matches -1
   - 其他:matches 不变
   代码里只需要 check "变化后是否恰好等于目标"(matches +1)和"变化后是否恰好比目标多/少 1"(说明变化前是相等的,现在破坏了 → matches -1)。

3. **循环内先 check matches == 26 再滑窗口**:这样保证最后一个窗口也能被 check(否则会漏掉 s1 == s2 的边界情况)。