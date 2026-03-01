// Helper function to display Bootstrap alerts.
function showAlert(message, type = 'success') {
  const alertContainer = document.getElementById('alert-container');
  const alertElement = document.createElement('div');
  
  alertElement.className = `alert alert-${type} alert-dismissible fade show`;
  alertElement.setAttribute('role', 'alert');
  alertElement.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  alertContainer.appendChild(alertElement);
  
  // Auto-remove alert after 5 seconds
  setTimeout(() => {
      alertElement.remove();
  }, 5000);
}

