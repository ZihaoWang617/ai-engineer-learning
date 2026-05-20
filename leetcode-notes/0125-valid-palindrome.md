## [#125] Valid Palindrome 🟢

- **Pattern**: Two Pointers
- **Link**: https://leetcode.com/problems/valid-palindrome/
- **Status**: 独立做出（最后 typo 一处：`r+1` 应为 `r-1`）
- **Time spent**: ~15 min

### Insight

判断一个字符串去掉非字母数字字符、忽略大小写后，是不是回文。

核心 insight：**回文判断 = 两端往中间对比**。不需要先清洗字符串再判断（O(n) 额外空间），而是用两个指针从两头向中间走，**遇到非字母数字直接跳过**，遇到字母数字就比较 lower case 是否相等。这样只用 O(1) 额外空间。

主要 trade-off：直接清洗 + 反转比较是 O(n) time + O(n) space，写法更短；two pointers 同样 O(n) time 但 O(1) space。面试官期待 two pointers 这版——space optimal 是这道题的考察点。

### Solution: Two Pointers

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        l, r = 0, len(s) - 1
        while l < r:
            while l < r and not self.alphanum(s[l]):
                l += 1
            while r > l and not self.alphanum(s[r]):
                r -= 1
            if s[l].lower() != s[r].lower():
                return False
            l, r = l + 1, r - 1
        return True

    def alphanum(self, c):
        return (ord('A') <= ord(c) <= ord('Z') or
                ord('a') <= ord(c) <= ord('z') or
                ord('0') <= ord(c) <= ord('9'))
```

- **Time**: O(n) — 两个指针总共最多扫过整个 string 一次，每个字符被访问 O(1) 次
- **Space**: O(1) — 只用了两个指针变量，没有创建新数据结构。注意：如果先 `s = "".join(c.lower() for c in s if c.isalnum())` 清洗再判断，会变成 O(n) space

### Alternative Approach: Clean + Reverse Compare

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        cleaned = "".join(c.lower() for c in s if c.isalnum())
        return cleaned == cleaned[::-1]
```

- **Time**: O(n)
- **Space**: O(n) — 创建了 cleaned string 和它的 reverse
- **Trade-off vs main solution**: 代码更短易读，但 space 变 O(n)。面试可以提一句"也可以这样写但 space 不 optimal"，主答案用 two pointers。

### Pythonic Note

- **`c.isalnum()`** 是 Python 内置方法，直接判断字符是否字母或数字（含 unicode），生产代码首选；面试时先问 "能用 isalnum 吗"，能用就用，不能就手写 ord 范围判断（如本题 main solution 的 helper）。
- **`s[::-1]`** 是 string reverse 的 idiom，比 `reversed(s)` + `"".join` 更简洁。
- **Multiple assignment**: `l, r = l + 1, r - 1` 一行同时更新两个指针——right-hand side 先全部 evaluate 再赋值，所以不会有先后顺序 bug。

### 踩过的坑

- **Typo: `r + 1` 应为 `r - 1`**:
  最后一行写成 `l, r = l + 1, r + 1`，让 right pointer 反方向走，会立刻越界 / 死循环。
  Root cause：写 `l + 1` 之后大脑 autocomplete 复制了 `+ 1`，没切换符号。
  Mitigation：**双指针题写到指针更新时强制停 2 秒，确认 l 加 r 减方向相反**。
- **Inner while 边界容易漏 `l < r`**:
  跳过非字母数字时，如果整个字符串都是 punctuation（如 `".,!"`），不加 `l < r` 边界 inner while 会越界。Two pointers 的 inner skip loop **永远要带外层边界条件**。

### Related Problems

- #167 Two Sum II - Input Array Is Sorted（Two Pointers 套路：sorted array 从两端逼近 target）
- #344 Reverse String（Two Pointers 最入门版，swap 而非比较）
- #680 Valid Palindrome II（进阶：允许删除一个字符，依然 Two Pointers + 分支判断）
- #5 Longest Palindromic Substring（扩展：从中心向外扩展 = Two Pointers 反向应用）

### Interview-Ready Phrasing

> "I'd use two pointers starting from both ends of the string, moving inward. At each step I skip over any non-alphanumeric characters by advancing the corresponding pointer, then compare the lowercased characters at both pointers. If they ever differ, return false; otherwise continue until the pointers meet. This runs in O(n) time since each character is visited at most once, and O(1) extra space because we don't build any new string. The alternative of cleaning the string first and comparing it to its reverse also works in O(n) time but costs O(n) space, so two pointers is preferred when space matters."

### 复习日期

- **First review (2 weeks)**: 2026/06/03
- **Second review (1 month)**: 2026/06/20
- **Third review (3 months)**: 2026/08/20