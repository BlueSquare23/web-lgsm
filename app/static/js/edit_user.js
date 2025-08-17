if (userRole == 'admin') {
  document.getElementById('is_admin').checked = true;
  togglePermissions();
}

// Function to apply the user permissions to the form.
function applyUserPermissions() {
  // Check or uncheck basic permissions based on userPerms.
  document.getElementById('install_servers').checked = userPerms.install_servers;
  document.getElementById('add_servers').checked = userPerms.add_servers;
  document.getElementById('mod_settings').checked = userPerms.mod_settings;
  document.getElementById('edit_cfgs').checked = userPerms.edit_cfgs;
  document.getElementById('edit_jobs').checked = userPerms.edit_jobs;
  document.getElementById('delete_server').checked = userPerms.delete_server;

  // Check the controls checkboxes.
  const controlCheckboxes = document.querySelectorAll('.control-checkbox');
  controlCheckboxes.forEach(checkbox => {
    if (userPerms.controls.includes(checkbox.value)) {
      checkbox.checked = true;
    }
  });

  // Check the servers checkboxes.
  const serverCheckboxes = document.querySelectorAll('.gameserver-checkbox');
  serverCheckboxes.forEach(checkbox => {
    if (userPerms.server_ids.includes(checkbox.value)) {
      checkbox.checked = true;
    }
  });
}

function toggleViewUserPassFields() {
  const userPassFields = document.getElementById('user_pass_fields');
  userPassFields.classList.toggle('d-none');
}

function togglePermissions() {
  const isAdmin = document.getElementById('is_admin').checked;
  const nonAdminPermissions = document.getElementById('non-admin-permissions');

  // Disable or enable all non-admin fields based on admin checkbox.
  nonAdminPermissions.querySelectorAll('input').forEach(input => {
      input.disabled = isAdmin;
  });

  nonAdminPermissions.querySelectorAll('button').forEach(button => {
      button.disabled = isAdmin;
  });
}

// Function to select/unselect all controls.
function toggleAllControls() {
  const allCommandCheckboxes = document.querySelectorAll('.control-checkbox');
  const isChecked = Array.from(allCommandCheckboxes).every(checkbox => checkbox.checked);
  allCommandCheckboxes.forEach(checkbox => checkbox.checked = !isChecked);
}

// Function to select/unselect all game servers.
function toggleAllGameServers() {
  const allGsCheckboxes = document.querySelectorAll('.gameserver-checkbox');
  const isChecked = Array.from(allGsCheckboxes).every(checkbox => checkbox.checked);
  allGsCheckboxes.forEach(checkbox => checkbox.checked = !isChecked);
}

// Initial call to set the correct state on page load.
// Call applyUserPermissions and togglePermissions to auto check checkboxes
// according backend user perms.
document.addEventListener('DOMContentLoaded', function() {
  applyUserPermissions();
  togglePermissions();
});

