# 案例 05 — Knowledge Explorer(浏览器工作台)

演示启动 Semantica 自带的**浏览器图工作台**(React 19 + Sigma.js),加载一个图 JSON,在 GUI 里探索决策与因果链。

## 这个案例展示什么

- 启动 `semantica-explorer` 服务(FastAPI 后端 + 预构建前端)
- 加载决策图 JSON(复用案例 01 生成的 `graph.json`)
- 浏览器工作区:Knowledge Graph / Decisions(因果链) / Analyze / Ontology Hub

## 前置

需要已构建前端(本仓库已完成 `npm run build`,产物在 `semantica/static/`)+ explorer Python 依赖:
```bash
pip install "semantica[explorer]"   # fastapi / uvicorn / websockets
```
本仓库 venv 已具备以上条件。

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate

# 先生成图数据(若 examples/case/01_.../graph.json 不存在)
python examples/case/01_decision_intelligence/run.py

# 启动工作台
python examples/case/05_explorer_server/run.py
```
浏览器自动打开 http://127.0.0.1:8000 。

## 关键端点(服务启动后)

| 端点 | 作用 |
|---|---|
| `/` | 工作台首页 |
| `/docs` | Swagger API 文档 |
| `/api/graph/stats` | 图统计 |
| `/api/decisions` | 决策列表 |
| `/api/decisions/{id}/chain` | 决策因果链 |

## 注意

- 绑定 `127.0.0.1`(仅本机);生产部署需配持久化图库后端(Neo4j 等)。
- 停止服务:`Ctrl+C`,或 `pkill -f semantica-explorer`。
