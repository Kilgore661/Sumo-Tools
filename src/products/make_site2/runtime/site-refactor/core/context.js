function bootSiteContext() {
  const context = siteContext();
  document.body.classList.add(`site-context-${context.id}`);
  if (context.titlePrefix) {
    document.title = `${context.titlePrefix} ${document.title}`;
  }
}
function siteContext() {
  const hostname = window.location.hostname.toLowerCase();
  if (hostname === "68.66.241.105" || hostname === "www.661.org.uk" || hostname === "661.org.uk") {
    return { id: "remote", label: "Remote Site", titlePrefix: "REMOTE" };
  }
  if (hostname.startsWith("192.168.")) {
    return { id: "local", label: "Danger Dr. Smith! Waterfall model detected! - B-9" };
  }
  return { id: "preview", label: "Preview Site", titlePrefix: "PREVIEW" };
}

export { bootSiteContext, siteContext };
