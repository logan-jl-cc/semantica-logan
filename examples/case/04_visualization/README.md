# 案例 04 — 可视化(KGVisualizer)

演示用项目自带的 `KGVisualizer` 把知识图谱导出为**可交互的 HTML**(基于 Plotly,可拖拽/缩放/悬停)。

## 这个案例展示什么

- 构建 KG → 用 `KGVisualizer` 导出交互式 HTML
- 项目自带的可视化能力(不是手写图)

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate
python examples/case/04_visualization/run.py
# 生成的 HTML 会自动在浏览器打开
```

## 关键 API

| API | 作用 |
|---|---|
| `KGVisualizer(layout="force")` | 力导向布局可视化器 |
| `viz.visualize_network(kg, output="interactive", file_path=...)` | 导出交互式 HTML |

## 其他可视化器(同理可用)

- `OntologyVisualizer` — 本体类层级树
- `EmbeddingVisualizer` — 嵌入 2D 投影(UMAP/t-SNE/PCA)
- `TemporalVisualizer` — 时间轴
