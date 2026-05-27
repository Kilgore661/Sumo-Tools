function wirePAPanelLayout() {
  updateStickyArtifactHeaders();
  window.requestAnimationFrame(updateStickyArtifactHeaders);
}

function updateStickyArtifactHeaders() {
  document.querySelectorAll(".pa-slot").forEach(slot => {
    const title = slot.querySelector(":scope > .artifact-title-block");
    const titleHeight = title ? Math.ceil(title.getBoundingClientRect().height) : 0;
    slot.style.setProperty("--artifact-title-sticky-offset", `${titleHeight}px`);
    slot.querySelectorAll(".artifact-table").forEach(table => {
      const sectionHeading = table.closest(".table-section")?.querySelector(":scope > h5");
      const sectionHeadingHeight = sectionHeading
        ? Math.ceil(sectionHeading.getBoundingClientRect().height)
        : 0;
      if (sectionHeading) {
        sectionHeading.style.top = `${titleHeight}px`;
      }
      let top = titleHeight + sectionHeadingHeight;
      table.querySelectorAll("thead tr").forEach(row => {
        row.querySelectorAll("th").forEach(cell => {
          cell.style.top = `${top}px`;
        });
        top += Math.ceil(row.getBoundingClientRect().height);
      });
    });
  });
}

export { wirePAPanelLayout, updateStickyArtifactHeaders };
