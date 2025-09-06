function showAlert(message, type = 'success') {
  const alertContainer = document.getElementById('alert-container');

  // Create the alert HTML and append it
  alertContainer.insertAdjacentHTML('beforeend', `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `);
  dismissAlert();
}

function dismissAlert(newAlert = null) {
  const alertContainer = document.getElementById('alert-container');

  // Get the newly created alert if non supplied
  if (newAlert == null) {
    const alerts = alertContainer.getElementsByClassName('alert');
    newAlert = alerts[alerts.length - 1];
  }

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (newAlert.parentNode) {
      const bsAlert = new bootstrap.Alert(newAlert);
      bsAlert.close();
    }
  }, 5000);
}

// Dismiss all alerts from backend
function dismissAll() {
  const alertContainer = document.getElementById('alert-container');
  const alerts = alertContainer.getElementsByClassName('alert');
  Array.from(alerts).forEach(alertElement => {
    dismissAlert(alertElement);
  });
}
dismissAll();
