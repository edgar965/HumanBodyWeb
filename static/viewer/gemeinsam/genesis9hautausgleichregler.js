import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Genesis9hautausgleich } from './genesis9hautausgleich.js';

/**
 * Genesis9hautausgleichregler — die Schieber des Hautausgleichs (Eigenheiten, Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche, Muttermale behalten) als aufklappbarer
 * Block „Korrekturen" (18.11.2026, Edgar: „die neuen Regler möchte ich bei den Eigenschaften der Haut, als neuer Unterabsatz: Korrekturen") — im Popup „Material · Haut" hinter dem
 * Zahnrad (`Genesis9hautdialogblock`) und seit 20.11.2026 auf der Foto-Genesis-Jobseite (`Fotogenesishautkorrektur`; Edgar: „Du solltest die Haut Regler aus "Charakter" auf die
 * Jobseite einbauen"), darum in `gemeinsam/`. Stünde derselbe Schieber zweimal auf der Seite, zöge der eine den anderen nach (`data-hautausgleich`). Gerechnet wird auf dem Server
 * (`Genesis9hautausgleich`), je Zug nach kurzer Ruhe; Schritte zu 5 %.
 *
 *     Genesis9hautausgleichregler.block(inst, { praefix, geaendert, hinweis })     // geaendert(): nach Loslassen und Doppelklick (Charakter: markDirty)
 */
export class Genesis9hautausgleichregler {

    static HINWEIS = 'Rechnet auf dem Server neue Hautbilder (je Zug ein bis zwei Sekunden) — gedacht für Häute aus Fotos (Auswahl „Haut": „… · Foto"), '
        + 'wirkt auf jede Haut. Maus auf ⓘ: was der Regler tut. Doppelklick: Standard.';

    static block(inst, { praefix = 'g9-hautausgleich-', geaendert = null, hinweis = Genesis9hautausgleichregler.HINWEIS } = {}) {
        const block = document.createElement('details');
        block.className = 'uma-gruppe hb-hautebenengruppe';
        block.open = true;
        block.innerHTML = '<summary>Korrekturen</summary>' + (hinweis ? `<div class="hb-font-size-0-72rem">${Htmltext.maskieren(hinweis)}</div>` : '');   // ohne: die Seite sagt es selbst
        for (const feld of Genesis9hautausgleich.FELDER) block.appendChild(Genesis9hautausgleichregler._zeile(inst, feld, praefix, geaendert));
        return block;
    }

    static _zeile(inst, feld, praefix, geaendert) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `${praefix}${feld.name}`;
        const wert = Genesis9hautausgleich.werte(inst)[feld.name];
        const label = Htmltext.maskieren(feld.label), hilfe = Htmltext.maskieren(feld.hilfe);
        // Erklärung beim Überfahren sofort (18.11.2026, Edgar: „mach mir ein hover bei den Korrekturen, was die bedeuten") — der Browser-Titel kam erst
        // nach einer Weile und fiel nicht auf; das ⓘ zeigt, dass es eine gibt (`genesis9material.css`, Jobseite `fotogenesis.css`: `.hb-korrektur-info`).
        zeile.innerHTML = `
            <label for="${kennung}" class="hb-korrektur-label">${label}<span class="hb-korrektur-info" data-erklaerung="${hilfe}">ⓘ</span></label>
            <input type="range" id="${kennung}" min="0" max="100" step="5" value="${wert}" data-hautausgleich="${feld.name}" aria-label="${label}: ${hilfe}">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        schieber.addEventListener('input', () => {
            const neu = Number(schieber.value);
            Genesis9hautausgleichregler._zeigen(feld.name, neu);
            Genesis9hautausgleich.setzen(inst, feld.name, neu);
        });
        schieber.addEventListener('change', () => geaendert?.());
        schieber.addEventListener('dblclick', () => {
            const vorgabe = Genesis9hautausgleich.vorgabe(feld.name);
            Genesis9hautausgleichregler._zeigen(feld.name, vorgabe);
            Genesis9hautausgleich.setzen(inst, feld.name, vorgabe);
            geaendert?.();
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
