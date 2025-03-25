document.addEventListener("DOMContentLoaded", function() {
    let currentPreferenceIndex = 0;
    const preferences = document.querySelectorAll('.preference');
    const finalMessage = document.querySelector('.final-message');
    const submitButton = document.getElementById('submit');
    const preferencesList = document.getElementById('preferences-list');
    const selectedPreferencesSection = document.querySelector('.selected-preferences');
    const cancelButton = document.getElementById('cancel');
    const saveButton = document.getElementById('save-preferences');

    let selectedPreferences = []; // Aquí se almacenarán las preferencias seleccionadas con "Sí"

    // Mostrar la primera preferencia
    showPreference(currentPreferenceIndex);

    // Función para mostrar la preferencia
    function showPreference(index) {
        if (index < preferences.length) {
            preferences[index].style.display = 'flex'; // Asegúrate de que la preferencia esté visible
            setTimeout(() => {
                preferences[index].classList.add('visible'); // Aplica la clase visible para animación
            }, 10); // Retardo pequeño para aplicar la animación correctamente
        } else {
            // Mostrar resumen de preferencias
            selectedPreferencesSection.style.display = "block";
            preferencesList.innerHTML = selectedPreferences.map(preference => `<li>${preference}</li>`).join('');
        }
    }

    // Función para manejar las respuestas
    function handleResponse(answer, preference) {
        const currentPreference = preferences[currentPreferenceIndex];
        currentPreference.classList.remove('visible'); // Eliminar la clase de visibilidad antes de pasar a la siguiente

        // Solo agregar la preferencia si el usuario dijo "Sí"
        if (answer) {
            selectedPreferences.push(preference);  // Almacenar solo las preferencias "Sí"
        }

        // Después de la animación, pasar a la siguiente preferencia
        setTimeout(() => {
            currentPreference.style.display = 'none'; // Ocultar la preferencia actual
            currentPreferenceIndex++;
            if (currentPreferenceIndex < preferences.length) {
                preferences[currentPreferenceIndex].style.display = 'flex'; // Mostrar la siguiente preferencia
                setTimeout(() => {
                    preferences[currentPreferenceIndex].classList.add('visible'); // Agregar la clase visible para la animación
                }, 10); // Retardo pequeño para aplicar la animación correctamente
            } else {
                // Mostrar el resumen si ya no hay más preferencias
                selectedPreferencesSection.style.display = "block";
                preferencesList.innerHTML = selectedPreferences.map(preference => `<li>${preference}</li>`).join('');
            }
        }, 600); // Tiempo de la animación de deslizamiento
    }

    // Añadir los eventos para los botones "Sí" y "No"
    document.querySelectorAll('.yes').forEach(button => {
        button.addEventListener('click', function() {
            handleResponse(true, button.closest('.preference').id); // Marcar como "Sí" la preferencia seleccionada
        });
    });

    document.querySelectorAll('.no').forEach(button => {
        button.addEventListener('click', function() {
            handleResponse(false, button.closest('.preference').id); // No agregar la preferencia si es "No"
        });
    });

    // Función para cancelar y volver a las preferencias
    cancelButton.addEventListener('click', function() {
        selectedPreferencesSection.style.display = "none";
        currentPreferenceIndex = 0;
        selectedPreferences = [];
        showPreference(currentPreferenceIndex);
    });

    // Función para guardar las preferencias al finalizar
    saveButton.addEventListener('click', function() {
        const userEmail = sessionStorage.getItem('user_email') || "user@example.com"; // Cambia esto por el correo del usuario autenticado
        
        if (selectedPreferences.length === 0) {
            alert("No has seleccionado ninguna preferencia.");
            return;
        }
    
        console.log("Preferencias a guardar:", selectedPreferences); // Verificar el contenido
    
        fetch('/save-preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail,
                preferencias: selectedPreferences // Solo se envían las preferencias seleccionadas como "Sí"
            })
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect; // Redirige al mapa si todo salió bien
            } else {
                alert("Error al guardar las preferencias: " + data.error);
            }
        }).catch(error => {
            console.error("Error en la solicitud:", error);
            alert("Hubo un problema al guardar las preferencias.");
        });
    });
});
