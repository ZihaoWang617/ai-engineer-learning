## [#0049] [Group Anagrams] [Medium] 🟡
- **Pattern**: [Arrays & Hashing]
- **Link**: https://leetcode.com/problems/group-anagrams/description/
- **Status**: 独立做出（算法），Python 语法 debug 求助
- **Time spent**: ~20 min

### Insight
**核心 insight**：anagrams 的本质 = 字符频率分布完全相同。
所以只要把"字符频率"作为 hashmap key，所有 anagrams 自然 group 到同一个 bucket。

频率表示用 size-26 数组（每个 index 代表一个字母），`ord(c) - ord('a')` 把字符映射到 0-25 的 index。
**关键细节：用 `tuple(count)` 不是 `count` 本身做 key——list 是 mutable 不可 hash，tuple 是 immutable 可 hash**。

### Solution: Hashmap with Frequency Tuple as Key
```python
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        result = defaultdict(list)
        for s in strs:
            count = [0] * 26
            for c in s:
                count[ord(c) - ord("a")] += 1
            result[tuple(count)].append(s)
        return list(result.values())
```
- **Time**: O(m·n) — m 个 string，每个最多 n 个字符
- **Space**: O(m·n) — 存储所有 string + 每个 string 对应的 26-tuple key（key 部分 O(m·26)=O(m)，但 string 内容本身占 O(m·n)）

### 对比另一种解法（次优）
也可以用 `sorted(s)` 作 key：
```python
result[''.join(sorted(s))].append(s)
```
- Time: O(m·n·log n) — 每个 string 排序要 n·log n
- 频率 tuple 方案 O(m·n) 严格更快
- 但 sorted-key 解法**代码更短，面试时如果忘了频率 tuple 写法可以兜底**

### Pythonic Notes
- `defaultdict(list)`：第一次访问任何 key 时自动初始化 value 为 `[]`，省去 `if key not in dict` 判断
- `ord(c) - ord('a')`：把小写字母映射到 0-25，标准 trick
- **`tuple()` vs `list`**：dict key 必须 hashable。list 不行（mutable），tuple 行（immutable）
- **`dict.values()` 不是 list**：返回的是 `dict_values` view object，LeetCode strict type check 不接受，必须 `list(...)` 包一层
- **`{}` 歧义**：`{}` 空字典；`{x}` 含元素则是 set（无 colon）；`{x: y}` 才是 dict

### 踩过的坑
1. **第一次 return 用了 `dict.values()` 没 wrap `list()`** → 报 `TypeError: dict_values(...) is not valid value for the expected return type list<list<string>>`
2. **第二次手滑写 `result = {defaultdict(list)}`** → 多一对大括号导致变成 set，set 不 subscriptable，`result[key]` 当场炸

### 复习日期
- **First review (2 weeks)**: 2026/5/27
- **Second review (1 month)**: 2026/6/13
- **Pre-interview review**: 投递期间（7 月中下旬）

### 同类题（NeetCode 150 Arrays & Hashing）
- #347 Top K Frequent Elements（用 bucket / heap）
- #36 Valid Sudoku（也用 frozenset / tuple 做 hashmap key）
- #128 Longest Consecutive Sequence