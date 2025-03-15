// Se asume que la validación de que el usuario es admin se ha realizado en el servidor antes de renderizar esta página.

let userData = [];
const itemsPerPage = 7;
let page = 1;

fetch('/users')
.then(response => {
    // Aquí podrías manejar el caso de no estar autenticado o no ser admin, redireccionando a login
    if(response.status === 403){
        window.location.href = '/login';
    }
    return response.json();
})
.then(data => {
    userData = data;
    updateTable(); // Se llama para mostrar solo los registros deseados
})
.catch(error => console.error("Error al cargar los usuarios:", error));

// Nueva función para limitar los usuarios mostrados
function updateTable() {
    const tbody = document.querySelector("#userTable tbody");
    tbody.innerHTML = "";
    let start = (page - 1) * itemsPerPage;
    let end = page * itemsPerPage;
    let limitedData = userData.slice(start, end);
    limitedData.forEach(user => {
        // Crea una nueva fila para cada usuario
        const row = document.createElement("tr");

        const tdName = document.createElement("td");
        tdName.textContent = user.name;
        row.appendChild(tdName);

        const tdEmail = document.createElement("td");
        tdEmail.textContent = user.email;
        row.appendChild(tdEmail);

        const tdStatus = document.createElement("td");
        const statusSquare = document.createElement("span");
        statusSquare.textContent = user.blocked ? "Bloqueado" : "Activo";
        statusSquare.classList.add(user.blocked ? "status-blocked" : "status-active");
        tdStatus.appendChild(statusSquare);
        row.appendChild(tdStatus);

        const tdType = document.createElement("td");
        tdType.textContent = user.type;
        row.appendChild(tdType);

        const tdActions = document.createElement("td");
        // Se añade el atributo data-userid para identificar el usuario
        tdActions.innerHTML = `
        <button class="btn btn-edit">Editar</button>
        <button class="btn btn-delete">Eliminar</button>
        <button class="btn btn-block" data-userid="${user._id}">${user.blocked ? "Desbloquear" : "Bloquear"}</button>
        `;
        row.appendChild(tdActions);

        // Asignar listener al botón: bloquea si no está bloqueado, desbloquea si ya lo está
        row.querySelector('.btn-block').addEventListener('click', function() {
            if (!user.blocked) {
                blockUser(user._id);
            } else {
                unblockUser(user._id);
            }
        });

        tbody.appendChild(row);
    });
    // Actualiza la información del rango de registros mostrados
    let startRecord = start + 1;
    let endRecord = Math.min(end, userData.length);
    document.getElementById('recordInfo').textContent = `Mostrando del número ${startRecord} al ${endRecord} de un total de ${userData.length} registros`;
    renderPagination();
}

// Función para bloquear al usuario (ya existente)
function blockUser(userId) {
    fetch('/admin/blockUser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userId, blocked: true })
    })
    .then(response => response.json())
    .then(data => {
        // Actualizar el objeto user correspondiente en userData
        const user = userData.find(u => u._id === userId);
        if (user) {
            user.blocked = true;
        }
        updateTable();
    })
    .catch(error => console.error("Error al bloquear el usuario:", error));
}

// Nueva función para desbloquear al usuario
function unblockUser(userId) {
    fetch('/admin/unblockUser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userId, blocked: false })
    })
    .then(response => response.json())
    .then(data => {
        const user = userData.find(u => u._id === userId);
        if (user) {
            user.blocked = false;
        }
        updateTable();
    })
    .catch(error => console.error("Error al desbloquear el usuario:", error));
}

function renderPagination() {
    const pagination = document.getElementById('paginationControls');
    pagination.innerHTML = "";
    const totalPages = Math.ceil(userData.length / itemsPerPage);

    const prevBtn = document.createElement('button');
    prevBtn.textContent = "Anterior";
    prevBtn.classList.add('page-num');
    prevBtn.disabled = (page === 1);
    prevBtn.addEventListener('click', () => {
        page--;
        updateTable();
    });
    pagination.appendChild(prevBtn);

    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.classList.add('page-num');
        if (i === page) {
            pageBtn.classList.add('active');
        }
        pageBtn.addEventListener('click', () => {
            page = i;
            updateTable();
        });
        pagination.appendChild(pageBtn);
    }

    const nextBtn = document.createElement('button');
    nextBtn.textContent = "Siguiente";
    nextBtn.classList.add('page-num');
    nextBtn.disabled = (page === totalPages);
    nextBtn.addEventListener('click', () => {
        page++;
        updateTable();
    });
    pagination.appendChild(nextBtn);
}

document.addEventListener('DOMContentLoaded', function() {
    const userName = document.querySelector('.user-name');
    const dropdown = document.getElementById('userDropdown');

    userName.addEventListener('click', function(event) {
        // Alterna la clase "open" para activar la animación
        dropdown.classList.toggle('open');
        event.stopPropagation(); // Evita que se cierre inmediatamente al propagar el evento
    });

    // Oculta el menú al hacer clic en cualquier parte de la página
    document.addEventListener('click', function() {
        dropdown.classList.remove('open');
    });

    // Llama a updateTable() cada vez que se cambia el <select>
    document.getElementById('recordsPerPage').addEventListener('change', updateTable);
});

// Nuevo: Cambiar imágenes de las opciones del menú
const opciones = document.querySelectorAll('.menuPanel li');
    
// Define las nuevas rutas para cada opción
const nuevasImagenes = [
    "/static/images/inicioBlanco.png",
    "/static/images/profileBlanco.png",
    "/static/images/ForoBlanco.png",
    "/static/images/ReseñasBlanco.png"
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
    
    // Al quitar el ratón, restaura la imagen original
    opcion.addEventListener('mouseleave', function() {
        const img = opcion.querySelector('img');
        if (img && img.dataset.original) {
            img.src = img.dataset.original;
        }
    });
});