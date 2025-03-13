document.addEventListener('DOMContentLoaded', function() {
    const userName = document.querySelector('.user-name');
    const dropdown = document.getElementById('userDropdown');

    userName.addEventListener('click', function(event) {
        // Alterna la clase "open" para activar la animación
        dropdown.classList.toggle('open');
        event.stopPropagation(); // Evita que se cierre inmediatamente al propagar el evento
    });

    // Oculta el menú al hacer clic en cualquier parte de la página
    document.addEventListener('click', function() {
        dropdown.classList.remove('open');
    });

    // Nuevo: Cambiar imágenes de las opciones del menú
    const opciones = document.querySelectorAll('.mapa-opcion-1 li');
    
    // Define las nuevas rutas para cada opción
    const nuevasImagenes = [
        "/static/images/inicioBlanco.png",
        "/static/images/profileBlanco.png",
        "/static/images/ForoBlanco.png",
        "/static/images/ReseñasBlanco.png"
    ];
    
    opciones.forEach((opcion, index) => {
        // Al pasar el ratón, cambia la imagen
        opcion.addEventListener('mouseenter', function() {
            const img = opcion.querySelector('img');
            if (img && nuevasImagenes[index]) {
                // Guarda el src original para volver a él después
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });
        
        // Al quitar el ratón, restaura la imagen original
        opcion.addEventListener('mouseleave', function() {
            const img = opcion.querySelector('img');
            if (img && img.dataset.original) {
                img.src = img.dataset.original;
            }
        });
    });
});