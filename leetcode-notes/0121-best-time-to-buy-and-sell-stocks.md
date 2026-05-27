## [#121] Best Time to Buy and Sell Stock [🟢 Easy]

- **Pattern**: Sliding Window(NeetCode 把它归在 Sliding Window,本质是 running min + running max profit 的单次遍历)
- **Link**: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
- **Status**: 看 hint 做出
- **Time spent**: ~15 min

### Insight

要找一对 (buy_day, sell_day) 满足 buy_day < sell_day,使 prices[sell_day] - prices[buy_day] 最大。

朴素思路:双循环每对组合都试,O(n²),n = 10^5 直接 TLE。

真正的 insight:**站在 day i 的角度思考——如果今天卖,最大利润 = prices[i] - 历史最低买入价**。所以只需边走边维护两个量:
- `stock_price`:目前为止见过的最低价(running min)
- `profit`:目前为止能达到的最大利润(running max profit)

单次遍历,O(n) time + O(1) space。**"running 状态 + 一次扫" 是底层 pattern**,Kadane's algorithm、Sliding Window 系列、很多 DP 题都是这种思路。

主要 trade-off:**brute force vs 单次扫**。一旦想到"只关心目前为止的 min,不需要回头看",就从 O(n²) 跳到 O(n)。

### Solution: One-pass running min + max profit
```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        stock_price = prices[0]
        profit = 0
        for i in range(len(prices)):
            stock_price = min(stock_price, prices[i])
            if prices[i] - stock_price > profit:
                profit = prices[i] - stock_price
        return profit
```
- **Time**: O(n) — 单次遍历,每个元素 O(1) 操作
- **Space**: O(1) — 只用两个 int 变量

### Pythonic Note

- `min(stock_price, prices[i])` 这种"更新 running min"在 Python 里很自然,避免 if/else 三行 verbose 版
- if 块也可以写成 `profit = max(profit, prices[i] - stock_price)` 一行,更 functional

### 踩过的坑

- **Running min vs pairwise min 混淆**:一开始写 `stock_price = min(prices[i], prices[i-1])`,这是"今天 vs 昨天"的 pairwise min,不是"目前为止最低"的 running min。
  - Trace `[7,1,5,3,6,4]`:i=3 时 pairwise 给 min(3,5)=3,但 running min 应该是 1。
  - 正确写法:`stock_price = min(stock_price, prices[i])` — 把之前累积的 running min 和今天对比。
- **Python 负数索引 wraparound 陷阱**:`prices[i-1]` 在 i=0 时变成 `prices[-1]` = 数组最后一个元素,不是 IndexError。涉及 `i-1` 永远要 mentally check i=0 那次会发生什么。
- **变量名 typo**:`profit[i]` 写错了,应该是 `prices[i]`。`profit` 是 int 不是 list,会 TypeError。**`profit` 和 `prices` 太接近,以后命名时让两者更有区分度**(比如 `max_profit` vs `prices`)。

### Related Problems

- #122 Best Time to Buy and Sell Stock II(关联点:多次交易版,贪心累加所有正涨幅)
- #53 Maximum Subarray(关联点:同样的"running 状态" — Kadane's algorithm 维护 running max subarray sum)
- #198 House Robber(关联点:DP + running 状态,加了"相邻不能同时选"的 constraint)

### Interview-Ready Phrasing

> "The naive O(n²) approach tries every buy-sell pair, but we can do this in O(n) with one pass. The insight: standing at day i, if we sell today, our profit is prices[i] minus the lowest price we've seen so far. So we maintain two running values — the minimum buy price up to day i, and the maximum profit achievable so far. We update both in a single pass. This 'running state' pattern shows up in Kadane's algorithm and many sliding window problems."

### 复习日期
- **First review (2 weeks)**: 2026/06/10
- **Second review (1 month)**: 2026/06/27
- **Third review (3 months)**: 2026/08/27