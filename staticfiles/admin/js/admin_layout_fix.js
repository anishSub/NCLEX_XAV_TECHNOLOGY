// Fix admin layout - force wide cards
document.addEventListener('DOMContentLoaded', function () {
  console.log('Admin layout fix loaded');

  // Force all cards and modules to be full width
  const cards = document.querySelectorAll('.card, .card-body, .module, fieldset.module');
  cards.forEach(card => {
    card.style.maxWidth = '100%';
    card.style.width = '100%';
  });

  // Force inline formsets to be full width
  const inlineGroups = document.querySelectorAll('.inline-group, .inline-related');
  inlineGroups.forEach(group => {
    group.style.maxWidth = '100%';
    group.style.width = '100%';
  });

  // Force form rows to be full width
  const formRows = document.querySelectorAll('.form-row');
  formRows.forEach(row => {
    row.style.maxWidth = '100%';
    row.style.width = '100%';
  });

  console.log('Admin layout fix applied');
});
