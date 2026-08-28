# 239. Sliding Window Maximum

**难度**: Hard
**Pattern**: Sliding Window + Monotonic Deque
**独立程度**: B
**日期**: 2026-08-26

## Insight

窗口内维护"可能成为未来最大值的候选下标"。当一个更大的数进来，前面所有比它小的数永远不可能再是最大值（因为它们比新来的小，且比新来的先出窗口），可以直接丢弃。

Monotonic decreasing deque 保证队首始终是当前窗口最大值。

## Solution

关键决策三个:
1. deque 存**下标**不存值 —— 因为要判断队首是否滑出窗口
2. 加入新元素时从队尾 pop 掉所有更小的下标（while 循环）
3. 每步检查队首是否过期（`dq[0] < i - k + 1`）

```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = collections.deque()
        result = []
        for i in range(len(nums)): 
            while dq and nums[i] > nums[dq[-1]]:
                dq.pop()
            dq.append(i)
            if dq and dq[0] < i - k + 1:
                dq.popleft()
            if i >= k - 1:
                result.append(nums[dq[0]])
        return result
```

## Complexity

- Time: **O(n)** — amortized，每个元素最多进 deque 一次、出 deque 一次
- Space: **O(k)** — deque 最多存 k 个下标

## Pythonic Notes

- `collections.deque` 而不是 list：`popleft()` 是 O(1)，`list.pop(0)` 是 O(n)
- deque 操作对照:
  - 看: `dq[0]` / `dq[-1]`
  - 删: `dq.popleft()` / `dq.pop()`
  - 加: `dq.appendleft(x)` / `dq.append(x)`

## Mistakes
- 一开始用 `dq[i]` 想取队尾（应该 `dq[-1]`）
- 一开始用 `if` pop 队尾（应该 `while`，一次可能 pop 多个）

## Review Dates

- 首次: 2026-08-26
- 3 天后: 2026-08-29
- 1 周后: 2026-09-02
- 2 周后: 2026-09-09

## Related Problems

- SW #1-3: 窗口维护 counts/hashmap，收缩条件是统计违反
- SW #4 (本题): 窗口大小固定，维护 monotonic deque
- 后续 monotonic stack 系列（Daily Temperatures 等）：同样的"淘汰前面更小/更大元素"思想