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
// 1) Inicializar el mapa cuando la API de Google Maps termine de cargar
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

  // Crear el mapa con estilo satélite sin labels/roads
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
  // Cargar datos para el mapa
  // =======================
  fetch('/api/rutas')
    .then(response => response.json())
    .then(data => { routes = data; })
    .catch(error => console.error("Error al cargar rutas:", error));

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

  fetch('/api/farmacias')
    .then(response => response.json())
    .then(data => {
      farmacias = data;
      crearMarcadoresFarmacias();
    })
    .catch(error => console.error("Error al cargar farmacias:", error));

  fetch('/api/tiendas')
    .then(response => response.json())
    .then(data => {
      tiendas = data;
      crearMarcadoresTiendas();
    })
    .catch(error => console.error("Error al cargar tiendas:", error));

  fetch('/api/parques')
    .then(response => response.json())
    .then(data => {
      parques = data;
      crearMarcadoresParques();
    })
    .catch(error => console.error("Error al cargar parques:", error));

  fetch('/api/atracciones')
    .then(response => response.json())
    .then(data => {
      atracciones = data;
      crearMarcadoresAtracciones();
    })
    .catch(error => console.error("Error al cargar atracciones:", error));

  fetch('/api/museos')
    .then(response => response.json())
    .then(data => {
      museos = data;
      crearMarcadoresMuseos();
    })
    .catch(error => console.error("Error al cargar museos:", error));

  fetch('/api/transporte')
    .then(response => response.json())
    .then(data => {
      transporte = data;
      crearMarcadoresTransporte();
    })
    .catch(error => console.error("Error al cargar transporte:", error));
}

// Función para fallback de imagen
function cambiarImagenFallback(img, imagenNombre) {
  img.onerror = function() {
    img.src = "/static/Images/Hoteles/default.jpg";
  };
  img.src = "/static/Images/Restaurantes/" + imagenNombre;
}

// =======================
// Crear Marcadores para hoteles, restaurantes, etc.
// =======================
function crearMarcadores() {
  hotels.forEach(hotel => {
    const marker = new google.maps.Marker({
      position: { lat: hotel.lat, lng: hotel.lng },
      map: map,
      title: hotel.nombre,
      icon: { url: "/static/Images/hotel.png", scaledSize: new google.maps.Size(80, 80) }
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
  restaurants.forEach(restaurant => {
    const marker = new google.maps.Marker({
      position: { lat: restaurant.lat, lng: restaurant.lng },
      map: map,
      title: restaurant.nombre,
      icon: { url: "/static/Images/restaurante.png", scaledSize: new google.maps.Size(80, 80) }
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

// Las siguientes funciones se definen de forma similar
function crearMarcadoresFarmacias() { /* ... */ }
function crearMarcadoresTiendas() { /* ... */ }
function crearMarcadoresParques() { /* ... */ }
function crearMarcadoresAtracciones() { /* ... */ }
function crearMarcadoresMuseos() { /* ... */ }
function crearMarcadoresTransporte() { /* ... */ }

// =======================
// Panel lateral e InfoWindow
// =======================
function getSidePanelHTML(item, rating) {
  let ratingText = "⭐ 0.0 (0 opiniones)";
  if (rating) {
    ratingText = `⭐ ${rating.media_puntuacion.toFixed(1)} (${rating.numero_comentarios} opiniones)`;
  }
  const descConSaltos = (item.descripcion || "").replace(/\\n/g, "<br>");
  const servicesList = item.servicios?.map(s => `<li>${s}</li>`).join("") || "";
  const detailsURL = `/hoteles/${item._id}`;
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
            <a href="/reservar/${item._id}" class="btn reserve">
              Reservar Ahora
            </a>
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
  sidebar.classList.remove("foro-style");
  const referenceLng = 13.66395;
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
  infoWindow.addListener("closeclick", () => { closeAll(); });
}

function closeAll() {
  closeSidebar();
  if (currentInfoWindow) {
    currentInfoWindow.close();
    currentInfoWindow = null;
  }
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
// Botones del menú: Hoteles, Rutas, Sitios, etc.
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

function mostrarRutas() {
  closeAll();
  let content = '<h3>Rutas Turísticas</h3><ul>';
  routes.forEach((route, index) => {
    const formattedName = route.ruta_nombre.replace(/ - \d+(\.\d+)?$/, '');
    content += `<li class="route-item" data-index="${index}" style="cursor:pointer;">${formattedName}</li>`;
  });
  content += '</ul>';
  document.getElementById("infoSection").innerHTML = content;
  showSidebar();
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

function mostrarForo() {
  // Cierra otras ventanas/infowindows
  closeAll();
  
  // Obtén el contenedor del sidebar y añade la clase para el foro
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.add("foro-style");
  
  // Realiza la petición para obtener los temas del foro
  fetch('/api/foro/temas')
    .then(response => response.json())
    .then(temas => {
      let content = '<div class="forum-container">';
      content += '<h3>Temas del Foro</h3><ul>';
      temas.forEach((tema, index) => {
        content += `<li class="tema-item" data-index="${index}" style="cursor:pointer;">${tema.titulo}</li>`;
      });
      content += '</ul></div>';
      document.getElementById("infoSection").innerHTML = content;
      showSidebar();
      
      // Añade el listener para cargar comentarios al hacer clic en cada tema
      document.querySelectorAll('.tema-item').forEach(item => {
        item.addEventListener('click', function() {
          const index = this.getAttribute('data-index');
          cargarComentarios(temas[index]);
        });
      });
    })
    .catch(error => console.error("Error al cargar los temas del foro:", error));
}


function cargarComentarios(tema) {
  fetch(`/api/foro/temas/${tema._id}/comentarios`)
    .then(response => response.json())
    .then(comentarios => {
      let content = `<h3>${tema.titulo}</h3>`;
      content += `<p>${tema.descripcion}</p>`;
      content += `<hr><h4>Comentarios</h4>`;
      if (comentarios.length === 0) {
        content += `<p>No hay comentarios aún.</p>`;
      } else {
        comentarios.forEach(c => {
          content += `<div class="comentario">
                        <p><strong>${c.autor}</strong> dice:</p>
                        <p>${c.comentario}</p>`;
          if(c.imagen_url) {
            content += `<img src="${c.imagen_url}" alt="Imagen de comentario" style="max-width: 100%;">`;
          }
          content += `</div><hr>`;
        });
      }
      // Formulario actualizado con botón personalizado y contenedor para vista previa
      content += `
        <h4>Agrega tu comentario</h4>
        <form id="comentarioForm" enctype="multipart/form-data">
          <textarea name="comentario" placeholder="Escribe tu comentario..." required></textarea>
          <div class="custom-file-upload">
            <input type="file" name="imagen" id="file-upload">
            <label for="file-upload" class="custom-file-label">Examinar</label>
          </div>
          <div id="uploadPreview"></div>
          <button type="submit">Enviar</button>
        </form>
      `;
      document.getElementById("infoSection").innerHTML = content;
      showSidebar();

      // Agregar evento para mostrar la vista previa del archivo seleccionado
      const fileInput = document.getElementById("file-upload");
      if (fileInput) {
        fileInput.addEventListener("change", function(e) {
          const preview = document.getElementById("uploadPreview");
          preview.innerHTML = "";
          const file = e.target.files[0];
          if (file && file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function(e) {
              const img = document.createElement("img");
              img.src = e.target.result;
              preview.appendChild(img);
            };
            reader.readAsDataURL(file);
          } else if(file) {
            preview.textContent = "Archivo seleccionado: " + file.name;
          }
        });
      }

      // Manejar el envío del formulario
      document.getElementById("comentarioForm").addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        formData.append("tema_id", tema._id);
        fetch('/api/foro/comentar', {
          method: "POST",
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if(data.success) {
            cargarComentarios(tema);
          } else {
            alert("Error al enviar el comentario");
          }
        })
        .catch(error => console.error("Error al enviar comentario:", error));
      });
    })
    .catch(error => console.error("Error al cargar comentarios:", error));
}


// =======================
// Función para dibujar la ruta vía Flask (Routes API v2)
// =======================
async function dibujarRuta(route) {
  if (currentRoutePolyline) {
    currentRoutePolyline.setMap(null);
  }
  const origin = { latitude: route.origen[0], longitude: route.origen[1] };
  const destination = { latitude: route.destino[0], longitude: route.destino[1] };
  try {
    const resp = await fetch("/get-route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin, destination }),
    });
    const data = await resp.json();
    if (!data.routes || !data.routes[0]) {
      console.error("No se encontró una ruta válida en la respuesta:", data);
      return;
    }
    const encoded = data.routes[0].polyline.encodedPolyline;
    const path = google.maps.geometry.encoding.decodePath(encoded);
    currentRoutePolyline = new google.maps.Polyline({
      path,
      geodesic: true,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 4,
      map: map,
    });
    if (path.length > 0) {
      map.setCenter(path[0]);
    }
  } catch (error) {
    console.error("Error llamando a /get-route:", error);
  }
}

// Función para marcar un reto como notificado
function marcarRetoNotificado(retoId) {
  fetch('/api/retos/marcar_notificado', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({reto_id: retoId})
  })
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      console.error("No se pudo marcar el reto como notificado", data.error);
    }
  })
  .catch(error => console.error("Error al marcar el reto", error));
}

// Función que consulta los retos completados pendientes de notificación
function checkRetosPendientes() {
  fetch('/api/retos_pendientes')
    .then(response => response.json())
    .then(retos => {
      if (retos.length > 0) {
        // Se muestra el primer reto pendiente
        const reto = retos[0];
        const popup = document.createElement('div');
        popup.id = "retoPopup";
        popup.style.position = "fixed";
        popup.style.top = "20px";
        popup.style.right = "20px";
        popup.style.backgroundColor = "#4caf50";
        popup.style.color = "#fff";
        popup.style.padding = "15px";
        popup.style.borderRadius = "5px";
        popup.style.zIndex = "1000";
        popup.textContent = `¡Nuevo reto: ${reto.nombre}! ${reto.descripcion}`;
        document.body.appendChild(popup);
        // Marcar el reto como notificado para que no se muestre en futuras cargas
        marcarRetoNotificado(reto.id);
        setTimeout(() => {
          popup.remove();
        }, 5000);
      }
    })
    .catch(error => console.error("Error al obtener retos pendientes:", error));
}

// Se consulta al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  checkRetosPendientes();
});


// =======================
// Asistente Virtual: Enviar mensaje y mostrar respuesta
// =======================
document.getElementById('assistant-send').addEventListener('click', async () => {
  const input = document.getElementById('assistant-input');
  const message = input.value.trim();
  if (!message) return;
  appendMessage('user', message);
  input.value = '';

  const loadingMessage = document.createElement('div');
  loadingMessage.className = 'message assistant loading';
  loadingMessage.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  const chatContainer = document.getElementById('assistant-chat');
  chatContainer.appendChild(loadingMessage);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    loadingMessage.remove();
    if (data.response) {
      appendMessage('assistant', data.response);
    } else {
      appendMessage('assistant', 'Lo siento, no pude obtener una respuesta.');
    }
  } catch (error) {
    loadingMessage.remove();
    appendMessage('assistant', 'Error al conectar con el asistente.');
    console.error(error);
  }
});

function appendMessage(sender, text) {
  const chatContainer = document.getElementById('assistant-chat');
  const messageElem = document.createElement('div');
  messageElem.className = 'message ' + sender;
  messageElem.innerHTML = marked.parse(text);
  chatContainer.appendChild(messageElem);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// =======================
// Asistente Virtual: Mostrar/Ocultar desplegable
// =======================
const assistant = document.getElementById('assistant');
const assistantHeader = document.querySelector('.assistant-header');

assistantHeader.addEventListener('click', function(e) {
  e.stopPropagation();
  assistant.classList.toggle('open');
});

document.addEventListener('click', function(e) {
  if (!assistant.contains(e.target)) {
    assistant.classList.remove('open');
  }
});

const profileImg = document.querySelector('.profile-img');
const dropdown = document.getElementById('userDropdown');

profileImg.addEventListener('click', function (event) {
    dropdown.classList.toggle('open');
    event.stopPropagation();
});

document.addEventListener('click', function () {
    dropdown.classList.remove('open');
});

// ------------------------------------------------
// --- INICIO NUEVO (LÓGICA PARA EL MODAL RESERVA)
// ------------------------------------------------

// Cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  const reservationModal = document.getElementById('reservationModal');
  const closeModalBtn = document.getElementById('closeModal');
  const reservationForm = document.getElementById('reservationForm');
  const hotelIdInput = document.getElementById('hotelIdInput');

  // Cerrar modal con la "X"
  closeModalBtn.addEventListener('click', function() {
    reservationModal.style.display = 'none';
  });

  // Cerrar modal si el usuario hace clic fuera del contenido
  window.addEventListener('click', function(e) {
    if (e.target === reservationModal) {
      reservationModal.style.display = 'none';
    }
  });

  // Capturar clic en cualquier botón/enlace con class="reserve"
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('reserve')) {
      e.preventDefault();
      console.log("¡Clic en Reservar Ahora!");
      // Obtener el _id del hotel desde data-hotel-id
      const hotelId = e.target.getAttribute('data-hotel-id');
      hotelIdInput.value = hotelId || '';

      // Mostrar el modal
      reservationModal.style.display = 'block';
    }
  });

  // Manejo del envío del formulario de reserva
  reservationForm.addEventListener('submit', function(e) {
    e.preventDefault();

    const hotelId = hotelIdInput.value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const numPersons = document.getElementById('numPersons').value;

    // Petición POST a /api/reservas
    fetch('/api/reservas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        hotelId: hotelId,
        startDate: startDate,
        endDate: endDate,
        numPersons: numPersons
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('Reserva realizada con éxito');
        // Opcional: redirige a otra página
        // window.location.href = '/misreservas';
        reservationModal.style.display = 'none';
      } else {
        alert('Error al realizar la reserva: ' + data.message);
      }
    })
    .catch(err => {
      console.error(err);
      alert('Hubo un error al conectarse al servidor');
    });
  });
});

// -----------------------------------------------
// --- FIN NUEVO (LÓGICA PARA EL MODAL RESERVA) ---
// -----------------------------------------------
