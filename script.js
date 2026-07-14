document.querySelector('#year').textContent = new Date().getFullYear();

const dialog = document.querySelector('.menu-dialog');
const dialogImage = dialog?.querySelector('img');
const dialogTitle = dialog?.querySelector('p');
const closeButton = dialog?.querySelector('.dialog-close');

if (dialog?.showModal) {
  document.querySelectorAll('[data-menu]').forEach((menu) => {
    menu.addEventListener('click', (event) => {
      event.preventDefault();
      const thumbnail = menu.querySelector('img');
      dialogImage.src = menu.href;
      dialogImage.alt = thumbnail.alt;
      dialogTitle.textContent = menu.dataset.title;
      dialog.showModal();
    });
  });

  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    const bounds = dialog.getBoundingClientRect();
    const outside = event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom;
    if (outside) dialog.close();
  });
  dialog.addEventListener('close', () => {
    dialogImage.src = '';
  });
}
