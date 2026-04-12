// show-spinners.js
function showSpinners() {
  const headerSpinner = document.getElementById('header-spinner');
  const spinnerText = document.getElementById('spinner-text');
  
  if (headerSpinner) {
    // Set appropriate text based on context
    if (spinnerText) {
      if (typeof installName !== 'undefined' && installName) {
        spinnerText.textContent = `Installing ${installName}`;
      } else if (typeof spinnerContext !== 'undefined' && spinnerContext) {
        spinnerText.textContent = spinnerContext;
      } else {
        spinnerText.textContent = 'Processing';
      }
    }
    
    headerSpinner.style.display = 'block';
  }
}

function hideSpinners() {
  const headerSpinner = document.getElementById('header-spinner');
  
  if (headerSpinner) {
    headerSpinner.style.display = 'none';
  }
}
