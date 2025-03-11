// Arreglo global de hoteles con su nombre y coordenadas
// (Las coordenadas son de ejemplo; puedes modificarlas según necesites)
const hotels = [
  { name: "Alletra Boutique Hotel", lat: 47.5636, lng: 13.6367 }, // HECHO
  { name: "Alletra Diamond Grand Hotel", lat: 47.5524, lng: 13.6496}, // HECHO
  { name: "Alletra Haven", lat: 47.55415, lng: 13.6465 }, // HECHO
  { name: "Alletra Resort", lat: 47.55245, lng: 13.6377 }, // HECHO
  { name: "Apollo Diamond Suites", lat: 47.56703, lng: 13.65034 }, // HECHO
  { name: "Apollo Executive Beach Resort", lat: 47.56005, lng: 13.64723 }, // HECHO
  { name: "Aruba Lodge", lat: 47.56238, lng: 13.64962 }, // HECHO
  { name: "Aruba Luxury Lodge", lat: 47.56229, lng: 13.66395}, // HECHO
  { name: "Cray Villas", lat: 47.5579, lng: 13.6793 }, // HECHO
  { name: "Ezmeral Grand Hotel", lat: 47.5555, lng: 13.6821}, // HECHO
  { name: "GreenLake Digital Business Suites", lat: 47.5506, lng: 13.6953}, // HECHO
  { name: "GreenLake Platinum Heritage Inn", lat: 47.555, lng: 13.6896}, // HECHO
  { name: "InfoSight Boutique Hotel", lat: 47.5573, lng: 13.6909}, // HECHO
  { name: "Nimble Inn", lat: 47.5560, lng: 13.6930 },
  { name: "Pointnext Signature Residences & Suites", lat: 47.5562, lng: 13.6942 },
  { name: "Primera Grand", lat: 47.5564, lng: 13.6954 },
  { name: "ProLiant Haven", lat: 47.5566, lng: 13.6966 },
  { name: "ProLiant Place", lat: 47.5568, lng: 13.6978 },
  { name: "ProLiant Towers", lat: 47.5570, lng: 13.6998 },
  { name: "Simplivity Golden Plaza Hotel", lat: 47.5572, lng: 13.6935 },
  { name: "Synergy Golden Grand Hotel", lat: 47.5574, lng: 13.6948 },
  { name: "dHCI Executive Boutique Hotel", lat: 47.5576, lng: 13.6961 },
  { name: "Apollo Resort & Spa", lat: 47.5578, lng: 13.6973 },
  { name: "Apollo Towers", lat: 47.56025, lng: 13.7074 }, // HECHO
  { name: "dHCI Platinum Beach Resort", lat: 47.55975, lng: 13.70892 } // HECHO
];

let map;
let currentInfoWindow = null; // Para saber cuál InfoWindow está abierto

function initMap() {
  // Centro del mapa
  const centerCoords = { lat: 47.5626, lng: 13.6493 };

  // Límites permitidos para el mapa (puedes ajustarlos)
  const allowedBounds = {
    north: 47.57,
    south: 47.55,
    west: 13.63,
    east: 13.71
  };

  // Creación del mapa
  map = new google.maps.Map(document.getElementById("map"), {
    center: centerCoords,
    zoom: 16,
    tilt: 60,
    heading: 20,
    mapId: "TU_MAP_ID", // Reemplaza con tu MAP ID (o quita esta propiedad si no la usas)
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

  // ============= CREACIÓN DE MARCADORES PARA CADA HOTEL =============
  hotels.forEach(hotel => {
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.name,
      icon: {
        url: "/static/Images/hotel.png", // Usa el mismo ícono para todos
        scaledSize: new google.maps.Size(80, 80)
      }
    });

    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="min-width:150px">
          <h3>${hotel.name}</h3>
          <p>Información sobre ${hotel.name}.</p>
        </div>
      `
    });

    marker.addListener("click", () => {
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1500);
      openMarkerInfo(marker, infoWindow, `
        <h3>${hotel.name}</h3>
        <p>Detalles y promociones de ${hotel.name}.</p>
      `);
    });
  });
}

// Inicializa el mapa al cargar la ventana
window.onload = initMap;

/* =======================================================
   FUNCIONES AUXILIARES PARA SINCRONIZAR INFOWINDOW Y PANEL
   ======================================================= */
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

function openMarkerInfo(marker, infoWindow, panelHTML) {
  // Cierra cualquier InfoWindow o panel abierto
  closeAll();
  // Abre el InfoWindow correspondiente
  infoWindow.open(map, marker);
  currentInfoWindow = infoWindow;
  // Actualiza el contenido del panel lateral
  document.getElementById("infoSection").innerHTML = panelHTML;
  showSidebar();
  // Si el usuario cierra el InfoWindow, también se cierra el panel
  infoWindow.addListener("closeclick", () => {
    closeAll();
  });
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar.classList.contains("open")) {
    closeAll();
  } else {
    showSidebar();
  }
}

/* =======================================================
   FUNCIÓN PARA MOSTRAR EL PANEL CON EL LISTADO DE HOTELES
   ======================================================= */
function mostrarHoteles() {
  let content = '<h3>Listado de Hoteles</h3><ul>';
  hotels.forEach(hotel => {
    content += `<li>${hotel.name}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  showSidebar();
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
