// Variables globales
let map;

function initMap() {
    console.log("Cargando mapa...");

    if (!document.getElementById("map")) {
        console.error("❌ Error: No se encontró el div con id='map'.");
        return;
    }

    const hallstatt = { lat: 47.5626, lng: 13.6493 };

    map = new google.maps.Map(document.getElementById("map"), {
        center: hallstatt,
        zoom: 16,
        mapTypeId: "satellite",
        disableDefaultUI: false,
    });

    console.log("✅ Mapa cargado correctamente.");

    // Agregar marcador
    const marker = new google.maps.Marker({
        position: hallstatt,
        map: map,
        title: "GreenLake Village",
    });

    // Evento clic en el marcador
    marker.addListener("click", () => {
        const infoWindow = new google.maps.InfoWindow({
            content: "<h3>GreenLake Village</h3><p>Un hermoso destino turístico.</p>",
        });
        infoWindow.open(map, marker);
    });
}

// Asegurar que el mapa se inicializa correctamente cuando la API de Google Maps se carga
google.maps.event.addDomListener(window, "load", initMap);

// Muestra información en el panel lateral
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

// Funciones para manejar el Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("open");
}

function showSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar.classList.contains("open")) {
        sidebar.classList.add("open");
    }
}

// Chatbot (Mejorado con try-catch)
async function sendMessage() {
    const userMessage = document.getElementById("user-input").value;

    if (!userMessage.trim()) {
        alert("Por favor escribe un mensaje.");
        return;
    }

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage }),
        });

        const data = await response.json();

        if (data.response) {
            document.getElementById("chat-response").innerHTML = `<p><strong>IA:</strong> ${data.response}</p>`;
        } else {
            document.getElementById("chat-response").innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
        }
    } catch (error) {
        console.error("❌ Error en el chatbot:", error);
        document.getElementById("chat-response").innerHTML = `<p><strong>Error:</strong> No se pudo obtener respuesta.</p>`;
    }
}
