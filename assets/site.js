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

// Native details remain usable without JavaScript; adapt the initial state to the viewport.
document.querySelectorAll('[data-article-directory]').forEach(directory => {
  const narrowScreen = window.matchMedia('(max-width: 760px)');
  const adaptDirectory = () => { directory.open = !narrowScreen.matches; };
  adaptDirectory();
  narrowScreen.addEventListener('change', adaptDirectory);
});

document.querySelectorAll('[data-video-player]').forEach(player => {
  const video = player.querySelector('video');
  const launch = player.querySelector('.video-launch');
  const status = player.querySelector('.video-status');
  video.hidden = true;
  launch.hidden = false;
  launch.addEventListener('click', async () => {
    status.hidden = true;
    launch.hidden = true;
    video.hidden = false;
    try {
      await video.play();
      video.focus();
    } catch {
      video.hidden = true;
      launch.hidden = false;
      status.hidden = false;
    }
  });
});
