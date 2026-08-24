import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bausteine des Bedienfelds der Ergebnisseite.
 *
 * Aus ui_panel.js und knopfleiste.js herausgeloest (Umbau 16.08.2026). Der
 * Ziehgriff ist der wichtigste Teil: das Muster
 * "mousedown → mousemove merken → bei mouseup beide abmelden" stand DREIMAL in
 * knopfleiste.js — für das Verschieben des Videofensters, für seine Größe und
 * für die Höhe der 3D-Ansicht. Zweimal davon mit eigener Rechnung für dasselbe.
 */

/** Element mit Klasse — kürzer als zwei Zeilen an jeder Stelle. */
export function el(tag, klasse) {
    const knoten = document.createElement(tag);
    if (klasse) knoten.className = klasse;
    return knoten;
}

/**
 * Ziehgriff — ein Element, an dem mit der Maus gezogen wird.
 *
 * `beginn` wird beim Drücken gerufen und darf Ausgangswerte merken; `ziehen`
 * bekommt den Abstand zum Druckpunkt. Vorher rechneten zwei der drei Stellen
 * mit Schritt-für-Schritt-Deltas, was bei schnellen Bewegungen wegläuft.
 */
export class Ziehgriff {

    /**
     * @param griff    Element, an dem gezogen wird
     * @param ziehen   (dx, dy) — Abstand zum Druckpunkt
     * @param wahl     { beginn, ausser, stoppen } — Startwerte merken, ein
     *                 Auswahlpfad, der nicht zieht (etwa ein Schließknopf),
     *                 und ob das Ereignis nicht weiterlaufen soll
     */
    static an(griff, ziehen, wahl = {}) {
        if (!griff) return null;
        const { beginn = null, ausser = null, stoppen = false } = wahl;
        griff.addEventListener('mousedown', ereignis => {
            if (ausser && ereignis.target.closest(ausser)) return;
            ereignis.preventDefault();
            if (stoppen) ereignis.stopPropagation();
            if (beginn) beginn(ereignis);
            const startX = ereignis.clientX;
            const startY = ereignis.clientY;
            const bewegen = lauf => ziehen(lauf.clientX - startX,
                                           lauf.clientY - startY);
            const loslassen = () => {
                document.removeEventListener('mousemove', bewegen);
                document.removeEventListener('mouseup', loslassen);
            };
            document.addEventListener('mousemove', bewegen);
            document.addEventListener('mouseup', loslassen);
        });
        return griff;
    }
}

/** Aufklappbarer Abschnitt mit Kopfzeile. */
export class Abschnitt {

    constructor(titel, offen) {
        this.el = el('div', 'rc-section' + (offen ? '' : ' collapsed'));
        this.kopf = el('div', 'rc-section-header');
        this.kopf.innerHTML =
            `<span>${titel}</span><span class="rc-chevron">&#9660;</span>`;
        this.kopf.addEventListener('click', ereignis => {
            // Knöpfe in der Kopfzeile (etwa "Reset") klappen nicht zu.
            if (ereignis.target.tagName === 'BUTTON') return;
            this.el.classList.toggle('collapsed');
        });
        this.inhalt = el('div', 'rc-section-body');
        this.el.append(this.kopf, this.inhalt);
    }

    anhaengen(...knoten) {
        this.inhalt.append(...knoten);
        return this;
    }
}

/** Zeile mit Beschriftung, Schieberegler und Wertanzeige. */
export class Reglerzeile {

    constructor(beschriftung, id, min, max, wert, schritt, form) {
        this.zeile = el('div', 'rc-slider-row');
        const text = el('label', '');
        text.textContent = beschriftung;
        this.eingabe = document.createElement('input');
        Object.assign(this.eingabe, { type: 'range', id, min, max, value: wert,
                                     step: schritt });
        this.anzeige = el('span', 'rc-slider-val');
        this.anzeige.textContent = form(wert);
        this.eingabe.addEventListener('input', () => {
            this.anzeige.textContent = form(this.zahl());
        });
        this.zeile.append(text, this.eingabe, this.anzeige);
    }

    zahl() {
        return parseInt(this.eingabe.value, 10);
    }
}

/**
 * Modellauswahl füllen. Stand zweimal fast gleich da — einmal für die
 * Kopfzeile, einmal für das Seitenfeld.
 */
export async function modellwahlFuellen(feld, wechseln, leeren = false) {
    if (!feld) return false;
    try {
        const daten = await Serverabruf.json('/api/character/models/');
        if (leeren) feld.innerHTML = '';
        for (const vorgabe of daten.presets || []) {
            const eintrag = new Option(vorgabe.label || vorgabe.name, vorgabe.name);
            eintrag.selected = vorgabe.name === state.currentPresetName;
            feld.appendChild(eintrag);
        }
    } catch (fehler) {
        Protokoll.warnung('result_character', 'Modell-Liste nicht ladbar:', fehler);
        return false;
    }
    feld.addEventListener('change', () => wechseln(feld.value));
    return true;
}
