/**
 * BVH Studio — BVH Library management (sidebar tree, context menus, file ops).
 */
import { state } from './state.js';
import { fn } from './registry.js';

// Module-level state
let _libOpenCats = new Set();
let _libSelectedItem = null;  // { category, name }
let _libCtxTarget = null;

// Expose _libSelectedItem getter for other modules
export function getLibSelectedItem() { return _libSelectedItem; }
export function setLibSelectedItem(val) { _libSelectedItem = val; }

function showLibCtx(menuId, x, y) {
    document.querySelectorAll('.lib-ctx').forEach(m => m.style.display = 'none');
    const menu = document.getElementById(menuId);
    if (!menu) return;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

async function libManage(action, data) {
    try {
        const resp = await fetch('/api/character/bvh-manage/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, ...data }),
        });
        const result = await resp.json();
        if (!resp.ok) { alert(result.error || 'Fehler'); return null; }
        return result;
    } catch (e) {
        alert('Fehler: ' + e.message);
        return null;
    }
}

function renameSelectedLibItem() {
    const sel = document.querySelector('.lib-item.selected');
    if (!sel) return;
    const cat = sel.dataset.category, name = sel.dataset.name;
    const newName = prompt('Neuer Name:', name);
    if (newName && newName !== name) {
        libManage('rename', { category: cat, name, new_name: newName }).then(r => {
            if (r) loadLibrary({ category: cat, name: newName });
        });
    }
}

function removeClipsFromTracks(category, name) {
    // Remove all clips referencing this BVH from all tracks
    let removed = 0;
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (let i = track.clips.length - 1; i >= 0; i--) {
            if (track.clips[i].category === category && track.clips[i].name === name) {
                if (track.mixer) {
                    track.mixer.stopAllAction();
                    if (track.clips[i].animClip) track.mixer.uncacheClip(track.clips[i].animClip);
                }
                track.clips.splice(i, 1);
                removed++;
            }
        }
        // Hide mesh + garments/hair if no clips left
        if (track.clips.length === 0 && track.group) track.group.visible = false;
        track._activeClip = null;
        track._activeAction = null;
    }
    if (removed > 0) {
        state.selectedClipIdx = -1;
        // Stop playback if no clips left
        const anyClips = state.project.tracks.some(t => t.clips.length > 0);
        if (!anyClips && state.playing) {
            state.playing = false;
            const icon = document.getElementById('pb-play-icon');
            if (icon) icon.className = 'fas fa-play';
        }
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        console.log(`[BVH Studio] Removed ${removed} clip(s) of ${category}/${name} from tracks`);
    }
}

function deleteSelectedLibItem() {
    const sel = document.querySelector('.lib-item.selected');
    if (!sel) return;
    const cat = sel.dataset.category, name = sel.dataset.name;
    if (confirm(`"${name}" wirklich löschen?`)) {
        _libOpenCats.add(cat);
        _libSelectedItem = null;
        libManage('delete', { category: cat, name }).then(r => {
            if (r) {
                removeClipsFromTracks(cat, name);
                loadLibrary();
            }
        });
    }
}

export async function loadLibrary(selectAfter) {
    if (selectAfter) _libSelectedItem = selectAfter;
    try {
        // Remember open categories before rebuild
        const tree0 = document.getElementById('lib-tree');
        if (tree0) tree0.querySelectorAll('.lib-cat.open').forEach(el => {
            if (el.dataset.category) _libOpenCats.add(el.dataset.category);
        });

        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('lib-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        for (const cat of Object.keys(categories).sort()) {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'lib-cat';
            catDiv.dataset.category = cat;

            const header = document.createElement('div');
            header.className = 'lib-cat-header';
            header.innerHTML = `<span class="lib-chevron"><i class="fas fa-chevron-right"></i></span> ${cat} <span style="color:var(--text-muted);font-size:0.7rem;">(${anims.length})</span>`;
            header.addEventListener('click', () => { catDiv.classList.toggle('open'); if (catDiv.classList.contains('open')) _libOpenCats.add(cat); else _libOpenCats.delete(cat); });
            // Restore open state
            if (_libOpenCats.has(cat)) catDiv.classList.add('open');
            // Also open if selected item is in this category
            if (_libSelectedItem && _libSelectedItem.category === cat) catDiv.classList.add('open');
            // Right-click on folder
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                _libCtxTarget = { type: 'folder', category: cat };
                showLibCtx('lib-ctx-folder', e.clientX, e.clientY);
            });
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'lib-cat-body';
            for (const anim of anims) {
                const item = document.createElement('div');
                item.className = 'lib-item';
                item.dataset.category = cat;
                item.dataset.name = anim.name;
                item.textContent = `${anim.name} (${anim.frames || '?'}f)`;
                item.draggable = true;
                item.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('application/json', JSON.stringify({
                        category: cat, name: anim.name, frames: anim.frames || 0,
                    }));
                    item.classList.add('dragging');
                });
                item.addEventListener('dragend', () => item.classList.remove('dragging'));
                // Double-click: add to selected track
                item.addEventListener('dblclick', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    fn.addClipToTrack(state.selectedTrackIdx, cat, anim.name, anim.frames || 0);
                });
                // Click: select
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    _libSelectedItem = { category: cat, name: anim.name };
                });
                // Restore selection
                if (_libSelectedItem && _libSelectedItem.category === cat && _libSelectedItem.name === anim.name) {
                    item.classList.add('selected');
                }
                // Right-click on file
                item.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    tree.querySelectorAll('.lib-item.selected').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    _libCtxTarget = { type: 'file', category: cat, name: anim.name, frames: anim.frames || 0 };
                    showLibCtx('lib-ctx-file', e.clientX, e.clientY);
                });
                body.appendChild(item);
            }
            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        }
    } catch (e) {
        console.error('[BVH Studio] Library load failed:', e);
    }
}

export function setupLibraryManagement() {
    // Close context menus
    document.addEventListener('click', () => {
        document.querySelectorAll('.lib-ctx').forEach(m => m.style.display = 'none');
    });

    // File context menu
    document.querySelectorAll('#lib-ctx-file .lib-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _libCtxTarget;
            if (!t) return;
            const action = item.dataset.action;
            if (action === 'add') {
                fn.addClipToTrack(state.selectedTrackIdx, t.category, t.name, t.frames);
            } else if (action === 'preview') {
                fn.previewAnimation(t.category, t.name);
            } else if (action === 'copy') {
                const newName = prompt('Kopie-Name:', t.name + '_copy');
                if (newName && newName !== t.name) {
                    const newCat = prompt('In welchen Ordner?', t.category);
                    if (newCat) {
                        libManage('copy', { category: t.category, name: t.name, new_category: newCat, new_name: newName }).then(r => {
                            if (r) {
                                fn.serverLog('bvh_copied', `${t.category}/${t.name} -> ${newCat}/${newName}`);
                                loadLibrary({ category: newCat, name: newName });
                            }
                        });
                    }
                }
            } else if (action === 'rename') {
                const newName = prompt('Neuer Name:', t.name);
                if (newName && newName !== t.name) {
                    if (await libManage('rename', { category: t.category, name: t.name, new_name: newName }))
                        loadLibrary({ category: t.category, name: newName });
                }
            } else if (action === 'move') {
                const newCat = prompt('In welchen Ordner verschieben?', t.category);
                if (newCat && newCat !== t.category) {
                    if (await libManage('move', { category: t.category, name: t.name, new_category: newCat })) loadLibrary();
                }
            } else if (action === 'delete') {
                if (confirm(`"${t.name}" wirklich löschen?`)) {
                    _libOpenCats.add(t.category);
                    _libSelectedItem = null;
                    if (await libManage('delete', { category: t.category, name: t.name })) {
                        removeClipsFromTracks(t.category, t.name);
                        loadLibrary();
                    }
                }
            }
        });
    });

    // Folder context menu
    document.querySelectorAll('#lib-ctx-folder .lib-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _libCtxTarget;
            if (!t) return;
            const action = item.dataset.action;
            if (action === 'rename-folder') {
                const newName = prompt('Neuer Ordnername:', t.category);
                if (newName && newName !== t.category) {
                    if (await libManage('rename_folder', { category: t.category, new_name: newName })) loadLibrary();
                }
            } else if (action === 'new-folder') {
                const name = prompt('Name des neuen Ordners:');
                if (name) {
                    if (await libManage('create_folder', { folder_name: name })) loadLibrary();
                }
            } else if (action === 'delete-folder') {
                if (confirm(`Ordner "${t.category}" wirklich löschen?\n(Nur wenn leer)`)) {
                    if (await libManage('delete_folder', { category: t.category })) loadLibrary();
                }
            }
        });
    });

    // Library toolbar buttons
    document.getElementById('lib-new-folder')?.addEventListener('click', async () => {
        const name = prompt('Name des neuen Ordners:');
        if (name) { if (await libManage('create_folder', { folder_name: name })) loadLibrary(); }
    });
    document.getElementById('lib-rename')?.addEventListener('click', () => renameSelectedLibItem());
    document.getElementById('lib-delete')?.addEventListener('click', () => deleteSelectedLibItem());
    document.getElementById('lib-refresh')?.addEventListener('click', () => loadLibrary());
}

export function setupSidebarResize() {
    const sidebar = document.getElementById('studio-sidebar');
    const handle = document.getElementById('sidebar-resize');
    if (!sidebar || !handle) return;

    // Restore saved width
    try {
        const saved = localStorage.getItem('bvhStudio_sidebarWidth');
        if (saved) sidebar.style.width = saved + 'px';
    } catch(e) {}

    let dragging = false;
    handle.addEventListener('mousedown', (e) => {
        dragging = true;
        handle.classList.add('dragging');
        e.preventDefault();
    });
    document.addEventListener('mousemove', (e) => {
        if (!dragging) return;
        const newWidth = Math.max(150, Math.min(600, e.clientX - sidebar.getBoundingClientRect().left));
        sidebar.style.width = newWidth + 'px';
    });
    document.addEventListener('mouseup', () => {
        if (dragging) {
            dragging = false;
            handle.classList.remove('dragging');
            try { localStorage.setItem('bvhStudio_sidebarWidth', parseInt(sidebar.style.width)); } catch(e) {}
            // Trigger resize for viewport/timeline
            window.dispatchEvent(new Event('resize'));
        }
    });
}

// Register functions in registry
fn.loadLibrary = loadLibrary;
fn.deleteSelectedLibItem = deleteSelectedLibItem;
fn.renameSelectedLibItem = renameSelectedLibItem;
