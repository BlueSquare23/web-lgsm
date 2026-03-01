function openForm(server, opt, formName) {
  document.getElementById(formName).style.display = "block";
  if ('send_cmd_form'.localeCompare(formName) === 0) {
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
