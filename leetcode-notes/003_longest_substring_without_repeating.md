## #3 Longest Substring Without Repeating Characters Medium 🟡

- **Pattern**: Sliding Window
- **Link**: https://leetcode.com/problems/longest-substring-without-repeating-characters/
- **Status**: 看答案 + NeetCode 混合后 AC (Status D)
- **Time spent**: ~20 min

### Insight

这道题是找:在一串字符里,找一段最长的连续片段,这段里每个字符只出现一次。
比如 "abcabcbb" 里最长的就是 "abc",长度 3。

暴力解法是 O(n³):n 个起点 × n 个终点 × 每段扫一遍查重 n。慢的原因是,
不同起点之间重复扫了大量相同字符。

关键 insight:用一个"窗口"(left 和 right 两个指针圈出来的一段)
和一个 set(装窗口内所有字符)来避免重复扫描。窗口从左往右滑:
- 新字符不重复 → 直接加进 set,右边界 right 前进
- 新字符已经在 set 里 → 说明窗口里有冲突,把左边字符一个一个踢出 set
  并让 left 前进,**直到**冲突字符被踢出去为止(所以用 while 不是 if,
  因为不知道要踢几个)

每次窗口合法时,用 right - left + 1 更新历史最大长度。整个过程 left 和
right 各走一遍 s,总共 2n,所以是 O(n)。

我犯过的关键错误:一开始想用 1 个变量 res 同时记 "当前窗口长度" 和
"历史最长长度",遇到重复字符就 reset res=1。这样每次重复都丢失了历史
最优。**必须用 2 个独立变量**:一个记当前窗口大小,一个记历史最大值。
### Solution: Sliding Window with Set

\`\`\`python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        charSet = set()
        l = 0
        res = 0
        for r in range(len(s)):
            while s[r] in charSet:
                charSet.remove(s[l])
                l += 1
            charSet.add(s[r])
            res = max(res, r - l + 1)
        return res
\`\`\`

- **Time**: O(n) — right 指针从左到右走一遍 n,left 指针最多也走 n 次,
  加起来最多 2n 次操作,所以是 O(n) 不是 O(n²)。
- **Space**: O(min(n, 字符集大小)) — set 里最多装窗口内不重复字符,
  英文字符上限 26,ASCII 上限 128。如果字符串本身比字符集小,
  set 最多装 n 个。所以取较小值。
### Alternative Approach: Sliding Window with Dict (char → last_index)

\`\`\`python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        char_idx = {}
        l = 0
        res = 0
        for r, c in enumerate(s):
            if c in char_idx and char_idx[c] >= l:
                l = char_idx[c] + 1
            char_idx[c] = r
            res = max(res, r - l + 1)
        return res
\`\`\`

- **Time**: O(n)
- **Space**: O(min(n, 字符集大小))
- **Trade-off vs main solution**: Set 版本遇到重复字符时 left 一步一步往右移;
  dict 版本记住每个字符上次出现的位置,可以直接跳过去,**省掉若干次循环**。
  但两者总复杂度都是 O(n)。
### Pythonic Note

[你填:这次题里你用到的 Python 特性。例如:`set()` 的 `in` 操作是 O(1) 而不是 list 的 O(n)。还有 `range(len(s))` 这种写法和 `enumerate(s)` 哪个更 Pythonic?]

### 踩过的坑

- **变量职责混淆**: 一开始想用 1 个 res 变量同时表达 "当前窗口长度" 和
  "历史最长",这等于把两个独立的状态压缩成一个,遇到重复字符 reset 时
  历史最优就丢了。教训:**任何"找极值"的题都至少有 2 个状态变量,
  当前状态 ≠ 历史最优。**

- **暴力复杂度算错**: 一开始以为 brute force 是 O(n!),实际是 O(n³)。
  记住四个常见复杂度的语义:n² = 两层循环 / n³ = 三层循环 / 2ⁿ = 子集
  / n! = 全排列。

- **学习方法的坑**: Status D 意味着 2 周后重做时大概率不记得。要靠
  spaced repetition + 真正自己写笔记弥补。
### Related Problems

- #424 Longest Repeating Character Replacement(关联点:同样 sliding window + 收缩条件不同)
- #76 Minimum Window Substring(关联点:sliding window 找最短而非最长,同样要维护窗口状态)
- #567 Permutation in String(关联点:固定大小窗口 + 字符 frequency)

### Interview-Ready Phrasing

[你填 — 用英文写一段 3-5 句的解释,**自己写**,不准翻译我上面的 Insight。
就当面试官问 "Can you walk me through your solution?",你怎么口头讲]

### 复习日期

- **First review (2 weeks)**: 2026/06/14
- **Second review (1 month)**: 2026/06/30
- **Third review (3 months)**: 2026/08/31