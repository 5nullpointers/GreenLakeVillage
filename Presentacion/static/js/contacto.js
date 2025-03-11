document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");

    contactForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const nombre = document.getElementById("nombre").value.trim();
        const email = document.getElementById("email").value.trim();
        const telefono = document.getElementById("telefono").value.trim();
        const motivo = document.getElementById("motivo").value;
        const mensaje = document.getElementById("mensaje").value.trim();

        if (nombre === "" || email === "" || motivo === "" || mensaje === "") {
            alert("Por favor, completa todos los campos obligatorios.");
            return;
        }

        if (!validateEmail(email)) {
            alert("Por favor, introduce un correo electrónico válido.");
            return;
        }

        if (telefono !== "" && !validatePhone(telefono)) {
            alert("Por favor, introduce un número de teléfono válido.");
            return;
        }

        alert("Gracias por tu consulta. Te responderemos pronto.");
        contactForm.reset();
    });

    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validatePhone(phone) {
        const phoneRegex = /^\d{9,15}$/;
        return phoneRegex.test(phone);
    }
});
