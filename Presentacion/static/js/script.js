let map;
let currentInfoWindow = null; // Para saber cuál InfoWindow está abierto

// Almacenará la lista de hoteles, rutas y restaurantes provenientes de MongoDB
let hotels = [];
let routes = [];
let restaurants = [];

// Variable global para almacenar la información de ratings
let ratingsInfo = {};

let currentRoutePolyline = null;

// =======================
// 1) Cargar Mapa e Iniciar
// =======================
function initMap() {
  // Centro del mapa
  const centerCoords = { lat: 47.5626, lng: 13.6493 };

  // Límites permitidos para el mapa
  const allowedBounds = {
    north: 47.58,
    south: 47.544,
    west: 13.612,
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

  // Obtener datos de hoteles y ratings
  fetch('/api/hoteles')
    .then(response => response.json())
    .then(data => {
      hotels = data;
      return fetch('/api/ratings');
    })
    .then(response => response.json())
    .then(ratingsData => {
      ratingsInfo = ratingsData;
      crearMarcadores();
    })
    .catch(error => console.error("Error al cargar hoteles:", error));

  // Obtener datos de restaurantes y ratings (se hace una sola solicitud)
  fetch('/api/restaurantes')
    .then(response => response.json())
    .then(data => {
      restaurants = data;
      return fetch('/api/ratings');
    })
    .then(response => response.json())
    .then(ratingsData => {
      ratingsInfo = ratingsData;
      crearMarcadoresHoteles();
    })
    .catch(error => console.error("Error al cargar restaurantes:", error));

  // Obtener rutas (no se dibujan automáticamente)
  fetch('/api/rutas')
    .then(response => response.json())
    .then(data => {
      routes = data;
    })
    .catch(error => console.error("Error al cargar rutas:", error));
}

// =======================
// 2) Crear Marcadores
// =======================
function crearMarcadores() {
  hotels.forEach(hotel => {
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.nombre,
      icon: {
        url: "/static/Images/hotel.png",
        scaledSize: new google.maps.Size(80, 80)
      }
    });

    hotel.marker = marker;
    const infoWindow = new google.maps.InfoWindow();

    marker.addListener("click", () => {
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1500);

      const ratingData = ratingsInfo[hotel.nombre] || null;
      let ratingContent = "<p>Sin opiniones</p>";
      if (ratingData) {
        ratingContent = `<p>⭐ ${ratingData.media_puntuacion.toFixed(1)} (${ratingData.numero_comentarios} opiniones)</p>`;
      }

      infoWindow.setContent(`
        <div style="min-width:250px">
          <img src="/static/Images/Hoteles/${hotel.imagen || "default.jpg"}" alt="${hotel.nombre}" style="width:100%; height:auto; margin-bottom:10px; max-height:150px;" />
          <h3>${hotel.nombre}</h3>
          ${ratingContent}
        </div>
      `);
      infoWindow.open(map, marker);

      const sidePanelHTML = getSidePanelHTML(hotel, ratingData);
      openMarkerInfo(marker, infoWindow, sidePanelHTML);
    });
  });
}

function crearMarcadoresHoteles() {
  restaurants.forEach(restaurant => {
    const marker = new google.maps.Marker({
      position: { lat: restaurant.lat, lng: restaurant.lng },
      map: map,
      title: restaurant.nombre,
      icon: {
        url: "/static/Images/restaurante.png",
        scaledSize: new google.maps.Size(80, 80)
      }
    });
    restaurant.marker = marker;
    const infoWindow = new google.maps.InfoWindow();

    marker.addListener("click", () => {
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1500);

      const ratingData = ratingsInfo[restaurant.nombre] || null;
      let ratingContent = "<p>Sin opiniones</p>";
      if (ratingData) {
        ratingContent = `<p>⭐ ${ratingData.media_puntuacion.toFixed(1)} (${ratingData.numero_comentarios} opiniones)</p>`;
      }

      infoWindow.setContent(`
        <div style="min-width:250px">
          <img src="/static/Images/Restaurantes/${restaurant.imagen || "default.jpg"}" alt="${restaurant.nombre}" style="width:100%; height:auto; margin-bottom:10px; max-height:150px;" />
          <h3>${restaurant.nombre}</h3>
          ${ratingContent}
        </div>
      `);
      infoWindow.open(map, marker);

      const sidePanelHTML = getSidePanelHTML(restaurant, ratingData);
      openMarkerInfo(marker, infoWindow, sidePanelHTML);
    });
  });
}

// =======================
// 3) Construir Tarjeta Grande
// =======================
function cambiarImagenFallback(img, imagenNombre) {
  img.onerror = function() {
    img.src = "/static/Images/Hoteles/default.jpg";
  };
  img.src = "/static/Images/Restaurantes/" + imagenNombre;
}

function getSidePanelHTML(item, rating) {
  // 'item' puede ser un hotel o restaurante
  let ratingText = "⭐ 0.0 (0 opiniones)";
  if (rating) {
    ratingText = `⭐ ${rating.media_puntuacion.toFixed(1)} (${rating.numero_comentarios} opiniones)`;
  }

  const descConSaltos = (item.descripcion || "").replace(/\\n/g, "<br>");
  const servicesList = item.servicios?.map(s => `<li>${s}</li>`).join("") || "";
  const attractionsList = item.atraccionesCercanas?.map(a => `<li>${a}</li>`).join("") || "";
  const restaurantsList = item.restaurantesCercanos?.map(r => `<li>${r}</li>`).join("") || "";
  const eventsList = item.eventosProximos?.map(e => `<li>${e}</li>`).join("") || "";
  const detailsURL = `/hoteles/${item._id}`;

  return `
    <div class="dropdown-container">
      <div class="hotel-card">
        <img src="/static/Images/Hoteles/${item.imagen || "default.jpg"}" onerror="cambiarImagenFallback(this, '${item.imagen}')" alt="${item.nombre}" class="hotel-image">
        <div class="hotel-info">
          <h2>${item.nombre}</h2>
          <p class="rating">${ratingText}</p>
          <p class="description">${descConSaltos}</p>
          <p><strong>Servicios</strong></p>
          <ul class="services">${servicesList}</ul>
          <p class="price">Desde <strong>$${item.precio || 0}</strong> por noche</p>
          <div class="buttons">
            <a href="#" class="btn reserve">Reservar Ahora</a>
            <a href="${detailsURL}" class="btn details">Ver Más Detalles</a>
            <a href="#" class="btn map">📍 Cómo Llegar</a>
          </div>
        </div>
      </div>
      <div class="nearby-info">
        <h3>🏞 Atracciones Cercanas</h3>
        <ul>${attractionsList}</ul>
        <h3>🍽 Restaurantes Recomendados</h3>
        <ul>${restaurantsList}</ul>
        <h3>🎉 Eventos Próximos</h3>
        <ul>${eventsList}</ul>
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

  const referenceLng = 13.66395; // Referencia para decidir el lado
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
  // Ocultar ruta si existe
  if (currentRoutePolyline) {
    currentRoutePolyline.setMap(null);
    currentRoutePolyline = null;
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
  closeAll()
  let content = '<h3>Listado de Hoteles</h3><ul>';
  hotels.forEach((hotel, index) => {
    content += `<li class="hotel-item" data-index="${index}" style="cursor:pointer;">${hotel.nombre}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  showSidebar()
  
  document.querySelectorAll('.hotel-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const hotel = hotels[index];
      if (hotel && hotel.marker) {
        google.maps.event.trigger(hotel.marker, 'click');
      }
      if (hotel) {
        const descripcionConSaltos = hotel.descripcion.replace(/\\n/g, '<br>');
        let infoHotelHTML = `
          <h3>${hotel.nombre}</h3>
          <p>${descripcionConSaltos}</p>
          <p><strong>Precio:</strong> ${hotel.precio} €</p>
          <h4>Servicios</h4>
          <ul>${hotel.servicios.map(servicio => `<li>${servicio}</li>`).join('')}</ul>
        `;
        document.getElementById("infoSection").innerHTML = infoHotelHTML;
      }
    });
  });
}

// =======================
// 6) Mostrar listado de Rutas y dibujar la seleccionada
// =======================
function mostrarRutas() {
  closeAll()
  let content = '<h3>Rutas Turísticas</h3><ul>';
  routes.forEach((route, index) => {
    const formattedName = route.ruta_nombre.replace(/ - \d+(\.\d+)?$/, '');
    content += `<li class="route-item" data-index="${index}" style="cursor:pointer;">${formattedName}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  showSidebar()

  document.querySelectorAll('.route-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const route = routes[index];
      if (route) {
        dibujarRuta(route);
        let infoRouteHTML = `
          <h3>${route.ruta_nombre}</h3>
          <p><strong>Tipo de ruta:</strong> ${route.tipo_ruta}</p>
          <p><strong>Longitud:</strong> ${route.longitud_km} Km</p>
          <p><strong>Duración:</strong> ${route.duracion_hr} horas</p>
          <p><strong>Popularidad:</strong> ${route.popularidad}</p>
        `;
        document.getElementById("infoSection").innerHTML = infoRouteHTML;
      }
    });
  });
}

function mostrarSitios() {
  closeAll()
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

function catmullRom(t, p0, p1, p2, p3) {
  return 0.5 * ((2 * p1) +
                (-p0 + p2) * t +
                (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t);
}

function getCurvePoints(path, numOfSegments = 20) {
  if (path.length < 2) {
    return path;
  }
  
  // Convertir cada objeto {lat, lng} en un objeto google.maps.LatLng
  let pts = path.map(coord => new google.maps.LatLng(coord.lat, coord.lng));
  
  // Agregar duplicados al inicio y al final para que la fórmula tenga suficientes puntos
  pts.unshift(pts[0]);
  pts.push(pts[pts.length - 1]);
  
  let curvePoints = [];
  // Iterar entre los puntos, creando segmentos curvos para cada "cuarteto"
  for (let i = 1; i < pts.length - 2; i++) {
    for (let j = 0; j <= numOfSegments; j++) {
      let t = j / numOfSegments;
      let lng = catmullRom(t, pts[i - 1].lng(), pts[i].lng(), pts[i + 1].lng(), pts[i + 2].lng());
      let lat = catmullRom(t, pts[i - 1].lat(), pts[i].lat(), pts[i + 1].lat(), pts[i + 2].lat());
      curvePoints.push(new google.maps.LatLng(lat, lng));
    }
  }
  return curvePoints;
}


// =======================
// Función para dibujar la ruta seleccionada
// =======================
function dibujarRuta(route) {
  const rutaPath = route.coordenadas; 
  
  // Generar puntos curvos a partir de la ruta original
  const curvedPath = getCurvePoints(rutaPath, 20); // Puedes ajustar 20 (número de segmentos) según el detalle deseado
  
  if (currentRoutePolyline) {
    currentRoutePolyline.setMap(null);
  }
  
  currentRoutePolyline = new google.maps.Polyline({
    path: curvedPath,
    geodesic: true, // Si bien esto traza la línea sobre la superficie terrestre, la suavización se logra con la interpolación
    strokeColor: "#39FF14",
    strokeOpacity: 1.0,
    strokeWeight: 2
  });
  
  currentRoutePolyline.setMap(map);
  if (curvedPath.length > 0) {
    map.setCenter(curvedPath[0]);
  }
  return currentRoutePolyline;
}


// Inicializa el mapa al cargar la ventana
window.onload = initMap;
