import { state } from './state.js';
import { _sliderVal } from './utils.js';

/**
 * Materialregler — Rauheit, Metallgrad und Farbe eines gewählten Teilnetzes.
 *
 * Umbau 16.08.2026: Dieses Muster stand SIEBEN Mal im Projekt, jedes Mal als
 * eigener Block:
 *
 *     const el = document.getElementById('<vorsilbe>-roughness');
 *     if (el) el.addEventListener('input', () => {
 *         if (state._syncingSliders) return;
 *         const sel = _selected…Mesh();
 *         if (sel) sel.mesh.material.roughness = _sliderVal('…') / 100;
 *     });
 *
 * — dreimal im Kleider-Reiter (`kleider-roughness/-metalness/-color`), viermal
 * im MakeHuman-Reiter (dort zusätzlich Deckkraft). `_syncingSliders` schützt
 * davor, dass das Nachziehen der Anzeige selbst eine Änderung auslöst.
 */
export class Materialregler {

    /**
     * @param vorsilbe  Kennungs-Vorsilbe der Regler, etwa 'kleider' oder 'mh'
     * @param gewaehlt  () => { mesh } | null
     */
    constructor(vorsilbe, gewaehlt) {
        this.vorsilbe = vorsilbe;
        this.gewaehlt = gewaehlt;
    }

    /** Rauheit, Metallgrad und Farbe verdrahten. */
    grundwerte() {
        this.anteil('roughness');
        this.anteil('metalness');
        this.farbe();
        return this;
    }

    /** Regler mit Wert 0..100, der als Bruch ins Material geht. */
    anteil(feld, kennung = null) {
        const id = `${this.vorsilbe}-${kennung || feld}`;
        return this.wirken(id, (material, wert) => {
            material[feld] = wert / 100;
        });
    }

    /** Deckkraft — braucht zusätzlich `transparent`, sonst bleibt sie wirkungslos. */
    deckkraft() {
        return this.wirken(`${this.vorsilbe}-opacity`, (material, wert) => {
            material.opacity = wert / 100;
            material.transparent = wert < 100;
        });
    }

    farbe() {
        const feld = document.getElementById(`${this.vorsilbe}-color`);
        feld?.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const auswahl = this.gewaehlt();
            if (auswahl) auswahl.mesh.material.color.set(feld.value);
        });
        return this;
    }

    wirken(id, tun) {
        document.getElementById(id)?.addEventListener('input', () => {
            if (state._syncingSliders) return;
            const auswahl = this.gewaehlt();
            if (auswahl) tun(auswahl.mesh.material, _sliderVal(id));
        });
        return this;
    }
}
