// PropiedadesUsuario.js
// Ejemplo sin paginación, columnas: Nombre, Tipo, Cancelaciones, Reservas, Precio

// Arreglo global para almacenar los datos de propiedades
let propiedadesData = [];

// 1) Al cargar la página, hacemos fetch al endpoint de propiedades
fetch('/propiedades')
  .then(response => {
    // Si tu backend retorna 403 cuando no hay autenticación o permisos
    if (response.status === 403) {
      window.location.href = '/login';
      return;
    }
    return response.json();
  })
  .then(data => {
    // data debe ser un array de propiedades con { nombre, tipo, cancelaciones, reservas, precio }
    propiedadesData = data;
    // Llamamos a la función que rellena la tabla
    updateTable();
  })
  .catch(error => console.error("Error al cargar las propiedades:", error));

// 2) Función para crear y mostrar filas en la tabla
function updateTable() {
  // Selecciona el <tbody> de la tabla
  const tbody = document.querySelector("#propiedadesTable tbody");
  if (!tbody) return;

  // Limpia las filas anteriores
  tbody.innerHTML = "";

  // Recorre cada propiedad y crea su fila <tr>
  propiedadesData.forEach(prop => {
    const row = document.createElement("tr");

    // Columna: Nombre
    const tdNombre = document.createElement("td");
    tdNombre.textContent = prop.nombre;
    row.appendChild(tdNombre);

    // Columna: Tipo
    const tdTipo = document.createElement("td");
    tdTipo.textContent = prop.tipo;
    row.appendChild(tdTipo);

    // Columna: Cancelaciones
    const tdCancelaciones = document.createElement("td");
    tdCancelaciones.textContent = prop.cancelaciones;
    row.appendChild(tdCancelaciones);

    // Columna: Reservas
    const tdReservas = document.createElement("td");
    tdReservas.textContent = prop.reservas;
    row.appendChild(tdReservas);

    // Columna: Precio
    const tdPrecio = document.createElement("td");
    tdPrecio.textContent = prop.precio;
    row.appendChild(tdPrecio);

    // Añade la fila al tbody
    tbody.appendChild(row);
  });
}

// 3) Función para ordenar columnas al hacer clic en los <th>
function sortColumn(colIndex) {
  const table = document.getElementById('propiedadesTable');
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));

  // Detecta la dirección de orden actual (asc o desc)
  const currentSortDir = table.dataset.sortDir === 'asc' ? 'asc' : 'desc';
  // Cambia la dirección
  const newSortDir = currentSortDir === 'asc' ? 'desc' : 'asc';
  table.dataset.sortDir = newSortDir;

  // Ordena las filas según la celda en colIndex
  rows.sort((a, b) => {
    const cellA = a.querySelectorAll('td')[colIndex].innerText;
    const cellB = b.querySelectorAll('td')[colIndex].innerText;

    // Intentar convertir a número (para precio, reservas, etc.)
    const valA = parseFloat(cellA.replace(',', '.')) || cellA.toLowerCase();
    const valB = parseFloat(cellB.replace(',', '.')) || cellB.toLowerCase();

    if (valA < valB) return newSortDir === 'asc' ? -1 : 1;
    if (valA > valB) return newSortDir === 'asc' ? 1 : -1;
    return 0;
  });

  // Reemplaza las filas ordenadas en el DOM
  tbody.innerHTML = '';
  rows.forEach(row => tbody.appendChild(row));
}

// 4) Escucha el DOMContentLoaded para otras interacciones del menú (opcional)
document.addEventListener('DOMContentLoaded', function() {
  // Si tu HTML tiene .user-name y #userDropdown:
  const userName = document.querySelector('.user-name');
  const dropdown = document.getElementById('userDropdown');
  if (userName && dropdown) {
    userName.addEventListener('click', function(event) {
      dropdown.classList.toggle('open');
      event.stopPropagation();
    });

    // Oculta el menú al hacer clic en cualquier parte
    document.addEventListener('click', function() {
      dropdown.classList.remove('open');
    });
  }

  // (Opcional) Lógica para cambiar imágenes del menú lateral
  const opciones = document.querySelectorAll('.menuPanel li');
  const nuevasImagenes = [
    "/static/images/inicioBlanco.png",
    "/static/images/profileBlanco.png",
    "/static/images/ForoBlanco.png",
    "/static/images/ReseñasBlanco.png"
  ];

  opciones.forEach((opcion, index) => {
    opcion.addEventListener('mouseenter', function() {
      const img = opcion.querySelector('img');
      if (img && nuevasImagenes[index]) {
        // Guarda el src original para restaurarlo luego
        if (!img.dataset.original) {
          img.dataset.original = img.src;
        }
        img.src = nuevasImagenes[index];
      }
    });
    opcion.addEventListener('mouseleave', function() {
      if(opcion.classList.contains('active')) return; 
      const img = opcion.querySelector('img');
      if (img && img.dataset.original) {
        img.src = img.dataset.original;
      }
    });
  });

  // Asegura que el elemento activo mantenga la imagen "blanca"
  document.querySelectorAll('.menuPanel li.active').forEach((opcion, index) => {
    const img = opcion.querySelector('img');
    if (img) {
      img.src = "/static/images/profileBlanco.png";
      img.dataset.original = "/static/images/profileBlanco.png";
    }
  });
});
