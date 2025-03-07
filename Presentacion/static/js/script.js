/* ----------------------------------------------
   script.js
   Lógica de la aplicación
---------------------------------------------- */

let map;

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
    mapId: "TU_MAP_ID",         // Reemplaza por tu MAP ID
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

  markerHotel.addListener("click", () => {
    markerHotel.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => {
      markerHotel.setAnimation(null);
    }, 2000);

    const infoWindow = new google.maps.InfoWindow({
      content: "<h3>Hotel Ficticio</h3><p>Descripción...</p>"
    });
    infoWindow.open(map, markerHotel);

    // Muestra info también en el panel
    document.getElementById("infoSection").innerHTML = `
      <h3>Hotel Ficticio</h3>
      <p>Este es un hotel imaginario...</p>
    `;
    // Asegúrate de que se abra el panel si estaba cerrado
    showSidebar();
  });
}

// Inicializa el mapa cuando se cargue la ventana
window.onload = initMap;

// Funciones para mostrar info en el panel
function mostrarHoteles() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Lista de Hoteles</h3>
    <ul>
      <li>Hotel Ficticio (Click en el mapa)</li>
      <li>...</li>
    </ul>
  `;
  showSidebar();
}

function mostrarRutas() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Rutas Turísticas</h3>
    <p>Aquí se mostrarían las rutas, polilíneas, etc.</p>
  `;
  showSidebar();
}

function mostrarSitios() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Sitios de Interés</h3>
    <p>Puedes listar y colocar marcadores en el mapa.</p>
  `;
  showSidebar();
}

// Función para abrir/cerrar el sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("open");
}

// Función para forzar que el sidebar se abra
function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}
