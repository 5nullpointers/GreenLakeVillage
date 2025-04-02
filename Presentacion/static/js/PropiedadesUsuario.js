// PropiedadesUsuario.js

document.addEventListener('DOMContentLoaded', function () {
  // Llamada al backend para obtener propiedades del usuario
  fetch('/Propietarios/PropiedadesUsuario', {
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Error al obtener las propiedades del usuario.");
      }
      return response.json();
    })
    .then(data => {
      propiedadesData = data.map(prop => ({
        nombre: prop.nombre,
        tipo: prop.tipo_servicio || "N/A",
        cancelaciones: prop.ocupacion.cancelaciones || 0,
        reservas: prop.ocupacion.reservas_confirmadas || 0,
        precio: typeof prop.ocupacion.precio === "number"
          ? `${prop.ocupacion.precio} €`
          : (prop.ocupacion.precio || "N/A")
      }));

      updateTable();
    })
    .catch(error => console.error("Error al cargar propiedades:", error));

  initMenuInteracciones(); // Carga el comportamiento del menú
});

let propiedadesData = [];

// Rellena la tabla HTML con los datos
function updateTable() {
  const tbody = document.querySelector("#propiedadesTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  propiedadesData.forEach(prop => {
    const row = document.createElement("tr");

    ["nombre", "tipo", "cancelaciones", "reservas", "precio"].forEach(key => {
      const td = document.createElement("td");
      td.textContent = prop[key];
      row.appendChild(td);
    });

    tbody.appendChild(row);
  });
}

// Ordena columnas por click en el header
function sortColumn(colIndex) {
  const table = document.getElementById('propiedadesTable');
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));

  const currentSortDir = table.dataset.sortDir === 'asc' ? 'asc' : 'desc';
  const newSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
  table.dataset.sortDir = newSortDir;

  rows.sort((a, b) => {
    const cellA = a.querySelectorAll('td')[colIndex].innerText;
    const cellB = b.querySelectorAll('td')[colIndex].innerText;

    const valA = parseFloat(cellA.replace(',', '.')) || cellA.toLowerCase();
    const valB = parseFloat(cellB.replace(',', '.')) || cellB.toLowerCase();

    if (valA < valB) return newSortDir === 'asc' ? -1 : 1;
    if (valA > valB) return newSortDir === 'asc' ? 1 : -1;
    return 0;
  });

  tbody.innerHTML = '';
  rows.forEach(row => tbody.appendChild(row));
}

// Maneja interacciones del menú lateral y dropdown de usuario
function initMenuInteracciones() {
  const userName = document.querySelector('.user-name');
  const dropdown = document.getElementById('userDropdown');
  if (userName && dropdown) {
    userName.addEventListener('click', function (event) {
      dropdown.classList.toggle('open');
      event.stopPropagation();
    });

    document.addEventListener('click', function () {
      dropdown.classList.remove('open');
    });
  }

  const opciones = document.querySelectorAll('.menuPanel li');
  const nuevasImagenes = [
    "/static/images/inicioBlanco.png",
    "/static/images/PropiedadesBlanco.png",
    "/static/images/ReseñasBlanco.png",
    "/static/images/PrevisionesBlanco.png"
  ];

  opciones.forEach((opcion, index) => {
    opcion.addEventListener('mouseenter', function () {
      const img = opcion.querySelector('img');
      if (img && nuevasImagenes[index]) {
        if (!img.dataset.original) {
          img.dataset.original = img.src;
        }
        img.src = nuevasImagenes[index];
      }
    });

    opcion.addEventListener('mouseleave', function () {
      if (opcion.classList.contains('active')) return;
      const img = opcion.querySelector('img');
      if (img && img.dataset.original) {
        img.src = img.dataset.original;
      }
    });
  });
}
