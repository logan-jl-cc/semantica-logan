# 案例 02 — 离线知识图谱管线(无需 LLM)

演示 Semantica 的核心管线可以**完全离线**运行:文本 → NER → 关系抽取 → 知识图谱 → 规则推理。
全程使用本地模型(spaCy / transformers),不调用任何 LLM 或外部服务。

## 这个案例展示什么

- 本地命名实体识别(spaCy `en_core_web_sm`)
- 本地关系抽取
- 构建 Knowledge Graph(内存)
- 确定性规则推理(Rete 引擎)

## 前置

```bash
# 已装 spaCy 英文模型(本仓库 venv 已装);若没有:
python -m spacy download en_core_web_sm
```

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate
python examples/case/02_offline_pipeline/run.py
```

## 关键 API

| API | 作用 |
|---|---|
| `NamedEntityRecognizer().extract_entities(text)` | 本地 NER |
| `RelationExtractor().extract_relations(text, entities)` | 本地关系抽取 |
| `GraphBuilder().build(sources)` | 构建 KG |
| `ReteEngine().match_patterns()` | 规则推理 |

## 注意

- 全程零 LLM、零网络、零外部服务。
- spaCy 模型未装时会自动降级到模式抽取(仍离线可用)。
