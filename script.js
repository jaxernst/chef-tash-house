const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

const revealElements = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealElements.forEach((element) => observer.observe(element));
} else {
  revealElements.forEach((element) => element.classList.add('visible'));
}

const gallery = document.querySelector('#gallery-viewer');
const galleryLinks = Array.from(document.querySelectorAll('.menu-art, .food-photo, .prep-photo'));

if (gallery && galleryLinks.length && typeof gallery.showModal === 'function') {
  const galleryImage = gallery.querySelector('.lightbox-image');
  const galleryCount = gallery.querySelector('.lightbox-count');
  const closeButton = gallery.querySelector('.lightbox-close');
  const previousButton = gallery.querySelector('.lightbox-prev');
  const nextButton = gallery.querySelector('.lightbox-next');
  let currentIndex = 0;
  let opener = null;

  const fullSizeSource = (link) => {
    const thumbnailPath = link.getAttribute('href');
    if (!thumbnailPath?.startsWith('assets/')) return link.href;
    return new URL(`assets/gallery/${thumbnailPath.slice('assets/'.length)}`, document.baseURI).href;
  };

  const showImage = (index) => {
    currentIndex = (index + galleryLinks.length) % galleryLinks.length;
    const link = galleryLinks[currentIndex];
    const thumbnail = link.querySelector('img');
    const description = thumbnail?.alt || link.getAttribute('aria-label') || '';

    galleryImage.src = fullSizeSource(link);
    galleryImage.alt = description;
    galleryCount.textContent = `${currentIndex + 1} / ${galleryLinks.length}`;

    const nextImage = new Image();
    nextImage.src = fullSizeSource(galleryLinks[(currentIndex + 1) % galleryLinks.length]);
  };

  galleryLinks.forEach((link, index) => {
    link.setAttribute('aria-haspopup', 'dialog');
    link.setAttribute('aria-controls', 'gallery-viewer');
    link.addEventListener('click', (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      showImage(index);
      if (!gallery.open) {
        gallery.showModal();
        gallery.focus({ preventScroll: true });
      }
    });
  });

  closeButton.addEventListener('click', () => gallery.close());
  previousButton.addEventListener('click', () => showImage(currentIndex - 1));
  nextButton.addEventListener('click', () => showImage(currentIndex + 1));

  gallery.addEventListener('click', (event) => {
    if (event.target === gallery) gallery.close();
  });

  gallery.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      showImage(currentIndex - 1);
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      showImage(currentIndex + 1);
    }
  });

  gallery.addEventListener('close', () => {
    galleryImage.removeAttribute('src');
    if (opener) opener.focus();
  });
}
