function toggleMode() {
      document.body.classList.toggle('light-mode');
      const button = document.querySelector('.toggle-mode');
      button.textContent = document.body.classList.contains('light-mode') ? '🌞' : '🌙';
    }