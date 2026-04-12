function doBarrelRoll() {
  document.body.classList.add('barrel-roll');
  setTimeout(() => document.body.classList.remove('barrel-roll'), 1000);
}
