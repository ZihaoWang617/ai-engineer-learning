## [#242] Valid Anagram [Easy] 🟢
- Pattern: Arrays & Hashing / Frequency counting
- Link: https://leetcode.com/problems/valid-anagram/
- Status: 独立做出（修了 5 个 bug 之后通过）
- Time spent: ~25 min

### Insight
"是否 anagram" = "字符组成相同？"
不能用 set（丢失 frequency），必须用 dict 记每个字符出现次数。
两个 dict 相等 ⟺ 两字符串 anagram。

### Solution 1: Frequency Hashmap (Optimal)
\`\`\`python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        a, b = {}, {}
        for char in s:
            if char not in a:
                a[char] = 1
            else:
                a[char] += 1
        for char in t:
            if char not in b:
                b[char] = 1
            else:
                b[char] += 1
        return a == b
\`\`\`
- Time: O(n + m)，两个顺序 loop
- Space: O(1)，dict 受 alphabet (26) 上限封顶，independent of input length

### Solution 2: Sort
\`\`\`python
return sorted(s) == sorted(t)
\`\`\`
- Time: O(n log n)，sort 代价
- Space: O(n)，sorted 返回新 list
- 面试 trade-off：代码短但更慢，space 也更糟

### Pythonic note
`a[char] = a.get(char, 0) + 1` 一行替代 if/else 判断——
`dict.get(key, default)` 在 key 不存在时返回 default，是 frequency counting 的 idiom。

### 踩过的坑
- `for s in s:` 变量遮蔽（循环变量与 input 同名）
- 混淆 dict 和 set：dict 没有 `.add()`，用 `a[key] = value`
- 语法：dict 索引用方括号，不是花括号或圆括号
- Redundant conditional：`if a == b: return True else: return False` → `return a == b`

### Related Problems
- #217 Contains Duplicate（set 解法，frequency 简化版）
- #1 Two Sum（complement hashmap）
- #49 Group Anagrams（anagram + grouping）
- #383 Ransom Note（frequency 比较的简单变体）

### 复习日期: 2026/05/26