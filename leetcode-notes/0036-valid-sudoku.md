# LeetCode #36 — Valid Sudoku

**Difficulty**: Medium  
**Topic**: Arrays & Hashing  
**Date solved**: 2026-05-15  
**Review date**: 2026-05-29  
**Independence**: B（看 NeetCode 视频后理解 + 重写）⚠️ 2 周后必须独立 redo

🔗 https://leetcode.com/problems/valid-sudoku/

---

## 问题核心

判断 9x9 数独 board 是否当前 valid（**不要求 solvable**，只要求**现状不违规**）：

- 每行 1-9 不重复
- 每列 1-9 不重复
- 每个 3x3 sub-box 1-9 不重复
- 空格用 `"."` 表示，忽略不验证

---

## 核心 Insight

**用 hashmap-of-sets 同时追踪 3 种 constraint 的"已见数字"**——
key = row / col / box 的 index，value = 该 row/col/box 已出现过的数字 set。
单次遍历 9x9，每格 O(1) 查 + 加。

### 3x3 Box Index Trick

`(r // 3, c // 3)` 把 9x9 分成 9 个 3x3：

| Box index | r 范围 | c 范围 |
|---|---|---|
| (0,0) | 0-2 | 0-2 |
| (0,1) | 0-2 | 3-5 |
| (0,2) | 0-2 | 6-8 |
| (1,0) | 3-5 | 0-2 |
| ... | ... | ... |
| (2,2) | 6-8 | 6-8 |

整数除法把连续 9 个格子映射到 3 个 box 槽位。

---

## 🚨 关键 Pattern：先 check 再 add

**顺序永远是**：
1. 先 `val in seen_set` 检查重复
2. 没重复才 `seen_set.add(val)`

**反了的话**（先 add 再 check）：刚 add 进去立刻 `in` 检查，永远 True，每次都 return False，整个程序坏。

---

## 最终解法

```python
from collections import defaultdict

class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = defaultdict(set)
        cols = defaultdict(set)
        boxes = defaultdict(set)
        
        for r in range(9):
            for c in range(9):
                val = board[r][c]
                if val == ".":
                    continue
                # check 再 add，顺序不能反
                if (val in rows[r] or 
                    val in cols[c] or 
                    val in boxes[(r // 3, c // 3)]):
                    return False
                rows[r].add(val)
                cols[c].add(val)
                boxes[(r // 3, c // 3)].add(val)
        
        return True
```

### 关键 Python API

```python
from collections import defaultdict

d = defaultdict(set)
d["row_0"].add(5)   # 自动 init d["row_0"] = set() 然后 add 5
# 等价于:
d = {}
if "row_0" not in d:
    d["row_0"] = set()
d["row_0"].add(5)
```

`defaultdict(set)` 的参数 `set` 是 class 本身（**不是 `set()` 实例**）——defaultdict 需要 default value 时调用 `set()` 创建空 set。

---

## 复杂度

- **Time**: O(81) = **O(1)** — board 固定 9x9
- **Space**: O(81) = **O(1)** — 三个 hashmap 最多存 81 个数

⚠️ 如果题目泛化为 N×N sudoku：T = O(N²)，S = O(N²)。

---

## 我犯的错 / 易错点

| 错误 | 后果 |
|---|---|
| `rang(9)` typo（少打 e） | runtime NameError |
| `if (... or ... or ...]:` 缺右括号配 `if (` | SyntaxError |
| 没 cache `val = board[r][c]`，每行重复 access 5 次 | 代码丑、效率略损 |
| 口述"先 add 再 check"（顺序反） | mental model 没固化的信号 |
| 没跑就贴代码 | production engineer 基本素养：**先 verify 再 ship** |

---

## Pattern 归纳

**Arrays & Hashing 经典**：用 set/dict 做 **O(1) membership check**。

适用场景：
- 检查"是否见过 / 是否重复"
- 检查"是否在某集合内"
- 多条 constraint 并行追踪（这道题：3 条 constraint）

类似题：
- [#217 Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) — 一维版
- [#242 Valid Anagram](https://leetcode.com/problems/valid-anagram/) — 字符计数版
- [#49 Group Anagrams](https://leetcode.com/problems/group-anagrams/) — hashmap 分组版

---

## 2 周后复习指令（5/29）

1. **不看这份 notes**
2. **不看 NeetCode 视频**
3. **独立 25 分钟**做出来
4. 做完对比这份 notes，验证：
   - [ ] 想到了用 hashmap-of-sets 同时追 3 种 constraint
   - [ ] 想到了 `(r//3, c//3)` 的 box index trick
   - [ ] 顺序写对了（先 check 再 add）
   - [ ] 用了 `defaultdict(set)` 或等价的 `dict.setdefault`

全部 ✅ = 真 own 了 pattern。任何 ❌ = 没 own，再看 notes 重写一次。