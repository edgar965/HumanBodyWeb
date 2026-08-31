/**
 * Scene Editor -- Pose browser + apply + rename/delete.
 *
 * UMBAU 18.08.2026: 236 Zeilen. Die Rechnung (Ruhelage, Deltas, Gliedmaßen,
 * T-Pose-Beine) steht jetzt in `posenanwendung.Posenanwendung`; hier bleibt die
 * Liste mit Auswahl, Kontextmenü und Tastaturkürzeln.
 */
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Posenanwendung } from './posenanwendung.js';

/** Ausgewählte Zeile und ihre Pose (`{id, name, category}`). */
let _zeile = null;
let _pose = null;

function _auswaehlen(zeile, pose) {
    _zeile?.classList.remove('pose-gewaehlt');
    _zeile = zeile;
    _pose = pose;
    zeile.classList.add('pose-gewaehlt');
}

/* ── Kontextmenü ── */
const _menue = () => document.getElementById('pose-ctx-menu');

function _menueZeigen(x, y) {
    const menue = _menue();
    if (!menue) return;
    menue.style.display = 'block';
    menue.style.left = x + 'px';
    menue.style.top = y + 'px';
    // Ins Fenster ziehen: Am rechten oder unteren Rand stünde es sonst halb
    // außerhalb und die letzten Einträge wären nicht erreichbar.
    const rahmen = menue.getBoundingClientRect();
    if (rahmen.right > window.innerWidth) {
        menue.style.left = (window.innerWidth - rahmen.width - 4) + 'px';
    }
    if (rahmen.bottom > window.innerHeight) {
        menue.style.top = (window.innerHeight - rahmen.height - 4) + 'px';
    }
}

function _menueVerbergen() {
    const menue = _menue();
    if (menue) menue.style.display = 'none';
}

/**
 * Posen umbenennen und löschen.
 *
 * Liefert im Fehlerfall `{ok: false, error}` statt zu werfen — die beiden
 * Aufrufer zeigen `error` in einem `alert`.
 */
async function poseManage(action, data) {
    try {
        return await Serverabruf.senden('/api/character/pose-manage/',
                                        { action, ...data });
    } catch (fehler) {
        Protokoll.fehler('Pose', action, fehler);
        return { ok: false, error: fehler.message };
    }
}

async function renameSelectedPose() {
    if (!_pose) return;
    const name = prompt('Neuer Name:', _pose.name);
    if (!name || name === _pose.name) return;
    const antwort = await poseManage('rename', { category: _pose.category,
                                                name: _pose.name,
                                                new_name: name });
    _nachAktion(antwort, 'Rename fehlgeschlagen');
}

async function deleteSelectedPose() {
    if (!_pose) return;
    if (!confirm(`Pose "${_pose.name}" wirklich löschen?`)) return;
    const antwort = await poseManage('delete', { category: _pose.category,
                                                name: _pose.name });
    _nachAktion(antwort, 'Delete fehlgeschlagen');
}

function _nachAktion(antwort, fehlertext) {
    if (!antwort.ok) {
        alert(antwort.error || fehlertext);
        return;
    }
    // Auswahl fallen lassen: Die Zeile, auf die sie zeigt, wird neu gebaut.
    _zeile = null;
    _pose = null;
    loadPoseUI();
}

/* ── Kontextmenü und Tastatur: je einmal anmelden ── */
let _menueGebunden = false;

function _menueBinden() {
    if (_menueGebunden) return;
    _menueGebunden = true;
    document.addEventListener('click', _menueVerbergen);
    const menue = _menue();
    if (!menue) return;
    const aktionen = { apply: () => Posenanwendung.vomServer(_pose?.id),
                       rename: renameSelectedPose,
                       delete: deleteSelectedPose };
    menue.querySelectorAll('.pose-ctx-item').forEach(eintrag => {
        eintrag.addEventListener('click', ereignis => {
            ereignis.stopPropagation();
            _menueVerbergen();
            if (eintrag.dataset.action === 'apply' && !_pose) return;
            aktionen[eintrag.dataset.action]?.();
        });
    });
}

let _tastenGebunden = false;

function _tastenBinden() {
    if (_tastenGebunden) return;
    _tastenGebunden = true;
    const liste = document.getElementById('pose-list');
    if (!liste) return;
    // `tabindex`: Ohne ihn bekommt die Liste keinen Fokus und keine Tasten.
    liste.setAttribute('tabindex', '0');
    liste.addEventListener('keydown', ereignis => {
        if (ereignis.key === 'F2') {
            ereignis.preventDefault();
            renameSelectedPose();
        } else if (ereignis.key === 'Delete') {
            ereignis.preventDefault();
            deleteSelectedPose();
        }
    });
}

/* ── Liste ── */

export async function loadPoseUI() {
    const liste = document.getElementById('pose-list');
    if (!liste) return;
    _menueBinden();
    _tastenBinden();
    try {
        const daten = await Serverabruf.json('/api/character/poses/');
        liste.innerHTML = '';
        for (const [kategorie, posen] of Object.entries(daten.categories || {})) {
            liste.appendChild(_ordner(kategorie, posen));
        }
    } catch (fehler) {
        Protokoll.fehler('Pose', 'Liste nicht ladbar', fehler);
        liste.innerHTML = '<div class="leer-hinweis">Poses nicht verfügbar</div>';
    }
    document.getElementById('pose-reset')
        ?.addEventListener('click', () => Posenanwendung.zuruecksetzen());
}

/**
 * Ein Kategorieordner. Nur `rest_poses` ist offen: Dort liegen T- und A-Pose,
 * die fast immer gemeint sind; alles andere sind Dutzende Stilposen.
 */
function _ordner(kategorie, posen) {
    const kasten = document.createElement('div');
    kasten.className = 'anim-folder';
    const kopf = document.createElement('div');
    kopf.className = 'anim-folder-header';
    kopf.innerHTML = `<span class="chevron">&#9660;</span> ${kategorie} `
        + `(${posen.length})`;
    kasten.appendChild(kopf);
    const koerper = document.createElement('div');
    koerper.className = 'anim-folder-body';
    for (const pose of posen) {
        koerper.appendChild(_zeileBauen(kategorie, pose));
    }
    kasten.appendChild(koerper);
    const klappen = (offen) => {
        koerper.style.display = offen ? '' : 'none';
        kopf.querySelector('.chevron').textContent = offen ? '▼' : '▶';
    };
    kopf.addEventListener('click',
                          () => klappen(koerper.style.display === 'none'));
    klappen(kategorie === 'rest_poses');
    return kasten;
}

function _zeileBauen(kategorie, pose) {
    const angabe = { id: pose.id, name: pose.name, category: kategorie };
    const zeile = document.createElement('div');
    zeile.className = 'anim-item pose-zeile';
    zeile.textContent = pose.name;
    zeile.addEventListener('click', () => _auswaehlen(zeile, angabe));
    zeile.addEventListener('dblclick',
                           () => Posenanwendung.vomServer(pose.id));
    zeile.addEventListener('contextmenu', ereignis => {
        ereignis.preventDefault();
        _auswaehlen(zeile, angabe);
        _menueZeigen(ereignis.clientX, ereignis.clientY);
    });
    return zeile;
}

export async function applyPoseFromServer(poseId) {
    return Posenanwendung.vomServer(poseId);
}

// Register
fn.loadPoseUI = loadPoseUI;
fn.applyPoseFromServer = applyPoseFromServer;
window.__applyPoseRuntime = applyPoseFromServer;
window.__characters = state.characters;
