document.addEventListener('DOMContentLoaded', function () {
    // Manejo del dropdown de usuario: se usa la imagen de perfil en lugar del span
    const profileImg = document.querySelector('.profile-img');
    const dropdown = document.getElementById('userDropdown');

    profileImg.addEventListener('click', function (event) {
        dropdown.classList.toggle('open');
        event.stopPropagation();
    });

    document.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });

    // Array con las rutas de las imágenes en versión blanca
    const nuevasImagenes = [
        "/static/Images/inicioBlanco.png",
        "/static/Images/PropiedadesBlanco.png",
        "/static/Images/ReseñasBlanco.png"
    ];

    // Selecciona todas las opciones del menú
    const opciones = document.querySelectorAll('.sidebar li');

    opciones.forEach((opcion, index) => {
        const img = opcion.querySelector('img');

        // Si la opción ya es la activa (por ejemplo, definida en el HTML),
        // se actualiza la imagen a la versión blanca
        if (opcion.classList.contains('active') && nuevasImagenes[index]) {
            if (!img.dataset.original) {
                img.dataset.original = img.src;
            }
            img.src = nuevasImagenes[index];
        }

        // Al pasar el mouse sobre la opción, se cambia la imagen a la versión blanca
        opcion.addEventListener('mouseenter', function () {
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });

        // Al quitar el mouse, se restaura la imagen original solo si la opción NO es la activa
        opcion.addEventListener('mouseleave', function () {
            if (img && img.dataset.original && !opcion.classList.contains('active')) {
                img.src = img.dataset.original;
            }
        });

        // (Opcional) Actualizar la opción activa al hacer clic
        opcion.addEventListener('click', function () {
            // Remueve la clase "active" de todas las opciones y restaura su imagen original
            opciones.forEach(o => {
                o.classList.remove('active');
                const imgTemp = o.querySelector('img');
                if (imgTemp && imgTemp.dataset.original) {
                    imgTemp.src = imgTemp.dataset.original;
                }
            });
            // Añade "active" a la opción clicada y actualiza su imagen a la versión blanca
            opcion.classList.add('active');
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });
    });

    // Nuevo helper para formatear números
    function formatNumber(num, decimals = 0) {
        return Number(num).toLocaleString('es-ES', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Actualizar las estadísticas dinámicamente (tasa de ocupación, reservas y cancelaciones)
    fetch('/api/estadisticas_ocupacion_Propietarios')
    .then(response => response.json())
    .then(data => {
      if(data.error){
          console.error('Error al obtener las estadísticas: ' + data.error);
          return;
      }
      
      // 1) Tasa de ocupación
      const ocupacionElem = document.getElementById('ocupacionRate');
      ocupacionElem.textContent = `${formatNumber(data.tasa_ocupacion_users)} Usuarios (${formatNumber(data.tasa_ocupacion_percent, 2)}%)`;
  
      // Barra de ocupación → se usa el porcentaje promedio
      const ocupacionBar = document.getElementById('ocupacionBarFill');
      ocupacionBar.style.width = data.tasa_ocupacion_percent + '%';
  
      // 2) Reservas confirmadas
      const reservasElem = document.getElementById('reservasRate');
      reservasElem.textContent = `${formatNumber(data.reservas_confirmadas)} Usuarios (${formatNumber(data.reservas_percent, 2)}%)`;
  
      const reservasBar = document.getElementById('reservasBarFill');
      reservasBar.style.width = data.reservas_percent + '%';
  
      // 3) Cancelaciones
      const cancelElem = document.getElementById('cancelacionesRate');
      cancelElem.textContent = `${formatNumber(data.cancelaciones)} Usuarios (${formatNumber(data.cancelaciones_percent, 2)}%)`;

      const cancelacionesBar = document.getElementById('cancelacionesBarFill');
      cancelacionesBar.style.width = data.cancelaciones_percent + '%';
      
    })
    .catch(error => console.error('Error al obtener las estadísticas:', error));

    // Ajustar el widget para tomar solo las propiedades del usuario
    fetch('/api/ratings_Propietarios')
      .then(response => response.json())
      .then(data => {
        console.log('Datos filtrados recibidos:', data); // DEBUG
        const ratingsArray = Object.keys(data).map(hotelName => ({
          hotelName,
          media_puntuacion: data[hotelName].media_puntuacion || 0,
          numero_comentarios: data[hotelName].numero_comentarios || 0
        }));
        if (!ratingsArray.length) {
          console.warn('No se encontraron hoteles en tus propiedades.');
          return;
        }
        // Ordenar por mayor media_puntuacion
        ratingsArray.sort((a, b) => b.media_puntuacion - a.media_puntuacion);
        const topHotels = ratingsArray.slice(0, 3);
        const podiumContainer = document.getElementById('podiumContainer');
        podiumContainer.innerHTML = '';

        const podiumClasses = ['podium-place-2', 'podium-place-1', 'podium-place-3'];
        const podiumImages = [
          '/static/Images/award_2_P.png',
          '/static/Images/award_1_P.png',
          '/static/Images/award_3_P.png'
        ];
        topHotels.forEach((hotel, index) => {
          const placeDiv = document.createElement('div');
          placeDiv.classList.add('podium-place', podiumClasses[index] || 'podium-place-3');
          placeDiv.innerHTML = `
            <img src="${podiumImages[index] || '/static/Images/podium-default.png'}" alt="Podio" class="Podio" style="width: 80px; height: auto;">
            <div class="podium-img">
              <div class="podium-name">${hotel.hotelName}</div>
            </div>
          `;
          podiumContainer.appendChild(placeDiv);
        });
      })
      .catch(error => console.error('Error al obtener los mejores hoteles:', error));
  
    fetch('/api/billed_Propietarios')
      .then(response => response.json())
      .then(data => {
        const topBilledContainer = document.getElementById('BilledContainer');
        if (!data || !data.length) {
          console.warn('No se encontraron propiedades para facturación.');
          return;
        }
        topBilledContainer.innerHTML = '';

        const podiumClassesBilled = ['podium-place-2', 'podium-place-1', 'podium-place-3'];
        const podiumImagesBilled = [
          '/static/Images/award_2_P.png',
          '/static/Images/award_1_P.png',
          '/static/Images/award_3_P.png'
        ];
        data.forEach((item, index) => {
          const placeDiv = document.createElement('div');
          placeDiv.classList.add('podium-place', podiumClassesBilled[index] || 'podium-place-3');
          placeDiv.innerHTML = `
            <img src="${podiumImagesBilled[index] || '/static/Images/podium-default.png'}" alt="Podio" class="Podio" style="width: 80px; height: auto;">
            <div class="podium-img">
              <div class="podium-name">${item.hotelName}</div>
            </div>
          `;
          topBilledContainer.appendChild(placeDiv);
        });
      })
      .catch(error => console.error('Error al obtener las propiedades con mayor facturación:', error));

    // Nuevo fetch para obtener las últimas reseñas en widget 4
    fetch('/api/latest_reviews_propietarios')
      .then(response => response.json())
      .then(data => {
        console.log('DEBUG: Reseñas recibidas:', data);  // Depuración
        const reviewsList = document.getElementById('latestReviews');
        reviewsList.innerHTML = ''; // limpiar lista
        if (data.error) {
          console.error('Error al obtener reseñas: ' + data.error);
          reviewsList.innerHTML = `<li>Error de conexión: ${data.error}</li>`;
          return;
        }
        if (data.length === 0) {
          console.warn('DEBUG: No se encontraron reseñas.');
          reviewsList.innerHTML = '<li>No se encontraron reseñas para tus propiedades.</li>';
          return;
        }
        data.forEach(review => {
          const li = document.createElement('li');
          li.innerHTML = `<strong>${review.nombre_servicio}:</strong> ${review.comentario}`;
          reviewsList.appendChild(li);
        });
      })
      .catch(error => {
        console.error('Error al obtener reseñas:', error);
        document.getElementById('latestReviews').innerHTML = `<li>Error de conexión: ${error.message}</li>`;
      });
});
