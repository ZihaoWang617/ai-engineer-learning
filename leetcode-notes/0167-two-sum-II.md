## [#167] Two Sum II - Input Array Is Sorted 🟡

- **Pattern**: Two Pointers
- **Link**: https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/
- **Status**: 思路独立想到，写法看视频确认
- **Time spent**: ~20 min

### Insight

给一个 **已排序** 的数组和一个 target，找到两个数的下标使它们的和等于 target。返回 1-indexed 下标。

核心 insight：**sorted 这个 constraint 是关键信号**——立刻应该想到 two pointers，不是 hashmap。

为什么 two pointers 在 sorted array 上 work：从两端开始计算 `nums[l] + nums[r]`，
- 如果 sum > target → 当前 right 值太大 → `r -= 1`（往小的方向移）
- 如果 sum < target → 当前 left 值太小 → `l += 1`（往大的方向移）
- 相等 → 找到答案

**为什么不会漏解**：每次移动指针都在排除"不可能是答案"的组合——right 太大时，所有 left 配它都太大；left 太小时，所有 right 配它都太小。**单调性**保证 O(n) 找到唯一解。

Trade-off：
- Two Pointers: O(n) time / O(1) space —— 利用了 sorted 的额外信息
- Hashmap（同 LC #1 Two Sum）: O(n) time / O(n) space —— 不需要 sorted 但费 space
- Brute force: O(n²) —— 完全不利用 sorted

面试 talking point：**"题目给你 sorted 这个 hint，就是在暗示你用 O(1) space 解法。如果数组不 sorted，hashmap 更优。"**

### Solution: Two Pointers

```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        l, r = 0, len(numbers) - 1
        while l < r:
            curSum = numbers[l] + numbers[r]
            if curSum > target:
                r -= 1
            elif curSum < target:
                l += 1
            else:
                return [l + 1, r + 1]
        return []
```

- **Time**: O(n) — 两个指针总共最多扫过 array 一次，每个元素被访问 O(1) 次
- **Space**: O(1) — 只用两个指针变量，没创建新数据结构

### Alternative Approach: Hashmap (for unsorted version, LC #1)

```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(numbers):
            complement = target - num
            if complement in seen:
                return [seen[complement] + 1, i + 1]
            seen[num] = i
        return []
```

- **Time**: O(n)
- **Space**: O(n)
- **Trade-off vs main solution**: 不需要 sorted（更通用），但 space O(n)。**这里有 sorted 信息却用 hashmap = 浪费 input 的额外结构**。面试时主答用 two pointers，可以提一句"如果数组没排序我会用 hashmap"。

### Pythonic Note

- **`return [l + 1, r + 1]`** —— 题目要求 1-indexed。Python 习惯 0-indexed，**写题前先 reread 题目对 index 的要求**，避免 off-by-one。
- **不需要 helper function**——逻辑全在主循环里，简洁。
- **`while l < r`** 而不是 `while l <= r`——相等时两个指针指同一个元素，不能用同一个数加自己（题目要求两个不同 index）。

### 踩过的坑

- **第一版没写 `else`，在 `l += 1` 下面直接 return**:
```python
  # 错误版本
  if curSum > target:
      r -= 1
  elif curSum < target:
      l += 1
      return [l + 1, r + 1]   # ← 这行错位置了！
```
  这样写的话，**只要 `curSum < target` 就 return**，但当时根本没找到答案（只是 left 移动了一步）。
  Root cause：**控制流分支搞混**——`elif curSum < target` 是"还没到答案，继续找"的分支，return 应该是"找到答案"的分支（也就是 `else: curSum == target`）。
  Mitigation：**写 if/elif/else 时显式问自己"这个分支语义是什么"**。这里三个分支：
  - `> target`：太大 → 缩小 right
  - `< target`：太小 → 扩大 left
  - `== target`（else）：找到 → return
  
  写完检查每个分支的语义和它的 action 是否对应。

- **`while l < r` 不是 `l <= r`**:
  这次没踩，但是个常见陷阱。`l == r` 时两个指针指向同一元素，违反"两个不同 index"。

### Related Problems

- #1 Two Sum（unsorted 版本，必须用 hashmap）
- #15 3Sum（套娃：sort 后固定一个数，剩下变 Two Sum II）
- #11 Container With Most Water（Two Pointers 但 update 规则不一样：移动较短的边）
- #125 Valid Palindrome（前一题，Two Pointers 入门）

### Interview-Ready Phrasing

> "Since the array is sorted, I can use two pointers starting from both ends. I compute the sum at each step: if it's greater than the target, I move the right pointer left to decrease the sum; if it's less than the target, I move the left pointer right to increase it; if equal, I return the indices. This works in O(n) time and O(1) space. The sorted property is what makes two pointers optimal here—if the array weren't sorted, I'd use a hashmap for O(n) time with O(n) space."

### 复习日期

- **First review (2 weeks)**: 2026/06/03
- **Second review (1 month)**: 2026/06/20
- **Third review (3 months)**: 2026/08/20