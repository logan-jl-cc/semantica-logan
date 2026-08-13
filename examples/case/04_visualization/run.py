"""案例 04 — 可视化:用项目自带的 KGVisualizer 导出交互式知识图谱 HTML。

运行: python examples/case/04_visualization/run.py
"""
import os
import webbrowser

from semantica.context import ContextGraph
from semantica.visualization import KGVisualizer


def main():
    # 1) 构建一个小型决策图
    g = ContextGraph(advanced_analytics=True)
    g.add_node("loan_A7291", "Loan", amount=85000, applicant="A-7291")
    g.add_node("alice", "Person", name="Alice Chen", role="Underwriter")
    app = g.record_decision(
        category="credit_application", scenario="A-7291 申请",
        reasoning="收入达标", outcome="proceed", confidence=0.88,
        decision_maker="system_auto", entities=["loan_A7291"],
    )
    uw = g.record_decision(
        category="loan_underwriting", scenario="A-7291 承销",
        reasoning="DTI达标", outcome="approved", confidence=0.94,
        decision_maker="alice", entities=["loan_A7291", "alice"],
    )
    g.add_causal_relationship(app, uw, relationship_type="CAUSED")

    # 2) 转成 KGVisualizer 需要的 {entities, relationships} 结构
    gd = g.to_dict()
    kg = {
        "entities": [
            {"id": n["id"], "type": n["type"], "text": n.get("content", "")}
            for n in gd["nodes"]
        ],
        "relationships": [
            {"source_id": e["source"], "target_id": e["target"], "type": e["type"]}
            for e in gd["edges"]
        ],
    }

    # 3) 导出交互式 HTML(力导向布局)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "graph.html")
    viz = KGVisualizer(layout="force", color_scheme="default")
    viz.visualize_network(kg, output="interactive", file_path=out_path)

    print("=" * 60)
    print("✓ 交互式知识图谱已导出")
    print(f"  文件: {out_path}")
    print(f"  大小: {os.path.getsize(out_path) // 1024} KB")
    print(f"  节点: {len(kg['entities'])}  边: {len(kg['relationships'])}")
    print("=" * 60)
    print("提示:在浏览器中可拖拽节点、缩放、悬停查看详情。")

    # 4) 自动打开浏览器
    try:
        webbrowser.open(f"file://{out_path}")
        print("→ 已在默认浏览器打开")
    except Exception:
        print(f"→ 请手动打开: file://{out_path}")


if __name__ == "__main__":
    main()
