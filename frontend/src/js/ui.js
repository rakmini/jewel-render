/**
 * JewelRender UI Module
 * DOM manipulation and event binding for all UI components.
 */

const UI = (() => {

  // ---- DOM References ----
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ---- Preset Tabs ----
  function renderPresetTabs() {
    const container = $('#presetTabs');
    const addBtn = $('#addPresetBtn');
    // Remove existing tabs (keep add button)
    container.querySelectorAll('.preset-tab').forEach(el => el.remove());

    const state = State.getState();
    state.presets.forEach(preset => {
      const tab = document.createElement('button');
      tab.className = `preset-tab${preset.id === state.activePresetId ? ' active' : ''}`;
      tab.dataset.presetId = preset.id;
      tab.textContent = preset.name;

      tab.addEventListener('click', () => {
        State.setActivePreset(preset.id);
      });

      tab.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showPresetContextMenu(e, preset.id);
      });

      container.insertBefore(tab, addBtn);
    });

    // Update template dropdown in new-preset modal
    const templateSelect = $('#newPresetTemplate');
    templateSelect.innerHTML = '<option value="">None (blank defaults)</option>';
    state.presets.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      templateSelect.appendChild(opt);
    });

    updateActiveContext();
  }

  // ---- Mode Switcher ----
  function renderModeSwitcher() {
    const state = State.getState();
    $$('.mode-pill').forEach(pill => {
      pill.classList.toggle('active', pill.dataset.mode === state.activeMode);
    });
    updateModeControls();
    updateActiveContext();
  }

  function updateModeControls() {
    const mode = State.getState().activeMode;
    $('#editControls').classList.toggle('hidden', mode !== 'edit');
    $('#generateControls').classList.toggle('hidden', mode !== 'generate');
    $('#videoControls').classList.toggle('hidden', mode !== 'video');
  }

  // ---- Active Context ----
  function updateActiveContext() {
    const preset = State.getActivePreset();
    const mode = State.getState().activeMode;
    const modeLabel = { edit: 'Edit', generate: 'Generate', video: '360 Video' }[mode];
    $('#activeContext').textContent = `${preset.name} / ${modeLabel}`;
  }

  // ---- Connection Status ----
  function updateConnectionStatus(connected) {
    const el = $('#connectionStatus');
    el.classList.toggle('connected', connected);
    el.querySelector('.status-text').textContent = connected ? 'Connected' : 'Disconnected';
  }

  // ---- Queue ----
  function renderQueue() {
    const list = $('#queueList');
    const state = State.getState();
    list.innerHTML = '';

    if (state.queue.length === 0) {
      list.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text-muted);font-size:11px;">No images in queue</div>';
    }

    state.queue.forEach(img => {
      const item = document.createElement('div');
      item.className = `queue-item${img.id === state.selectedImageId ? ' selected' : ''}`;
      item.dataset.imageId = img.id;
      item.innerHTML = `
        <img class="queue-thumb" src="${img.thumbUrl}" alt="${img.name}">
        <div class="queue-info">
          <div class="queue-name">${img.name}</div>
          <div class="queue-meta">${img.status}</div>
        </div>
        <div class="queue-feedback">
          <button class="feedback-btn${img.feedback === 'approve' ? ' approved' : ''}" data-fb="approve" title="Approve">+</button>
          <button class="feedback-btn${img.feedback === 'reject' ? ' rejected' : ''}" data-fb="reject" title="Reject">&minus;</button>
        </div>
      `;

      // Click to select / open editor
      item.addEventListener('click', (e) => {
        if (e.target.closest('.feedback-btn')) return;
        State.selectImage(img.id);
      });

      item.addEventListener('dblclick', (e) => {
        if (e.target.closest('.feedback-btn')) return;
        State.openEditor(img.id);
      });

      // Feedback buttons
      item.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          State.setFeedback(img.id, btn.dataset.fb);
        });
      });

      list.appendChild(item);
    });

    // Update count & stats
    $('#queueCount').textContent = `${state.queue.length} image${state.queue.length !== 1 ? 's' : ''}`;
    $('#queueStats').querySelector('.approved').textContent = `${State.getApprovedCount()} approved`;
    $('#queueStats').querySelector('.rejected').textContent = `${State.getRejectedCount()} rejected`;
  }

  // ---- Preview ----
  function updatePreview() {
    const img = State.getSelectedImage();
    const previewImg = $('#previewImage');
    const previewEmpty = $('#previewEmpty');

    if (img) {
      previewImg.src = img.renderOutput || img.thumbUrl;
      previewImg.classList.remove('hidden');
      previewEmpty.classList.add('hidden');
    } else {
      previewImg.classList.add('hidden');
      previewEmpty.classList.remove('hidden');
    }
  }

  // ---- Preset Adjust Sliders ----
  function renderPresetAdjusts() {
    const preset = State.getActivePreset();
    if (!preset) return;

    $$('.preset-adjusts .slider').forEach(slider => {
      const param = slider.dataset.param;
      const val = preset.defaults[param] || 0;
      slider.value = val;
      const label = $(`.slider-val[data-slider="${param}"]`);
      if (label) label.textContent = val;
    });
  }

  // ---- RIL ----
  function renderRIL() {
    const state = State.getState();
    const presetId = state.activePresetId;
    const images = state.ril[presetId] || [];
    const grid = $('#rilGrid');
    const count = $('#rilCount');

    grid.innerHTML = '';
    count.textContent = images.length;

    images.forEach(img => {
      const thumb = document.createElement('img');
      thumb.className = 'ril-thumb';
      thumb.src = img.url || img.thumbUrl;
      thumb.alt = img.filename;
      grid.appendChild(thumb);
    });
  }

  // ---- Editor ----
  function openEditor(imageId) {
    const img = State.getQueueImage(imageId);
    if (!img) return;

    $('#editorImage').src = img.renderOutput || img.thumbUrl;
    $('#editorOverlay').classList.remove('hidden');
    resetEditorSliders();
  }

  function closeEditor() {
    $('#editorOverlay').classList.add('hidden');
  }

  function resetEditorSliders() {
    $$('.editor-controls .slider').forEach(slider => {
      slider.value = 0;
      const key = slider.dataset.adjust;
      const label = $(`.slider-val[data-editor="${key}"]`);
      if (label) label.textContent = key === 'straighten' ? '0\u00B0' : '0';
    });
  }

  function switchEditorTab(tab) {
    $$('.editor-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    $('#adjustPanel').classList.toggle('hidden', tab !== 'adjust');
    $('#cropPanel').classList.toggle('hidden', tab !== 'crop');
  }

  // ---- Settings ----
  function openSettings() {
    const s = State.getState().settings;
    $('#settingsHost').value = s.comfyui.host;
    $('#settingsPort').value = s.comfyui.port;
    $('#settingsCheckpoint').value = s.comfyui.checkpoint;
    $('#settingsVideoModel').value = s.video.model;
    $('#settingsAutoApprove').checked = s.feedback.auto_add_approved_to_ril;
    $('#settingsAutoDeposit').checked = s.feedback.auto_deposit_exports_to_ril;
    $('#settingsParamLogging').checked = s.feedback.parameter_logging;
    $('#settingsExportPath').value = s.export_folder;
    $('#settingsOverlay').classList.remove('hidden');
  }

  function closeSettings() {
    $('#settingsOverlay').classList.add('hidden');
  }

  // ---- Progress Bar ----
  function updateProgress(rendering, progress) {
    const bar = $('#progressBar');
    const fill = $('#progressFill');
    const text = $('#progressText');
    bar.classList.toggle('hidden', !rendering);
    fill.style.width = `${progress}%`;
    text.textContent = `${Math.round(progress)}%`;
  }

  // ---- Context Menu ----
  let contextPresetId = null;

  function showPresetContextMenu(e, presetId) {
    contextPresetId = presetId;
    const menu = $('#presetContextMenu');
    menu.classList.remove('hidden');
    menu.style.left = `${e.clientX}px`;
    menu.style.top = `${e.clientY}px`;
  }

  function hideContextMenu() {
    $('#presetContextMenu').classList.add('hidden');
    contextPresetId = null;
  }

  function getContextPresetId() {
    return contextPresetId;
  }

  // ---- New Preset Modal ----
  function openNewPresetModal() {
    $('#newPresetName').value = '';
    $('#newPresetStyle').value = '';
    $('#newPresetTemplate').value = '';
    $('#newPresetModal').classList.remove('hidden');
    $('#newPresetName').focus();
  }

  function closeNewPresetModal() {
    $('#newPresetModal').classList.add('hidden');
  }

  // ---- Drag & Drop ----
  function setupDragDrop() {
    const dropZone = $('#dropZone');
    const fileInput = $('#fileInput');

    ['dragenter', 'dragover'].forEach(evt => {
      dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      dropZone.addEventListener(evt, () => {
        dropZone.classList.remove('drag-over');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      handleFiles(e.dataTransfer.files);
    });

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
      handleFiles(fileInput.files);
      fileInput.value = '';
    });
  }

  function handleFiles(files) {
    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        State.addToQueue(file);
      }
    });
  }

  // ---- Recede ----
  function setupRecede() {
    const slider = $('#recedeSlider');
    const value = $('#recedeValue');
    const btn = $('#recedeBtn');

    slider.addEventListener('input', () => {
      const val = slider.value;
      value.textContent = `${val}%`;
      btn.disabled = val === '0';
      btn.textContent = val === '0' ? 'Recede' : `Recede ${val}%`;
    });
  }

  return {
    renderPresetTabs,
    renderModeSwitcher,
    updateConnectionStatus,
    renderQueue,
    updatePreview,
    renderPresetAdjusts,
    renderRIL,
    openEditor,
    closeEditor,
    switchEditorTab,
    openSettings,
    closeSettings,
    updateProgress,
    showPresetContextMenu,
    hideContextMenu,
    getContextPresetId,
    openNewPresetModal,
    closeNewPresetModal,
    setupDragDrop,
    setupRecede,
  };
})();
