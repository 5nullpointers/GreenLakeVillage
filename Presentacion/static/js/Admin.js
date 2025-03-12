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
});