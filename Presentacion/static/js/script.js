// Variables globales
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
    mapId: "TU_MAP_ID",  // Reemplaza con tu MAP ID
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
}

// Inicializa el mapa al cargar la ventana
window.onload = initMap;

// Muestra info en el panel
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

function mostrarRutas() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Rutas Turísticas</h3>
    <p>Aquí se mostrarían rutas en el mapa (senderismo, bici, etc.)</p>
  `;
  showSidebar();
}

function mostrarSitios() {
  document.getElementById("infoSection").innerHTML = `
    <h3>Sitios de Interés</h3>
    <p>Marcadores de monumentos, museos, miradores...</p>
  `;
  showSidebar();
}

// Abre / Cierra el sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("open");
}

// Fuerza que el sidebar se abra
function showSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar.classList.contains("open")) {
    sidebar.classList.add("open");
  }
}
