document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/propietarios/reservas")
      .then(res => res.json())
      .then(data => {
        const tbody = document.getElementById("tablaReservasBody");
        if (data.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5">No hay reservas registradas aún.</td></tr>`;
          return;
        }
  
        tbody.innerHTML = data.map(reserva => `
          <tr>
            <td>${reserva.nombre_hotel}</td>
            <td>${reserva.nombre_usuario}</td>
            <td>${reserva.fecha_inicio}</td>
            <td>${reserva.fecha_fin}</td>
            <td>${reserva.numero_personas}</td>
          </tr>
        `).join("");
      })
      .catch(err => {
        console.error("Error cargando reservas:", err);
        Swal.fire("Error", "No se pudieron cargar las reservas.", "error");
      });
  });
  