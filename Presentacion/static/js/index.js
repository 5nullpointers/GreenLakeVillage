document.addEventListener("DOMContentLoaded", () => {
    const contactForm = document.getElementById("contactForm");
    contactForm.addEventListener("submit", (e) => {
      e.preventDefault();
      alert("Gracias por tu consulta. Te responderemos pronto.");
      contactForm.reset();
    });
  });
  