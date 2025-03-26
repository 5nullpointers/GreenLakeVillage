document.addEventListener('DOMContentLoaded', function () {
    // -- Manejo del dropdown de usuario y hover en la barra lateral (sin cambios) --
    const profileImg = document.querySelector('.profile-img');
    const dropdown = document.getElementById('userDropdown');

    profileImg.addEventListener('click', function (event) {
        dropdown.classList.toggle('open');
        event.stopPropagation();
    });
    document.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });

    const nuevasImagenes = [
        "/static/images/inicioBlanco.png",
        "/static/images/profileBlanco.png",
        "/static/images/ForoBlanco.png",
        "/static/images/ReseñasBlanco.png"
    ];
    const opciones = document.querySelectorAll('.sidebar li');

    opciones.forEach((opcion, index) => {
        const img = opcion.querySelector('img');
        if (opcion.classList.contains('active') && nuevasImagenes[index]) {
            if (!img.dataset.original) {
                img.dataset.original = img.src;
            }
            img.src = nuevasImagenes[index];
        }
        opcion.addEventListener('mouseenter', function () {
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });
        opcion.addEventListener('mouseleave', function () {
            if (img && img.dataset.original && !opcion.classList.contains('active')) {
                img.src = img.dataset.original;
            }
        });
        opcion.addEventListener('click', function () {
            opciones.forEach(o => {
                o.classList.remove('active');
                const imgTemp = o.querySelector('img');
                if (imgTemp && imgTemp.dataset.original) {
                    imgTemp.src = imgTemp.dataset.original;
                }
            });
            opcion.classList.add('active');
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });
    });

    // -- Función para convertir la valoración numérica en estrellas --
    function convertRatingToStars(rating) {
        const maxStars = 5;
        const fullStars = Math.floor(rating);
        const halfStar = rating - fullStars >= 0.5 ? 1 : 0;
        const emptyStars = maxStars - fullStars - halfStar;
        let starsHtml = "";
        for (let i = 0; i < fullStars; i++) {
            starsHtml += "<span class='star full'>★</span>";
        }
        if (halfStar) {
            starsHtml += "<span class='star half'>☆</span>";
        }
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += "<span class='star empty'>☆</span>";
        }
        return starsHtml;
    }

    // -- Estadísticas dinámicas (tasa de ocupación, reservas y cancelaciones) --
    fetch('/api/estadisticas_ocupacion')
      .then(response => response.json())
      .then(data => {
          const ocupacionElem = document.getElementById('ocupacionRate');
          ocupacionElem.textContent = `${data.tasa_ocupacion_users} Usuarios (${data.tasa_ocupacion_percent}%)`;
          const ocupacionBar = document.getElementById('ocupacionBarFill');
          ocupacionBar.style.width = data.tasa_ocupacion_percent + '%';

          const reservasElem = document.getElementById('reservasRate');
          reservasElem.textContent = `${data.reservas_confirmadas} Usuarios (${data.reservas_percent}%)`;
          const reservasBar = document.getElementById('reservasBarFill');
          reservasBar.style.width = data.reservas_percent + '%';

          const cancelElem = document.getElementById('cancelacionesRate');
          cancelElem.textContent = `${data.cancelaciones} Usuarios (${data.cancelaciones_percent}%)`;
          const cancelacionesBar = document.getElementById('cancelacionesBarFill');
          cancelacionesBar.style.width = data.cancelaciones_percent + '%';
      })
      .catch(error => console.error('Error al obtener las estadísticas:', error));

    // -- Top 3 Hoteles (manteniendo award_1, award_2, award_3) --
    fetch('/api/top_hoteles')
      .then(response => response.json())
      .then(data => {
        const topHotelesList = document.getElementById('topHotelesList');
        topHotelesList.innerHTML = '';  // Limpia por si acaso

        data.forEach((item, index) => {
          const li = document.createElement('li');
          li.innerHTML = `
            <div class="ranking-row">
              <!-- Aquí insertamos la imagen de premio -->
              <img src="/static/images/award_${index + 1}.png" alt="Award ${index + 1}" class="award-icon"/>
              <div class="ranking-content">
                <div class="service-name">${item._id}</div>
                <div class="rating-section">
                  ${convertRatingToStars(item.media_puntuacion)}
                  <span class="rating-number">(${item.media_puntuacion.toFixed(2)})</span>
                  <span class="opiniones">(${item.numero_comentarios} opiniones)</span>
                </div>
              </div>
            </div>
          `;
          topHotelesList.appendChild(li);
        });
      })
      .catch(error => console.error('Error al obtener el top de hoteles:', error));

    // -- Top 3 Servicios (manteniendo award_1, award_2, award_3) --
    fetch('/api/top_servicios')
      .then(response => response.json())
      .then(data => {
        const topServiciosList = document.getElementById('topServiciosList');
        topServiciosList.innerHTML = '';

        data.forEach((item, index) => {
          const li = document.createElement('li');
          li.innerHTML = `
            <div class="ranking-row">
              <img src="/static/images/award_${index + 1}.png" alt="Award ${index + 1}" class="award-icon"/>
              <div class="ranking-content">
                <div class="service-name">${item._id}</div>
                <div class="rating-section">
                  ${convertRatingToStars(item.media_puntuacion)}
                  <span class="rating-number">(${item.media_puntuacion.toFixed(2)})</span>
                  <span class="opiniones">(${item.numero_comentarios} opiniones)</span>
                </div>
              </div>
            </div>
          `;
          topServiciosList.appendChild(li);
        });
      })
      .catch(error => console.error('Error al obtener el top de servicios:', error));

    // -- Top 3 Rutas (manteniendo award_1, award_2, award_3) --
    fetch('/api/top_rutas')
      .then(response => response.json())
      .then(data => {
        const topRutasList = document.getElementById('topRutasList');
        topRutasList.innerHTML = '';

        data.forEach((item, index) => {
          const li = document.createElement('li');
          li.innerHTML = `
            <div class="ranking-row">
              <img src="/static/images/award_${index + 1}.png" alt="Award ${index + 1}" class="award-icon"/>
              <div class="ranking-content">
                <div class="service-name">${item._id}</div>
                <div class="rating-section">
                  ${convertRatingToStars(item.media_puntuacion)}
                  <span class="rating-number">(${item.media_puntuacion.toFixed(2)})</span>
                  <span class="opiniones">(${item.numero_comentarios} opiniones)</span>
                </div>
              </div>
            </div>
          `;
          topRutasList.appendChild(li);
        });
      })
      .catch(error => console.error('Error al obtener el top de rutas:', error));
});
