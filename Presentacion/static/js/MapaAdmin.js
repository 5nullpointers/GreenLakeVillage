// Variables globales
let map;
let heatmap; // Capa de heatmap

function initMap() {
  const hallstatt = { lat: 47.5626, lng: 13.6493 };

  const allowedBounds = {
    north: 47.57,
    south: 47.55,
    west: 13.63,
    east: 13.71
  };

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

  // Ejemplo de marcador
  const markerHotel = new google.maps.Marker({
    position: { lat: 47.5630, lng: 13.6498 },
    map: map,
    title: "Hotel Ficticio"
  });

  // Evento clic en el marcador
  markerHotel.addListener("click", () => {
    markerHotel.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => {
      markerHotel.setAnimation(null);
    }, 2000);

    const infoWindow = new google.maps.InfoWindow({
      content: "<h3>Hotel Ficticio</h3><p>Descripción...</p>"
    });
    infoWindow.open(map, markerHotel);

    // Muestra info también en el panel lateral
    document.getElementById("infoSection").innerHTML = `
      <h3>Hotel Ficticio</h3>
      <p>Este es un hotel imaginario...</p>
    `;
    showSidebar();
  });

  // Inicializar heatmap (ejemplo de datos)
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
  
  heatmap = new google.maps.visualization.HeatmapLayer({
    data: heatmapData,
    map: null, // Se inicia desactivado
    radius: 100, // Aumenta el radio de dispersión
    opacity: 0.8 // Ajusta la opacidad
  });

  // Asignar eventos a los botones de control del mapa
  if (document.getElementById("toggleHeatmap")) {
    document.getElementById("toggleHeatmap").addEventListener("click", toggleHeatmap);
  }
  if (document.getElementById("setSatellite")) {
    document.getElementById("setSatellite").addEventListener("click", () => setMapType("satellite"));
  }
  if (document.getElementById("setTerrain")) {
    document.getElementById("setTerrain").addEventListener("click", () => setMapType("terrain"));
  }
  if (document.getElementById("setNormal")) {
    document.getElementById("setNormal").addEventListener("click", () => setMapType("roadmap"));
  }
}

// Inicializa el mapa al cargar la ventana
window.onload = initMap;

// Función para activar o desactivar el heatmap
function toggleHeatmap() {
  if (heatmap.getMap()) {
    heatmap.setMap(null);
  } else {
    heatmap.setMap(map);
  }
}

// Cambia el tipo de mapa
function setMapType(type) {
  map.setMapTypeId(type);
  // Aplica un estilo global para quitar todos los íconos (POI, tránsito, etc.)
  map.setOptions({
    styles: [
      // Oculta todas las etiquetas de texto
      { featureType: "all", elementType: "labels", stylers: [{ visibility: "off" }] },
      // Oculta específicamente los íconos (incluye POI, transit, etc.)
      { featureType: "all", elementType: "labels.icon", stylers: [{ visibility: "off" }] },
      // Deshabilita la representación geométrica de puntos de interés
      { featureType: "poi", elementType: "geometry", stylers: [{ visibility: "off" }] },
      // Deshabilita la representación de elementos de tránsito
      { featureType: "transit", elementType: "geometry", stylers: [{ visibility: "off" }] }
    ]
  });
}

// Muestra información de hoteles en el panel lateral
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

// Muestra información de rutas turísticas en el panel lateral
function mostrarRutas() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Rutas Turísticas</h3>
    <p>Aquí se mostrarían rutas en el mapa (senderismo, bici, etc.)</p>
  `;
  showSidebar();
}

// Muestra información de sitios de interés en el panel lateral
function mostrarSitios() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Sitios de Interés</h3>
    <p>Marcadores de monumentos, museos, miradores...</p>
  `;
  showSidebar();
}

// Abre o cierra el sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("open");
}

// Fuerza la apertura del sidebar
function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}

// Función para enviar mensajes al chatbot
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
