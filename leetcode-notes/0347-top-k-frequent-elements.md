## [#0347] [Top K Frequent Elements] [Medium] 🟡
- **Pattern**: [Arrays & Hashing / Bucket Sort]
- **Link**: https://leetcode.com/problems/top-k-frequent-elements/description/
- **Status**: 看视频
- **Time spent**: ~35 min（含 25 min 独立思考 + 视频 + 复现 + follow-up 讨论）

### Insight
**核心 insight**：`frequency` 在这道题里**被天然 bound 在 [1, len(nums)]** —— 这意味着可以用 **frequency 当 array 的 index**，把"按频率排序"变成"按 index 顺序遍历"，O(n log n) → O(n)。

具体设计：
- `count` dict 记每个数字的频率
- `freq` 是一个数组，**`freq[i]` 存"出现 i 次的数字们"**（list，因为可能多个数字同频率）
- 从高 frequency index 往低 iterate，收集到 k 个就停

**关键 mental model**：用 array（不是 dict）当 buckets，因为 array 的 index 天然有序——iterate 不需要排序。这是 bucket sort 比 sort/heap 快的根本原因。

### Solution: Bucket Sort
```python
class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = {}
        freq = [[] for i in range(len(nums) + 1)]

        for n in nums:
            count[n] = 1 + count.get(n, 0)
        for key, value in count.items():
            freq[value].append(key)
        result = []
        for i in range(len(freq) - 1, 0, -1):
            for n in freq[i]:
                result.append(n)
                if len(result) == k:
                    return result
```
- **Time**: O(n) — counting O(n) + bucket 填充 O(unique) + outer loop O(n)，总 O(n)
- **Space**: O(n) — count dict + freq array（最坏情况 n+1 slots）

### 对比其他解法
| 方法 | 复杂度 | 适用场景 |
|---|---|---|
| `sorted(count.items(), key=lambda x: -x[1])[:k]` | O(n log n) | 代码最短，n 不大时可接受 |
| `heapq.nlargest(k, count.keys(), key=count.get)` | O(n log k) | streaming / k << n 时好 |
| Bucket sort（本解） | O(n) | 最优，但需要 frequency bound 已知 |

**面试 follow-up**：如果是 streaming 数据，nums 不断进来怎么实时维护 top k？→ 用 **min-heap of size k**（不能 bucket sort，因为长度未知）。

### Pythonic Notes
- `count[n] = 1 + count.get(n, 0)` —— 不用 defaultdict 也能避免 KeyError 的 idiom
- `[[] for i in range(N)]` —— 创建 N 个独立空 list 的标准写法（不能写 `[[]] * N`，那样所有引用同一个 list）
- `range(start, stop, step)` 负步长：`range(len(freq)-1, 0, -1)` 从高到低
- **`len()` 返回元素数量本身，不减 1**：N 个元素 → index 0 到 N-1
- **要让 `array[i]` 能访问，array 必须有 i+1 个 slot**：所以 `range(len(nums) + 1)` 是为了让 `freq[len(nums)]` 这种最大频率的情况可访问

### 踩过的坑
1. **拼错 `mums`**（应 `nums`）—— LeetCode 不会报参数名错，会报 NameError，得自己看
2. **`result.sort()`** —— dict **没有** `.sort()` 方法，list 才有
3. **`result[:k]`** —— dict 不支持 slicing
4. **初版 `if len(result) == k` 在 outer loop level** —— 如果一个 bucket 有多个元素（同频率），inner loop 会全部 append 完才 check，可能 overshoot 然后 fallthrough。**Fix**：把 `if` 移到 inner loop 内，append 一个就 check 一个
5. **概念 misconception：以为 `len(nums)` 比实际数量少 1** —— 错。len 永远返回真实数量。Python 从 0 开始的是 **index**，不是 len 返回值

### 复习日期
- **First review (2 weeks)**: 2026/5/27
- **Second review (1 month)**: 2026/6/13
- **Pre-interview review**: 投递期间（7 月中下旬）

### 同类题（Arrays & Hashing / Bucket Sort）
- #49 Group Anagrams（hashmap with frequency tuple key，已做）
- #1 Two Sum（hashmap，已做）
- #128 Longest Consecutive Sequence（bucket sort 思路变体）
- #451 Sort Characters By Frequency（同 bucket sort）