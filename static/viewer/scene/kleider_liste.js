/**
 * Kleiderliste: anzeigen, auswaehlen, Kontextmenue, gemerkter Zustand.
 *
 * Aus kleider.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';


function _kleiderSelectById(id) {
    state._selectedKleiderId = id;
    const list = document.getElementById('kleider-list');
    if (!list) return;

    // 1. Collapse ALL folders first
    list.querySelectorAll('.anim-folder').forEach(folder => {
        const body = folder.querySelector('.anim-folder-body');
        if (body) body.style.display = 'none';
        const chev = folder.querySelector('.chevron');
        if (chev) chev.textContent = '\u25B6';
    });

    // 2. Find the item, expand its parent folder, select it
    list.querySelectorAll('.anim-item').forEach(el => {
        if (el.dataset.kleiderId === id) {
            // Expand parent folder
            const folder = el.closest('.anim-folder');
            if (folder) {
                const body = folder.querySelector('.anim-folder-body');
                if (body) body.style.display = '';
                const chev = folder.querySelector('.chevron');
                if (chev) chev.textContent = '\u25BC';
            }
            // Select + highlight
            list.querySelectorAll('.anim-item').forEach(e => e.classList.remove('selected'));
            el.classList.add('selected');
            state._selectedKleiderId = id;

            // 3. Set category dropdown to match
            const catSelect = document.getElementById('kleider-category');
            if (catSelect && folder) {
                const g = state._garmentCatalog.find(g => g.id === id);
                if (g && g._category) catSelect.value = g._category;
            }
        }
    });
}

function _selectedKleiderMesh() {
    if (!state._selectedSubMesh || !state._selectedSubMesh.key.startsWith('kld_')) return null;
    const inst = state.characters.get(state._selectedSubMesh.charId);
    if (!inst) return null;
    return { inst, key: state._selectedSubMesh.key, mesh: inst.clothMeshes[state._selectedSubMesh.key] };
}

// Persist last open category + selected garment
const KLD_STORAGE_KEY = 'kleider_state';

let _kldOpenCat = '';

function _saveKldState() {
    localStorage.setItem(KLD_STORAGE_KEY, JSON.stringify({
        openCat: _kldOpenCat,
        selectedId: state._selectedKleiderId,
    }));
}

function _loadKldState() {
    try {
        const s = JSON.parse(localStorage.getItem(KLD_STORAGE_KEY));
        if (s) { _kldOpenCat = s.openCat || ''; state._selectedKleiderId = s.selectedId || ''; }
    } catch(e) {}
}

// Context menu for garment items (shared between Kleider and MH)
let _kldCtxTarget = null;

function _showKldCtx(x, y, garment) {
    _kldCtxTarget = garment;
    let menu = document.getElementById('kld-ctx-menu');
    if (!menu) {
        menu = document.createElement('div');
        menu.id = 'kld-ctx-menu';
        menu.style.cssText = 'position:fixed;z-index:9999;background:var(--bg-secondary);border:1px solid var(--border);border-radius:4px;padding:4px 0;min-width:140px;font-size:0.8rem;box-shadow:0 4px 12px rgba(0,0,0,.4);';
        menu.innerHTML = `
            <div class="ctx-item" data-action="rename" style="padding:4px 12px;cursor:pointer;">Umbenennen</div>
            <div class="ctx-item" data-action="move" style="padding:4px 12px;cursor:pointer;">Verschieben...</div>
            <div class="ctx-item" data-action="copy" style="padding:4px 12px;cursor:pointer;">Kopieren...</div>
            <div style="border-top:1px solid var(--border);margin:2px 0;"></div>
            <div class="ctx-item" data-action="delete" style="padding:4px 12px;cursor:pointer;color:#f44;">Löschen</div>
        `;
        menu.querySelectorAll('.ctx-item').forEach(item => {
            item.addEventListener('mouseenter', () => item.style.background = 'var(--accent)');
            item.addEventListener('mouseleave', () => item.style.background = '');
            item.addEventListener('click', () => _handleKldCtx(item.dataset.action));
        });
        document.body.appendChild(menu);
        document.addEventListener('click', () => { menu.style.display = 'none'; }, { capture: true });
    }
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.style.display = 'block';
}

async function _handleKldCtx(action) {
    const g = _kldCtxTarget;
    if (!g) return;
    const menu = document.getElementById('kld-ctx-menu');
    if (menu) menu.style.display = 'none';

    if (action === 'rename') {
        const newName = prompt('Neuer Name:', g.name || g.id);
        if (newName && newName !== g.name) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'rename', id: g.id, new_name: newName }),
                });
                g.name = newName;
                _renderKleiderList();
            } catch(e) { console.error('Rename failed:', e); }
        }
    } else if (action === 'move') {
        const cats = [...new Set(state._garmentCatalog.map(x => x._category))];
        const target = prompt('Verschieben nach Kategorie:\n' + cats.join(', '), g._category);
        if (target && target !== g._category) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'move', id: g.id, target_category: target }),
                });
                g._category = target;
                _kldOpenCat = target;
                _renderKleiderList();
            } catch(e) { console.error('Move failed:', e); }
        }
    } else if (action === 'copy') {
        const newName = prompt('Kopie-Name:', (g.name || g.id) + '_copy');
        if (newName) {
            try {
                await fetch('/api/character/garment/manage/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'copy', id: g.id, new_name: newName }),
                });
                state._garmentCatalog.length = 0;
                const resp = await fetch('/api/character/garment/library/');
                const data = await resp.json();
                if (data.garments) {
                    for (const cat of Object.keys(data.garments)) {
                        for (const gg of data.garments[cat]) {
                            gg._category = cat;
                            state._garmentCatalog.push(gg);
                        }
                    }
                }
                _renderKleiderList();
            } catch(e) { console.error('Copy failed:', e); }
        }
    } else if (action === 'delete') {
        if (!confirm(`"${g.name || g.id}" wirklich löschen?`)) return;
        try {
            await fetch('/api/character/garment/manage/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'delete', id: g.id }),
            });
            const idx = state._garmentCatalog.indexOf(g);
            if (idx >= 0) state._garmentCatalog.splice(idx, 1);
            if (state._selectedKleiderId === g.id) state._selectedKleiderId = '';
            _renderKleiderList();
        } catch(e) { console.error('Delete failed:', e); }
    }
}

function _renderKleiderList() {
    const list = document.getElementById('kleider-list');
    if (!list) return;
    list.innerHTML = '';

    _loadKldState();

    const catFilter = document.getElementById('kleider-category')?.value || '';
    const filtered = catFilter
        ? state._garmentCatalog.filter(g => g._category === catFilter)
        : state._garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Kleider gefunden</div>';
        return;
    }

    const groups = {};
    for (const g of filtered) {
        if (!groups[g._category]) groups[g._category] = [];
        groups[g._category].push(g);
    }

    for (const [cat, items] of Object.entries(groups)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-folder';
        catDiv.innerHTML = `<div class="anim-folder-header"><span class="chevron">&#9660;</span> ${cat} (${items.length})</div>`;
        const body = document.createElement('div');
        body.className = 'anim-folder-body';

        const isOpen = _kldOpenCat === cat;
        body.style.display = isOpen ? '' : 'none';
        catDiv.querySelector('.chevron').textContent = isOpen ? '\u25BC' : '\u25B6';

        for (const g of items) {
            const row = document.createElement('div');
            row.className = 'anim-item';
            row.dataset.kleiderId = g.id;
            row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:4px 8px;cursor:pointer;';
            if (state._selectedKleiderId === g.id) row.classList.add('selected');
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;';
                row.appendChild(img);
            }
            const name = document.createElement('span');
            name.textContent = g.name || g.id;
            name.style.cssText = 'font-size:0.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            row.appendChild(name);
            row.addEventListener('click', () => {
                state._selectedKleiderId = g.id;
                _kldOpenCat = cat;
                _saveKldState();
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
                const offEl = document.getElementById('kleider-offset');
                if (offEl && g.offset != null) offEl.value = Math.round(g.offset * 1000);
                const stEl = document.getElementById('kleider-stiffness');
                if (stEl && g.stiffness != null) stEl.value = Math.round(g.stiffness * 100);
                fetch('/api/ui-pref/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'last_kleider_id', value: g.id }),
                }).catch(() => {});
            });
            row.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                state._selectedKleiderId = g.id;
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
                _showKldCtx(e.clientX, e.clientY, g);
            });
            body.appendChild(row);
        }
        catDiv.appendChild(body);
        const header = catDiv.querySelector('.anim-folder-header');
        header.addEventListener('click', () => {
            const opening = body.style.display === 'none';
            body.style.display = opening ? '' : 'none';
            header.querySelector('.chevron').textContent = opening ? '\u25BC' : '\u25B6';
            if (opening) {
                _kldOpenCat = cat;
                _saveKldState();
            }
        });
        list.appendChild(catDiv);
    }

    if (state._selectedKleiderId) {
        const sel = list.querySelector(`[data-kleider-id="${state._selectedKleiderId}"]`);
        if (sel) setTimeout(() => sel.scrollIntoView({ block: 'nearest' }), 50);
    }
}

export { _kleiderSelectById, _selectedKleiderMesh, _renderKleiderList };
