"""案例 07 — 对照实验:同一问题,两种记忆底座。

问题:"A-7291 的利率决策是怎么来的?"
  A 组 = 向量记忆(裸 Agno 原生 Knowledge 范式:切块 + 嵌入 + 相似度检索)
  B 组 = 图谱记忆(Semantica ContextGraph:节点 + 因果边 + 遍历)

控制变量:两组存入完全相同的信息——图的每条节点/边都序列化成文本喂给 A 组。
比较的是检索底座(两组若接同一 LLM,差异也正来自这一层)。

运行: python examples/case/07_memory_comparison/run.py
"""
from semantica.context import ContextGraph
from semantica.vector_store import VectorStore

QUERY = "How was the interest rate decision for loan A-7291 made? What caused it and on what reasoning?"


def build_graph():
    """建图(与案例 01 同款):业务对象 + 3 决策 + 2 因果边。"""
    g = ContextGraph(advanced_analytics=True)
    g.add_node("loan_A7291", "Loan", amount=85000, currency="USD", applicant="A-7291", status="approved")
    g.add_node("alice", "Person", name="Alice Chen", role="Senior Underwriter")
    app = g.record_decision(
        category="credit_application", scenario="A-7291 personal loan: income 85k, DTI 31%",
        reasoning="Income meets threshold; employment stable",
        outcome="proceed_to_underwriting", confidence=0.88,
        decision_maker="system_auto", entities=["loan_A7291"],
    )
    uw = g.record_decision(
        category="loan_underwriting", scenario="A-7291 underwriting review",
        reasoning="DTI 31% within policy; 36-month clean credit history; risk tier B2",
        outcome="approved", confidence=0.94,
        decision_maker="alice", entities=["loan_A7291", "alice"],
    )
    rate = g.record_decision(
        category="interest_rate", scenario="A-7291 rate assignment",
        reasoning="Prime + 2.4% based on risk tier B2",
        outcome="rate_set_8.9pct", confidence=0.99,
        decision_maker="system_auto", entities=["loan_A7291"],
    )
    g.add_causal_relationship(app, uw, relationship_type="CAUSED")
    g.add_causal_relationship(uw, rate, relationship_type="INFLUENCED")
    return g, app, uw, rate


def serialize_graph_as_text(g):
    """公平性关键:把图的全部节点与边,序列化成 A 组可摄入的文本行。"""
    gd = g.to_dict()
    id2node = {n["id"]: n for n in gd["nodes"]}
    lines = []
    for n in gd["nodes"]:
        p = n.get("properties", {})
        if n["type"] == "decision":
            lines.append(
                f"Decision record [{p.get('category')}]: scenario={p.get('scenario')}; "
                f"outcome={p.get('outcome')}; reasoning={p.get('reasoning')}; "
                f"confidence={p.get('confidence')}; decision_maker={p.get('decision_maker')}; "
                f"id={n['id'][:8]}"
            )
        elif n["type"] in ("Loan", "Person"):
            lines.append(f"Business object {n['type']}: {p}")
    for e in gd["edges"]:
        s, t = id2node.get(e["source"], {}), id2node.get(e["target"], {})
        sc = s.get("properties", {}).get("category") or s.get("type", "")
        tc = t.get("properties", {}).get("category") or t.get("type", "")
        lines.append(f"Relationship: {sc} --[{e['type']}]--> {tc}")
    return lines


def side_a_vector(lines):
    """A 组:向量记忆检索(Agno 原生 Knowledge 范式)。"""
    from semantica.embeddings import TextEmbedder
    emb = TextEmbedder(model_name="BAAI/bge-small-en-v1.5", normalize=True)
    vecs = emb.embed_batch(lines)
    vs = VectorStore(backend="inmemory", dimension=len(vecs[0]))
    vs.store(vectors=vecs,
             metadata=[{"text": line, "seq": i} for i, line in enumerate(lines)])
    hits = vs.search(QUERY, limit=6)
    out = []
    for h in hits:
        md = h.get("metadata", {}) or {}
        out.append({"score": float(h.get("score", 0.0)),
                    "text": md.get("text", "")})
    return out


def side_b_graph(g, rate_id):
    """B 组:沿因果边向上游遍历(图的 native 能力)。上游遍历按 target 索引。"""
    gd = g.to_dict()
    id2node = {n["id"]: n for n in gd["nodes"]}
    upstream = {e["target"]: (e["type"], e["source"])
                for e in gd["edges"] if e["type"] in ("CAUSED", "INFLUENCED")}
    chain, cur, hop = [], rate_id, 0
    while cur in upstream:
        rel, parent = upstream[cur]
        hop += 1
        pn = id2node[parent].get("properties", {})
        chain.append({
            "hop": hop, "relation_upstream": rel,
            "category": pn.get("category"), "outcome": pn.get("outcome"),
            "reasoning": pn.get("reasoning"),
            "decision_maker": pn.get("decision_maker"),
            "confidence": pn.get("confidence"),
        })
        cur = parent
    return chain


def main():
    print("=" * 74)
    print("  对照实验:同一问题,两种记忆底座")
    print("=" * 74)
    print(f"\n[问题] {QUERY}\n")

    g, app, uw, rate = build_graph()
    lines = serialize_graph_as_text(g)
    print(f"[控制变量] 图序列化为 {len(lines)} 条文本行,两组信息完全相同")
    print(f"           图侧: {len(g.to_dict()['nodes'])} 节点 / {len(g.to_dict()['edges'])} 边\n")

    # ---------- A 组:向量检索 ----------
    print("─" * 74)
    print("A 组 · 向量记忆(裸 Agno 原生范式:相似度 top-6)")
    print("─" * 74)
    hits = side_a_vector(lines)
    a_hits_desc = []
    for h in hits:
        txt = h.get("text", "")[:90]
        score = h.get("score", h.get("similarity", 0))
        a_hits_desc.append((score, txt))
        print(f"  score={score:.3f}  {txt}")
    retrieved_set = {t for _, t in a_hits_desc}
    has_rate_record = any(t.startswith("Decision record [interest_rate]") for _, t in a_hits_desc)
    has_rate_mention = any("interest_rate" in t for _, t in a_hits_desc)
    has_uw_chunk = any("loan_underwriting" in t for _, t in a_hits_desc)
    has_app_chunk = any("credit_application" in t for _, t in a_hits_desc)
    has_cause_edge = any("--[CAUSED]" in t for _, t in a_hits_desc)
    has_influence_edge = any("--[INFLUENCED]" in t for _, t in a_hits_desc)
    has_causal_edge = has_cause_edge or has_influence_edge
    edge_recall = (1 if has_cause_edge else 0) + (1 if has_influence_edge else 0)

    # ---------- B 组:图遍历 ----------
    print()
    print("─" * 74)
    print("B 组 · 图谱记忆(沿 CAUSED/INFLUENCED 边向上游遍历)")
    print("─" * 74)
    chain = side_b_graph(g, rate)
    rn = g.to_dict()
    id2node = {n["id"]: n for n in rn["nodes"]}
    rp = id2node[rate]["properties"]
    print(f"  [起点] interest_rate / {rp['outcome']} / conf {rp['confidence']} / by {rp['decision_maker']}")
    for c in chain:
        print(f"  ↑ hop{c['hop']} {c['relation_upstream']}: {c['category']} / {c['outcome']} "
              f"/ conf {c['confidence']} / by {c['decision_maker']}")
        print(f"         reasoning: {c['reasoning']}")
    b_complete = len(chain) == 2  # app→uw→rate 完整两跳

    # ---------- 对比结论 ----------
    print()
    print("=" * 74)
    print("  对比(检索底座层)")
    print("=" * 74)
    print(f"""
  维度                A组(向量)                         B组(图谱)
  ─────────────────────────────────────────────────────────────────
  命中利率决策本体     {'✓ 完整记录' if has_rate_record else ('仅关系行提及' if has_rate_mention else '✗')}           ✓(遍历起点)
  因果关系是否显式     {'部分(靠边文本被召回)' if has_causal_edge else '✗ 未召回关系行'}              ✓(结构化 INFLUENCED/CAUSED)
  因果边召回           {edge_recall}/2(链环缺失则无法拼接)              {'2/2 ✓' if b_complete else '✗'}
  顺序/跳数            无序(相似度排序)                    ✓ hop1←hop2,可数
  溯源(id/责任主体)   仅当文本里写了                      ✓ 每跳带 maker/confidence/reasoning
  确定性               随措辞/嵌入模型变化                  确定(同图同链,永远同结果)
  噪音                 {sum(1 for _, t in a_hits_desc if 'Relationship' not in t and 'interest_rate' not in t and 'underwriting' not in t and 'credit_application' not in t)} 条无关行混入                       0(遍历只走因果边)
""")

    print("  [判读] A 组召回什么取决于嵌入相似度——本次结果:")
    print(f"         利率决策完整记录={'召回' if has_rate_record else '未召回'}, 承销={'召回' if has_uw_chunk else '未召回'}, "
          f"申请={'召回' if has_app_chunk else '未召回'}")
    print(f"         因果边: INFLUENCED={'召回' if has_influence_edge else '未召回'}, CAUSED={'召回' if has_cause_edge else '未召回'}"
          f" → 链环 {'完整' if edge_recall==2 else '缺环,LLM 需自行脑补该跳关系'}")
    print("         换个问法/换嵌入模型,召回集合就会变——这是范式属性,不是运气。")
    print("         B 组的答案由边结构唯一决定:重放一万次,同一链。")
    print("\n→ 若两组接同一个 LLM:A 组答案=模型缝合召回碎片(可能缺环/幻觉补全);")
    print("   B 组答案=沿着可验证的边读出,每跳带依据与责任主体。")


if __name__ == "__main__":
    main()
