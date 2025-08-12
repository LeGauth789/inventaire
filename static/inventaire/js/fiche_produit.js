document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.toggle-historique-btn');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const targetId = button.getAttribute('data-target');
      const target = document.getElementById(targetId);

      if (!target) return;

      const isShown = target.classList.contains('show');

      if (isShown) {
        // Cacher l'historique
        target.classList.remove('show');
        button.setAttribute('aria-expanded', 'false');
      } else {
        // Montrer l'historique
        target.classList.add('show');
        button.setAttribute('aria-expanded', 'true');
      }
    });
  });
});
