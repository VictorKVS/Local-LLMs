
const current = document.documentElement.dataset.page;
document.querySelectorAll('.nav a').forEach(a => {
  if (a.dataset.page === current) a.classList.add('active');
});
