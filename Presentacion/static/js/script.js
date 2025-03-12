// Arreglo global de hoteles con su nombre y coordenadas
const hotels = [
  { name: "Alletra Boutique Hotel", lat: 47.5636, lng: 13.6367 },
  { name: "Alletra Diamond Grand Hotel", lat: 47.5524, lng: 13.6496 },
  { name: "Alletra Haven", lat: 47.55415, lng: 13.6465 },
  { name: "Alletra Resort", lat: 47.55245, lng: 13.6377 },
  { name: "Apollo Diamond Suites", lat: 47.56703, lng: 13.65034 },
  { name: "Apollo Executive Beach Resort", lat: 47.56005, lng: 13.64723 },
  { name: "Aruba Lodge", lat: 47.56238, lng: 13.64962 },
  { name: "Aruba Luxury Lodge", lat: 47.56229, lng: 13.66395 },
  { name: "dHCI Platinum Beach Resort", lat: 47.5579, lng: 13.6793 },
  { name: "Ezmeral Grand Hotel", lat: 47.5555, lng: 13.6821 },
  { name: "GreenLake Digital Business Suites", lat: 47.5506, lng: 13.6953 },
  { name: "GreenLake Platinum Heritage Inn", lat: 47.5553, lng: 13.6896 },
  { name: "InfoSight Boutique Hotel", lat: 47.5573, lng: 13.6909 },
  { name: "Nimble Inn", lat: 47.55431, lng: 13.6874 },
  { name: "Pointnext Signature Residences & Suites", lat: 47.55391, lng: 13.68545 },
  { name: "Primera Grand", lat: 47.5524, lng: 13.6798 },
  { name: "ProLiant Haven", lat: 47.5589, lng: 13.682 },
  { name: "ProLiant Place", lat: 47.55408, lng: 13.6977 },
  { name: "ProLiant Towers", lat: 47.5571, lng: 13.702 },
  { name: "Simplivity Golden Plaza Hotel", lat: 47.55726, lng: 13.6464 },
  { name: "Synergy Golden Grand Hotel", lat: 47.5575, lng: 13.68524 },
  { name: "dHCI Executive Boutique Hotel", lat: 47.5563, lng: 13.6969 },
  { name: "Apollo Resort & Spa", lat: 47.5559, lng: 13.7027 },
  { name: "Apollo Towers", lat: 47.56025, lng: 13.7074 },
  { name: "Cray Villas", lat: 47.55975, lng: 13.70892 }  
];

let map;
let currentInfoWindow = null; // Para saber cuál InfoWindow está abierto
let ratingsInfo = {}; // Variable global para almacenar la información de ratings

// 1) Diccionario que asocia cada hotel con su archivo de imagen
// Ajusta los nombres de archivo según tu carpeta /static/Images/Hoteles
const hotelImages = {
  "Alletra Boutique Hotel": "alletra_boutique.jpg",
  "Alletra Diamond Grand Hotel": "alletra_diamond.jpg",
  "Alletra Haven": "alletra_haven.jpg",
  "Alletra Resort": "alletra_resort.jpg",
  "Apollo Diamond Suites": "apollo_diamond.jpg",
  "Apollo Executive Beach Resort": "apollo_executive.jpg",
  "Aruba Lodge": "aruba_lodge.jpg",
  "Aruba Luxury Lodge": "aruba_luxury.jpg",
  "Cray Villas": "cray_villas.jpg",
  "Ezmeral Grand Hotel": "ezmeral_grand.jpg",
  "GreenLake Digital Business Suites": "greenlake_digital.jpg",
  "GreenLake Platinum Heritage Inn": "greenlake_platinum.jpg",
  "InfoSight Boutique Hotel": "infosight_boutique.jpg",
  "Nimble Inn": "nimble_inn.jpg",
  "Pointnext Signature Residences & Suites": "pointnext_signature.jpg",
  "Primera Grand": "primera_grand.jpg",
  "ProLiant Haven": "proliant_haven.jpg",
  "ProLiant Place": "proliant_place.jpg",
  "ProLiant Towers": "proliant_towers.jpg",
  "Simplivity Golden Plaza Hotel": "simplivity_golden.jpg",
  "Synergy Golden Grand Hotel": "synergy_golden.jpg",
  "dHCI Executive Boutique Hotel": "dhci_executive.jpg",
  "Apollo Resort & Spa": "apollo_resort.jpg",
  "Apollo Towers": "apollo_towers.jpg",
  "dHCI Platinum Beach Resort": "dhci_platinum.jpg"
};

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

  // 2) Obtener la información de ratings desde la API
  fetch('/api/ratings')
    .then(response => response.json())
    .then(data => {
      ratingsInfo = data;
      // 3) Cuando tengamos los ratings, creamos los marcadores
      crearMarcadores();
    })
    .catch(error => console.error("Error al obtener ratings:", error));
}

// Crea todos los marcadores y les asigna el InfoWindow con su puntuación e imagen
function crearMarcadores() {
  hotels.forEach(hotel => {
    // Creamos el marcador
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.name,
      icon: {
        url: "/static/Images/hotel.png",
        scaledSize: new google.maps.Size(80, 80)
      }
    });

    // Creamos un InfoWindow (lo rellenamos al hacer click)
    const infoWindow = new google.maps.InfoWindow();

    // Escuchamos el click en el marcador
    marker.addListener("click", () => {
      // Animación de rebote
      marker.setAnimation(google.maps.Animation.BOUNCE);
      setTimeout(() => marker.setAnimation(null), 1500);

      // 4) Prepara el contenido con la puntuación
      let ratingContent = "";
      if (ratingsInfo[hotel.name]) {
        const rating = ratingsInfo[hotel.name];
        ratingContent = `<p>⭐ ${rating.media_puntuacion.toFixed(1)} 
                         (${rating.numero_comentarios} opiniones)</p>`;
      } else {
        ratingContent = "<p>Sin opiniones</p>";
      }

      // 5) Determina el archivo de imagen; si no hay, usa default
      let hotelImage = hotelImages[hotel.name];
      if (!hotelImage) {
        hotelImage = "default.jpg"; // Ajusta si tienes una imagen de respaldo
      }

      // 6) Ajusta el contenido del InfoWindow (imagen + puntuación + descripción)
      infoWindow.setContent(`
        <div style="min-width:250px">
          <img src="/static/Images/Hoteles/${hotelImage}" 
           alt="${hotel.name}" 
           style="width:100%; height:auto; margin-bottom:10px; max-height:200px;" />
          <h3>${hotel.name}</h3>
          ${ratingContent}
        </div>
      `);

      // Abre el InfoWindow sobre el marcador
      infoWindow.open(map, marker);

      // 7) Abre el panel lateral (sin puntuación, si así lo deseas)
      openMarkerInfo(
        marker,
        infoWindow,
        `
          <h3>${hotel.name}</h3>
          <p>Detalles y promociones de ${hotel.name}.</p>
        `
      );
    });
  });
}

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

  const sidebar = document.getElementById("sidebar");
  // Elimina clases previas de posicionamiento
  sidebar.classList.remove("left", "right");

  // Definimos la longitud de referencia de "Aruba Luxury Lodge"
  const referenceLng = 13.66395;
  const markerLng = marker.getPosition().lng();

  // Si el marcador está a la izquierda (menor lng) de Aruba Luxury Lodge, se abre a la derecha; de lo contrario, a la izquierda
  if (markerLng < referenceLng) {
    sidebar.classList.add("right");
  } else {
    sidebar.classList.add("left");
  }

  // Mantén la lógica de InfoWindow si gustas (aunque ya lo abrimos arriba)
  infoWindow.open(map, marker);
  currentInfoWindow = infoWindow;

  // Actualiza el contenido del panel lateral (sin rating, si no lo deseas)
  document.getElementById("infoSection").innerHTML = panelHTML;
  showSidebar();

  // Si se cierra el InfoWindow, se cierra también el panel
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

// Inicializa el mapa al cargar la ventana
window.onload = initMap;
