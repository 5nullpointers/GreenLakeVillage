document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  
  document.querySelectorAll('.hidden').forEach(el => {
    observer.observe(el);
  });
});

function toggleOpiniones() {
  var extraOpiniones = document.getElementById('opinion-adicional');
  var button = document.getElementById('mostrar-mas-btn');
  if (extraOpiniones.style.display === 'none') {
    extraOpiniones.style.display = 'block';
    button.innerText = 'Mostrar menos';
  } else {
    extraOpiniones.style.display = 'none';
    button.innerText = 'Mostrar más';
  }
}
