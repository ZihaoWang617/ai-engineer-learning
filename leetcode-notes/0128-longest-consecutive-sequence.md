## [#128] Longest Consecutive Sequence [Medium] 🟡

- **Pattern**: Arrays & Hashing
- **Link**: https://leetcode.com/problems/longest-consecutive-sequence/
- **Status**: 看视频做出（25 min 自想未果 → NeetCode Tim 视频 → 自己 retype + TLE debug）
- **Time spent**: ~?? min（你填实际数字，包括 debug TLE 时间）

### Insight
我一开始以为这题要 sort,然后我看了视频我们可以直接用set找出list里所有的数然后找所有数的n-1是否存在set里，如果不在就说明这个数字是一个consecutive的开头，那就开始iteration，然后我们每次都检查一个数的n-1就可以得到所有连续数组，然后找最长的就行。
### Solution: Hash Set + Sequence Start Detection
​```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        numSet = set(nums)
        longest = 0

        for n in numSet:   # ⚠️ 必须 iterate numSet 不是 nums，否则 TLE
            if (n - 1) not in numSet:   # n 是 sequence start
                length = 0
                while (n + length) in numSet:
                    length += 1
                longest = max(longest, length)
        return longest
​```
- **Time**: O(n) amortized——outer O(n)，inner while 只在 sequence start 触发；每个 element 全程最多 visit 2 次（外层 1 + 内层 1）
- **Space**: O(n) for hash set

### Alternative Approach: Sort + Linear Scan
​```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums: return 0
        nums.sort()
        longest = current = 1
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1]: continue           # skip dup
            elif nums[i] == nums[i-1] + 1: current += 1
            else: current = 1
            longest = max(longest, current)
        return longest
​```
- **Time**: O(n log n)
- **Space**: O(1) extra (in-place sort) or O(n) if input immutable
- **Trade-off vs main**: 时间慢但空间省 + 实现更直观。面试问 "what if memory constrained?" 时这是答案。

### Pythonic Note

- `set(nums)` 一行构造 hash set，O(n) + 自动去重
- `in` 操作对 **set/dict 是 O(1)**，对 **list/tuple 是 O(n)**——本算法的 O(n) 全程依赖这个差别。**面试问 "why hash set not list" 这一句话就是 answer**

### 踩过的坑

- **TLE: iterate `nums` 而不是 `numSet`**: 抄视频时写成 `for n in nums`，85 testcases 过 81。原因：**用nums会有很多重复的数字，这样会导致超时, k 个 sequence start 的 duplicates 各跑一遍 inner while → total work k × n → O(n²)"**
- **Complexity 混淆: sum vs product**: 被 mentor probe "删掉 if 行复杂度变什么"，答 O(n!)，错。正确推导：**[公式是1+2+3+。。。+n,推导出来是n（n+1)/2 就是n^2 ]**

### Interview-Ready Phrasing
> [TBD — 明早 fresh 状态写]
### Related Problems
<!-- 候选（verify 这些 association 对你 make sense，否则替换）：-->

- #1 Two Sum（关联：hash 实现 O(1) lookup 的同一 idiom）
- #217 Contains Duplicate（关联：set membership check 基础形）
- #49 Group Anagrams（关联：用 dict 做分组的 Arrays & Hashing 经典 pattern）

### 复习日期
- **First review (2 weeks)**: 2026/06/02
- **Second review (1 month)**: 2026/06/19
- **Third review (3 months)**: 2026/08/19