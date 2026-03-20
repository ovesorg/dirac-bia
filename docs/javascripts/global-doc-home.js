(function () {
  function normalizeDirectoryUrl() {
    var current = new URL(window.location.href);
    if (current.pathname.endsWith("/")) {
      return;
    }
    var tail = current.pathname.split("/").pop() || "";
    if (tail.indexOf(".") >= 0) {
      return;
    }
    current.pathname += "/";
    window.location.replace(current.toString());
  }

  function normalizeUrl(value) {
    return String(value || "").trim();
  }

  function withGlobalSearchQuery(target, query) {
    var url = new URL(target, window.location.href);
    url.searchParams.delete("q");
    url.searchParams.delete("query");
    if (query) {
      url.hash = "oves-global-query=" + encodeURIComponent(query);
    } else {
      url.hash = "";
    }
    return url.toString();
  }

  function isLocalHost() {
    return new Set(["127.0.0.1", "localhost"]).has(window.location.hostname);
  }

  function getHubConfig() {
    var globalLink = document.querySelector("a.oves-global-search-link[data-oves-hub-cloud-home]");
    var homeLink = document.querySelector("[data-oves-hub-home-link][data-oves-hub-cloud-home]");
    var source = globalLink || homeLink;
    if (!source) {
      return null;
    }
    return {
      cloudHome: normalizeUrl(source.getAttribute("data-oves-hub-cloud-home")),
      localHome: normalizeUrl(source.getAttribute("data-oves-hub-local-home"))
    };
  }

  function targetUrl(config) {
    if (!config || !config.cloudHome) {
      return "";
    }
    if (isLocalHost() && config.localHome) {
      return config.localHome;
    }
    return config.cloudHome;
  }

  function rewriteHubLinks(config) {
    var href = targetUrl(config);
    if (!href) {
      return;
    }
    var globalHref = href.replace(/\/$/, "") + "/global-search/";
    document
      .querySelectorAll("[data-oves-hub-home-link][href]")
      .forEach(function (link) {
        link.href = href;
        link.title = "Back to Document Hub";
        link.setAttribute("aria-label", "Back to Document Hub");
      });
    document
      .querySelectorAll("a.oves-global-search-link[href]")
      .forEach(function (link) {
        link.href = globalHref;
        link.title = "Search all docs";
        link.setAttribute("aria-label", "Search all docs");
      });
  }

  function currentLocalSearchQuery() {
    var input = document.querySelector(".md-search__input");
    return input ? String(input.value || "").trim() : "";
  }

  function bindGlobalSearchLinks() {
    if (!document.querySelector("a.oves-global-search-link")) {
      return;
    }
    document
      .querySelectorAll("a.oves-global-search-link[href]")
      .forEach(function (link) {
        if (link.dataset.ovesGlobalBound === "1") {
          return;
        }
        link.dataset.ovesGlobalBound = "1";
        link.addEventListener("click", function (event) {
          event.preventDefault();
          var target = link.href;
          var query = currentLocalSearchQuery();
          target = withGlobalSearchQuery(target, query);
          window.location.href = target;
        });
      });
  }

  function start() {
    normalizeDirectoryUrl();
    var config = getHubConfig();
    if (!config) {
      return;
    }
    rewriteHubLinks(config);
    bindGlobalSearchLinks();
    if (window.document$ && typeof window.document$.subscribe === "function") {
      window.document$.subscribe(function () {
        rewriteHubLinks(config);
        bindGlobalSearchLinks();
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
