const frame = document.getElementById("content-frame");
const framePanel = document.getElementById("frame-panel");
const welcomePanel = document.getElementById("welcome-panel");
const navLinks = document.querySelectorAll(".nav-link");

for (const link of navLinks) {
  link.addEventListener("click", event => {
    event.preventDefault();
    selectPage(link);
  });
}

function selectPage(link) {
  const frameSrc = link.dataset.frameSrc;
  frame.src = frameSrc;
  welcomePanel.hidden = true;
  framePanel.hidden = false;
}
