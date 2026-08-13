# 案例 03 — 多后端组合存储

演示 Semantica 的存储是**可多选组合**的:同一条数据可同时落进多个不同用途的后端。

## 这个案例展示什么

四个后端同时工作(零外部服务):
- **内存 ContextGraph** — 图结构 + 决策(默认,易失)
- **Oxigraph** — 内嵌 RDF 三元组库(持久化到磁盘目录)
- **FAISS** — 向量库(语义检索)
- **SQLite** — ProvenanceManager 溯源(持久化)

## 前置

```bash
pip install pyoxigraph    # 本仓库 venv 已装
```

## 运行

```bash
cd /Users/administrator/Semantica-logan
source .venv/bin/activate
python examples/case/03_multi_backend_storage/run.py
```

## 关键点

- **跨类后端自由组合**(图库 + 向量库 + 溯源库),这是设计的常态。
- **同类后端单选**(一个 ContextGraph 持有一个图后端)。
- Oxigraph 用 `storage_path=`(本仓库已修复的别名)或 `path=` 指定**目录**。
- 持久化文件落在 `/tmp`,进程结束后仍可重新打开验证。

## 注意

- RDF 三元组的 subject 必须是合法 IRI(如 `https://x/a`),不能用裸 UUID。
