"""Firecrawl（前缀修复）web 插件 — 内置 firecrawl provider 的用户插件副本。

修复 firecrawl-py SDK v2 的 urljoin 缺陷：api_url 带路径前缀（如 /firecrawl）
时，SDK 内部 _build_url 用 urljoin 会把前缀吞掉，导致请求打到
http://host:port/v1/scrape 而非 /firecrawl/v1/scrape。插件在 _get_firecrawl_client
中 monkey-patch _build_url 拼回前缀（补丁逻辑随文件一起复制，位于 provider.py 内）。

放在用户插件目录（~/.hermes/plugins/web/），独立于 repo 源码，hermes update 不会覆盖。
"""

from __future__ import annotations

from .provider import FirecrawlWebSearchProvider


def register(ctx) -> None:
    """注册为 web search/extract provider。"""
    ctx.register_web_search_provider(FirecrawlWebSearchProvider())