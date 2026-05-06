const frame = document.getElementById("content-frame");
const framePanel = document.getElementById("frame-panel");
const welcomePanel = document.getElementById("welcome-panel");
const activeTitle = document.getElementById("active-title");
const activeSummary = document.getElementById("active-summary");
const openPage = document.getElementById("open-page");
const navLinks = document.querySelectorAll(".nav-link");

for (const link of navLinks) {
  link.addEventListener("click", event => {
    event.preventDefault();
    selectPage(link);
  });
}

function selectPage(link) {
  const frameSrc = link.dataset.frameSrc;
  activeTitle.textContent = link.dataset.title;
  activeSummary.textContent = link.dataset.summary;
  frame.src = frameSrc;
  openPage.href = link.href;
  openPage.hidden = false;
  welcomePanel.hidden = true;
  framePanel.hidden = false;
}
