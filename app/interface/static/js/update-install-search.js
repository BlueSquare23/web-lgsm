const searchForm = document.getElementById('search-form');
const installCards = document.querySelectorAll('[id^="form-"]');
const noResults = document.getElementById('no-results');

searchForm.addEventListener('input', (event) => {
  const searchValue = event.target.value.toLowerCase();
  let visibleCount = 0;

  installCards.forEach(card => {
    const shortName = card.dataset.shortName.toLowerCase();
    const longName = card.dataset.longName.toLowerCase();

    if (
      shortName.includes(searchValue) ||
      longName.includes(searchValue)
    ) {
      card.style.display = '';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  noResults.classList.toggle('d-none', visibleCount !== 0);
});
