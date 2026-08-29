/**
 * Animationsbaum: Kategorien, Kontextmenue, Verwaltung.
 *
 * Aus animations.js herausgeloest (Umbau 15.08.2026): 250 Zeilen fuer die Liste
 * links und ihre Bedienung.
 */

import { loadBVHAnimation } from './wiedergabe.js';
import { Animationsverwaltung } from './verwaltung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kategoriekasten } from '../gemeinsam/kategoriekasten.js';


// =========================================================================
// Animation tree
// =========================================================================
export async function loadAnimationTree() {
    try {
        const data = await Serverabruf.json('/api/character/animations/');
        const tree = document.getElementById('anim-tree');
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div class="leer-hinweis-gross">Keine Animationen gefunden</div>';
            return;
        }

        catNames.forEach(cat => {
            const anims = categories[cat];
            const {kasten: catDiv, kopf: header} =
                Kategoriekasten.bauen(cat, anims.length);
            catDiv.dataset.category = cat;
            // Right-click on folder
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                _animCtxTarget = { type: 'folder', category: cat };
                showAnimCtx('anim-ctx-folder', e.clientX, e.clientY);
            });
            const body = catDiv.querySelector('.anim-category-body');

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
    document.querySelectorAll('.hb-kontextmenue')
            .forEach(m => m.style.display = 'none');
    const menu = document.getElementById(menuId);
    if (!menu) return;
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
}

export async function bvhManage(action, data) {
    try {
        return await Serverabruf.senden('/api/character/bvh-manage/',
                                        { action, ...data });
    } catch (e) {
        alert('Fehler: ' + e.message);
        return null;
    }
}

/**
 * Bedienung der Animationsliste anmelden. Die Vorgänge selbst stehen in
 * `Animationsverwaltung` — vorher waren sie hier in 151 Zeilen doppelt
 * ausgeschrieben, einmal für das Kontextmenü und einmal für die Knöpfe.
 */
export function setupAnimManagement() {
    return new Animationsverwaltung({
        ziel: () => _animCtxTarget,
        neuLaden: () => loadAnimationTree(),
        serverruf: (aktion, daten) => bvhManage(aktion, daten),
    }).aufbauen();
}
