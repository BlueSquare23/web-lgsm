const gslist = document.getElementById('game-servers-list');
const chevron = document.getElementById('chevron'); // assuming you have this

function toggleServersList() {
  const isHidden = gslist.style.display === 'none';

  if (isHidden) {
    gslist.style.display = 'block';
    chevron.src = '/static/img/chevron-up.png';
    sessionStorage.setItem('serversListVisible', 'true');
  } else {
    gslist.style.display = 'none';
    chevron.src = '/static/img/chevron-down.png';
    sessionStorage.setItem('serversListVisible', 'false');
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const savedState = sessionStorage.getItem('serversListVisible');

  if (savedState === 'false') {
    gslist.style.display = 'none';
    chevron.src = '/static/img/chevron-down.png';
  } else {
    // default to visible if nothing saved
    gslist.style.display = 'block';
    chevron.src = '/static/img/chevron-up.png';
  }
});
