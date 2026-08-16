/**
 * Liste der MakeHuman-Proxys: anzeigen, Kontextmenue, gemerkter Zustand.
 *
 * Aus mh_proxy.js herausgeloest (Umbau 16.08.2026).
 */

import { state } from './state.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';


// Persist last open category + selected garment
const MH_STORAGE_KEY = 'mh_proxy_state';

function _saveMHState() {
    // `setItem` wirft bei vollem Speicher (QuotaExceededError) und im privaten
    // Fenster (SecurityError). Ungefangen brach damit der AUFRUFER ab — in
    // `_renderMHList` etwa die Zeile, die die Kategorie aufklappt: Die Liste
    // reagierte scheinbar grundlos nicht mehr. Ein verlorener Merkzustand ist
    // dagegen harmlos.
    try {
        localStorage.setItem(MH_STORAGE_KEY, JSON.stringify({
            openCat: _mhOpenCat,
            selectedId: state._selectedMHId,
        }));
    } catch (e) {
        console.warn('[MH-Proxy] Zustand nicht speicherbar:', e?.name || e);
    }
}

function _loadMHState() {
    try {
        const s = JSON.parse(localStorage.getItem(MH_STORAGE_KEY));
        if (s) { _mhOpenCat = s.openCat || ''; state._selectedMHId = s.selectedId || ''; }
    } catch(e) {}
}

let _mhOpenCat = '';

// Context menu for garment items
let _mhCtxTarget = null;

function _showMHCtx(x, y, garment) {
    _mhCtxTarget = garment;
    let menu = document.getElementById('mh-ctx-menu');
    if (!menu) {
        menu = document.createElement('div');
        menu.id = 'mh-ctx-menu';
        menu.className = 'ctx-menu';
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
            item.addEventListener('click', () => _handleMHCtx(item.dataset.action));
        });
        document.body.appendChild(menu);
        document.addEventListener('click', () => { menu.style.display = 'none'; }, { capture: true });
    }
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    menu.style.display = 'block';
}

async function _handleMHCtx(action) {
    const g = _mhCtxTarget;
    if (!g) return;
    const menu = document.getElementById('mh-ctx-menu');
    if (menu) menu.style.display = 'none';

    if (action === 'rename') {
        const newName = prompt('Neuer Name:', g.name || g.id);
        if (newName && newName !== g.name) {
            try {
                await Serverabruf.senden('/api/character/garment/manage/',
                    { action: 'rename', id: g.id, new_name: newName });
                g.name = newName;
                _renderMHList();
            } catch(e) { console.error('Rename failed:', e); }
        }
    } else if (action === 'move') {
        const cats = [...new Set(state._garmentCatalog.map(x => x._category))];
        const target = prompt('Verschieben nach Kategorie:\n' + cats.join(', '), g._category);
        if (target && target !== g._category) {
            try {
                await Serverabruf.senden('/api/character/garment/manage/',
                    { action: 'move', id: g.id, target_category: target });
                g._category = target;
                _mhOpenCat = target;
                _renderMHList();
            } catch(e) { console.error('Move failed:', e); }
        }
    } else if (action === 'copy') {
        const newName = prompt('Kopie-Name:', (g.name || g.id) + '_copy');
        if (newName) {
            try {
                await Serverabruf.senden('/api/character/garment/manage/',
                    { action: 'copy', id: g.id, new_name: newName });
                // Reload catalog
                state._garmentCatalog.length = 0;
                const data = await Serverabruf.json('/api/character/garment/library/');
                if (data.garments) {
                    for (const cat of Object.keys(data.garments)) {
                        for (const gg of data.garments[cat]) {
                            gg._category = cat;
                            state._garmentCatalog.push(gg);
                        }
                    }
                }
                _renderMHList();
            } catch(e) { console.error('Copy failed:', e); }
        }
    } else if (action === 'delete') {
        if (!confirm(`"${g.name || g.id}" wirklich löschen?`)) return;
        try {
            await Serverabruf.senden('/api/character/garment/manage/',
                    { action: 'delete', id: g.id });
            const idx = state._garmentCatalog.indexOf(g);
            if (idx >= 0) state._garmentCatalog.splice(idx, 1);
            if (state._selectedMHId === g.id) state._selectedMHId = '';
            _renderMHList();
        } catch(e) { console.error('Delete failed:', e); }
    }
}

function _renderMHList() {
    const list = document.getElementById('mh-list');
    if (!list) return;
    list.innerHTML = '';

    _loadMHState();

    const catFilter = document.getElementById('mh-category')?.value || '';
    const filtered = catFilter
        ? state._garmentCatalog.filter(g => g._category === catFilter)
        : state._garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments</div>';
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

        // Only open the last-used category, collapse all others
        const isOpen = _mhOpenCat === cat;
        body.style.display = isOpen ? '' : 'none';
        catDiv.querySelector('.chevron').textContent = isOpen ? '\u25BC' : '\u25B6';

        for (const g of items) {
            const row = document.createElement('div');
            row.className = 'anim-item';
            row.dataset.garmentId = g.id;
            row.style.cssText = 'display:flex;align-items:center;gap:6px;padding:4px 8px;cursor:pointer;';
            if (state._selectedMHId === g.id) row.classList.add('selected');
            if (g.has_thumb) {
                const img = document.createElement('img');
                // Erst beim Aufklappen laden — 4,77 MB und 125 Anfragen
                // weniger je Seitenaufruf (siehe Bildnachlader).
                Bildnachlader.vormerken(
                    img, `/api/character/garment/thumb/${g.id}/`);
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;';
                row.appendChild(img);
            }
            const name = document.createElement('span');
            name.textContent = g.name || g.id;
            name.style.cssText = 'font-size:0.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            row.appendChild(name);
            row.addEventListener('click', () => {
                state._selectedMHId = g.id;
                _mhOpenCat = cat;
                _saveMHState();
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
            });
            row.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                state._selectedMHId = g.id;
                list.querySelectorAll('.anim-item').forEach(el => el.classList.remove('selected'));
                row.classList.add('selected');
                _showMHCtx(e.clientX, e.clientY, g);
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
                _mhOpenCat = cat;
                _saveMHState();
            }
        });
        list.appendChild(catDiv);
    }

    // Scroll to selected item
    if (state._selectedMHId) {
        const sel = list.querySelector(`[data-garment-id="${state._selectedMHId}"]`);
        if (sel) setTimeout(() => sel.scrollIntoView({ block: 'nearest' }), Zeiten.ROLLEN_MS);
    }
}

export { _renderMHList };
