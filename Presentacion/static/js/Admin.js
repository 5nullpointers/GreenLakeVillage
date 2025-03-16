document.addEventListener('DOMContentLoaded', function () {
    // Manejo del dropdown de usuario: se usa la imagen de perfil en lugar del span
    const profileImg = document.querySelector('.profile-img');
    const dropdown = document.getElementById('userDropdown');

    profileImg.addEventListener('click', function (event) {
        dropdown.classList.toggle('open');
        event.stopPropagation();
    });

    document.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });

    // Array con las rutas de las imágenes en versión blanca
    const nuevasImagenes = [
        "/static/images/inicioBlanco.png",
        "/static/images/profileBlanco.png",
        "/static/images/ForoBlanco.png",
        "/static/images/ReseñasBlanco.png"
    ];

    // Selecciona todas las opciones del menú
    const opciones = document.querySelectorAll('.sidebar li');

    opciones.forEach((opcion, index) => {
        const img = opcion.querySelector('img');

        // Si la opción ya es la activa (por ejemplo, definida en el HTML),
        // se actualiza la imagen a la versión blanca
        if (opcion.classList.contains('active') && nuevasImagenes[index]) {
            if (!img.dataset.original) {
                img.dataset.original = img.src;
            }
            img.src = nuevasImagenes[index];
        }

        // Al pasar el mouse sobre la opción, se cambia la imagen a la versión blanca
        opcion.addEventListener('mouseenter', function () {
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });

        // Al quitar el mouse, se restaura la imagen original solo si la opción NO es la activa
        opcion.addEventListener('mouseleave', function () {
            if (img && img.dataset.original && !opcion.classList.contains('active')) {
                img.src = img.dataset.original;
            }
        });

        // (Opcional) Actualizar la opción activa al hacer clic
        opcion.addEventListener('click', function () {
            // Remueve la clase "active" de todas las opciones y restaura su imagen original
            opciones.forEach(o => {
                o.classList.remove('active');
                const imgTemp = o.querySelector('img');
                if (imgTemp && imgTemp.dataset.original) {
                    imgTemp.src = imgTemp.dataset.original;
                }
            });
            // Añade "active" a la opción clicada y actualiza su imagen a la versión blanca
            opcion.classList.add('active');
            if (img && nuevasImagenes[index]) {
                if (!img.dataset.original) {
                    img.dataset.original = img.src;
                }
                img.src = nuevasImagenes[index];
            }
        });
    });
});


