/**
 * scene-manager.js — API bridge to Django HumanBody endpoints.
 * All fetch calls go to the same origin (Django serves both the page and the API).
 */

/**
 * Fetch list of saved scenes.
 * @returns {Promise<Array<{name: string, label: string, character_count: number}>>}
 */
export async function fetchSceneList() {
    const resp = await fetch('/api/character/scenes/');
    if (!resp.ok) throw new Error(`Scene list error: ${resp.status}`);
    const data = await resp.json();
    return data.scenes || [];
}

/**
 * Fetch a single scene by name.
 * @param {string} name
 * @returns {Promise<Object>} Full scene JSON
 */
export async function fetchScene(name) {
    const resp = await fetch(`/api/character/scene/${encodeURIComponent(name)}/`);
    if (!resp.ok) throw new Error(`Scene load error: ${resp.status}`);
    return resp.json();
}

/**
 * Save a scene.
 * @param {string} name
 * @param {Object} data Scene data object
 * @returns {Promise<{ok: boolean, filename: string}>}
 */
export async function saveScene(name, data) {
    const resp = await fetch('/api/character/scene/save/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, data }),
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || `Scene save error: ${resp.status}`);
    }
    return resp.json();
}

/**
 * Fetch list of model presets.
 * @returns {Promise<Array<{name: string, label: string}>>}
 */
export async function fetchModelList() {
    const resp = await fetch('/api/character/models/');
    if (!resp.ok) throw new Error(`Model list error: ${resp.status}`);
    const data = await resp.json();
    return data.presets || [];
}

/**
 * Fetch a single model preset by name.
 * @param {string} name
 * @returns {Promise<Object>} Full preset JSON (body_type, morphs, etc.)
 */
export async function fetchModel(name) {
    const resp = await fetch(`/api/character/model/${encodeURIComponent(name)}/`);
    if (!resp.ok) throw new Error(`Model load error: ${resp.status}`);
    return resp.json();
}

/**
 * Fetch animation (BVH) category tree.
 * @returns {Promise<Object>} { categories: { CategoryName: [{name, category, url, frames}, ...] } }
 */
export async function fetchAnimationList() {
    const resp = await fetch('/api/character/animations/');
    if (!resp.ok) throw new Error(`Animation list error: ${resp.status}`);
    const data = await resp.json();
    return data.categories || {};
}

/**
 * Fetch a BVH file as text.
 * @param {string} category
 * @param {string} name
 * @returns {Promise<string>} Raw BVH text
 */
export async function fetchBVH(category, name) {
    const url = `/api/character/bvh/${encodeURIComponent(category)}/${encodeURIComponent(name)}/`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`BVH load error: ${resp.status}`);
    return resp.text();
}
