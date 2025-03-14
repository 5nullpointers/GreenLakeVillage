// Se asume que la validación de que el usuario es admin se ha realizado en el servidor antes de renderizar esta página.
fetch('/users')
.then(response => {
    // Aquí podrías manejar el caso de no estar autenticado o no ser admin, redireccionando a login
    if(response.status === 403){
        window.location.href = '/login';
    }
    return response.json();
})
.then(data => {
    const tbody = document.querySelector("#userTable tbody");
    data.forEach(user => {
        // Crea una nueva fila para cada usuario
        const row = document.createElement("tr");

        const tdId = document.createElement("td");
        tdId.textContent = user._id;
        row.appendChild(tdId);

        const tdName = document.createElement("td");
        tdName.textContent = user.name;
        row.appendChild(tdName);

        const tdEmail = document.createElement("td");
        tdEmail.textContent = user.email;
        row.appendChild(tdEmail);

        const tdType = document.createElement("td");
        tdType.textContent = user.type;
        row.appendChild(tdType);

        tbody.appendChild(row);
    });
})
.catch(error => console.error("Error al cargar los usuarios:", error));