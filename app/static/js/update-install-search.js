// Used for search box on install page.
const searchForm = document.getElementById('search-form');
const allInstallForms = document.querySelectorAll('form.form-group');

searchForm.addEventListener('input', (event) =>  {
  const inputValue = event.target.value;

  hideNonMatching(inputValue);
//  console.log(inputValue);
})

function hideNonMatching(searchStr) {
  allInstallForms.forEach(form => {
    const shortName = form[0].value;
    const longName = form[1].value;
    const divId = 'form-'.concat(shortName);
    const installFormDiv = document.getElementById(divId);

    const lShortName = shortName.toLowerCase();
    const lLongName = longName.toLowerCase();
    const lSearchStr = searchStr.toLowerCase();

//    console.log(lShortName);
//    console.log(lLongName);

    if (lShortName.includes(lSearchStr) || lLongName.includes(lSearchStr)) {
      installFormDiv.style.display = null;
      installFormDiv.style.height = null;
    } else {
      installFormDiv.style.display = 'none';
      installFormDiv.style.height = '';
      console.log(installFormDiv.style.height);
    }
  });
}
