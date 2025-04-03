// Nueva función para obtener registros y actualizar la tabla
function updateTable() {
  // Seleccionar el tbody dentro de la tabla (la tabla tiene id "tablaReservasBody")
  const tbody = document.querySelector("#tablaReservasBody tbody");
  tbody.innerHTML = "";
  
  fetch("/propietarios/api/propietarios/reservas")
    .then(response => response.json())
    .then(data => {
        console.log("Reservas recibidas:", data); // Debug: imprimir los datos recibidos
        data.forEach(reservas => {
            // Crea una nueva fila para cada reserva
            const row = document.createElement("tr");

            const tdHotel = document.createElement("td");
            tdHotel.textContent = reservas.nombre_hotel;
            row.appendChild(tdHotel);

            const tdUser = document.createElement("td");
            tdUser.textContent = reservas.nombre_usuario;
            row.appendChild(tdUser);

            const tdInicio = document.createElement("td");
            tdInicio.textContent = reservas.fecha_inicio;
            row.appendChild(tdInicio);

            const tdFin = document.createElement("td");
            tdFin.textContent = reservas.fecha_fin;
            row.appendChild(tdFin);

            const tdUsers = document.createElement("td");
            tdUsers.textContent = reservas.numero_personas;
            row.appendChild(tdUsers);

            tbody.appendChild(row);
        });
        // ...excluir paginación y otros datos...
    })
    .catch(error => console.error("Error al obtener reservas:", error));
}

// Llamar a la actualización de la tabla al cargar la página
document.addEventListener("DOMContentLoaded", updateTable);

// Nuevo: Cambiar imágenes de las opciones del menú
const opciones = document.querySelectorAll('.menuPanel li');
    
// Define las nuevas rutas para cada opción
const nuevasImagenes = [
    "/static/images/inicioBlanco.png",
    "/static/images/PropiedadesBlanco.png",
    "/static/images/ReseñasBlanco.png",
    "/static/images/PrevisionesBlanco.png"
];

opciones.forEach((opcion, index) => {
    // Al pasar el ratón, cambia la imagen
    opcion.addEventListener('mouseenter', function() {
        const img = opcion.querySelector('img');
        if (img && nuevasImagenes[index]) {
            // Guarda el src original para volver a él después
            if (!img.dataset.original) {
                img.dataset.original = img.src;
            }
            img.src = nuevasImagenes[index];
        }
    });
    
    // Al quitar el ratón, restaura la imagen original solo si no es el elemento activo
    opcion.addEventListener('mouseleave', function() {
        if(opcion.classList.contains('active')) return; // Mantiene la imagen si está activo
        const img = opcion.querySelector('img');
        if (img && img.dataset.original) {
            img.src = img.dataset.original;
        }
    });
});
