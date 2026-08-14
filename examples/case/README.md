# Semantica 案例集

今天对 Semantica 探索过程中产生的可运行案例,每个案例一个独立文件夹、可独立运行。

## 环境前置(一次性)

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate    # Python 3.11 venv,已装好核心依赖
```

## 案例清单

| # | 案例 | 演示什么 | 命令 |
|---|---|---|---|
| 01 | [决策智能](01_decision_intelligence/) | 记录因果决策链 → 影响分析 → 合规校验 → PROV-O 审计导出 | `python examples/case/01_decision_intelligence/run.py` |
| 02 | [离线管线](02_offline_pipeline/) | 文本 → NER → 关系抽取 → KG → 规则推理(零 LLM) | `python examples/case/02_offline_pipeline/run.py` |
| 03 | [多后端组合](03_multi_backend_storage/) | 内存图 + Oxigraph + FAISS + SQLite 四后端同时写入 | `python examples/case/03_multi_backend_storage/run.py` |
| 04 | [可视化](04_visualization/) | 项目自带 KGVisualizer 导出交互式 HTML | `python examples/case/04_visualization/run.py` |
| 05 | [Explorer 工作台](05_explorer_server/) | 启动浏览器图工作台(加载案例 01 的图) | `python examples/case/05_explorer_server/run.py` |
| 06 | [Agno 双 Agent](06_agno_two_agents/) | Agno 双 agent 团队共享 Semantica 上下文做贷款审批 | `python examples/case/06_agno_two_agents/run.py --wiring-only` |

## 案例间的依赖

```
01 决策智能 ──生成 graph.json──▶ 05 Explorer 工作台(复用该图)
```
其余案例(02/03/04)相互独立。

## 已验证

- 01–04 已在本机 venv 实测跑通(见各文件夹下的产物,如 `loan_audit.ttl` / `graph.json` / `graph.html`)。
- 05 需常驻服务,运行后浏览器访问 http://127.0.0.1:8000 。

## 产物说明(部分会生成)

- `01_.../loan_audit.ttl` — PROV-O 审计文件(可提交监管)
- `01_.../graph.json` — 图数据(供 explorer 加载)
- `04_.../graph.html` — 交互式知识图谱(浏览器打开)
- `03_...` 的持久化文件落在 `/tmp/`(进程结束仍在)
