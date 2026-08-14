"""案例 06 — Agno 双 Agent + Semantica 决策集成。

场景:贷款审批。
  - Researcher(核验员):核验收入/信用/DTI,把事实写入共享知识图谱
  - DecisionAdvisor(决策顾问):基于共享图谱做审批决策并记录(带因果)
两个 agent 共享同一份 AgnoSharedContext(Semantica 的 ContextGraph + 决策账本)。

运行:
  # 完整 agent 运行(需 LLM key):
  python examples/case/06_agno_two_agents/run.py
  # 仅验证集成层接线(无需 LLM):
  python examples/case/06_agno_two_agents/run.py --wiring-only
"""
import argparse
import os
import sys


def build_shared_context():
    """构建两个 agent 共享的 Semantica 上下文(图 + 决策账本)。"""
    from semantica.context import ContextGraph
    from integrations.agno import AgnoSharedContext

    kg = ContextGraph(advanced_analytics=True)
    # 业务对象:申请人/贷款 —— 决策所作用的载体
    kg.add_node("applicant_A7291", "Person", name="A-7291", income=85000,
                employment_years=3, dti=0.31, credit_history_months=36)
    kg.add_node("loan_A7291", "Loan", amount=85000, status="pending")

    shared = AgnoSharedContext(
        knowledge_graph=kg,
        decision_tracking=True,     # 启用决策账本
    )
    return shared


def build_team(shared):
    """用 Agno 框架建一个双 agent 团队,各绑定共享上下文 + Semantica Toolkit。"""
    # 延迟导入:agent 框架在 wiring-only 模式下也装了,但 Model 后端可能没有
    from integrations.agno import AgnoDecisionKit, AgnoKGToolkit

    # Researcher 用 KG 工具:抽事实、写图谱、查询
    researcher_tools = AgnoKGToolkit(context=shared)
    # DecisionAdvisor 用决策工具:记决策、追因果、查合规
    advisor_tools = AgnoDecisionKit(context=shared, enable_policy_check=True)

    print("✓ 两个 Toolkit 就绪:")
    print("   KGToolkit 工具:    ", [m for m in ("extract_entities", "add_to_graph", "query_graph", "find_related") if hasattr(researcher_tools, m)])
    print("   DecisionKit 工具:  ", [m for m in ("record_decision", "trace_causal_chain", "find_precedents", "check_policy", "analyze_impact") if hasattr(advisor_tools, m)])

    # 选模型:优先 OpenAI,其次 Ollama 本地;都没有则提示
    model = _pick_model()

    from agno.agent import Agent

    researcher = Agent(
        name="Researcher",
        role="核验申请人事实并写入共享知识图谱",
        model=model,
        tools=[researcher_tools],
        instructions=(
            "你是贷款核验员。核实申请人的收入、DTI、信用记录后,"
            "用 add_to_graph / extract_entities 把已确认的事实写入共享图谱,"
            "不要直接做审批结论。"
        ),
    )
    advisor = Agent(
        name="DecisionAdvisor",
        role="基于共享图谱事实做出可审计的审批决策",
        model=model,
        tools=[advisor_tools],
        instructions=(
            "你是贷款决策顾问。先 query_graph 读核验员写入的事实,"
            "再用 record_decision 记录审批决策(category=loan_underwriting,"
            "必须带 decision_maker 与 reasoning),最后用 check_policy 校验合规。"
        ),
    )

    # 注:当前 Agno 版本 Team 用 members=(不是旧文档的 agents=)
    from agno.team import Team
    team = Team(
        name="LoanApprovalTeam",
        members=[researcher, advisor],
        model=model,
        instructions="按顺序:先由 Researcher 核验并写入事实,再由 DecisionAdvisor 做决策并记录。",
    )
    return team, researcher, advisor


def _pick_model():
    """选一个可用的 LLM 后端;都没有则抛出清晰错误。"""
    if os.environ.get("OPENAI_API_KEY"):
        from agno.models.openai import OpenAIChat
        return OpenAIChat(id="gpt-4o-mini")
    if os.environ.get("ANTHROPIC_API_KEY"):
        from agno.models.anthropic import Claude
        return Claude(id="claude-sonnet-5")
    # 尝试本地 Ollama
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
        from agno.models.ollama import Ollama
        return Ollama(id="qwen2.5:7b")
    except Exception:
        raise RuntimeError(
            "未找到可用 LLM。请二选一:\n"
            "  export OPENAI_API_KEY=sk-...\n"
            "  或本地起 Ollama: ollama serve && ollama pull qwen2.5:7b\n"
            "或仅验证接线: python run.py --wiring-only"
        )


def verify_wiring(shared):
    """离线验证集成层(无需 LLM):两个 agent 共享同一图,决策能落入共享账本。"""
    print("\n" + "=" * 60)
    print("  集成层验证(无需 LLM)")
    print("=" * 60)

    # 1) 共享图:业务对象在
    kg = shared.knowledge_graph
    gd = kg.to_dict()
    print(f"[共享图谱] 节点 {len(gd['nodes'])} / 边 {len(gd['edges'])}")

    # 2) 模拟 Researcher 写入一条核验事实到共享图
    kg.add_node("fact_credit_clean", "Fact",
                subject="applicant_A7291", claim="36个月信用记录无逾期",
                verified=True, verified_by="Researcher")
    print("[Researcher] 已写入核验事实: 36个月信用记录无逾期")

    # 3) 模拟 DecisionAdvisor 基于共享图做决策并记录(经 DecisionKit 的底层 = 共享图)
    did = shared.record_decision(
        category="loan_underwriting",
        scenario="A-7291 贷款审批: 收入85k, DTI 31%, 信用记录干净",
        reasoning="DTI 31% 在政策上限内;核验员确认36个月信用无逾期;风险等级 B2",
        outcome="approved",
        confidence=0.94,
        agent_role="DecisionAdvisor",   # ← 责任主体(SharedContext 用 agent_role 标记)
        entities=["applicant_A7291", "loan_A7291"],
    )
    print(f"[DecisionAdvisor] 已记录决策: {did[:8]}…  outcome=approved")

    # 4) 验证:决策落进了两个 agent 共享的同一张图
    gd2 = kg.to_dict()
    decision_nodes = [n for n in gd2["nodes"] if n.get("type") == "decision"]
    print(f"\n[验证] 共享图中决策节点数: {len(decision_nodes)}")
    if decision_nodes:
        d = decision_nodes[0]["properties"]
        print(f"        category={d.get('category')} outcome={d.get('outcome')} "
              f"confidence={d.get('confidence')} by={d.get('decision_maker') or d.get('agent_role') or '?'}")
    print(f"[验证] 共享图中事实节点(核验员写的): "
          f"{len([n for n in gd2['nodes'] if n.get('type')=='Fact'])} 条")

    print("\n→ 双 agent 共享同一 Semantica 上下文:核验员写事实 / 决策顾问记决策,落到同一张可审计图 ✔")
    print("  (配 LLM key 后,运行不带 --wiring-only 即可让 agent 自主完成上述流程)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiring-only", action="store_true",
                    help="只验证集成层接线,不调用 LLM")
    args = ap.parse_args()

    print("=" * 60)
    print("  Agno 双 Agent + Semantica 决策集成(贷款审批)")
    print("=" * 60)

    shared = build_shared_context()
    print("✓ 共享上下文就绪(AgnoSharedContext: ContextGraph + 决策账本)")

    if args.wiring_only:
        # 不实例化 Agent(避免触发 Model 选择),直接验证共享层
        verify_wiring(shared)
        return

    # 完整 agent 模式:建团队并运行
    try:
        team, researcher, advisor = build_team(shared)
        print(f"\n✓ 团队就绪: {researcher.name} + {advisor.name},共享同一上下文")
        print("\n[运行] team.run() —— 由 LLM 驱动 agent 自主协作...")
        result = team.run("审批申请人 A-7291 的 85000 美元个人贷款。")
        print("\n[团队输出]")
        print(result)
        verify_wiring(shared)  # 跑完再看共享账本里落了什么
    except RuntimeError as e:
        print(f"\n⚠ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
