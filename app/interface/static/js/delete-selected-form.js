let deleteForm = document.getElementById("delete-selected-form");
if (deleteForm) {
  deleteForm.addEventListener('submit', async function(e) {
    e.preventDefault(); // Prevent the default form submission

    // Get all checked toggles.
    const checkboxes = document.querySelectorAll('input[name="server_id"]:checked');

    console.log(checkboxes);

    if (checkboxes.length === 0) {
        alert('No servers selected for deletion.');
        return;
    }

    if (!confirm('Are you sure you want to delete these servers?')) {
        return;
    }

    showSpinners();
    try {
        // Create an array of delete promises
        const deletePromises = Array.from(checkboxes).map(checkbox => {
            const serverId = checkbox.value;
            return fetch(`/api/delete/${serverId}`, { method: 'DELETE' });
        });
        
        // Wait for all deletions to complete.
        const responses = await Promise.all(deletePromises);
        
        // Check if all responses were successful.
        const allSuccessful = responses.every(response => response.ok);
        
        if (!allSuccessful) {
            throw new Error('Some servers failed to delete.');
        }
  
        // Redirect home on success
        window.location.replace("/home");
        
    } catch (error) {
        // Error Alert (Bootstrap)
        showAlert(`Error: ${error.message}`, 'danger');
    }
  });
};

