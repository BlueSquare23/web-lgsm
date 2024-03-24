function openForm(server, opt, formName) {
  document.getElementById(formName).style.display = "block";
  if ('sudo_pass_form'.localeCompare(formName) === 0) {
    if (server) {
      document.getElementById('server_name').value=server;
      document.getElementById('full_name').value=opt;
      document.getElementById('install_btn').value="Install " + opt;
    }
  } else if ('send_cmd_form'.localeCompare(formName) === 0) {
    if (server) {
      document.getElementById('server').value=server;
      document.getElementById('command').value=opt;
      document.getElementById('send_btn').value="Send";
    }
  }
}

function closeForm(formName){
  document.getElementById(formName).style.display = "none";
}
