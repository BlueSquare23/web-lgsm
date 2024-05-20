const flexSwitchCheck = document.getElementById("flexSwitchCheckChecked");
checkAndReload();

flexSwitchCheck.addEventListener('click', function(){
  checkAndReload();
});

function checkAndReload() {
  if (flexSwitchCheck.checked) {
    setTimeout(function(){
      if (flexSwitchCheck.checked) {
        window.location.reload(1);
      }
    }, 1000 * 60 * 5);
  }
}
