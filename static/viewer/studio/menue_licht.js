import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Menuelicht — der Licht-Zweig des Menüs „Clip hinzufügen".
 *
 * Herausgelöst aus `zeitleiste_spurmenue.js` (372 Zeilen).
 *
 * **Paar oder einzeln** ist keine Spielerei: Ein Schlüssel gilt ab seinem Bild
 * nach vorn. Wer an EINER Stelle den Wert für davor und danach getrennt setzen
 * will, braucht zwei Schlüssel am selben Bild — sonst blendet das Licht über
 * das ganze vorige Segment über.
 *
 * **Die Vorgaben FÜGEN Lichter hinzu**, sie ersetzen keine. Das steht auch im
 * Hinweistext des Eintrags: Wer eine Bühnenvorgabe wählt und die alten Lichter
 * stehen lässt, hat sonst plötzlich die doppelte Helligkeit und sucht den Fehler.
 */
export class Menuelicht {

    static ENDPUNKT = '/api/studio/theatre-presets/';

    constructor(menue) {
        this.menue = menue;
    }

    fuellen() {
        this.menue.leeren();
        this.menue.ziel.appendChild(this.menue.spureintrag(
            'Lichteigenschaft (Pair: vor/nach)',
            () => fn.addLightKeyframePair(this.menue.nummer, this.menue.bild),
            { titel: 'Legt zwei Keyframes am gleichen Frame an — einer für das '
                     + 'Segment davor, einer für danach' }));
        this.menue.ziel.appendChild(this.menue.spureintrag(
            'Lichteigenschaft (einzel)',
            () => fn.addLightKeyframe(this.menue.nummer, this.menue.bild)));
        this.menue.ziel.appendChild(this._vorgabenordner());
    }

    _vorgabenordner() {
        const kopf = this.menue.eintrag({
            symbol: 'fa-star',
            farbe: this.menue.constructor.SYMBOLE.light[1],
            text: 'Presets', rechts: '<i class="fas fa-caret-right"></i>',
            klasse: 'has-submenu',
        }, null);
        const unter = this.menue.untermenue(kopf);
        unter.innerHTML = '<div class="ctx-submenu-empty">Lade...</div>';
        this._nachladen(unter);
        return kopf;
    }

    async _nachladen(unter) {
        let vorgaben;
        try {
            vorgaben = await (fn.fetchTheatrePresets?.()
                ?? fetch(Menuelicht.ENDPUNKT)
                    .then(antwort => antwort.json())
                    .then(daten => daten.presets || []));
        } catch (fehler) {
            unter.innerHTML =
                '<div class="ctx-submenu-empty">Fehler beim Laden</div>';
            Protokoll.warnung('bvh_studio', 'Licht-Vorgaben nicht ladbar:', fehler);
            return;
        }
        if (!vorgaben?.length) {
            unter.innerHTML = '<div class="ctx-submenu-empty">Keine Presets</div>';
            return;
        }
        unter.innerHTML = '';
        for (const vorgabe of vorgaben) unter.appendChild(this._zeile(vorgabe));
    }

    _zeile(vorgabe) {
        return this.menue.eintrag({
            symbol: 'fa-lightbulb',
            farbe: this.menue.constructor.SYMBOLE.light[1],
            text: `<span>${vorgabe.label}</span>`,
            rechts: vorgabe.lightCount + 'x',
            titel: (vorgabe.description || '')
                + '\n\nFügt Preset-Lichter HINZU (existierende bleiben erhalten).',
        }, () => fn.applyTheatrePresetAdditive?.(vorgabe.name, this.menue.bild));
    }
}
