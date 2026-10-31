document.querySelectorAll('[data-project-filter]').forEach(button => {
  button.addEventListener('click', () => {
    const category = button.dataset.projectFilter;
    document.querySelectorAll('[data-project-filter]').forEach(item => {
      item.setAttribute('aria-pressed', String(item === button));
    });
    let count = 0;
    document.querySelectorAll('[data-project-category]').forEach(project => {
      project.hidden = category !== '全部' && project.dataset.projectCategory !== category;
      if (!project.hidden) count++;
    });
    const status = document.querySelector('[data-filter-status]');
    if (status) status.textContent = `显示 ${count} 个项目`;
  });
});
// Filters progressively enhance the complete server-rendered project list.
document.querySelectorAll('[data-project-filter]').forEach(button => { button.hidden = false; });
