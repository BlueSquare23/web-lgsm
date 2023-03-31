function openForm(server, fullName){
  document.getElementById("sudo_pass_form").style.display = "block";
  if (server){
    document.getElementById('server_name').value=server;
    document.getElementById('full_name').value=fullName;
    document.getElementById('install_btn').value="Install " + fullName;
  }
}

function closeForm(){
  document.getElementById("sudo_pass_form").style.display = "none";
}
