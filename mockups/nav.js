/* Shared navigation widget for all mockup pages */
const PAGES = [
  { file: 'index.html',    label: 'Overview — All User Stories' },
  { file: 'us-01-queue.html',    label: 'US-01 Upload & Queue' },
  { file: 'us-02-presets.html',  label: 'US-02 Preset Selection' },
  { file: 'us-03-edit.html',     label: 'US-03 Image Edit Mode' },
  { file: 'us-04-recede.html',   label: 'US-04 Recede Outpainting' },
  { file: 'us-05-generate.html', label: 'US-05 Image Generation' },
  { file: 'us-06-video.html',    label: 'US-06 360° Video Mode' },
  { file: 'us-07-editor.html',   label: 'US-07 VSCO Image Editor' },
  { file: 'us-08-ril.html',      label: 'US-08 Reference Library' },
  { file: 'us-09-settings.html', label: 'US-09 Settings' },
];

function renderNav() {
  const current = window.location.pathname.split('/').pop() || 'index.html';
  const el = document.createElement('div');
  el.className = 'mockup-nav';
  el.innerHTML = `
    <div class="mockup-nav-menu" id="navMenu">
      ${PAGES.map((p, i) => `
        <a href="${p.file}" class="${p.file === current ? 'active' : ''}">
          <span class="nav-num">${i === 0 ? '⌂' : String(i).padStart(2,'0')}</span>
          ${p.label}
        </a>`).join('')}
    </div>
    <button class="mockup-nav-toggle" id="navToggle" title="Navigate mockups">☰</button>
  `;
  document.body.appendChild(el);
  document.getElementById('navToggle').addEventListener('click', () => {
    document.getElementById('navMenu').classList.toggle('open');
  });
  document.addEventListener('click', e => {
    if (!el.contains(e.target)) document.getElementById('navMenu').classList.remove('open');
  });
}

document.addEventListener('DOMContentLoaded', renderNav);
