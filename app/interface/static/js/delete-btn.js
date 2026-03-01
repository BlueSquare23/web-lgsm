let deleteBtn = document.getElementById("delete-btn")

// On click run delete route fetch. Alert if fails.
deleteBtn.addEventListener('click', async function() {
  if (!confirm('Are you sure you want to delete this server?')) return;

  showSpinners();
  try {
      const response = await fetch(`/api/delete/${serverId}`, { method: 'DELETE' });
      
      if (!response.ok) throw new Error('Failed to delete server.');

      // Redirect home on success.
      window.location.replace("/home");
      
  } catch (error) {
      // Error Alert (Bootstrap)
      showAlert(`Error: ${error.message}`, 'danger');
  }
});
