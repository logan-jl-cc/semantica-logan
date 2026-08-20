"""案例 05 — 启动 Knowledge Explorer 浏览器工作台。

加载案例 01 生成的 graph.json,启动 FastAPI 服务,自动打开浏览器。
运行: python examples/case/05_explorer_server/run.py
"""
import os
import subprocess
import sys

# 复用案例 01 生成的 graph.json
GRAPH_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "01_decision_intelligence", "graph.json",
)
GRAPH_JSON = os.path.abspath(GRAPH_JSON)

VENV_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".venv", "bin")
EXPLORER = os.path.abspath(os.path.join(VENV_BIN, "semantica-explorer"))


def main():
    if not os.path.exists(GRAPH_JSON):
        print("graph.json 不存在,先运行案例 01 生成:")
        print("  python examples/case/01_decision_intelligence/run.py")
        sys.exit(1)

    if not os.path.exists(EXPLORER):
        print("semantica-explorer 未找到。请先安装:")
        print('  pip install "semantica[explorer]"')
        sys.exit(1)

    print("=" * 60)
    print("  Semantica Knowledge Explorer")
    print("=" * 60)
    print(f"  图数据: {GRAPH_JSON}")
    print(f"  地址:   http://127.0.0.1:8000")
    print(f"  API 文档: http://127.0.0.1:8000/docs")
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)

    # 启动服务(前台运行,带 --no-browser 由调用者手动开,或去掉该 flag 自动开)
    # v0.6.5 起上游给 API 加了认证:本地开发用 SEMANTICA_ALLOW_ANONYMOUS=true 豁免;
    # 共享部署请改用 SEMANTICA_API_KEY=<secret>(客户端请求需带 X-API-Key 头)。
    env = os.environ.copy()
    if not env.get("SEMANTICA_API_KEY"):
        env.setdefault("SEMANTICA_ALLOW_ANONYMOUS", "true")
        print("  认证:本地匿名模式(SEMANTICA_ALLOW_ANONYMOUS=true)")
    else:
        print("  认证:API key 模式(客户端需带 X-API-Key 头)")
    cmd = [EXPLORER, "--graph", GRAPH_JSON, "--port", "8000", "--host", "127.0.0.1"]
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n已停止 Explorer 服务")


if __name__ == "__main__":
    main()
