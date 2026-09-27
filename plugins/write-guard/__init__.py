"""write-guard 插件入口：注册 pre_tool_call hook。"""


def register(ctx):
    import logging
    from pathlib import Path

    import importlib.util

    # R-4：按文件路径加载为唯一模块身份（write_guard_handler），不进 sys.path、
    # 不占通用模块名 —— 避免多插件同名 handler.py 在 sys.modules 互相遮蔽。
    path = Path(__file__).resolve().parent / "handler.py"
    spec = importlib.util.spec_from_file_location("write_guard_handler", str(path))
    handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler)

    logging.getLogger(__name__).info("write-guard loaded from %s", path)
    ctx.register_hook("pre_tool_call", handler.on_pre_tool_call)
