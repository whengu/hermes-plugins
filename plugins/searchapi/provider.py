"""元搜索引擎 web search provider。

通过自建元搜索 API（Playwright + CDP 真实浏览器聚合百度/必应/搜狗）提供
web_search 能力。请求链路：

    本机 -> 44 nginx (:8000 /to68/) -> 68 nginx-proxy (:24123 /searchAPI/)
         -> cdp_search_engine 容器 (:18999) -> 元搜索服务

Search-only —— 网页提取仍由 web.extract_backend（firecrawl）负责。
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

_DEFAULT_API_BASE = "http://192.168.155.44:8000/to68/searchAPI"
_DEFAULT_TIMEOUT_S = 90


def _api_base() -> str:
    """返回元搜索 API 基础地址：优先 SEARCHAPI_URL 环境变量，缺省用内网入口。"""
    try:
        from hermes_cli.config import get_env_value

        val = get_env_value("SEARCHAPI_URL")
    except Exception:  # noqa: BLE001
        val = None
    if val is None:
        val = os.getenv("SEARCHAPI_URL", "")
    val = (val or "").strip()
    if not val:
        return _DEFAULT_API_BASE
    return val.rstrip("/")


class SearchAPIWebSearchProvider(WebSearchProvider):
    """Search via the self-hosted metasearch engine API."""

    @property
    def name(self) -> str:
        return "searchapi"

    @property
    def display_name(self) -> str:
        return "元搜索API (68)"

    def is_available(self) -> bool:
        """自建服务无需密钥，配置入口存在即可用。"""
        return bool(_api_base())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        import httpx

        base_url = _api_base()
        if not base_url:
            return {"success": False, "error": "SEARCHAPI_URL is not set"}

        params: Dict[str, Any] = {
            "keyword": query,
            "max_results": limit,
        }

        try:
            resp = httpx.get(
                f"{base_url}/api/search",
                params=params,
                timeout=_DEFAULT_TIMEOUT_S,
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.warning("元搜索 API HTTP error: %s", exc)
            return {
                "success": False,
                "error": f"元搜索 API returned HTTP {exc.response.status_code}",
            }
        except httpx.RequestError as exc:
            logger.warning("元搜索 API request error: %s", exc)
            return {
                "success": False,
                "error": f"Could not reach 元搜索 API at {base_url}: {exc}",
            }

        try:
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("元搜索 API response parse error: %s", exc)
            return {
                "success": False,
                "error": "Could not parse 元搜索 API response as JSON",
            }

        raw_results = data.get("results", [])[:limit]

        web_results = [
            {
                "title": str(r.get("title", "")),
                "url": str(r.get("url", "")),
                "description": str(r.get("content", "")),
                "position": i + 1,
            }
            for i, r in enumerate(raw_results)
        ]

        logger.info(
            "元搜索 API '%s': %d results (limit %d)",
            query,
            len(web_results),
            limit,
        )

        return {"success": True, "data": {"web": web_results}}

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "元搜索API (68)",
            "badge": "self-hosted",
            "tag": "自建元搜索引擎（百度/必应/搜狗聚合），经 44 nginx /to68 入口访问。",
            "env_vars": [
                {
                    "key": "SEARCHAPI_URL",
                    "prompt": "元搜索 API 基础地址（默认 http://192.168.155.44:8000/to68/searchAPI）",
                    "url": "",
                },
            ],
        }