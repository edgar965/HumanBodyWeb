/**
 * Kleiderliste: anzeigen, auswaehlen, Kontextmenue, gemerkter Zustand.
 *
 * Aus kleider.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 18.08.2026: 267 Zeilen, drei Themen. Jetzt:
 *
 *     kleiderverwaltung.js  Umbenennen/Verschieben/Kopieren/Löschen + Menü
 *     kleiderzustand.js     gemerkte Kategorie und Auswahl (localStorage)
 *
 * Hier bleibt das Zeichnen der Liste und das Auswählen — und die Inline-Stile
 * sind zu Klassen geworden (`kld-*` in `static/css/kleider.css`), Befund
 * `jsstilfassungen`.
 */

import { state } from './state.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Kleiderverwaltung } from './kleiderverwaltung.js';
import { Kleiderzustand } from './kleiderzustand.js';

const zustand = new Kleiderzustand();
const verwaltung = new Kleiderverwaltung(
    (kategorie) => {
        if (kategorie) zustand.kategorie = kategorie;
        _renderKleiderList();
    });

/** Ein Kleidungsstück auswählen — Ordner aufklappen, Zeile hervorheben. */
function _kleiderSelectById(id) {
    state._selectedKleiderId = id;
    const liste = document.getElementById('kleider-list');
    if (!liste) return;
    // Erst ALLE Ordner zuklappen, dann den einen öffnen: Sonst bleibt bei
    // mehreren Treffern der zuvor offene Ordner mit offen.
    liste.querySelectorAll('.anim-folder').forEach(ordner => _klappen(ordner, false));
    for (const zeile of liste.querySelectorAll('.anim-item')) {
        if (zeile.dataset.kleiderId !== id) continue;
        const ordner = zeile.closest('.anim-folder');
        if (ordner) _klappen(ordner, true);
        _hervorheben(liste, zeile);
        _kategorieWaehlen(ordner, id);
    }
}

function _klappen(ordner, offen) {
    const koerper = ordner.querySelector('.anim-folder-body');
    if (koerper) koerper.style.display = offen ? '' : 'none';
    const pfeil = ordner.querySelector('.chevron');
    if (pfeil) pfeil.textContent = offen ? '▼' : '▶';
}

function _hervorheben(liste, zeile) {
    liste.querySelectorAll('.anim-item.selected')
        .forEach(el => el.classList.remove('selected'));
    zeile.classList.add('selected');
    state._selectedKleiderId = zeile.dataset.kleiderId;
}

function _kategorieWaehlen(ordner, id) {
    const auswahl = document.getElementById('kleider-category');
    if (!auswahl || !ordner) return;
    const stueck = state._garmentCatalog.find(g => g.id === id);
    if (stueck && stueck._category) auswahl.value = stueck._category;
}

/** Das ausgewählte Kleidungsnetz der ausgewählten Figur — oder `null`. */
function _selectedKleiderMesh() {
    const wahl = state._selectedSubMesh;
    if (!wahl || !wahl.key.startsWith('kld_')) return null;
    const figur = state.characters.get(wahl.charId);
    if (!figur) return null;
    return { inst: figur, key: wahl.key, mesh: figur.clothMeshes[wahl.key] };
}

/** Die Liste neu aufbauen — gruppiert nach Kategorie. */
function _renderKleiderList() {
    const liste = document.getElementById('kleider-list');
    if (!liste) return;
    liste.innerHTML = '';
    zustand.laden();
    const gruppen = _gruppen();
    if (!gruppen) {
        liste.innerHTML = '<div class="leer-hinweis">Keine Kleider gefunden</div>';
        return;
    }
    for (const [kategorie, stuecke] of Object.entries(gruppen)) {
        liste.appendChild(_ordner(liste, kategorie, stuecke));
    }
    _auswahlInDenBlick(liste);
}

/** Nach Kategorie gruppiert — `null`, wenn der Filter nichts übrig lässt. */
function _gruppen() {
    const filter = document.getElementById('kleider-category')?.value || '';
    const gewaehlt = filter
        ? state._garmentCatalog.filter(g => g._category === filter)
        : state._garmentCatalog;
    if (gewaehlt.length === 0) return null;
    const gruppen = {};
    for (const stueck of gewaehlt) {
        (gruppen[stueck._category] = gruppen[stueck._category] || []).push(stueck);
    }
    return gruppen;
}

function _ordner(liste, kategorie, stuecke) {
    const kasten = document.createElement('div');
    kasten.className = 'anim-folder';
    kasten.innerHTML = '<div class="anim-folder-header">'
        + `<span class="chevron">&#9660;</span> ${kategorie} (${stuecke.length})</div>`;
    const koerper = document.createElement('div');
    koerper.className = 'anim-folder-body';
    _klappen(kasten, zustand.kategorie === kategorie);
    for (const stueck of stuecke) {
        koerper.appendChild(_zeile(liste, kategorie, stueck));
    }
    kasten.appendChild(koerper);
    const kopf = kasten.querySelector('.anim-folder-header');
    kopf.addEventListener('click', () => {
        const oeffnen = koerper.style.display === 'none';
        _klappen(kasten, oeffnen);
        if (oeffnen) {
            zustand.kategorie = kategorie;
            zustand.merken();
        }
    });
    return kasten;
}

function _zeile(liste, kategorie, stueck) {
    const zeile = document.createElement('div');
    zeile.className = 'anim-item kld-zeile';
    zeile.dataset.kleiderId = stueck.id;
    if (state._selectedKleiderId === stueck.id) zeile.classList.add('selected');
    if (stueck.has_thumb) zeile.appendChild(_bild(stueck));
    const name = document.createElement('span');
    name.className = 'kld-name';
    name.textContent = stueck.name || stueck.id;
    zeile.appendChild(name);
    zeile.addEventListener('click',
                           () => _auswaehlen(liste, zeile, kategorie, stueck));
    zeile.addEventListener('contextmenu', ereignis => {
        ereignis.preventDefault();
        _hervorheben(liste, zeile);
        verwaltung.zeigen(ereignis.clientX, ereignis.clientY, stueck);
    });
    return zeile;
}

function _bild(stueck) {
    const bild = document.createElement('img');
    bild.className = 'kld-bild';
    // Erst beim Aufklappen laden — 4,77 MB und 125 Anfragen weniger je
    // Seitenaufruf (siehe Bildnachlader).
    Bildnachlader.vormerken(bild, `/api/character/garment/thumb/${stueck.id}/`);
    return bild;
}

function _auswaehlen(liste, zeile, kategorie, stueck) {
    _hervorheben(liste, zeile);
    zustand.kategorie = kategorie;
    zustand.merken();
    _reglerSetzen(stueck);
    zustand.aufDemServerMerken(stueck.id);
}

/** Abstand und Steifigkeit des Stücks in die Regler schreiben. */
function _reglerSetzen(stueck) {
    const abstand = document.getElementById('kleider-offset');
    if (abstand && stueck.offset != null) {
        abstand.value = Math.round(stueck.offset * 1000);      // Meter -> mm
    }
    const steife = document.getElementById('kleider-stiffness');
    if (steife && stueck.stiffness != null) {
        steife.value = Math.round(stueck.stiffness * 100);     // 0..1 -> Prozent
    }
}

function _auswahlInDenBlick(liste) {
    if (!state._selectedKleiderId) return;
    const zeile = liste.querySelector(
        `[data-kleider-id="${state._selectedKleiderId}"]`);
    if (!zeile) return;
    // Erst nach dem Aufklappen scrollen, sonst steht die Zeile noch auf 0 Höhe.
    setTimeout(() => zeile.scrollIntoView({ block: 'nearest' }), Zeiten.ROLLEN_MS);
}

export { _kleiderSelectById, _selectedKleiderMesh, _renderKleiderList };
