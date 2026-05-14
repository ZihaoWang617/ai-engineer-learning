# 271. Encode and Decode Strings

## 一句话定位
Serialization 设计题：把任意 ASCII string list 编码成单一 string，
要求 decode 能完美还原。考点：delimiter 选择的设计陷阱 + length-prefix 解法。

## 关键设计陷阱（25 分钟独立思考期我踩的坑）
- 第一反应：用 " " 或某个特殊字符当 delimiter
- 致命问题：题目说 string 可以包含 any ASCII chars——任何字符都可能在 input 里出现
- 顿悟：**delimiter 不需要"唯一不出现"。如果 decoder 用 length 而不是 delimiter
  找边界，content 内的 delimiter 字符完全不影响**

## 解法：Length-prefix encoding
每段 string 编码为 `{length}#{content}`，decoder 读 digits 直到第一个 `#`，
然后**严格按 length** 读 content（不管 content 里是否含 `#`）。

```python
class Solution:
    def encode(self, strs: List[str]) -> str:
        result = []
        for s in strs:
            result.append(f"{len(s)}#{s}")
        return "".join(result)
    def decode(self, s: str) -> List[str]:
        result, i= [], 0

        while i < len(s):
            j = i
            while s[j] != "#":
                j += 1
            length = int(s[i : j])
            result.append(s[j + 1: j + 1 + length])
            i = j + 1 + length

        return result             
```

## 复杂度
- encode: O(n) where n = total chars
- decode: O(n)
- Space: O(n) for output

## 踩的坑
1. encode 第一版用 `result = ""` + `result.append(...)`——string 没 append 方法
   → 改成 list + join
2. 第一版 for loop 写成 `range(len(strs)-1)`——被"join with delimiter"思维
   定势带偏。length-prefix 每段独立，不需要 special-case 任何元素
3. 一开始想用 hash 给每个 string 标记 ID——hash 是单向的不能 decode 还原。
   思路对（给每段标记 metadata），工具错（hash 应换成 length）

## 现实世界类比
- HTTP/TCP Content-Length header
- Protocol Buffers / BSON / MessagePack 等二进制序列化
- Pascal length-prefixed strings vs C null-terminated strings

## 2 周后重做要点
- 不要先想 delimiter——先想"decoder 怎么找边界"
- list + "".join() 不要写成 `+=`