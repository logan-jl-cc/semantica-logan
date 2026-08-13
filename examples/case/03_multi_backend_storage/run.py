"""案例 03 — 多后端组合:内存图 + Oxigraph(RDF) + FAISS(向量) + SQLite(溯源)。

演示同一条决策被同时写入四个不同后端,各自独立可读回。
零外部服务(Oxigraph 内嵌、FAISS 内存、SQLite 本地文件)。
运行: python examples/case/03_multi_backend_storage/run.py
"""
import os
import shutil

from semantica.context import ContextGraph
from semantica.provenance import ProvenanceManager
from semantica.semantic_extract.triplet_extractor import Triplet  # 与测试同源
from semantica.triplet_store.oxigraph_store import OxigraphStore
from semantica.vector_store import VectorStore

# 持久化路径(案例可重复运行:先清空)
SQLITE_PATH = "/tmp/semantica_case03_prov.db"
OXI_DIR = "/tmp/semantica_case03_rdf"
NS = "https://semantica.dev/ns#"


def main():
    for p in (SQLITE_PATH, OXI_DIR):
        if os.path.exists(p):
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    print("=" * 60)
    print("  组合 4 个后端:内存图 + Oxigraph + FAISS + SQLite")
    print("=" * 60)

    # ① 内存 ContextGraph(图结构 + 决策)
    graph = ContextGraph(advanced_analytics=True)

    # ② Oxigraph 内嵌 RDF(持久化到目录)
    rdf = OxigraphStore(storage_path=OXI_DIR)

    # ③ FAISS 向量库(内存)
    vs = VectorStore(backend="inmemory", dimension=64)

    # ④ ProvenanceManager → SQLite(持久化溯源)
    prov = ProvenanceManager(storage_path=SQLITE_PATH)

    # [1] 记录一条决策 → 写入图 + 溯源
    did = graph.record_decision(
        category="loan_underwriting",
        scenario="A-7291 承销复核, DTI 31%",
        reasoning="DTI 在政策内;36个月信用记录干净;风险B2",
        outcome="approved", confidence=0.94,
        decision_maker="alice", entities=["loan_A7291"],
    )
    prov.track_entity(did, source="loan_system/api",
                      metadata={"category": "loan_underwriting"})
    print(f"\n[1] 决策已记录: {did[:8]}…  → 图 + SQLite 溯源 ✓")

    # [2] 图导出为 RDF 三元组 → 写入 Oxigraph
    gd = graph.to_dict()
    triplets = [
        Triplet(subject=NS + n["id"], predicate=NS + "type", object=n["type"])
        for n in gd["nodes"]
    ]
    res = rdf.add_triplets(triplets)
    print(f"[2] Oxigraph 写入三元组: {res.get('triplets_loaded')}  → RDF ✓")

    # [3] 决策理由生成向量 → 写入 FAISS
    vs.store_decision(scenario="A-7291 承销复核, DTI 31%",
                      outcome="approved", confidence=0.94,
                      category="loan_underwriting")
    print("[3] FAISS 存入决策向量  → 向量 ✓")

    # ===== 验证四个后端各自读回 =====
    print("\n" + "=" * 60)
    print("  验证:四个后端各自独立读回")
    print("=" * 60)

    v1 = graph.to_dict()
    print(f"[① 内存图]      节点 {len(v1['nodes'])} / 边 {len(v1['edges'])}")

    # 释放原实例持有的文件锁,才能在同进程里重新打开磁盘库
    import gc
    del rdf
    gc.collect()
    reopened_rdf = OxigraphStore(storage_path=OXI_DIR)
    triples = reopened_rdf.get_triplets()
    print(f"[② Oxigraph RDF] 重新打开磁盘库,三元组: {len(triples)} 条")

    hits = vs.search("loan underwriting", limit=3)
    print(f"[③ FAISS 向量]  相似检索命中: {len(hits)} 条")

    reopened_prov = ProvenanceManager(storage_path=SQLITE_PATH)
    stats = reopened_prov.get_statistics()
    entries = stats.get("total_entries", "?") if stats else "?"
    print(f"[④ SQLite 溯源] 重新打开,条目数: {entries}")

    print(f"\n→ 同一决策已同时落进 4 个后端 ✔")
    print(f"  持久化文件: SQLite={os.path.getsize(SQLITE_PATH)}B "
          f"Oxigraph 目录={len(os.listdir(OXI_DIR))} 个文件")
    print("  (进程结束后,SQLite 与 Oxigraph 数据仍在;内存图与 FAISS 需重新加载)")


if __name__ == "__main__":
    main()
