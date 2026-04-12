// JavaScript to handle modal data
document.addEventListener('DOMContentLoaded', function() {
  // Handle advanced settings button click
  const advancedSettingsButtons = document.querySelectorAll('.advanced-settings-btn');
  
  advancedSettingsButtons.forEach(button => {
    button.addEventListener('click', function() {
      const scriptName = this.getAttribute('data-script-name');
      const fullName = this.getAttribute('data-full-name');
      const installPath = this.getAttribute('data-install-path');
      const username = this.getAttribute('data-username');
      const install_type = 'local';

      console.log(scriptName);
      console.log(fullName);
      console.log(installPath);
      console.log(username);

      // Set the script name in the modal form
      document.getElementById('modal_script_name').value = scriptName;
      
      // Pre-fill the script name field if it exists in the form
      const scriptNameField = document.querySelector('#advancedSettingsForm input[name="script_name"]');
      if (scriptNameField) {
        scriptNameField.value = scriptName;
      }

      const installNameField = document.querySelector('#advancedSettingsForm input[name="install_name"]');
      if (installNameField) {
        installNameField.value = fullName;
      }

      const installPathField = document.querySelector('#advancedSettingsForm input[name="install_path"]');
      if (installPathField) {
        installPathField.value = installPath;
      }

      const usernameField = document.querySelector('#advancedSettingsForm input[name="username"]');
      if (usernameField) {
        usernameField.value = username;
      }
      
      // Update modal title or display editing info
      const editingHeader = document.getElementById('editingHeader');
      const currentEditName = document.getElementById('currentEditName');
      
      // Show editing header if editing existing
      editingHeader.style.display = 'block';
      currentEditName.textContent = `Currently Editing ${fullName}`;
    });
  });
  
  // Reset modal when closed
  const modal = document.getElementById('advancedSettingsModal');
  modal.addEventListener('hidden.bs.modal', function() {
    document.getElementById('modal_script_name').value = '';
    document.getElementById('editingHeader').style.display = 'none';
  });
});

