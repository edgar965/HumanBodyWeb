import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';

/**
 * Genesis9texturmischung — der Bereich „Textur" ganz unten in den Eigenschaften
 * einer Genesis-9-Figur: alle Hautsätze der Bibliothek, je Satz ein Regler in
 * Prozent (`inst.hautmischung`, gemischt im Shader — `gemeinsam/
 * genesis9hautmischung.js`).
 *
 * Edgar, 21.09.2026: „mach eine Kategorie und Einstellung ganz unten bei den
 * Modell Eigenschaften, «Textur» mit allen Texturen die du hast, und Regler
 * dazu in %". Die Liste ist dieselbe wie in der Auswahl «Haut» oben
 * (`plan.haut`: Essentials, Charaktere, Toon); 0 % heißt „nicht dabei".
 *
 * Kein Serverlauf beim Ziehen: das Gewicht ist ein Uniform. Erst ein Satz,
 * der von 0 auf > 0 geht, holt seine Bilder (einmal je Satz und Kachel).
 */
export class Genesis9texturmischung {

    static BEREICH = 'prop-genesis9-textur';

    static fuellen(inst, plan) {
        const behaelter = document.getElementById(Genesis9texturmischung.BEREICH);
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const saetze = plan.haut || [];
        if (!saetze.length) {
            behaelter.innerHTML = '<div class="gedaempft">Keine Hautsätze gefunden.</div>';
            return;
        }
        behaelter.innerHTML = '<div class="hb-font-size-0-72rem">Weitere Hautsätze mit Gewicht '
            + 'über der gewählten Haut — Albedo, Normalen und Rauheit je Kachel.</div>';
        for (const satz of saetze) {
            behaelter.appendChild(Genesis9texturmischung._zeile(inst, satz));
        }
    }

    static _zeile(inst, satz) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `g9-textur-${satz.id.replace(/[^a-z0-9_]/gi, '_')}`;
        const wert = Number(inst.hautmischung?.[satz.id]) || 0;
        const name = satz.geschlecht ? `${satz.name} (${satz.geschlecht})` : satz.name;
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(satz.id)}">${escapeHtml(name)}</label>
            <input type="range" id="${kennung}" min="0" max="100" step="1" value="${wert}">
            <span class="slider-value">${wert} %</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseInt(schieber.value, 10) || 0;
            anzeige.textContent = `${neu} %`;
            inst.hautmischungSetzen(satz.id, neu);
        });
        schieber.addEventListener('change', () => markDirty());
        return zeile;
    }
}
