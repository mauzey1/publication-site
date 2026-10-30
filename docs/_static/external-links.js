document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("a[href]").forEach((link) => {
    const destination = new URL(link.href, document.baseURI);
    if (
      ["http:", "https:"].includes(destination.protocol) &&
      destination.origin !== window.location.origin
    ) {
      link.target = "_blank";
      link.relList.add("noopener", "noreferrer");
    }
  });
});
