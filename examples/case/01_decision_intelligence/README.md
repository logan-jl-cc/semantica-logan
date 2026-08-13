# 案例 01 — 决策智能(Decision Intelligence)

演示 Semantica 的核心能力:把 AI/人的"判断"记录为图中**可追溯、可审计、可查询**的一等节点。

## 这个案例展示什么

- 记录一条因果决策链(贷款申请 → 承销 → 定价)
- 把孤立决策连成"决策图谱"
- 回溯因果、分析影响、合规校验
- 导出审计轨迹(PROV-O)

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate
python examples/case/01_decision_intelligence/run.py
```

## 关键 API

| API | 作用 |
|---|---|
| `ContextGraph.record_decision(...)` | 记录决策(含 reasoning / decision_maker / confidence) |
| `add_causal_relationship(...)` | 连因果边(CAUSED / INFLUENCED / PRECEDENT_FOR) |
| `analyze_decision_impact(id)` | 下游影响分析 |
| `check_decision_rules(...)` | 合规闸门(校验责任主体等) |
| `RDFExporter().export(...)` | 导出 PROV-O 审计文件 |

## 注意

- `decision_maker` 字段是**合规必填**——不传则 `check_decision_rules` 判不合规。
- 本案例纯内存运行,无需 LLM、无需外部服务。
