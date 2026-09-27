"""toast-notify 插件入口：注册 post_llm_call / pre_approval_request 两个观察者 hook。

按 write-guard 同款 R-4 约定：handler 按文件路径加载为唯一模块身份（toast_notify_handler），
不进 sys.path、不占通用模块名，避免多插件同名 handler.py 互相遮蔽。
"""


def register(ctx):
    import logging
    from pathlib import Path

    import importlib.util

    path = Path(__file__).resolve().parent / "handler.py"
    spec = importlib.util.spec_from_file_location("toast_notify_handler", str(path))
    handler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler)

    logging.getLogger(__name__).info("toast-notify loaded from %s", path)
    ctx.register_hook("post_llm_call", handler.on_post_llm_call)
    ctx.register_hook("pre_approval_request", handler.on_pre_approval_request)
