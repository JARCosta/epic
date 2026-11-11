const form = document.getElementById('item-form');
const input = document.getElementById('item-input');
const itemsList = document.getElementById('items');

async function loadItems() {
  const response = await fetch('/api/items');
  const data = await response.json();
  renderItems(data.items || []);
}

function renderItems(items) {
  itemsList.innerHTML = '';
  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = item.text;
    itemsList.appendChild(li);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) {
    return;
  }

  await fetch('/api/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  input.value = '';
  await loadItems();
});

loadItems();
