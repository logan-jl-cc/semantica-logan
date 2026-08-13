"""案例 02 — 离线知识图谱管线:文本 → NER → 关系 → KG → 规则推理。

全程本地、确定性,无需 LLM 或外部服务。
运行: python examples/case/02_offline_pipeline/run.py
"""
from semantica.semantic_extract import NamedEntityRecognizer, RelationExtractor
from semantica.kg import GraphBuilder
from semantica.reasoning import ReteEngine, Rule, Fact, RuleType


def main():
    text = (
        "Anthropic CEO Dario Amodei announced a $7.3B Series E round "
        "with Google and Spark Capital, valuing Anthropic at $61.5B."
    )
    print("=" * 60)
    print("  离线管线:文本 → NER → 关系 → KG → 规则推理(零 LLM)")
    print("=" * 60)
    print(f"\n[输入文本]\n  {text}\n")

    # 1) 本地 NER(spaCy / transformers,无需 LLM)
    ner = NamedEntityRecognizer(confidence_threshold=0.3)
    ents = ner.extract_entities(text)
    print(f"[① 本地 NER] 抽取到 {len(ents)} 个实体:")
    for e in ents[:8]:
        d = e.to_dict() if hasattr(e, "to_dict") else vars(e)
        print(f"   - {d.get('text', '?'):20s} ({d.get('label', '?')})")

    # 2) 本地关系抽取
    rel = RelationExtractor(confidence_threshold=0.3)
    rels = rel.extract_relations(text, entities=ents)
    print(f"\n[② 本地关系抽取] 抽取到 {len(rels)} 条关系")

    # 3) 构建 KG(纯内存)
    sources = [{"id": "s1", "text": text, "source": "inline"}]
    kg = GraphBuilder(merge_entities=True).build(sources)
    n_entities = len(kg.get("entities", []))
    n_rels = len(kg.get("relationships", []))
    print(f"\n[③ KG 构建] {n_entities} 实体 / {n_rels} 关系")

    # 4) 确定性规则推理(Rete 引擎,无 LLM)
    rete = ReteEngine()
    rete.build_network([
        Rule(
            rule_id="mega_round",
            name="大额融资",
            conditions=[{"field": "amount", "operator": ">", "value": 1_000_000_000}],
            conclusion="flag_mega_round",
            rule_type=RuleType.IMPLICATION,
        ),
    ])
    rete.add_fact(Fact("f1", "funding", [{"amount": 7_300_000_000}]))
    matches = rete.match_patterns()
    # Match 对象用属性访问;兼容 dict 返回
    rules_hit = []
    for m in (matches or []):
        rules_hit.append(m.get("rule") if isinstance(m, dict) else getattr(m, "rule", None))
    print(f"\n[④ 规则推理] 命中规则: {rules_hit}")

    print("\n→ ingest → extract → KG → reason 全程离线完成 ✔")


if __name__ == "__main__":
    main()
