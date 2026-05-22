"""URL policy helpers for generated public-site links."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .classes import SiteBuildConfig


def cache_busted_url(url: str, config: SiteBuildConfig, cache_bust_token: str) -> str:
    """Append the build cache-bust token to an internal generated URL."""

    if config.cache_mode != "dev" or not cache_bust_token:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[config.cache_bust_param] = cache_bust_token
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )
