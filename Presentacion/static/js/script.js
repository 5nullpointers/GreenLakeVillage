/* Presentacion/static/js/script.js */

// Variables globales
let map;
let currentInfoWindow = null;
let hotels = [];
let routes = [];
let restaurants = [];
let farmacias = [];
let tiendas = [];
let parques = [];
let atracciones = [];
let museos = [];
let transporte = [];
let ratingsInfo = {};
let currentRoutePolyline = null;

// =======================
// 1) Se llama automáticamente cuando la API de Google Maps termina de cargar
// =======================
function initMap() {
  const centerCoords = { lat: 47.5626, lng: 13.6493 };

  // Límites permitidos para el mapa
  const allowedBounds = {
    north: 47.58,
    south: 47.544,
    west: 13.612,
    east: 13.72
  };

  // Crear el mapa con estilo satélite y sin labels/roads
  map = new google.maps.Map(document.getElementById("map"), {
    center: centerCoords,
    zoom: 16,
    tilt: 60,
    heading: 20,
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

  // =======================
  // 1. Cargar rutas de la API (para mostrarlas en el panel)
  // =======================
  fetch('/api/rutas')
    .then(response => response.json())
    .then(data => {
      routes = data; // Guardamos en variable global
    })
    .catch(error => console.error("Error al cargar rutas:", error));

  // 2. Cargar hoteles y sus ratings
  fetch('/api/hoteles')
    .then(response => response.json())
    .then(data => {
      hotels = data;
      return fetch('/api/ratings');
    })
    .then(response => response.json())
    .then(ratingsData => {
      ratingsInfo = ratingsData;
      crearMarcadores(); // Marcadores de hoteles
    })
    .catch(error => console.error("Error al cargar hoteles:", error));

  // 3. Cargar restaurantes y sus ratings
  fetch('/api/restaurantes')
    .then(response => response.json())
    .then(data => {
      restaurants = data;
      return fetch('/api/ratings');
    })
    .then(response => response.json())
    .then(ratingsData => {
      ratingsInfo = ratingsData;
      crearMarcadoresHoteles(); // Marcadores de restaurantes (el nombre "Hoteles" es herencia)
    })
    .catch(error => console.error("Error al cargar restaurantes:", error));

  // 4. Cargar farmacias
  fetch('/api/farmacias')
    .then(response => response.json())
    .then(data => {
      farmacias = data;
      crearMarcadoresFarmacias();
    })
    .catch(error => console.error("Error al cargar farmacias:", error));

  // 5. Cargar tiendas
  fetch('/api/tiendas')
    .then(response => response.json())
    .then(data => {
      tiendas = data;
      crearMarcadoresTiendas();
    })
    .catch(error => console.error("Error al cargar tiendas:", error));

  // 6. Cargar parques
  fetch('/api/parques')
    .then(response => response.json())
    .then(data => {
      parques = data;
      crearMarcadoresParques();
    })
    .catch(error => console.error("Error al cargar parques:", error));

  // 7. Cargar atracciones
  fetch('/api/atracciones')
    .then(response => response.json())
    .then(data => {
      atracciones = data;
      crearMarcadoresAtracciones();
    })
    .catch(error => console.error("Error al cargar atracciones:", error));

  // 8. Cargar museos
  fetch('/api/museos')
    .then(response => response.json())
    .then(data => {
      museos = data;
      crearMarcadoresMuseos();
    })
    .catch(error => console.error("Error al cargar museos:", error));

  // 9. Cargar transporte
  fetch('/api/transporte')
    .then(response => response.json())
    .then(data => {
      transporte = data;
      crearMarcadoresTransporte();
    })
    .catch(error => console.error("Error al cargar transporte:", error));
}

function cambiarImagenFallback(img, imagenNombre) {
  // Intentar cargar desde la carpeta "Restaurantes"
  img.onerror = function() {
      // Si tampoco está en "Restaurantes", usar la imagen por defecto de Hoteles
      img.src = "/static/Images/Hoteles/default.jpg";
  };
  img.src = "/static/Images/Restaurantes/" + imagenNombre;
}

// =======================
// 2) Crear Marcadores (hoteles, restaurantes, etc.)
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
          <img src="/static/Images/Hoteles/${hotel.imagen || "default.jpg"}" 
               alt="${hotel.nombre}" 
               onerror="cambiarImagenFallback(this, '${hotel.imagen}')"
               style="width:100%; height:auto; margin-bottom:10px; max-height:150px;" />
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
  // A pesar del nombre, esto crea marcadores de "restaurants"
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
          <img src="/static/Images/Restaurantes/${restaurant.imagen || "default.jpg"}"
               alt="${restaurant.nombre}"
               onerror="cambiarImagenFallback(this, '${restaurant.imagen}')"
               style="width:100%; height:auto; margin-bottom:10px; max-height:150px;" />
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

// Crea marcadores para farmacias, tiendas, parques, etc. (lógica similar)
function crearMarcadoresFarmacias() { /* ... */ }
function crearMarcadoresTiendas() { /* ... */ }
function crearMarcadoresParques() { /* ... */ }
function crearMarcadoresAtracciones() { /* ... */ }
function crearMarcadoresMuseos() { /* ... */ }
function crearMarcadoresTransporte() { /* ... */ }

// =======================
// Panel lateral (side panel) e InfoWindow
// =======================
function getSidePanelHTML(item, rating) {
  // Muestra información detallada en el panel lateral
  let ratingText = "⭐ 0.0 (0 opiniones)";
  if (rating) {
    ratingText = `⭐ ${rating.media_puntuacion.toFixed(1)} (${rating.numero_comentarios} opiniones)`;
  }

  const descConSaltos = (item.descripcion || "").replace(/\\n/g, "<br>");
  const servicesList = item.servicios?.map(s => `<li>${s}</li>`).join("") || "";
  const detailsURL = `/hoteles/${item._id}`; // Por si quieres un link a detalles

  return `
    <div class="dropdown-container">
      <div class="hotel-card">
        <img src="/static/Images/Hoteles/${item.imagen || "default.jpg"}" 
             alt="${item.nombre}" 
             onerror="cambiarImagenFallback(this, '${item.imagen}')"
             class="hotel-image">
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
    </div>
  `;
}

function openMarkerInfo(marker, infoWindow, panelContent) {
  closeAll();
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.remove("left", "right");

  const referenceLng = 13.66395; // Para decidir el lado del panel
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
  // Si hay una ruta dibujada, la quitamos
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
// Botones del menú: "Hoteles", "Rutas", "Sitios", etc.
// =======================
function mostrarHoteles() {
  closeAll();
  let content = '<h3>Listado de Hoteles</h3><ul>';
  hotels.forEach((hotel, index) => {
    content += `<li class="hotel-item" data-index="${index}" style="cursor:pointer;">${hotel.nombre}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  showSidebar();

  document.querySelectorAll('.hotel-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const hotel = hotels[index];
      if (hotel && hotel.marker) {
        google.maps.event.trigger(hotel.marker, 'click');
      }
    });
  });
}

function mostrarSitios() {
  closeAll();
  document.getElementById("infoSection").innerHTML = "<h3>Sitios de Interés</h3><p>Próximamente...</p>";
  showSidebar();
}

// =======================
// Mostrar listado de Rutas y dibujar la seleccionada
// (versión “al estilo Node”: llamamos a /get-route, decodificamos polyline)
// =======================
function mostrarRutas() {
  closeAll();
  let content = '<h3>Rutas Turísticas</h3><ul>';
  routes.forEach((route, index) => {
    // Quitar la parte " - 6.1" si existe
    const formattedName = route.ruta_nombre.replace(/ - \d+(\.\d+)?$/, '');
    content += `<li class="route-item" data-index="${index}" style="cursor:pointer;">${formattedName}</li>`;
  });
  content += '</ul>';

  document.getElementById("infoSection").innerHTML = content;
  showSidebar();

  // Evento click en cada ruta
  document.querySelectorAll('.route-item').forEach(item => {
    item.addEventListener('click', function() {
      const index = this.getAttribute('data-index');
      const route = routes[index];
      if (route) {
        // Llamar a /get-route en Flask y dibujar la polyline
        dibujarRuta(route);

        // Mostrar info de la ruta en el panel
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

// =======================
// Función para dibujar la ruta en el mapa con la “Routes API v2” vía Flask
// (al estilo Node: pedimos la polyline a /get-route, luego decodificamos)
// =======================
async function dibujarRuta(route) {
  // Quitar la polilínea anterior si existe
  if (currentRoutePolyline) {
    currentRoutePolyline.setMap(null);
  }

  // Construir el objeto origin/destination
  const origin = { latitude: route.origen[0], longitude: route.origen[1] };
  const destination = { latitude: route.destino[0], longitude: route.destino[1] };

  try {
    // 1) Llamar a nuestro backend Flask
    const resp = await fetch("/get-route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin, destination }),
    });
    const data = await resp.json();

    // 2) Verificar que haya una ruta
    if (!data.routes || !data.routes[0]) {
      console.error("No se encontró una ruta válida en la respuesta:", data);
      return;
    }

    // 3) Decodificar la polyline
    const encoded = data.routes[0].polyline.encodedPolyline;
    const path = google.maps.geometry.encoding.decodePath(encoded);

    // 4) Dibujar la polyline en el mapa
    currentRoutePolyline = new google.maps.Polyline({
      path,
      geodesic: true,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 4,
      map: map,
    });

    // 5) Centrar el mapa en el primer punto (opcional)
    if (path.length > 0) {
      map.setCenter(path[0]);
    }
  } catch (error) {
    console.error("Error llamando a /get-route:", error);
  }
}
