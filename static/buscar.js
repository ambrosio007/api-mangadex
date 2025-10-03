// Abre e fecha dropdown ao clicar no botão
document.querySelectorAll(".dropdown-btn").forEach(btn => {
  btn.addEventListener("click", function(e) {
    e.stopPropagation(); // evita conflito com o listener global
    this.parentElement.classList.toggle("show");
  });
});

// Fecha dropdown apenas se clicar fora de todos eles
window.addEventListener("click", function(event) {
  document.querySelectorAll(".dropdown").forEach(dropdown => {
    if (!dropdown.contains(event.target)) {
      dropdown.classList.remove("show");
    }
  });
});

// Captura valores antes de enviar (opcional)
document.getElementById("filtroForm").addEventListener("submit", function(e) {
  const incluir = Array.from(document.querySelectorAll("input[name='incluir']:checked")).map(el => el.value);
  const excluir = Array.from(document.querySelectorAll("input[name='excluir']:checked")).map(el => el.value);

  console.log("Incluir:", incluir);
  console.log("Excluir:", excluir);
});
