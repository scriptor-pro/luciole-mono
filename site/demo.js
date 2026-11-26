// Terminal de démonstration : taille et style du texte saisi.
const screen = document.querySelector(".screen");
const size = document.querySelector("#size");
const sizeOut = document.querySelector("#size-out");
const pt = (px) => Math.round(px * 0.75 * 10) / 10;

function setSize() {
  screen.style.fontSize = size.value + "px";
  sizeOut.textContent = `${size.value} px (${pt(size.value)} pt)`;
}
size.addEventListener("input", setSize);
setSize();

for (const button of document.querySelectorAll(".styles button")) {
  button.addEventListener("click", () => {
    for (const other of document.querySelectorAll(".styles button")) {
      other.setAttribute("aria-pressed", String(other === button));
    }
    screen.style.fontWeight = button.dataset.weight;
    screen.style.fontStyle = button.dataset.style;
  });
}
