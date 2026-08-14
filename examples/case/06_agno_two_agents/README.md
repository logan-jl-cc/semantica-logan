# 案例 06 — Agno 双 Agent + Semantica 决策集成

用一个 **Agno 双 agent** 团队完成"贷款审批"决策,两个 agent **共享同一份 Semantica 上下文图与决策账本**。

## 场景

| Agent | 职责 | 用的 Semantica 工具 |
|---|---|---|
| **核验员** (Researcher) | 核验申请人收入/信用/DTI,把事实写入共享知识图谱 | `AgnoKGToolkit`(extract_entities / add_to_graph / query_graph) |
| **决策顾问** (DecisionAdvisor) | 基于共享图谱的事实,做出审批决策并记录(带因果) | `AgnoDecisionKit`(record_decision / trace_causal_chain / check_policy) |

两人读写**同一张** `AgnoSharedContext` → 核验员写入的事实,决策顾问立刻可读;最终决策进入可审计的决策账本。

## 前置

```bash
pip install "semantica[agno]"      # agno 框架(本仓库 venv 已装)
# agent.run() 需要一个 LLM,二选一:
export OPENAI_API_KEY=sk-...        # 云端 LLM
# 或本地起 Ollama:  ollama serve && ollama pull qwen2.5:7b
```

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate

# A) 完整 agent 运行(需要 LLM key):
python examples/case/06_agno_two_agents/run.py

# B) 仅验证集成层接线(无需 LLM,本机可跑):
python examples/case/06_agno_two_agents/run.py --wiring-only
```

## 关键点

- `AgnoSharedContext` 让多 agent 共享一份 ContextGraph + 决策账本(无需复制同步)。
- 每个 agent 用 `shared.bind_agent(role)` 绑同一份共享记忆。
- 决策一经 `record_decision` 记录,即成为可追溯、可审计的一等节点(满足《决策原生方法论》的可审计+可追责)。
- Agno 当前版本 `Team` 用 `members=`(非旧文档的 `agents=`)。

## 注意

- agent 数量 ≠ Semantica 价值。单 agent / 无 agent 也能用 Semantica;双 agent 只在需要"分工 + 共享上下文"时才必要。
