let map;
let currentInfoWindow = null; // Para saber cuál InfoWindow está abierto

// Almacenará la lista de hoteles que viene de MongoDB
let hotels = [];

// Variable global para almacenar la información de ratings
let ratingsInfo = {};

// =======================
// 1) Cargar Mapa e Iniciar
// =======================
function initMap() {
  // Centro del mapa
  const centerCoords = { lat: 47.5626, lng: 13.6493 };

  // Límites permitidos para el mapa
  const allowedBounds = {
    north: 47.58,
    south: 47.55,
    west: 13.63,
    east: 13.72
  };

  // Creación del mapa
  map = new google.maps.Map(document.getElementById("map"), {
    center: centerCoords,
    zoom: 16,
    tilt: 60,
    heading: 20,
    mapId: "TU_MAP_ID", // Reemplaza con tu MAP ID
    disableDefaultUI: true,
    restriction: {
      latLngBounds: allowedBounds,
      strictBounds: true
    },
    mapTypeId: "satellite",
    styles: [
      { elementType: "labels", stylers: [{ visibility: "off" }] },
      { featureType: "road", stylers: [{ visibility: "off" }] },
      { featureType: "transit", stylers: [{ visibility: "off" }] },
      { featureType: "poi", stylers: [{ visibility: "off" }] }
    ]
  });

  // Ocultar overlay de carga cuando el mapa esté listo
  google.maps.event.addListenerOnce(map, "idle", () => {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) {
      overlay.style.opacity = "0";
      setTimeout(() => {
        overlay.style.display = "none";
      }, 500);
    }
  });

  // 2) Primero obtenemos la lista de hoteles desde MongoDB
  fetch('/api/hoteles')
    .then(response => response.json())
    .then(data => {
      hotels = data; // Guardamos la lista de hoteles
      // 3) Luego obtenemos las puntuaciones desde /api/ratings (si lo deseas)
      return fetch('/api/ratings');
    })
    .then(response => response.json())
    .then(ratingsData => {
      ratingsInfo = ratingsData; // Guardamos el diccionario de ratings
      // 4) Creamos los marcadores en el mapa
      crearMarcadores();
    })
    .catch(error => console.error("Error al cargar datos:", error));
}

// =======================
// 2) Crear Marcadores
// =======================
function crearMarcadores() {
  hotels.forEach(hotel => {
    // hotel: { nombre, lat, lng, imagen, descripcion, precio, servicios, ... }

    // Creamos el marcador
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.nombre,
      icon: {
        url: "/static/Images/hotel.png", // Ícono base, ajusta si deseas
        scaledSize: new google.maps.Size(80, 80)
      }
    });

    // Guardamos el marcador en el objeto hotel para acceder a él luego desde la lista
    hotel.marker = marker;

    // Creamos un InfoWindow (tarjeta pequeña)
    const infoWindow = new google.maps.InfoWindow();

    // Escuchamos el click en el marcador
    marker.addListener("click", () => {
      // Animación de rebote
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1500);

      // Obtenemos la puntuación del hotel si existe
      const ratingData = ratingsInfo[hotel.nombre] || null;
      let ratingContent = "<p>Sin opiniones</p>";
      if (ratingData) {
        ratingContent = `<p>⭐ ${ratingData.media_puntuacion.toFixed(1)}
          (${ratingData.numero_comentarios} opiniones)</p>`;
      }

      // Tarjeta pequeña (InfoWindow) con imagen, nombre, rating
      infoWindow.setContent(`
        <div style="min-width:250px">
          <img src="/static/Images/Hoteles/${hotel.imagen || "default.jpg"}"
               alt="${hotel.nombre}"
               style="width:100%; height:auto; margin-bottom:10px; max-height:150px;" />
          <h3>${hotel.nombre}</h3>
          ${ratingContent}
        </div>
      `);
      infoWindow.open(map, marker);

      // Tarjeta grande (panel lateral) con más detalles
      const sidePanelHTML = getSidePanelHTML(hotel, ratingData);
      openMarkerInfo(marker, infoWindow, sidePanelHTML);
    });
  });
}


// =======================
// 3) Construir Tarjeta Grande
// =======================
function getSidePanelHTML(hotel, rating) {
  // rating: { media_puntuacion, numero_comentarios }
  let ratingText = "⭐ 0.0 (0 opiniones)";
  if (rating) {
    ratingText = `⭐ ${rating.media_puntuacion.toFixed(1)}
      (${rating.numero_comentarios} opiniones)`;
  }

  // Listas dinámicas
  const servicesList = hotel.servicios?.map(s => `<li>${s}</li>`).join("") || "";
  const attractionsList = hotel.atraccionesCercanas?.map(a => `<li>${a}</li>`).join("") || "";
  const restaurantsList = hotel.restaurantesCercanos?.map(r => `<li>${r}</li>`).join("") || "";
  const eventsList = hotel.eventosProximos?.map(e => `<li>${e}</li>`).join("") || "";

  return `
    <div class="dropdown-container">
      <div class="hotel-card">
        <img src="/static/Images/Hoteles/${hotel.imagen || "default.jpg"}"
             alt="${hotel.nombre}" class="hotel-image">
        <div class="hotel-info">
          <h2>${hotel.nombre}</h2>
          <p class="rating">${ratingText}</p>
          <p class="description">${hotel.descripcion || ""}</p>
          <ul class="services">
            ${servicesList}
          </ul>
          <p class="price">Desde <strong>$${hotel.precio || 0}</strong> por noche</p>
          <div class="buttons">
            <a href="#" class="btn reserve">Reservar Ahora</a>
            <a href="#" class="btn details">Ver Más Detalles</a>
            <a href="#" class="btn map">📍 Cómo Llegar</a>
          </div>
        </div>
      </div>
      <div class="nearby-info">
        <h3>🏞 Atracciones Cercanas</h3>
        <ul>
          ${attractionsList}
        </ul>
        <h3>🍽 Restaurantes Recomendados</h3>
        <ul>
          ${restaurantsList}
        </ul>
        <h3>🎉 Eventos Próximos</h3>
        <ul>
          ${eventsList}
        </ul>
      </div>
    </div>
  `;
}

// =======================
// 4) Lógica del Panel Lateral e InfoWindow
// =======================
function openMarkerInfo(marker, infoWindow, panelContent) {
  closeAll();

  const sidebar = document.getElementById("sidebar");
  sidebar.classList.remove("left", "right");

  // Decide si el panel se abre a la izquierda o a la derecha
  const referenceLng = 13.66395; // "Aruba Luxury Lodge"
  const markerLng = marker.getPosition().lng();
  if (markerLng < referenceLng) {
    sidebar.classList.add("right");
  } else {
    sidebar.classList.add("left");
  }

  infoWindow.open(map, marker);
  currentInfoWindow = infoWindow;

  document.getElementById("infoSection").innerHTML = panelContent;
  showSidebar();

  infoWindow.addListener("closeclick", () => {
    closeAll();
  });
}

function closeAll() {
  closeSidebar();
  if (currentInfoWindow) {
    currentInfoWindow.close();
    currentInfoWindow = null;
  }
}

function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}

function closeSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar.classList.contains("open")) {
    sidebar.classList.remove("open");
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar.classList.contains("open")) {
    closeAll();
  } else {
    showSidebar();
  }
}

// =======================
// 5) Botón "Hoteles" (lista en panel lateral)
// =======================
function mostrarHoteles() {
  let content = '<h3>Listado de Hoteles</h3><ul>';
  hotels.forEach((hotel, index) => {
    content += `<li class="hotel-item" data-index="${index}" style="cursor:pointer;">${hotel.nombre}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  
  // Agregamos el listener para cada item de la lista
  document.querySelectorAll('.hotel-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const hotel = hotels[index];
      if (hotel && hotel.marker) {
        // Disparamos el evento click en el marcador del hotel, simulando el clic del usuario
        google.maps.event.trigger(hotel.marker, 'click');
      }
    });
  });
  
  showSidebar();
}

// =======================
// 6) Rutas y Sitios (opcional)
// =======================
function mostrarRutas() {
  // Lógica para mostrar rutas en el panel, si procede
  document.getElementById("infoSection").innerHTML = "<h3>Rutas Turísticas</h3><p>Próximamente...</p>";
  showSidebar();
}

function mostrarSitios() {
  // Lógica para mostrar sitios en el panel, si procede
  document.getElementById("infoSection").innerHTML = "<h3>Sitios de Interés</h3><p>Próximamente...</p>";
  showSidebar();
}

// =======================
// 7) Chatbot (opcional)
// =======================
function sendMessage() {
  const userMessage = document.getElementById("user-input")?.value;
  if (!userMessage) {
    alert("Por favor escribe un mensaje");
    return;
  }

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.response) {
        document.getElementById("chat-response").innerHTML =
          `<p><strong>IA:</strong> ${data.response}</p>`;
      } else {
        document.getElementById("chat-response").innerHTML =
          `<p><strong>Error:</strong> ${data.error}</p>`;
      }
    })
    .catch(error => console.error("Error:", error));
}

// Inicializa el mapa al cargar la ventana
window.onload = initMap;
