// Variables globales
let map;
let heatmap; // Capa de heatmap

// Referencias a los botones del grupo Heatmap
let btnToggleHeatmap;

// Referencias a los botones del grupo MapType
let btnSatellite, btnTerrain, btnNormal;
let mapTypeButtons = []; // Array para los botones de tipo de mapa
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
// Nueva variable global: propiedades asociadas al usuario propietario
let currentUserProperties = [
  "Alletra Boutique Hotel",
  "Alletra Haven",
  "Alletra Diamond Grand Hotel",
  "Alletra Resort",
  "Transportes Bou S.L. Restaurante"
];

/**
 * Función principal de inicialización del mapa
 */
function initMap() {
  const hallstatt = { lat: 47.5626, lng: 13.6493 };

  const allowedBounds = {
    north: 47.57,
    south: 47.55,
    west: 13.63,
    east: 13.71
  };

  // Inicializa el mapa de Google
  map = new google.maps.Map(document.getElementById("map"), {
    center: hallstatt,
    zoom: 16,
    tilt: 60,
    heading: 20,
    disableDefaultUI: true,
    restriction: {
      latLngBounds: allowedBounds,
      strictBounds: true
    },
    mapTypeId: 'satellite',
    styles: [
      { elementType: "labels", stylers: [{ visibility: "off" }] },
      { featureType: "road", stylers: [{ visibility: "off" }] },
      { featureType: "transit", stylers: [{ visibility: "off" }] },
      { featureType: "poi", stylers: [{ visibility: "off" }] }
    ]
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

  // Datos de ejemplo para el Heatmap
  const heatmapData = [
    new google.maps.LatLng(47.5636, 13.6367),
    new google.maps.LatLng(47.5524, 13.6496),
    new google.maps.LatLng(47.55415, 13.6465),
    new google.maps.LatLng(47.55245, 13.6377),
    new google.maps.LatLng(47.56703, 13.65034),
    new google.maps.LatLng(47.56005, 13.64723),
    new google.maps.LatLng(47.56238, 13.64962),
    new google.maps.LatLng(47.56229, 13.66395),
    new google.maps.LatLng(47.5579, 13.6793),
    new google.maps.LatLng(47.5555, 13.6821),
    new google.maps.LatLng(47.5506, 13.6953),
    new google.maps.LatLng(47.5553, 13.6896),
    new google.maps.LatLng(47.5573, 13.6909),
    new google.maps.LatLng(47.55431, 13.6874),
    new google.maps.LatLng(47.55391, 13.68545),
    new google.maps.LatLng(47.5524, 13.6798),
    new google.maps.LatLng(47.5589, 13.682),
    new google.maps.LatLng(47.55408, 13.6977),
    new google.maps.LatLng(47.5571, 13.702),
    new google.maps.LatLng(47.55726, 13.6464),
    new google.maps.LatLng(47.5575, 13.68524),
    new google.maps.LatLng(47.5563, 13.6969),
    new google.maps.LatLng(47.5559, 13.7027),
    new google.maps.LatLng(47.56025, 13.7074),
    new google.maps.LatLng(47.55975, 13.70892)
  ];

  // Crea la capa de heatmap, inicialmente apagada (map: null)
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: heatmapData,
    map: null,
    radius: 100,
    opacity: 0.8
  });

  // Obtiene las referencias a los botones
  btnToggleHeatmap = document.getElementById("toggleHeatmap");
  btnSatellite = document.getElementById("setSatellite");
  btnTerrain = document.getElementById("setTerrain");
  btnNormal = document.getElementById("setNormal");

  // Define el array de botones de tipo de mapa
  mapTypeButtons = [btnSatellite, btnTerrain, btnNormal];

  // Asigna eventos al botón de Heatmap
  if (btnToggleHeatmap) {
    btnToggleHeatmap.addEventListener("click", toggleHeatmap);
  }
  // Asigna eventos a los botones de tipo de mapa
  if (btnSatellite) {
    btnSatellite.addEventListener("click", () => setMapType("satellite"));
  }
  if (btnTerrain) {
    btnTerrain.addEventListener("click", () => setMapType("terrain"));
  }
  if (btnNormal) {
    btnNormal.addEventListener("click", () => setMapType("roadmap"));
  }

  // Si deseas marcar por defecto un botón de tipo de mapa como activo (por ejemplo, Satélite):
  if (btnSatellite) {
    highlightActiveMapTypeButton(btnSatellite);
  }
}

/**
 * Se llama al cargar la ventana
 */
window.onload = initMap;

/**
 * Activa/Desactiva el heatmap
 * Este botón actúa de forma independiente, es decir, su estado activo
 * no afecta ni es afectado por los botones de tipo de mapa.
 */
function toggleHeatmap() {
  if (!heatmap) return;

  if (heatmap.getMap()) {
    // Si el heatmap está activo, se apaga y se quita el resaltado en su botón
    heatmap.setMap(null);
    btnToggleHeatmap.classList.remove("active");
  } else {
    // Si estaba apagado, se enciende y se resalta el botón de heatmap
    heatmap.setMap(map);
    btnToggleHeatmap.classList.add("active");
  }
}

/**
 * Cambia el tipo de mapa (satellite, terrain, roadmap, etc.)
 * Aquí solo se afectan los botones de tipo de mapa.
 */
function setMapType(type) {
  map.setMapTypeId(type);

  // Aplica un estilo global para quitar íconos y etiquetas
  map.setOptions({
    styles: [
      { featureType: "all", elementType: "labels", stylers: [{ visibility: "off" }] },
      { featureType: "all", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
      { featureType: "poi", elementType: "geometry", stylers: [{ visibility: "off" }] },
      { featureType: "transit", elementType: "geometry", stylers: [{ visibility: "off" }] }
    ]
  });

  // Dependiendo del "type", resalta el botón correspondiente del grupo de tipo de mapa
  switch (type) {
    case "satellite":
      highlightActiveMapTypeButton(btnSatellite);
      break;
    case "terrain":
      highlightActiveMapTypeButton(btnTerrain);
      break;
    case "roadmap":
      highlightActiveMapTypeButton(btnNormal);
      break;
    default:
      // Si no se reconoce, se desmarcan todos del grupo map type
      highlightActiveMapTypeButton(null);
  }
}

// =======================
// 2) Crear Marcadores (hoteles, restaurantes, etc.)
// =======================
function crearMarcadores() {
  hotels.forEach(hotel => {
    // Solo crea marcador si la propiedad del hotel está en las propiedades del usuario
    if (!currentUserProperties.includes(hotel.nombre)) return;
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.nombre,
      icon: {
        url: "/static/images/hotel.png",
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
          <img src="/static/images/Hoteles/${hotel.imagen || "default.jpg"}" 
               alt="${hotel.nombre}" 
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
    // Solo crea marcador si el restaurante está en las propiedades del usuario
    if (!currentUserProperties.includes(restaurant.nombre)) return;
    const marker = new google.maps.Marker({
      position: { lat: restaurant.lat, lng: restaurant.lng },
      map: map,
      title: restaurant.nombre,
      icon: {
        url: "/static/images/restaurante.png",
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
          <img src="/static/images/Restaurantes/${restaurant.imagen || "default.jpg"}"
               alt="${restaurant.nombre}"
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

/**
 * Marca un botón del grupo MapType como activo (y desmarca los demás)
 * Si se pasa null, se desmarcan todos.
 */
function highlightActiveMapTypeButton(buttonElement) {
  mapTypeButtons.forEach(btn => {
    if (!btn) return;
    btn.classList.remove("active");
  });
  if (buttonElement) {
    buttonElement.classList.add("active");
  }
}

/* --------------------------------------
   Funciones del panel lateral (sidebar)
---------------------------------------*/

/**
 * Muestra información de hoteles en el panel lateral
 */
function mostrarHoteles() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Hoteles</h3>
    <ul>
      <li>Hotel Ficticio (Haz clic en el mapa)</li>
      <li>Hotel Panorama</li>
      <li>Hotel Lago Azul</li>
    </ul>
  `;
  showSidebar();
}

/**
 * Muestra información de rutas turísticas en el panel lateral
 */
function mostrarRutas() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Rutas Turísticas</h3>
    <p>Aquí se mostrarían rutas en el mapa (senderismo, bici, etc.)</p>
  `;
  showSidebar();
}

/**
 * Muestra información de sitios de interés en el panel lateral
 */
function mostrarSitios() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Sitios de Interés</h3>
    <p>Marcadores de monumentos, museos, miradores...</p>
  `;
  showSidebar();
}

/**
 * Abre o cierra el sidebar
 */
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("open");
}

/**
 * Fuerza la apertura del sidebar
 */
function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}

/* --------------------------------------
   Función para enviar mensajes al chatbot
---------------------------------------*/
function sendMessage() {
  const userMessage = document.getElementById("user-input").value;

  if (!userMessage) {
    alert("Por favor escribe un mensaje");
    return;
  }

  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: userMessage }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.response) {
        document.getElementById("chat-response").innerHTML = `<p><strong>IA:</strong> ${data.response}</p>`;
      } else {
        document.getElementById("chat-response").innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
      }
    })
    .catch(error => console.error("Error:", error));
}
