function runPreInstall(sName) {
  var serverName = sName;
  console.log(serverName);
  window.scrollTo(0,0);
  closeForm('sudo_pass_form');
  document.getElementById('pre_install').style.display = 'block';
  document.getElementById('spinners').style.display = 'block';
  var interval = setInterval(function() {
    document.getElementById('pre_install').style.display = 'block';
    document.getElementById('spinners').style.display = 'block';
    updateTerminal(serverName);
  }, 1000);
}
