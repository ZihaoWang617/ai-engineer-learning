## [#217] Contains Duplicate [Easy] 🟢
- Pattern: Arrays & Hashing
- Link: https://leetcode.com/problems/contains-duplicate/
- Status: 独立做出（O(n²) TLE 后优化到 O(n)）
- Time spent: ~30 min

### Insight
判断"有没有重复" = 判断"之前见过没"。
用 set 的 O(1) 查找把整体复杂度从 O(n²) 降到 O(n)。
经典的 time-space trade-off：多用 O(n) 空间，换取时间从 n² 到 n。

### Solution 1: Brute Force (TLE)
```python
class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        for i in range(len(nums)):
            for j in range(i+1, len(nums)):
                if nums[i] == nums[j]:
                    return True
        return False
```
- Time: O(n²), Space: O(1)
- TLE on large inputs (n ~ 10^5)

### Solution 2: Hashset (Optimal)
```python
class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False
```
- Time: O(n), Space: O(n)

### Pythonic note
`for num in nums` 优于 `for i in range(len(nums)): nums[i]`——
直接遍历元素，不需要索引时不要用 range(len(...))。

### 复习日期: 2026/05/25