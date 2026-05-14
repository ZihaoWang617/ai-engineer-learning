# 238. Product of Array Except Self

## 25 分钟独立期：我想到的是 O(n²) brute force
思路：for each i, 把 nums[i] 乘到 result[j] (j != i) 的每个位置。
算法正确，但 nested loop = O(n²)。题目明确要求 O(n) → 必然 TLE。

## NeetCode 视频后理解的 O(n) 解法：Prefix / Suffix products
**核心 insight**：result[i] = (i 左边所有数的乘积) × (i 右边所有数的乘积)
- 左乘积可以 forward pass O(n) 算出
- 右乘积可以 backward pass O(n) 算出
- 用 output array 自身存储中间值，避免额外 O(n) 空间

## 关键优化：postfix 用 scalar 而不是 array
Naive 实现会用两个长度 n 的 prefix/suffix array，O(n) extra space。
优化版：forward pass 时把 prefix 写进 result[i]，backward pass 时
用单个 scalar postfix 累乘——result 直接被原地更新，extra space = O(1) 个变量。

## 代码
[贴代码]

## 复杂度
- Time: O(n)（两次单 pass）
- Space: O(1) extra（不算 output array）

## 踩坑
- 初始化 prefix/postfix 用 1（乘法 identity），不是 0
- result 初始化用 `[1]*len(nums)` 不是 `[]*len(nums)`（后者是空 list）

## 2 周后重做要点
- 关键词联想：每位置答案 = 左半乘积 × 右半乘积
- 不要先想"怎么避免除法"——想"怎么分两半"
- output array 当中间存储是省空间的关键 trick

## 关联问题
- #2483 类似的 prefix/suffix 思想
- 前缀和/后缀和数组（求 sum 而不是 product）是同一 pattern