# LC 11. Container With Most Water (Medium) · Two Pointers

> 给定 height 数组，找两条线形成容器装最多水。`area = (r - l) × min(h[l], h[r])`，返回 max area。

**Pattern**: Opposing Two-Pointer + Greedy Move  
**Date**: 2026/05/21 (Day 47)

---

## 🎯 核心思路：双指针向中间夹 + 移动较矮那一侧

1. **`l=0, r=len-1`**，从两端开始
2. 每次算 area，更新 `res = max(res, area)`
3. **较矮那一侧移动一步**（greedy choice）
4. `l < r` 退出

---

## 💻 Code (O(n) time, O(1) space)

```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        res = 0
        l, r = 0, len(height) - 1
        while l < r:
            area = (r - l) * min(height[l], height[r])
            res = max(res, area)
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return res
```

---

## 🔑 Key Insight: **为什么移动较矮那一侧**（5 步推理链）

```
area = (r - l) × min(h[l], h[r])
       └─ width ┘   └─ height ┘
                    (bounded by 较矮)

1. 每次移动，width (r-l) 必然 -1
2. area 想变大，唯一途径是 min 变大
3. min 由较矮那一侧决定（bottleneck）
4. 移动较矮 → 新位置可能更高 → min 有机会变大 → area 有机会变大
   移动较高 → min 仍被较矮锁死 → area 只能变小或持平
5. 结论：只能移动较矮（shorter side）
```

**面试 A 级答案 = 完整 5 步链条**，不是"shorter side 挪能找到 longer edge"这种 1 步 fragment。

### `<` 还是 `<=`？

```python
if height[l] < height[r]:    # < 和 <= 都行
    l += 1
else:
    r -= 1
```

相等时移动哪个都不会让 area 变大（min 不变，width -1）—— 所以怎么 break tie 不影响 correctness。

---

## ⚡ 为什么是 O(n)

每次 iteration 至少有一个 pointer 移动 1 步，l 和 r 总共最多移动 `len(height)` 步 → **O(n)**。

每个元素**最多被访问一次** —— 这是 two-pointer 相对 brute force O(n²) 的核心优势。

---

## 🔗 Contrast with #15 3Sum（必背 A 级答案）

**关键问题**：#11 为什么不需要 skip duplicates，但 #15 需要？

**A 级 3 步链条**（从 IO 数据结构入手）：

| | #11 maxArea | #15 threeSum |
|---|---|---|
| Output | `int`（标量） | `list[list[int]]`（三元组列表） |
| "duplicate entry" 概念 | ❌ 不存在 | ✅ 存在（同样三元组重复算两个 entry）|
| 需要 dedup？ | 不需要 | 必须 |

**3 步推理**：
1. #15 output 是 list，list entry 概念决定了"同样三元组重复出现是问题"
2. #11 output 是 scalar int，没有 "entry" 概念，**无法**重复
3. 所以 #11 根本不存在 dedup 这个问题

**senior 直觉**：**永远先看 IO 数据结构**。问题本质往往在那。

---

## 🧠 Pattern: Opposing Two-Pointer + Greedy Move

**特征**：
- 两端 pointer 向中间夹
- 每次 iteration 必须 shrink window
- 需要 track optimum
- 决策：**移动哪个 pointer 有改进 answer 的可能性**

**家族题**：
- LC 11 Container (本题)
- LC 42 Trapping Rain Water
- LC 167 Two Sum II（已做）
- LC 125 Valid Palindrome（已做）
- LC 15 3Sum（已做，需 skip）

---

## ⚠️ Common Pitfalls

1. ❌ 忘 `res = max(res, area)` → 只返回最后一次 area，不是最大
2. ❌ 把 `r = len(height)` 写成（忘 `-1`）→ IndexError
3. ❌ 移动较高那一侧 → area 单调减，错过 max
4. ❌ 把 `area` 写在 if/else 里 → 重复代码，可读性差

---

## 🎯 Trigger Check（2 周后复习用）

30 秒内能答出来吗？

1. **为什么 O(n)？**  
   → 每次 iteration 至少一个 pointer 移动，l 和 r 总共最多走 len(height) 步

2. **为什么移动较矮那一侧？**（必给 5 步链条，不是 1 句）  
   → 看上面 Key Insight 那 5 步

3. **#11 vs #15 contrast，为什么 #11 不需要 skip duplicates？**（必给 3 步链条）  
   → output 数据结构差异（int vs list）

4. **`<` 还是 `<=`？为什么都行？**  
   → 相等时 min 不变，移动哪个都不让 area 变大

**答不出来 = recitation level，重看到能 synthesis**。

---

## 📝 Day 47 自己的发现

- **新 trigger**：答 why 类问题时**强制至少 3 步逻辑链**，少于 3 步 = fragmented = 面试 1 层 follow-up 就崩
- **senior 直觉**：先看 IO 数据结构，往往省一层推理
- "完整 reasoning chain" 是 conclusion 之外**真正区分 A 级 vs B 级**的地方
- 早上 Q-D2.2 的 A- + 现在第一次主动给 3 步链条 = trigger 正在 internalize 的早期信号