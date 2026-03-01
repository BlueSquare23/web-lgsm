function populateFormWithJson(jsonData) {
    // Set the basic text fields.
    document.getElementById('install_name').value = jsonData.install_name || '';
    document.getElementById('install_path').value = jsonData.install_path || '';
    document.getElementById('script_name').value = jsonData.script_name || '';
    document.getElementById('username').value = jsonData.username || '';

    // Set the install type radio button.
    const installType = jsonData.install_type || 'local';
    const radioButtons = document.querySelectorAll('input[name="install_type"]');
    radioButtons.forEach(radio => {
        if (radio.value === installType) {
            radio.checked = true;
        } else {
            radio.checked = false;
        }
    });

    // Handle the remote host field visibility and value.
    const remoteHostDiv = document.getElementById('remote_host');
    if (installType === 'remote') {
        remoteHostDiv.style.display = 'block';
        document.getElementById('install_host').value = jsonData.install_host || '';
    } else {
        remoteHostDiv.style.display = 'none';
    }

    // Set hidden server_id field.
    const serverIdField = document.getElementById('server_id');
    if (serverIdField && jsonData.id) {
        serverIdField.value = jsonData.id;
    }

    // For keyfile path.
/*    const keyfileField = document.getElementById('keyfile_path');
 *  TODO: Implement this.
    if (keyfileField && jsonData.keyfile_path) {
        keyfileField.value = jsonData.keyfile_path;
    }
*/
}

populateFormWithJson(jsonData);
