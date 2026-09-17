"""write-guard 插件入口：注册 pre_tool_call hook。"""


def register(ctx):
    import logging

    logger = logging.getLogger(__name__)
    # 插件加载时以本文件所在目录为根导入 handler（避免相对导入对加载上下文的依赖）
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import handler

    ctx.register_hook("pre_tool_call", handler.on_pre_tool_call)
    logger.info("write-guard: pre_tool_call hook 已注册")
