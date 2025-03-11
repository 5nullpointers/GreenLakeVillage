// Variables globales
let map;
let currentInfoWindow = null;  // Para saber cuál InfoWindow está abierto

function initMap() {
  const hallstatt = { lat: 47.5626, lng: 13.6493 };

  const allowedBounds = {
    north: 47.57,
    south: 47.55,
    west: 13.63,
    east: 13.71
  };

  // Creación del mapa
  map = new google.maps.Map(document.getElementById("map"), {
    center: hallstatt,
    zoom: 16,
    tilt: 60,
    heading: 20,
    mapId: "TU_MAP_ID",  // Reemplaza con tu MAP ID (o quita si no usas uno)
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

  // Ocultar overlay de carga cuando el mapa ya esté listo
  google.maps.event.addListenerOnce(map, "idle", () => {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) {
      overlay.style.opacity = "0";
      setTimeout(() => {
        overlay.style.display = "none";
      }, 500);
    }
  });

  // ============= MARCADOR 1: Hotel =============
  const hotelMarker = new google.maps.Marker({
    position: { lat: 47.5620, lng: 13.6488 },
    map: map,
    title: "Hotel Buenavista 3D",
    icon: {
      url: "/static/Images/hotel.png",
      scaledSize: new google.maps.Size(80, 80)
    }
  });

  // Creamos el InfoWindow del hotel (fuera del listener para reusarlo)
  const hotelInfoWindow = new google.maps.InfoWindow({
    content: `
      <div style="min-width:150px">
        <h3>Hotel Buenavista</h3>
        <p>¡Bienvenido a un hotel con vista panorámica!</p>
      </div>
    `
  });

  // Al hacer clic en el marcador, abrimos su InfoWindow y panel
  hotelMarker.addListener("click", () => {
    hotelMarker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => hotelMarker.setAnimation(null), 1500);

    // Abrimos (cerrando cualquier anterior)
    openMarkerInfo(hotelMarker, hotelInfoWindow, `
      <h3>Hotel Buenavista</h3>
      <p>Información adicional del hotel...</p>
    `);
  });

  // ============= MARCADOR 2: Exploración Restos =============
  const restosMarker = new google.maps.Marker({
    position: { lat: 47.560, lng: 13.674 },
    map: map,
    title: "Exploración de Restos",
    icon: {
      url: "/static/Images/pirate_boat.png",
      scaledSize: new google.maps.Size(80, 80)
    }
  });

  const restosInfoWindow = new google.maps.InfoWindow({
    content: `
      <div style="min-width:150px">
        <h3>Exploración de Restos</h3>
        <p>Descubre un antiguo naufragio y su historia.</p>
      </div>
    `
  });

  restosMarker.addListener("click", () => {
    restosMarker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => restosMarker.setAnimation(null), 1500);

    openMarkerInfo(restosMarker, restosInfoWindow, `
      <h3>Exploración de Restos</h3>
      <p>¡Sumérgete en una aventura submarina y descubre un naufragio histórico!</p>
    `);
  });

  // ============= MARCADOR 3: Buceo =============
  const buceoMarker = new google.maps.Marker({
    position: { lat: 47.56, lng: 13.66 },
    map: map,
    title: "Zona de Buceo",
    icon: {
      url: "/static/Images/coral.png",
      scaledSize: new google.maps.Size(60, 60)
    }
  });

  const buceoInfoWindow = new google.maps.InfoWindow({
    content: `
      <div style="min-width:150px">
        <h3>Buceo</h3>
        <p>Disfruta de la riqueza submarina y la fauna marina local.</p>
      </div>
    `
  });

  buceoMarker.addListener("click", () => {
    buceoMarker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => buceoMarker.setAnimation(null), 1500);

    openMarkerInfo(buceoMarker, buceoInfoWindow, `
      <h3>Buceo</h3>
      <p>Explora arrecifes y corales sumergidos en estas aguas cristalinas.</p>
    `);
  });

  // ============= MARCADOR 4: Puerto =============
  const puertoMarker = new google.maps.Marker({
    position: { lat: 47.5564, lng: 13.6490 },
    map: map,
    title: "Puerto",
    icon: {
      url: "/static/Images/boat.png",
      scaledSize: new google.maps.Size(60, 60)
    }
  });

  const puertoInfoWindow = new google.maps.InfoWindow({
    content: `
      <div style="min-width:150px">
        <h3>Puerto</h3>
        <p>Embarcaciones turísticas y pesca tradicional.</p>
      </div>
    `
  });

  puertoMarker.addListener("click", () => {
    puertoMarker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => puertoMarker.setAnimation(null), 1500);

    openMarkerInfo(puertoMarker, puertoInfoWindow, `
      <h3>Puerto</h3>
      <p>En este muelle podrás tomar paseos en barco y conocer la vida marinera local.</p>
    `);
  });
}

// Inicializa el mapa al cargar la ventana
window.onload = initMap;

/* =======================================================
   FUNCIONES AUXILIARES PARA SINCRONIZAR INFOWINDOW Y PANEL
   ======================================================= */

/**
 * Cierra todo: panel lateral e InfoWindow (si existe)
 */
function closeAll() {
  // Cerrar panel si está abierto
  closeSidebar();
  // Cerrar InfoWindow actual (si hay uno)
  if (currentInfoWindow) {
    currentInfoWindow.close();
    currentInfoWindow = null;
  }
}

/**
 * Muestra el panel lateral
 */
function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}

/**
 * Cierra el panel lateral
 */
function closeSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar.classList.contains("open")) {
    sidebar.classList.remove("open");
  }
}

/**
 * Abre el InfoWindow del marcador y muestra el panel con el contenido dado,
 * cerrando cualquier InfoWindow anterior.
 */
function openMarkerInfo(marker, infoWindow, panelHTML) {
  // 1) Cerrar todo lo anterior (otro InfoWindow/panel)
  closeAll();

  // 2) Abrir este InfoWindow
  infoWindow.open(map, marker);
  currentInfoWindow = infoWindow;

  // 3) Ponemos contenido en el panel y lo abrimos
  document.getElementById("infoSection").innerHTML = panelHTML;
  showSidebar();

  // 4) Si el usuario cierra el InfoWindow (clic en la X), cierra también el panel
  infoWindow.addListener("closeclick", () => {
    closeAll();
  });
}

/**
 * Abre/cierra el panel lateral.
 * Si estaba abierto, cierra todo (panel + InfoWindow).
 * Si estaba cerrado, lo abre (pero no abre InfoWindow por sí solo).
 */
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar.classList.contains("open")) {
    // Si está abierto, cierra todo
    closeAll();
  } else {
    // Si está cerrado, lo abre
    showSidebar();
  }
}

/* ---- Opcional: funciones para chatbot, etc. ---- */
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