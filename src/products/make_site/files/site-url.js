(function () {
  const DEFAULT_CACHE_PARAM = "cb";
  const DEFAULT_PAGE_PARAM = "page";

  function siteUrlConfig(scope = document.body) {
    return {
      cacheMode: scope?.dataset.cacheMode || "dev",
      cacheBust: scope?.dataset.cacheBust || "",
      cacheBustParam: scope?.dataset.cacheBustParam || DEFAULT_CACHE_PARAM,
      pageParam: scope?.dataset.deepLinkPageParam || DEFAULT_PAGE_PARAM
    };
  }

  function toUrl(value, base = window.location.href) {
    return new URL(value, base);
  }

  function mergeParams(urlValue, params, base) {
    const url = toUrl(urlValue, base);
    for (const [key, value] of Object.entries(params || {})) {
      if (value === undefined || value === null || value === "") {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, String(value));
      }
    }
    return url;
  }

  function withParams(urlValue, params, base) {
    return mergeParams(urlValue, params, base).toString();
  }

  function displayUrl(urlValue, base) {
    const url = toUrl(urlValue, base);
    if (url.origin === window.location.origin) {
      return `${url.pathname}${url.search}${url.hash}`;
    }
    return url.toString();
  }

  function withDisplayParams(urlValue, params, base) {
    return displayUrl(mergeParams(urlValue, params, base), base);
  }

  function withoutParams(urlValue, paramNames, base) {
    const url = toUrl(urlValue, base);
    for (const name of paramNames || []) {
      url.searchParams.delete(name);
    }
    return url;
  }

  function withoutDisplayParams(urlValue, paramNames, base) {
    return displayUrl(withoutParams(urlValue, paramNames, base), base);
  }

  function cacheBustParams(config = siteUrlConfig()) {
    if (config.cacheMode !== "dev" || !config.cacheBust) return {};
    return { [config.cacheBustParam || DEFAULT_CACHE_PARAM]: config.cacheBust };
  }

  function withCacheBust(urlValue, config = siteUrlConfig(), base) {
    return withDisplayParams(urlValue, cacheBustParams(config), base);
  }

  function readSearchState(search = window.location.search, config = siteUrlConfig()) {
    const params = new URLSearchParams(search);
    params.delete(config.cacheBustParam || DEFAULT_CACHE_PARAM);
    return Object.fromEntries(params.entries());
  }

  function readShellState(search = window.location.search, config = siteUrlConfig()) {
    const state = readSearchState(search, config);
    const page = state[config.pageParam || DEFAULT_PAGE_PARAM] || "";
    delete state[config.pageParam || DEFAULT_PAGE_PARAM];
    return { page, params: state };
  }

  function buildShellSearch(page, params = {}, config = siteUrlConfig()) {
    const search = new URLSearchParams();
    if (page) search.set(config.pageParam || DEFAULT_PAGE_PARAM, page);
    for (const [key, value] of Object.entries(cacheBustParams(config))) {
      search.set(key, value);
    }
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        search.set(key, String(value));
      }
    }
    return search.toString();
  }

  window.SiteUrl = {
    buildShellSearch,
    cacheBustParams,
    displayUrl,
    readSearchState,
    readShellState,
    siteUrlConfig,
    withCacheBust,
    withDisplayParams,
    withParams,
    withoutDisplayParams,
    withoutParams
  };
}());
