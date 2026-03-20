/**
 * JewelRender API Client
 * Handles all communication with the backend server.
 */

const API = (() => {
  const BASE = '/api';

  async function request(path, options = {}) {
    const url = `${BASE}${path}`;
    const config = {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    };

    // Don't set Content-Type for FormData
    if (options.body instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    try {
      const res = await fetch(url, config);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      if (e.name === 'TypeError') {
        throw new Error('Cannot connect to server');
      }
      throw e;
    }
  }

  // ---- Health ----
  async function checkHealth() {
    return request('/health');
  }

  // ---- Presets ----
  async function listPresets() {
    return request('/presets');
  }

  async function getPreset(id) {
    return request(`/presets/${id}`);
  }

  async function createPreset(data) {
    return request('/presets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async function updatePreset(id, data) {
    return request(`/presets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async function deletePreset(id) {
    return request(`/presets/${id}`, { method: 'DELETE' });
  }

  async function duplicatePreset(id) {
    return request(`/presets/${id}/duplicate`, { method: 'POST' });
  }

  // ---- Render ----
  async function queueRender(params) {
    return request('/render', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async function getRenderStatus(jobId) {
    return request(`/render/${jobId}`);
  }

  // ---- Settings ----
  async function getSettings() {
    return request('/settings');
  }

  async function updateSettings(data) {
    return request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // ---- Images / RIL ----
  async function uploadImage(presetId, file, target = 'queue') {
    const form = new FormData();
    form.append('file', file);
    form.append('target', target);
    return request(`/presets/${presetId}/images`, {
      method: 'POST',
      body: form,
    });
  }

  async function listRIL(presetId) {
    return request(`/presets/${presetId}/library`);
  }

  async function addToRIL(presetId, file) {
    const form = new FormData();
    form.append('file', file);
    return request(`/presets/${presetId}/library`, {
      method: 'POST',
      body: form,
    });
  }

  async function removeFromRIL(presetId, imageId) {
    return request(`/presets/${presetId}/library/${imageId}`, {
      method: 'DELETE',
    });
  }

  // ---- Feedback ----
  async function submitFeedback(presetId, imageId, feedback) {
    return request(`/presets/${presetId}/images/${imageId}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ feedback }),
    });
  }

  // ---- Export ----
  async function exportImages(presetId, imageIds) {
    return request(`/presets/${presetId}/export`, {
      method: 'POST',
      body: JSON.stringify({ image_ids: imageIds }),
    });
  }

  // ---- Test ComfyUI ----
  async function testComfyUI(host, port) {
    return request('/comfyui/test', {
      method: 'POST',
      body: JSON.stringify({ host, port }),
    });
  }

  return {
    checkHealth,
    listPresets,
    getPreset,
    createPreset,
    updatePreset,
    deletePreset,
    duplicatePreset,
    queueRender,
    getRenderStatus,
    getSettings,
    updateSettings,
    uploadImage,
    listRIL,
    addToRIL,
    removeFromRIL,
    submitFeedback,
    exportImages,
    testComfyUI,
  };
})();
