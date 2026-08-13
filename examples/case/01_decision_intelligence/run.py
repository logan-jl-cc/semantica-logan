"""案例 01 — 决策智能:记录一条因果决策链并做查询/合规/导出。

运行: python examples/case/01_decision_intelligence/run.py
"""
import json
import os

from semantica.context import ContextGraph
from semantica.export import RDFExporter


def main():
    # 1) 创建上下文图(内存,无需外部服务)
    g = ContextGraph(advanced_analytics=True)

    # 先建业务对象 —— 决策所作用的载体
    g.add_node("loan_A7291", "Loan", amount=85000, currency="USD",
               applicant="A-7291", status="pending")
    g.add_node("alice", "Person", name="Alice Chen", role="Senior Underwriter")

    # 2) 记录一条因果决策链:申请 → 承销 → 定价
    app = g.record_decision(
        category="credit_application",
        scenario="个人贷款 A-7291: 收入85k, DTI 31%, 在职3年",
        reasoning="收入达标、就业稳定、无不良信用事件",
        outcome="proceed_to_underwriting",
        confidence=0.88,
        decision_maker="system_auto",          # ← 责任主体(合规必填)
        entities=["loan_A7291"],
        metadata={"applicant_id": "A-7291", "channel": "online"},
    )
    uw = g.record_decision(
        category="loan_underwriting",
        scenario="A-7291 承销复核",
        reasoning="DTI 31% 在政策内;36个月信用记录干净;风险等级 B2",
        outcome="approved",
        confidence=0.94,
        decision_maker="alice",                # ← 真人责任主体
        entities=["loan_A7291", "alice"],
        metadata={"risk_tier": "B2", "dti": 0.31},
    )
    rate = g.record_decision(
        category="interest_rate",
        scenario="A-7291 定价",
        reasoning="Prime + 2.4%, 风险等级 B2",
        outcome="rate_set_8.9pct",
        confidence=0.99,
        decision_maker="system_auto",
        entities=["loan_A7291"],
    )

    # 3) 连成决策图谱(因果边)
    g.add_causal_relationship(app, uw, relationship_type="CAUSED")
    g.add_causal_relationship(uw, rate, relationship_type="INFLUENCED")

    print("=" * 60)
    print("✓ 已记录 3 条决策 + 2 条因果边")
    print(f"  app={app[:8]}…  uw={uw[:8]}…  rate={rate[:8]}…")

    # 4) 影响分析:承销决策影响了什么(沿 INFLUENCED 正向遍历)
    impact = g.analyze_decision_impact(uw)
    print(f"\n[影响分析] 承销决策影响了 {impact['total_influenced']} 个下游"
          f" | 最高影响分 {impact['max_influence_score']:.2f}")

    # 5) 合规闸门:有责任主体、结果合法吗?
    result = g.check_decision_rules({
        "category": "loan_underwriting",
        "outcome": "approved",
        "confidence": 0.94,
        "decision_maker": "alice",
    })
    print(f"\n[合规检查] compliant={result['compliant']}  violations={result['violations']}")

    # 对比:缺 decision_maker 时会判不合规
    bad = g.check_decision_rules({
        "category": "loan_underwriting",
        "outcome": "approved",
        "confidence": 0.94,
        # 故意不传 decision_maker
    })
    print(f"[合规检查(缺责任主体)] compliant={bad['compliant']}  violations={bad['violations']}")

    # 6) 导出审计轨迹(PROV-O / Turtle,供监管提交)
    out_dir = os.path.dirname(os.path.abspath(__file__))
    audit_path = os.path.join(out_dir, "loan_audit.ttl")
    gd = g.to_dict()
    kg = {
        "entities": [{"id": n["id"], "type": n["type"], "text": n.get("content", "")}
                     for n in gd["nodes"]],
        "relationships": [{"source_id": e["source"], "target_id": e["target"], "type": e["type"]}
                          for e in gd["edges"]],
    }
    RDFExporter().export(kg, audit_path, format="turtle")
    print(f"\n[审计导出] PROV-O 文件: {audit_path}  ({os.path.getsize(audit_path)} bytes)")

    # 7) 同时导出图 JSON(供案例 05 的 explorer 使用)
    graph_json = os.path.join(out_dir, "graph.json")
    with open(graph_json, "w", encoding="utf-8") as f:
        json.dump(gd, f, ensure_ascii=False, indent=2)
    print(f"[图数据] JSON: {graph_json}  ({len(gd['nodes'])} 节点 / {len(gd['edges'])} 边)")

    print("\n→ 完整闭环:记录 → 因果 → 影响 → 合规 → 审计导出 ✔")


if __name__ == "__main__":
    main()
