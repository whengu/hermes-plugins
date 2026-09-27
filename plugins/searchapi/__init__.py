"""元搜索 API 插件 — 通过自建元搜索引擎提供 web_search 能力。"""

from __future__ import annotations

from .provider import SearchAPIWebSearchProvider


def register(ctx) -> None:
    """注册为 web search provider。"""
    ctx.register_web_search_provider(SearchAPIWebSearchProvider())