document.addEventListener('DOMContentLoaded', function () {
  // --- Manejo del dropdown de usuario y hover en la barra lateral ---
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

  // --- Mapa de colores por transporte ---
  const colorMap = {
    "Bicicleta": "#003f5c",
    "Metro": "#ffa600",
    "Autobús": "#ff6361",
    "Coche Compartido": "#ff8531",
    "Tranvía": "#58508d",
    "Taxi": "#bc5090"
  };

  // --- Mapa de íconos por transporte ---
  const iconMap = {
    "Bicicleta": "/static/images/transportes/bike.png",
    "Metro": "/static/images/transportes/train-front.png",
    "Autobús": "/static/images/transportes/bus-front.png",
    "Coche Compartido": "/static/images/transportes/car-front.png",
    "Tranvía": "/static/images/transportes/tram-front.png",
    "Taxi": "/static/images/transportes/car-taxi-front.png"
  };

  // --- Objeto para almacenar las imágenes precargadas ---
  const loadedImages = {};

  // --- Función para precargar las imágenes y ejecutar callback al terminar ---
  function preloadImages(callback) {
    const keys = Object.keys(iconMap);
    let loadedCount = 0;
    
    keys.forEach(label => {
      const img = new Image();
      img.src = iconMap[label];
      img.onload = () => {
        loadedCount++;
        if (loadedCount === keys.length) {
          callback();
        }
      };
      loadedImages[label] = img;
    });
  }

  // --- Plugin de Chart.js usando METADATA para alinear íconos ---
  const iconOnBarPlugin = {
    id: 'iconOnBar',
    afterDatasetsDraw(chart, args, pluginOptions) {
      const { ctx } = chart;
      // Obtenemos la metadata del primer (y único) dataset
      const meta = chart.getDatasetMeta(0);

      meta.data.forEach((barElement, index) => {
        const label = chart.data.labels[index];
        const img = loadedImages[label];
        if (!img) return;

        // barElement.x, barElement.y => coordenadas del centro de la barra
        const imgWidth = 24;
        const imgHeight = 24;
        const marginTop = 5; // margen sobre la barra
        const xPos = barElement.x - (imgWidth / 2);
        const yPos = barElement.y - imgHeight - marginTop;

        ctx.drawImage(img, xPos, yPos, imgWidth, imgHeight);
      });
    }
  };

  // --- Función para convertir la valoración numérica en estrellas ---
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

  // --- Estadísticas dinámicas (tasa de ocupación, reservas y cancelaciones) ---
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

  // --- Top 3 Hoteles ---
  fetch('/api/top_hoteles')
    .then(response => response.json())
    .then(data => {
        const topHotelesList = document.getElementById('topHotelesList');
        topHotelesList.innerHTML = '';
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
            topHotelesList.appendChild(li);
        });
    })
    .catch(error => console.error('Error al obtener el top de hoteles:', error));

  // --- Top 3 Servicios ---
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

  // --- Top 3 Rutas ---
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

  // --- Función para cargar el gráfico de barras con colores e íconos ---
  function cargarGraficoTransporte(startDate = '', endDate = '') {
    let url = '/api/uso_transporte';
    const params = [];
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate)   params.push(`end_date=${endDate}`);
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
  
    fetch(url)
      .then(response => response.json())
      .then(data => {
        const labels = Object.keys(data);
        const valores = Object.values(data);
        const backgroundColors = labels.map(label => colorMap[label] || 'rgba(0, 150, 136, 0.5)');
  
        if (window.miBarChart) {
          window.miBarChart.destroy();
        }
  
        const ctx = document.getElementById('transporteChart').getContext('2d');
        window.miBarChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: '', // Vacío para no mostrar "Número de Usuarios"
              data: valores,
              backgroundColor: backgroundColors,
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            // Para dejar margen arriba y que los íconos no se corten
            layout: {
              padding: {
                top: 30 // Ajusta según necesites
              }
            },
            // También puedes usar 'grace' para el eje Y
            scales: {
              y: {
                beginAtZero: true,
                grace: '10%' // Deja 10% extra arriba
              }
            },
            plugins: {
              legend: {
                display: false
              }
            }
          },
          // Usamos el plugin que emplea la metadata
          plugins: [iconOnBarPlugin]
        });
      })
      .catch(error => console.error('Error al obtener datos de transporte:', error));
  }

  // --- Precargamos las imágenes y luego cargamos el gráfico de barras ---
  preloadImages(() => {
    // Cargamos el gráfico de barras inicialmente
    cargarGraficoTransporte();

    // Listener para filtrar por fecha en el widget doble
    const filtrarBtn = document.getElementById('filtrarBtn');
    if (filtrarBtn) {
      filtrarBtn.addEventListener('click', () => {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        cargarGraficoTransporte(startDate, endDate);
      });
    }
  });

  // --- Pie Chart (Widget Normal) con leyenda SOLO iconos ---
  // (Reutilizamos colorMap e iconMap definidos arriba)

  // 3) Función para generar la leyenda personalizada (solo íconos + texto)
  function buildCustomLegend(labels) {
    const legendContainer = document.getElementById("customLegendContainer");
    legendContainer.innerHTML = ""; // Limpia si había algo

    labels.forEach(label => {
      const icon = iconMap[label] || "";

      // Contenedor de cada item
      const item = document.createElement("div");
      item.style.display = "flex";
      item.style.alignItems = "center";
      item.style.marginBottom = "8px";

      // Imagen del ícono (si existe)
      if (icon) {
        const iconImg = document.createElement("img");
        iconImg.src = icon;
        iconImg.alt = label;
        iconImg.style.width = "24px";
        iconImg.style.height = "24px";
        iconImg.style.marginRight = "8px";
        item.appendChild(iconImg);
      }

      // Texto
      const textSpan = document.createElement("span");
      textSpan.textContent = label;
      textSpan.style.fontSize = "16px";
      item.appendChild(textSpan);

      legendContainer.appendChild(item);
    });
  }

  // 4) Crear el Pie Chart y luego generar la leyenda (solo iconos)
  fetch('/api/uso_transporte')
    .then(response => response.json())
    .then(data => {
        const labels = Object.keys(data);
        const valores = Object.values(data);

        // Generar el array de colores a partir del colorMap
        const backgroundColors = labels.map(label => colorMap[label] || "#999");

        // Crear el Pie Chart
        const ctxPie = document.getElementById('transportePieChart').getContext('2d');
        new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: valores,
                    backgroundColor: backgroundColors
                }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  display: false
                }
              }
            }
        });

        buildCustomLegend(labels);
    })
    .catch(error => console.error('Error al obtener datos para el pie chart:', error));
});