## [#42] Trapping Rain Water [🔴 Hard]

- **Pattern**: Two Pointers
- **Link**: https://leetcode.com/problems/trapping-rain-water/
- **Status**: 看 hint 做出
- **Time spent**: ~45 min

### Insight

题目要在不规则地形上算雨水积累。第一次脑子里的想法是"一行一行剥",从底层往上数,但跑出来是 O(n × max_h),max_h 到 10^5 时直接 TLE。

真正的 insight:**不要 think in rows, think in columns**。每个位置 i 头顶能存多少水,只取决于三个量:
- 左边见过的最高柱子 `leftmax[i]`
- 右边见过的最高柱子 `rightmax[i]`
- 它自己 `height[i]`

公式:`water[i] = min(leftmax[i], rightmax[i]) - height[i]`(水位线由两边矮的那面墙决定,柱子占的高度从水位减去)

主要 trade-off:**时间 vs 空间**。DP 版用两个数组预存 leftmax/rightmax,O(n) time + O(n) space。Two Pointers 版可以压到 O(1) space — 关键洞察是"较小的那侧 max 已经被对面的墙封住了水位",所以可以从两端向中间走、只追踪两个 running max。

### Solution: DP with prefix max arrays
```python
class Solution:
    def trap(self, height: List[int]) -> int:
        n = len(height)
        if n == 0:
            return 0
        leftmax = [0] * n
        rightmax = [0] * n
        
        leftmax[0] = height[0]
        for i in range(1, n):
            leftmax[i] = max(leftmax[i-1], height[i])
        
        rightmax[n-1] = height[n-1]
        for i in range(n-2, -1, -1):
            rightmax[i] = max(rightmax[i+1], height[i])
        
        total = 0
        for i in range(n):
            total += min(leftmax[i], rightmax[i]) - height[i]
        
        return total
```
- **Time**: O(n) — 三次顺序遍历,常数 3
- **Space**: O(n) — 两个长度为 n 的辅助数组

### Alternative Approach: Two Pointers (O(1) space)

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        if not height:
            return 0
        l, r = 0, len(height) - 1
        left_max, right_max = 0, 0
        total = 0
        
        while l < r:
            if height[l] < height[r]:
                if height[l] >= left_max:
                    left_max = height[l]
                else:
                    total += left_max - height[l]
                l += 1
            else:
                if height[r] >= right_max:
                    right_max = height[r]
                else:
                    total += right_max - height[r]
                r -= 1
        
        return total
```
- **Time**: O(n) — 单次双指针遍历
- **Space**: O(1) — 常数个变量
- **Trade-off vs main solution**: 空间从 O(n) 降到 O(1),但思路更难一次想出来。面试 follow-up 经典升级题。

### Pythonic Note

- `range(n-2, -1, -1)` 是从右往左遍历的正确写法,`(start, stop, step)` 用**逗号**分隔,不是冒号(冒号是 slicing 语法)
- Python 负数索引 wraparound 陷阱:`prices[-1]` 是最后一个元素而不是越界报错,涉及 `i-1` 的代码要小心 i=0 的情况

### 踩过的坑

- **复杂度估算不到位**:第一次写了"逐层剥离"的算法(每层减 1),没意识到外层循环跑 max_h 次而不是 n 次。永远要把"内层 ops × 外层迭代数"代入题目 constraint,看会不会过 1 秒 ≈ 10^8 ops 这条线。
- **Per-position vs per-range 思维混淆**:一开始尝试 `min(leftmax, rightmax) * width - sum(heights)` 这种"算一片矩形面积"的思路,跑偏了。Trapping Rain Water 是 column-wise 问题,每个格子独立算自己头顶的水,不是 region-wise。
- **公式正负号搞反**:写成 `height[i] - min(leftmax, rightmax)` 得到负数。物理直觉:水量必须 ≥ 0,水位线 - 柱子高度 才是非负的方向。
- **数组初始化错误**:`leftmax = 0` 然后 `leftmax[i] = ...` 直接 TypeError。要 `leftmax = [0] * n`。
- **结构混乱**:把 DP 解法和 Two Pointers 解法混在一起写,搞出 `while l < r` 嵌套 for 循环的怪物。两种解法是 alternative,不能拼接。
- **rightmax 递推方向**:从右往左填的时候要看 `rightmax[i+1]` 而不是 `[i-1]`(前一个已填好的是右边那个)。
- **`min(leftmax, rightmax)` 直接传整个数组**:Python 会做 list 字典序比较返回某个 list,然后 `list - int` 报错。要用 `min(leftmax[i], rightmax[i])`。

### Related Problems

- #11 Container With Most Water(关联点:也是由两边矮墙决定容量,但只算"两墙之间最大矩形",更简单)
- #84 Largest Rectangle in Histogram(关联点:同样基于柱状图,但用 monotonic stack)
- #407 Trapping Rain Water II(关联点:2D 版本,用 priority queue + BFS)

### Interview-Ready Phrasing

> "The core insight is that water trapped at each column equals min(leftMax, rightMax) - height[i], where leftMax and rightMax are the tallest bars to the left and right of position i. My first attempt was layer-by-layer, but that's O(n × maxHeight) which times out for the given constraints. The DP solution precomputes leftMax and rightMax in two passes, then sums water in a third pass — O(n) time, O(n) space. The follow-up optimization uses two pointers to achieve O(1) space: we move whichever pointer has the smaller running max inward, because the smaller max already bounds the water level on that side regardless of what's in between."

### 复习日期
- **First review (2 weeks)**: 2026/06/10
- **Second review (1 month)**: 2026/06/27
- **Third review (3 months)**: 2026/08/27