/**
 * Animationsbaum: Kategorien, Kontextmenue, Verwaltung.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026): 250 Zeilen fuer die Liste
 * links und ihre Bedienung.
 */

import { loadBVHAnimation } from './wiedergabe.js';


// =========================================================================
// Animation tree
// =========================================================================
export async function loadAnimationTree() {
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree');
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:16px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'anim-category';
            catDiv.dataset.category = cat;

            const header = document.createElement('div');
            header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
                <span>${cat}</span>
                <span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            // Right-click on folder
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                _animCtxTarget = { type: 'folder', category: cat };
                showAnimCtx('anim-ctx-folder', e.clientX, e.clientY);
            });
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'anim-category-body';

            anims.forEach(anim => {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.dataset.url = anim.url;
                item.dataset.category = cat;
                item.dataset.name = anim.name;
                item.innerHTML = `<span>${anim.name}</span><span class="frames">${anim.frames}f</span>`;
                item.addEventListener('click', () => {
                    // Deselect all
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    loadBVHAnimation(anim.url, anim.name, anim.frames);
                });
                // Right-click on file
                item.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    _animCtxTarget = { type: 'file', category: cat, name: anim.name, url: anim.url };
                    showAnimCtx('anim-ctx-file', e.clientX, e.clientY);
                });
                body.appendChild(item);
            });

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        });
    } catch (e) {
        console.error('Failed to load animations:', e);
    }
}

// =========================================================================
// Animation file management
// =========================================================================
export let _animCtxTarget = null;

export function showAnimCtx(menuId, x, y) {
    document.querySelectorAll('.anim-ctx').forEach(m => m.style.display = 'none');
    const menu = document.getElementById(menuId);
    if (!menu) return;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

export async function bvhManage(action, data) {
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

export function setupAnimManagement() {
    // Close context menus on click
    document.addEventListener('click', () => {
        document.querySelectorAll('.anim-ctx').forEach(m => m.style.display = 'none');
    });

    // File context menu actions
    document.querySelectorAll('#anim-ctx-file .anim-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _animCtxTarget;
            if (!t) return;
            const action = item.dataset.action;

            if (action === 'play') {
                loadBVHAnimation(t.url, t.name, 0);
            } else if (action === 'rename') {
                const newName = prompt('Neuer Name:', t.name);
                if (newName && newName !== t.name) {
                    const r = await bvhManage('rename', { category: t.category, name: t.name, new_name: newName });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'move') {
                const newCat = prompt('In welchen Ordner verschieben?', t.category);
                if (newCat && newCat !== t.category) {
                    const r = await bvhManage('move', { category: t.category, name: t.name, new_category: newCat });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'delete') {
                if (confirm(`"${t.name}" wirklich loeschen?`)) {
                    const r = await bvhManage('delete', { category: t.category, name: t.name });
                    if (r?.ok) loadAnimationTree();
                }
            }
        });
    });

    // Folder context menu actions
    document.querySelectorAll('#anim-ctx-folder .anim-ctx-item').forEach(item => {
        item.addEventListener('click', async () => {
            const t = _animCtxTarget;
            if (!t) return;
            const action = item.dataset.action;

            if (action === 'rename-folder') {
                const newName = prompt('Neuer Ordnername:', t.category);
                if (newName && newName !== t.category) {
                    const r = await bvhManage('rename_folder', { category: t.category, new_name: newName });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'new-folder') {
                const name = prompt('Name des neuen Unterordners:');
                if (name) {
                    const r = await bvhManage('create_folder', { folder_name: name });
                    if (r?.ok) loadAnimationTree();
                }
            } else if (action === 'delete-folder') {
                if (confirm(`Ordner "${t.category}" wirklich loeschen?\n(Nur wenn leer)`)) {
                    const r = await bvhManage('delete_folder', { category: t.category });
                    if (r?.ok) loadAnimationTree();
                }
            }
        });
    });

    // Toolbar buttons
    document.getElementById('anim-new-folder')?.addEventListener('click', async () => {
        const name = prompt('Name des neuen Ordners:');
        if (name) {
            const r = await bvhManage('create_folder', { folder_name: name });
            if (r?.ok) loadAnimationTree();
        }
    });

    document.getElementById('anim-rename')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            const newName = prompt('Neuer Name:', name);
            if (newName && newName !== name) {
                bvhManage('rename', { category: cat, name, new_name: newName }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-move')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            const newCat = prompt('In welchen Ordner verschieben?', cat);
            if (newCat && newCat !== cat) {
                bvhManage('move', { category: cat, name, new_category: newCat }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-delete')?.addEventListener('click', () => {
        const active = document.querySelector('.anim-item.active');
        if (active) {
            const cat = active.dataset.category;
            const name = active.dataset.name;
            if (confirm(`"${name}" wirklich loeschen?`)) {
                bvhManage('delete', { category: cat, name }).then(r => { if (r?.ok) loadAnimationTree(); });
            }
        } else {
            alert('Bitte zuerst eine Animation auswaehlen.');
        }
    });

    document.getElementById('anim-refresh')?.addEventListener('click', () => loadAnimationTree());

    // Help dropdown + modal
    const helpDD = document.getElementById('anim-help-dropdown');
    const helpMenu = document.getElementById('anim-help-menu');
    document.getElementById('anim-help-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        helpMenu.style.display = helpMenu.style.display === 'block' ? 'none' : 'block';
    });
    document.addEventListener('click', () => { if (helpMenu) helpMenu.style.display = 'none'; });
    document.getElementById('anim-help-animations')?.addEventListener('click', () => {
        helpMenu.style.display = 'none';
        document.getElementById('anim-help-modal')?.classList.add('open');
    });
    document.getElementById('anim-help-close')?.addEventListener('click', () => {
        document.getElementById('anim-help-modal')?.classList.remove('open');
    });
    document.getElementById('anim-help-modal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) e.currentTarget.classList.remove('open');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT') return;
        if (e.key === 'F2') {
            e.preventDefault();
            document.getElementById('anim-rename')?.click();
        }
        if (e.key === 'Delete') {
            const active = document.querySelector('.anim-item.active');
            if (active) {
                e.preventDefault();
                document.getElementById('anim-delete')?.click();
            }
        }
    });
}
