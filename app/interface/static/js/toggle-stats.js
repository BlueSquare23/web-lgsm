function toggleStats() {
  if (stats.style.display === 'none'){
      stats.style.display = 'block';
      chevron.src = '/static/img/chevron-up.png'
  } else {
      stats.style.display = 'none';
      chevron.src = '/static/img/chevron-down.png'
  }
}
