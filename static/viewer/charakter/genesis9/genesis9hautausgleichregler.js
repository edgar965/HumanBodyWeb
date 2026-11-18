import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautausgleich } from '../../gemeinsam/genesis9hautausgleich.js';

/**
 * Genesis9hautausgleichregler — die vier Schieber des Hautausgleichs (Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche) als aufklappbarer Block
 * „Korrekturen" (18.11.2026, Edgar: „die neuen Regler möchte ich bei den Eigenschaften der Haut, als neuer Unterabsatz: Korrekturen") im Popup
 * „Material · Haut" hinter dem Zahnrad (`Genesis9hautdialogblock`). Stünde derselbe Schieber zweimal auf der Seite, zöge der eine den anderen nach
 * (`data-hautausgleich`). Gerechnet wird auf dem Server (`Genesis9hautausgleich`), je Zug nach kurzer Ruhe; Schritte zu 5 %.
 */
export class Genesis9hautausgleichregler {

    static block(inst, praefix = 'g9-hautausgleich-') {
        const block = document.createElement('details');
        block.className = 'uma-gruppe hb-hautebenengruppe';
        block.open = true;
        block.innerHTML = '<summary>Korrekturen</summary>'
            + '<div class="hb-font-size-0-72rem">Rechnet auf dem Server neue Hautbilder (je Zug ein bis zwei Sekunden) — gedacht für Häute aus Fotos (Auswahl „Haut": „… · Foto"), '
            + 'wirkt auf jede Haut. Maus auf ⓘ: was der Regler tut. Doppelklick: Standard.</div>';
        for (const feld of Genesis9hautausgleich.FELDER) block.appendChild(Genesis9hautausgleichregler._zeile(inst, feld, praefix));
        return block;
    }

    static _zeile(inst, feld, praefix) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `${praefix}${feld.name}`;
        const wert = Genesis9hautausgleich.werte(inst)[feld.name];
        // Erklärung beim Überfahren sofort (18.11.2026, Edgar: „mach mir ein hover bei den Korrekturen, was die bedeuten") — der Browser-Titel kam erst
        // nach einer Weile und fiel nicht auf; das ⓘ zeigt, dass es eine gibt (`genesis9material.css`: `.hb-korrektur-info`).
        zeile.innerHTML = `
            <label for="${kennung}" class="hb-korrektur-label">${escapeHtml(feld.label)}<span class="hb-korrektur-info" data-erklaerung="${escapeHtml(feld.hilfe)}">ⓘ</span></label>
            <input type="range" id="${kennung}" min="0" max="100" step="5" value="${wert}" data-hautausgleich="${feld.name}" aria-label="${escapeHtml(feld.label)}: ${escapeHtml(feld.hilfe)}">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        schieber.addEventListener('input', () => {
            const neu = Number(schieber.value);
            Genesis9hautausgleichregler._zeigen(feld.name, neu);
            Genesis9hautausgleich.setzen(inst, feld.name, neu);
        });
        schieber.addEventListener('change', () => markDirty());
        schieber.addEventListener('dblclick', () => {
            const vorgabe = Genesis9hautausgleich.vorgabe(feld.name);
            Genesis9hautausgleichregler._zeigen(feld.name, vorgabe);
            Genesis9hautausgleich.setzen(inst, feld.name, vorgabe);
            markDirty();
        });
        return zeile;
    }

    /** Alle Schieber dieses Feldes auf der Seite auf `wert` (Bedienfeld und Popup). */
    static _zeigen(name, wert) {
        for (const s of document.querySelectorAll(`input[data-hautausgleich="${name}"]`)) {
            s.value = String(wert);
            const anzeige = s.parentElement?.querySelector('.slider-value');
            if (anzeige) anzeige.textContent = `${wert} %`;
        }
    }
}
