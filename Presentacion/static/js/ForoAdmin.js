document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modalCrearTema");
  const btn = document.getElementById("crearTemaBtn");
  const span = document.querySelector(".cerrar");

  btn.onclick = () => (modal.style.display = "block");
  span.onclick = () => (modal.style.display = "none");
  window.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };

  cargarTemasAdmin();

  document
    .getElementById("formNuevoTema")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      fetch("/api/admin/crear-tema", {
        method: "POST",
        body: formData,
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            modal.style.display = "none";
            cargarTemasAdmin();
          } else {
            alert("Error al crear el tema");
          }
        });
    });
});

function cargarTemasAdmin() {
  fetch("/api/foro/temas")
    .then((r) => r.json())
    .then((temas) => {
      let html = "<ul>";
      temas.forEach((tema, index) => {
        html += `<li class="tema-item" data-index="${index}" style="cursor:pointer;">${tema.titulo}</li>`;
      });
      html += "</ul>";
      document.getElementById("temasAdmin").innerHTML = html;
      document.querySelectorAll('.tema-item').forEach(item => {
        item.addEventListener('click', function() {
          const index = this.getAttribute('data-index');
          verComentariosAdmin(temas[index]);
        });
      });
    })
    .catch(error => console.error("Error al cargar los temas del foro:", error));
}

function verComentariosAdmin(tema) {
  fetch(`/api/foro/temas/${tema._id}/comentarios`)
    .then((r) => r.json())
    .then((comentarios) => {
      let html = `<h3>${tema.titulo}</h3><p>${tema.descripcion}</p><hr>`;
      if (comentarios.length === 0) {
        html += `<p>No hay comentarios aún.</p>`;
      } else {
        comentarios.forEach((c) => {
          html += `<div class="comentario"><strong>${c.autor}</strong>: ${c.comentario}`;
          if (c.imagen_url) {
            html += `<br><img src="${c.imagen_url}" style="max-width: 200px;">`;
          }
          html += `</div><hr>`;
        });
      }
      document.getElementById("comentariosAdmin").innerHTML = html;
    });
}
