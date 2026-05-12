## [#1] Two Sum [Easy] 🟢
- Pattern: Arrays & Hashing / Complement lookup
- Link: https://leetcode.com/problems/two-sum/
- Status: 独立做出（修了 3 个 bug 后通过）
- Time spent: ~30 min

### Insight
"找两数之和 = target" 转化成 "对每个 num，complement = target - num 是否之前出现过"。
一边遍历一边记录 `{数: 它的 index}` 进 dict，查 complement 是否在 dict 里即可。
把"找 pair" 转成 "single lookup"，从 O(n²) 降到 O(n)。

### Solution: Complement Hashmap (Optimal)
\`\`\`python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i in range(len(nums)):
            complement = target - nums[i]
            if complement in seen:
                return [seen[complement], i]
            seen[nums[i]] = i
\`\`\`
- Time: O(n) — single pass through nums, each inner operation is O(1) including dict membership check & insertion due to hashmap's average-case lookup
- Space: O(n) — unlike #242 where alphabet capped hashmap at 26 entries giving O(1), here integers aren't bounded by a small constant (constraint -10^9 to 10^9), so hashmap grows proportional to input size in worst case

### Alternative Approach: Sort + Two Pointers
\`\`\`python
# 需要保留原 index：sort tuples
indexed = sorted(enumerate(nums), key=lambda x: x[1])
left, right = 0, len(nums) - 1
while left < right:
    s = indexed[left][1] + indexed[right][1]
    if s == target:
        return sorted([indexed[left][0], indexed[right][0]])
    elif s < target:
        left += 1
    else:
        right -= 1
\`\`\`
- Time: O(n log n) — sort dominates
- Space: O(n) — for the indexed tuples
- 面试 trade-off：比 hashmap 慢，但对 #167 (sorted input given) 是最优解；用在 #1 是因为本身需要 sort

### Pythonic note
`for i, num in enumerate(nums)` 比 `for i in range(len(nums)): nums[i]` 更 Pythonic——
同时拿到 index 和 value，不用每次写 `nums[i]`。重构版本：
\`\`\`python
for i, num in enumerate(nums):
    complement = target - num
    if complement in seen:
        return [seen[complement], i]
    seen[num] = i
\`\`\`

### 踩过的坑
- **先查再存的顺序至关重要**：`[3, 3], target=6` 的 case 只有"先查后存"才不会用同一个元素两次（i=0 时 seen 为空，不会把第一个 3 误算作 complement；i=1 时 seen={3:0}，查到匹配返回 [0, 1]）。先存后查会返回 [0, 0]，违反 constraint。
- **`elif` 不能中间夹语句**：`if ... ; complement = ... ; elif ...` 是 SyntaxError，`elif` 必须紧跟 `if` 块。
- **`for i in range(len(nums))` 模式下变量名混淆**：循环里没有 `num`，只有 `i` 和 `nums[i]`。一开始误写 `seen[num] = i`，NameError。
- **#1 vs #167 混淆**：#1 是 unsorted input，#167 是 pre-sorted input。一开始想用 sort + two pointers 解 #1，会破坏原 index 信息——题目要求返回 indices，不是 values。Hashmap 是正解。

### Related Problems
- #217 Contains Duplicate（set 解法，frequency 简化版）
- #242 Valid Anagram（frequency dict 比较）
- #167 Two Sum II - Sorted Array（two pointers 标准解法）
- #15 3Sum（two sum 扩展，sort + two pointers）
- #167 在 NeetCode 顺序里在 Two Pointers 类别，#1 在 Arrays & Hashing 类别

### 复习日期: 2026/05/26