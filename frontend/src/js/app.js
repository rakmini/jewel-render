/**
 * JewelRender Application
 * Main entry point — wires state, UI, and API together.
 */

(function App() {
  'use strict';

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ================================================================
  // INITIALIZATION
  // ================================================================

  async function init() {
    // Setup UI interactions
    UI.setupDragDrop();
    UI.setupRecede();
    bindEvents();
    bindStateListeners();

    // Initial render
    UI.renderPresetTabs();
    UI.renderModeSwitcher();
    UI.renderQueue();
    UI.renderPresetAdjusts();
    UI.renderRIL();

    // Try connecting to backend
    await checkConnection();

    // Load presets from server
    await loadPresets();
  }

  // ================================================================
  // CONNECTION
  // ================================================================

  async function checkConnection() {
    try {
      await API.checkHealth();
      State.setConnected(true);
    } catch {
      State.setConnected(false);
    }
  }

  // Poll connection every 30s
  setInterval(checkConnection, 30000);

  // ================================================================
  // LOAD DATA
  // ================================================================

  async function loadPresets() {
    try {
      const data = await API.listPresets();
      if (data.presets && data.presets.length > 0) {
        State.setPresets(data.presets);
        State.setActivePreset(data.presets[0].id);
      }
    } catch {
      // Use defaults — already loaded in State
    }
  }

  // ================================================================
  // EVENT BINDINGS
  // ================================================================

  function bindEvents() {
    // ---- Mode Switcher ----
    $$('.mode-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        State.setActiveMode(pill.dataset.mode);
      });
    });

    // ---- Settings ----
    $('#settingsBtn').addEventListener('click', UI.openSettings);
    $('#settingsClose').addEventListener('click', UI.closeSettings);
    $('#settingsOverlay').addEventListener('click', (e) => {
      if (e.target === $('#settingsOverlay')) UI.closeSettings();
    });

    // Test connection button
    $('#testConnectionBtn').addEventListener('click', async () => {
      const result = $('#connectionResult');
      result.textContent = 'Testing...';
      result.style.color = 'var(--text-dim)';
      try {
        const host = $('#settingsHost').value;
        const port = parseInt($('#settingsPort').value);
        await API.testComfyUI(host, port);
        result.textContent = 'Connected!';
        result.style.color = 'var(--green)';
      } catch {
        result.textContent = 'Failed to connect';
        result.style.color = 'var(--red)';
      }
    });

    // ---- Add Preset ----
    $('#addPresetBtn').addEventListener('click', UI.openNewPresetModal);
    $('#newPresetCancel').addEventListener('click', UI.closeNewPresetModal);
    $('#newPresetModal').addEventListener('click', (e) => {
      if (e.target === $('#newPresetModal')) UI.closeNewPresetModal();
    });

    $('#newPresetCreate').addEventListener('click', async () => {
      const name = $('#newPresetName').value.trim();
      const style = $('#newPresetStyle').value.trim();
      const template = $('#newPresetTemplate').value;

      if (!name) return;

      const id = State.generatePresetId(name);
      let defaults = { temperature: 0, saturation: 0, contrast: 0, sharpness: 0, grain: 0 };

      if (template) {
        const src = State.getState().presets.find(p => p.id === template);
        if (src) defaults = { ...src.defaults };
      }

      const preset = { id, name, style: style || name, defaults };

      // Try server first
      try {
        await API.createPreset(preset);
      } catch {
        // Offline — just add locally
      }

      State.addPreset(preset);
      State.setActivePreset(id);
      UI.closeNewPresetModal();
    });

    // ---- Context Menu ----
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.context-menu')) {
        UI.hideContextMenu();
      }
    });

    $$('.context-item').forEach(item => {
      item.addEventListener('click', () => {
        const presetId = UI.getContextPresetId();
        if (!presetId) return;

        const action = item.dataset.action;
        handlePresetAction(action, presetId);
        UI.hideContextMenu();
      });
    });

    // ---- Editor ----
    $('#editorClose').addEventListener('click', () => State.closeEditor());
    $('#editorOverlay').addEventListener('click', (e) => {
      if (e.target === $('#editorOverlay')) State.closeEditor();
    });

    // Editor tabs
    $$('.editor-tab').forEach(tab => {
      tab.addEventListener('click', () => UI.switchEditorTab(tab.dataset.tab));
    });

    // Editor sliders
    $$('.editor-controls .slider').forEach(slider => {
      slider.addEventListener('input', () => {
        const key = slider.dataset.adjust;
        const val = parseInt(slider.value);
        State.setEditorAdjustment(key, val);

        const label = document.querySelector(`.slider-val[data-editor="${key}"]`);
        if (label) {
          label.textContent = key === 'straighten' ? `${val}\u00B0` : val;
        }
      });
    });

    // Reset all editor adjustments
    $('#editorReset').addEventListener('click', () => {
      State.resetEditorAdjustments();
      UI.openEditor(State.getState().editorImageId);
    });

    // Editor nav
    $('#editorPrev').addEventListener('click', () => navigateEditor(-1));
    $('#editorNext').addEventListener('click', () => navigateEditor(1));

    // Before/After compare
    let comparing = false;
    let originalSrc = '';
    $('#editorCompare').addEventListener('mousedown', () => {
      const img = State.getQueueImage(State.getState().editorImageId);
      if (img) {
        originalSrc = $('#editorImage').src;
        $('#editorImage').src = img.thumbUrl;
        comparing = true;
      }
    });
    document.addEventListener('mouseup', () => {
      if (comparing) {
        $('#editorImage').src = originalSrc;
        comparing = false;
      }
    });

    // Aspect ratio pills
    $$('.aspect-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        $$('.aspect-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        State.setEditorCrop('ratio', pill.dataset.ratio);
      });
    });

    // Transform buttons
    $('#rotateLeftBtn').addEventListener('click', () => {
      const crop = State.getState().editorCrop;
      State.setEditorCrop('rotation', crop.rotation - 90);
    });
    $('#rotateRightBtn').addEventListener('click', () => {
      const crop = State.getState().editorCrop;
      State.setEditorCrop('rotation', crop.rotation + 90);
    });
    $('#flipHBtn').addEventListener('click', () => {
      const crop = State.getState().editorCrop;
      State.setEditorCrop('flipH', !crop.flipH);
    });
    $('#flipVBtn').addEventListener('click', () => {
      const crop = State.getState().editorCrop;
      State.setEditorCrop('flipV', !crop.flipV);
    });

    // Apply & Export in editor
    $('#editorApply').addEventListener('click', () => {
      // TODO: Apply adjustments server-side
      State.closeEditor();
    });

    $('#editorExport').addEventListener('click', async () => {
      const imageId = State.getState().editorImageId;
      if (!imageId) return;
      try {
        await API.exportImages(State.getState().activePresetId, [imageId]);
      } catch {
        // Offline
      }
      State.closeEditor();
    });

    // ---- Preset Adjust Sliders ----
    $$('.preset-adjusts .slider').forEach(slider => {
      slider.addEventListener('input', () => {
        const param = slider.dataset.param;
        const val = parseInt(slider.value);
        const label = document.querySelector(`.slider-val[data-slider="${param}"]`);
        if (label) label.textContent = val;

        // Update preset defaults
        const preset = State.getActivePreset();
        if (preset) {
          preset.defaults[param] = val;
          // Debounce save to server
          debouncedSavePreset(preset);
        }
      });
    });

    // ---- Render All ----
    $('#renderAllBtn').addEventListener('click', handleRenderAll);

    // ---- Export ----
    $('#exportBtn').addEventListener('click', handleExport);

    // ---- RIL Drop Zone ----
    const rilDrop = $('#rilDropZone');
    rilDrop.addEventListener('click', () => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.multiple = true;
      input.addEventListener('change', () => {
        Array.from(input.files).forEach(file => {
          const id = `ril-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
          const url = URL.createObjectURL(file);
          State.addRILImage(State.getState().activePresetId, {
            id, filename: file.name, url, source: 'manual',
          });
          // Try uploading to server
          API.addToRIL(State.getState().activePresetId, file).catch(() => {});
        });
      });
      input.click();
    });

    // ---- Keyboard shortcuts ----
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (State.getState().editorOpen) State.closeEditor();
        else if (!$('#settingsOverlay').classList.contains('hidden')) UI.closeSettings();
        else if (!$('#newPresetModal').classList.contains('hidden')) UI.closeNewPresetModal();
        UI.hideContextMenu();
      }
    });
  }

  // ================================================================
  // STATE LISTENERS
  // ================================================================

  function bindStateListeners() {
    State.on('connection', (connected) => UI.updateConnectionStatus(connected));
    State.on('presets', () => UI.renderPresetTabs());
    State.on('activePreset', () => {
      UI.renderPresetTabs();
      UI.renderPresetAdjusts();
      UI.renderRIL();
    });
    State.on('activeMode', () => UI.renderModeSwitcher());
    State.on('queue', () => {
      UI.renderQueue();
      updateExportCount();
    });
    State.on('selection', () => {
      UI.renderQueue();
      UI.updatePreview();
    });
    State.on('editor', (data) => {
      if (data.open) UI.openEditor(data.imageId);
      else UI.closeEditor();
    });
    State.on('render', (data) => UI.updateProgress(data.rendering, data.progress));
    State.on('ril', () => UI.renderRIL());
  }

  // ================================================================
  // ACTIONS
  // ================================================================

  function handlePresetAction(action, presetId) {
    const state = State.getState();
    const preset = state.presets.find(p => p.id === presetId);
    if (!preset) return;

    switch (action) {
      case 'rename': {
        const newName = prompt('Rename preset:', preset.name);
        if (newName && newName.trim()) {
          State.updatePreset(presetId, { name: newName.trim() });
          API.updatePreset(presetId, { name: newName.trim() }).catch(() => {});
        }
        break;
      }
      case 'duplicate': {
        const newId = `${presetId}-copy-${Date.now().toString(36).slice(-4)}`;
        const dup = { ...preset, id: newId, name: `${preset.name} Copy`, defaults: { ...preset.defaults } };
        State.addPreset(dup);
        API.createPreset(dup).catch(() => {});
        State.setActivePreset(newId);
        break;
      }
      case 'delete': {
        if (state.presets.length <= 1) {
          alert('Cannot delete the last preset.');
          return;
        }
        if (confirm(`Delete "${preset.name}"?`)) {
          State.removePreset(presetId);
          API.deletePreset(presetId).catch(() => {});
        }
        break;
      }
    }
  }

  async function handleRenderAll() {
    const state = State.getState();
    const readyImages = state.queue.filter(img => img.status === 'ready');
    if (readyImages.length === 0) return;

    State.setRendering(true, 0);
    let completed = 0;

    for (const img of readyImages) {
      img.status = 'rendering';
      UI.renderQueue();

      try {
        const result = await API.queueRender({
          preset_id: state.activePresetId,
          mode: state.activeMode,
          params: {
            image_id: img.id,
            ...State.getActivePreset().defaults,
          },
        });

        img.status = 'complete';
        img.renderOutput = result.image_url || img.thumbUrl;
      } catch {
        img.status = 'failed';
      }

      completed++;
      State.setRenderProgress((completed / readyImages.length) * 100);
      UI.renderQueue();
    }

    State.setRendering(false, 100);
    setTimeout(() => State.setRendering(false, 0), 2000);
  }

  async function handleExport() {
    const state = State.getState();
    const approved = state.queue.filter(img => img.feedback === 'approve' || img.status === 'complete');
    if (approved.length === 0) return;

    try {
      await API.exportImages(state.activePresetId, approved.map(i => i.id));
    } catch {
      // Offline
    }
  }

  function updateExportCount() {
    const count = State.getState().queue.filter(
      img => img.feedback === 'approve' || img.status === 'complete'
    ).length;
    $('#exportCount').textContent = count > 0 ? count : '';
  }

  function navigateEditor(dir) {
    const state = State.getState();
    const queue = state.queue;
    if (queue.length === 0) return;

    const idx = queue.findIndex(img => img.id === state.editorImageId);
    let next = idx + dir;
    if (next < 0) next = queue.length - 1;
    if (next >= queue.length) next = 0;

    State.openEditor(queue[next].id);
  }

  // ---- Debounce ----
  let saveTimer = null;
  function debouncedSavePreset(preset) {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
      API.updatePreset(preset.id, { defaults: preset.defaults }).catch(() => {});
    }, 500);
  }

  // ================================================================
  // BOOT
  // ================================================================

  document.addEventListener('DOMContentLoaded', init);

})();
