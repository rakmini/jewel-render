/**
 * JewelRender Application State
 * Central state store with event-based updates.
 */

const State = (() => {
  // ---- Default presets (fallback if API unavailable) ----
  const DEFAULT_PRESETS = [
    {
      id: 'cool-blue',
      name: 'Cool Blue',
      style: 'baby-blue background, softly lit',
      defaults: { temperature: 0, saturation: 0, contrast: 0, sharpness: 0, grain: 0 },
    },
    {
      id: 'white-retail',
      name: 'White Retail',
      style: 'clean white background',
      defaults: { temperature: 0, saturation: 0, contrast: 0, sharpness: 0, grain: 0 },
    },
    {
      id: 'yashica-film',
      name: 'Yashica Film',
      style: 'AI models, Yashica T4 aesthetic',
      defaults: { temperature: 15, saturation: 10, contrast: 5, sharpness: 0, grain: 20 },
    },
  ];

  // ---- State ----
  const state = {
    connected: false,
    presets: [...DEFAULT_PRESETS],
    activePresetId: 'cool-blue',
    activeMode: 'edit', // 'edit' | 'generate' | 'video'

    // Queue: array of { id, name, file, thumbUrl, feedback, status }
    queue: [],
    selectedImageId: null,

    // Editor
    editorOpen: false,
    editorImageId: null,
    editorAdjustments: resetAdjustments(),
    editorCrop: { ratio: 'free', straighten: 0, flipH: false, flipV: false, rotation: 0 },

    // Render
    rendering: false,
    renderProgress: 0,
    renderJobs: [],

    // RIL per preset
    ril: {}, // { [presetId]: [{ id, filename, url, source }] }

    // Settings
    settings: {
      comfyui: { host: '127.0.0.1', port: 8188, checkpoint: 'sd_xl_base_1.0.safetensors' },
      output: { width: 1170, height: 2532, jpeg_quality: 95 },
      video: { model: 'sv3d_p' },
      feedback: { auto_add_approved_to_ril: true, auto_deposit_exports_to_ril: true, parameter_logging: true },
      export_folder: '~/JewelRender/exports/',
    },
  };

  // ---- Event System ----
  const listeners = {};

  function on(event, fn) {
    if (!listeners[event]) listeners[event] = [];
    listeners[event].push(fn);
  }

  function off(event, fn) {
    if (!listeners[event]) return;
    listeners[event] = listeners[event].filter(f => f !== fn);
  }

  function emit(event, data) {
    if (listeners[event]) {
      listeners[event].forEach(fn => fn(data));
    }
  }

  // ---- Getters ----
  function getState() { return state; }

  function getActivePreset() {
    return state.presets.find(p => p.id === state.activePresetId) || state.presets[0];
  }

  function getQueueImage(id) {
    return state.queue.find(img => img.id === id);
  }

  function getSelectedImage() {
    return state.selectedImageId ? getQueueImage(state.selectedImageId) : null;
  }

  function getApprovedCount() {
    return state.queue.filter(img => img.feedback === 'approve').length;
  }

  function getRejectedCount() {
    return state.queue.filter(img => img.feedback === 'reject').length;
  }

  // ---- Mutations ----

  function setConnected(connected) {
    state.connected = connected;
    emit('connection', connected);
  }

  function setPresets(presets) {
    state.presets = presets;
    emit('presets', presets);
  }

  function setActivePreset(id) {
    state.activePresetId = id;
    emit('activePreset', id);
    emit('contextChange');
  }

  function setActiveMode(mode) {
    state.activeMode = mode;
    emit('activeMode', mode);
    emit('contextChange');
  }

  function addPreset(preset) {
    state.presets.push(preset);
    emit('presets', state.presets);
  }

  function updatePreset(id, updates) {
    const idx = state.presets.findIndex(p => p.id === id);
    if (idx !== -1) {
      state.presets[idx] = { ...state.presets[idx], ...updates };
      emit('presets', state.presets);
    }
  }

  function removePreset(id) {
    state.presets = state.presets.filter(p => p.id !== id);
    if (state.activePresetId === id && state.presets.length > 0) {
      state.activePresetId = state.presets[0].id;
    }
    emit('presets', state.presets);
    emit('activePreset', state.activePresetId);
  }

  // Queue
  let nextImageId = 1;

  function addToQueue(file) {
    const id = `img-${nextImageId++}`;
    const thumbUrl = URL.createObjectURL(file);
    const item = {
      id,
      name: file.name,
      file,
      thumbUrl,
      feedback: null,  // null | 'approve' | 'reject'
      status: 'ready',  // 'ready' | 'rendering' | 'complete' | 'failed'
      renderOutput: null,
    };
    state.queue.push(item);
    emit('queue', state.queue);
    return item;
  }

  function removeFromQueue(id) {
    const item = getQueueImage(id);
    if (item) URL.revokeObjectURL(item.thumbUrl);
    state.queue = state.queue.filter(img => img.id !== id);
    if (state.selectedImageId === id) {
      state.selectedImageId = null;
      emit('selection', null);
    }
    emit('queue', state.queue);
  }

  function selectImage(id) {
    state.selectedImageId = id;
    emit('selection', id);
  }

  function setFeedback(id, feedback) {
    const item = getQueueImage(id);
    if (item) {
      item.feedback = item.feedback === feedback ? null : feedback;
      emit('queue', state.queue);
      emit('feedback', { id, feedback: item.feedback });
    }
  }

  // Editor
  function openEditor(imageId) {
    state.editorOpen = true;
    state.editorImageId = imageId;
    state.editorAdjustments = resetAdjustments();
    state.editorCrop = { ratio: 'free', straighten: 0, flipH: false, flipV: false, rotation: 0 };
    emit('editor', { open: true, imageId });
  }

  function closeEditor() {
    state.editorOpen = false;
    state.editorImageId = null;
    emit('editor', { open: false });
  }

  function setEditorAdjustment(key, value) {
    state.editorAdjustments[key] = value;
    emit('editorAdjust', state.editorAdjustments);
  }

  function resetEditorAdjustments() {
    state.editorAdjustments = resetAdjustments();
    emit('editorAdjust', state.editorAdjustments);
  }

  function setEditorCrop(key, value) {
    state.editorCrop[key] = value;
    emit('editorCrop', state.editorCrop);
  }

  // Render
  function setRendering(rendering, progress = 0) {
    state.rendering = rendering;
    state.renderProgress = progress;
    emit('render', { rendering, progress });
  }

  function setRenderProgress(progress) {
    state.renderProgress = progress;
    emit('render', { rendering: state.rendering, progress });
  }

  // RIL
  function setRIL(presetId, images) {
    state.ril[presetId] = images;
    emit('ril', { presetId, images });
  }

  function addRILImage(presetId, image) {
    if (!state.ril[presetId]) state.ril[presetId] = [];
    state.ril[presetId].push(image);
    emit('ril', { presetId, images: state.ril[presetId] });
  }

  // Settings
  function setSettings(settings) {
    Object.assign(state.settings, settings);
    emit('settings', state.settings);
  }

  // ---- Helpers ----
  function resetAdjustments() {
    return {
      exposure: 0, contrast: 0, highlights: 0, shadows: 0,
      temperature: 0, tint: 0, saturation: 0, vibrance: 0, skinTone: 0,
      sharpness: 0, clarity: 0,
      grain: 0, fade: 0, vignette: 0,
    };
  }

  function generatePresetId(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  return {
    on, off, emit,
    getState, getActivePreset, getQueueImage, getSelectedImage,
    getApprovedCount, getRejectedCount,
    setConnected, setPresets, setActivePreset, setActiveMode,
    addPreset, updatePreset, removePreset,
    addToQueue, removeFromQueue, selectImage, setFeedback,
    openEditor, closeEditor,
    setEditorAdjustment, resetEditorAdjustments, setEditorCrop,
    setRendering, setRenderProgress,
    setRIL, addRILImage,
    setSettings,
    generatePresetId,
    DEFAULT_PRESETS,
  };
})();
