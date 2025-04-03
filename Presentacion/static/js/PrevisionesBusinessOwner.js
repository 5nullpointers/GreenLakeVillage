document.addEventListener('DOMContentLoaded', () => {
    /***********************************/
    /* 1) Manejo del menú y sus iconos */
    /***********************************/
    const sideBarOptions = document.querySelectorAll('.menuPanel ul li');
    const whiteIcons = [
        "/static/images/inicioBlanco.png",
        "/static/images/PropiedadesBlanco.png",
        "/static/images/ReseñasBlanco.png",
        "/static/images/PrevisionesBlanco.png"
    ];

    sideBarOptions.forEach((option, index) => {
        const img = option.querySelector('img');
        if (option.classList.contains('active') && whiteIcons[index]) {
            if (!img.dataset.original) {
                img.dataset.original = img.src;
            }
            img.src = whiteIcons[index];
        }
        option.addEventListener('mouseenter', function() {
            if (!option.classList.contains('active') && whiteIcons[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = whiteIcons[index];
            }
        });
        option.addEventListener('mouseleave', function() {
            if (!option.classList.contains('active') && img.dataset.original) {
                img.src = img.dataset.original;
            }
        });
        option.addEventListener('click', function() {
            sideBarOptions.forEach(o => {
                o.classList.remove('active');
                const imgTemp = o.querySelector('img');
                if (imgTemp && imgTemp.dataset.original) {
                    imgTemp.src = imgTemp.dataset.original;
                }
            });
            option.classList.add('active');
            if (img && whiteIcons[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = whiteIcons[index];
            }
        });
    });

    /***************************************************************/
    /* 2) Obtener y mostrar las previsiones para las propiedades 
          del usuario, usando un nuevo endpoint filtrado.         */
    /***************************************************************/
    let predictionsData = [];
    const monthButtonsDiv = document.getElementById('monthButtons');
    const predictionsTableBody = document.getElementById('predictionsTable').querySelector('tbody');

    fetch('/api/prediccionesOcupacion_Propietarios')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            predictionsData = data;
            const months = [...new Set(data.map(item => item.mes))].sort();
            months.forEach((month, index) => {
                const btn = document.createElement('button');
                btn.textContent = month;
                btn.dataset.month = month;
                if (index === 0) btn.classList.add('active');
                btn.addEventListener('click', () => {
                    document.querySelectorAll('#monthButtons button').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    updateTable(month);
                });
                monthButtonsDiv.appendChild(btn);
            });
            if (months.length > 0) {
                updateTable(months[0]);
            }
        })
        .catch(error => {
            console.error('Error al obtener las previsiones:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron obtener las previsiones.'
            });
        });

    function updateTable(selectedMonth) {
        predictionsTableBody.innerHTML = '';
        const filtered = predictionsData.filter(item => item.mes === selectedMonth);
        filtered.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.hotel_nombre}</td>
                <td>${item.tasa_ocupacion}</td>
                <td>${item.reservas_confirmadas}</td>
                <td>${item.cancelaciones}</td>
                <td>${item.precio_promedio_noche}</td>
            `;
            predictionsTableBody.appendChild(row);
        });
    }
});