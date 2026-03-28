let isEditable = false;

const list = document.getElementById('server-list');
const toggleBtn = document.getElementById('toggle-btn');
const sortSelect = document.getElementById('sort-select');

// Store original custom order
let originalOrder = Array.from(list.querySelectorAll('.list-group-item'));

const sortable = new Sortable(list, {
  animation: 150,
  handle: '.drag-handle',
  disabled: true,

  onEnd: function () {
    // Update stored custom order
    originalOrder = Array.from(list.querySelectorAll('.list-group-item'));

    // Build full payload
    const order = originalOrder.map(el => ({
      id: el.dataset.id,
      name: el.dataset.name
    }));

    // Send POST request
    fetch('/api/update-order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        order: order
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to update order');
      }
      return response.json(); // optional
    })
    .then(data => {
      console.log('Order successfully updated:', data);
    })
    .catch(error => {
      console.error('Error updating order:', error);
    });
  }
});

// Toggle reorder mode
toggleBtn.addEventListener('click', () => {
  isEditable = !isEditable;
  sortable.option("disabled", !isEditable);

  if (isEditable) {
    list.classList.add('editable');
    toggleBtn.innerText = "Lock Order";
    sortSelect.disabled = true; // prevent conflicts
  } else {
    list.classList.remove('editable');
    toggleBtn.innerText = "Enable Reorder";
    sortSelect.disabled = false;
  }
});

// Sorting logic
sortSelect.addEventListener('change', function () {
  const items = Array.from(list.querySelectorAll('.list-group-item'));

  let sorted;

  if (this.value === 'asc') {
    sorted = items.sort((a, b) =>
      a.dataset.name.localeCompare(b.dataset.name)
    );
  } else if (this.value === 'desc') {
    sorted = items.sort((a, b) =>
      b.dataset.name.localeCompare(a.dataset.name)
    );
  } else {
    // Restore custom order
    sorted = originalOrder;
  }

  sorted.forEach(el => list.appendChild(el));
});

