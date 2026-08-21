# 案例 07 — 对照实验:向量记忆 vs 图谱记忆

同一问题、同一份信息,两种记忆底座谁能支撑"关系型追问"。

## 实验设计

- **问题**:`How was the interest rate decision for loan A-7291 made? What caused it...?`
- **控制变量**:A/B 两组存入**完全相同的信息**——图的每个节点与边都序列化成文本喂给 A 组,不给图侧私藏
- **A 组** = 向量记忆(裸 Agno 原生 Knowledge 范式:切块 + 嵌入 + 相似度 top-k)
- **B 组** = 图谱记忆(Semantica ContextGraph:沿 CAUSED/INFLUENCED 边遍历)
- **比较层**:检索底座(两组接同一 LLM 时,答案差异正来自这一层;本实验无需 LLM/API key)

## 实测结论(详见运行输出)

| 维度 | A 向量 | B 图谱 |
|---|---|---|
| 决策记录召回 | 三条都可能召回,**但不稳定**(见下) | 遍历起点,必达 |
| 因果边召回 | 1/2(CAUSED 边漏)——**链环缺失** | 2/2,结构化 |
| 顺序/跳数 | 无序 | hop1←hop2 可数 |
| 溯源 | 仅当文本里写了 | 每跳带 maker/confidence/reasoning |
| 确定性 | **随无关扰动变化** | 重放一万次同一链 |

**意外发现(两轮运行抓到)**:文本中无关的 UUID 后缀变化 → 嵌入微移 → 近似分数(0.73–0.76 区间)排序翻转,利率记录一次第 1、一次跌出 top-6。A 组召回集合对**语义无关的扰动**敏感,是范式属性。

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate
python examples/case/07_memory_comparison/run.py
```

零 LLM、零 API key、离线可跑(嵌入用本地 bge-small)。
