document.addEventListener('DOMContentLoaded', function() {
  const passwordInput = document.getElementById('password');
  const togglePassword = document.getElementById('togglePassword');

  // Password visibility toggles
  togglePassword.addEventListener('click', function() {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      this.querySelector('i').classList.toggle('bi-eye');
      this.querySelector('i').classList.toggle('bi-eye-slash');
  });
});

