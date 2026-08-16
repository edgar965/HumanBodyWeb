import { state } from './state.js';
import { loadBVH } from './bvh_animation.js';
import { reloadForPreset } from './presets.js';
import { modellwahlFuellen } from './bauteile.js';

/**
 * Kopfbedienung — die Bedienelemente in der Kopfzeile der Ergebnisseite:
 * Modellauswahl, Fußkorrektur, Delta-Normalisierung, Haar ein/aus.
 *
 * Aus `initResultCharacter()` herausgeloest (Umbau 16.08.2026). Drei der vier
 * Elemente lösen dasselbe aus — die BVH neu laden —, standen aber als drei
 * einzeln geschriebene Blöcke da.
 */
export class Kopfbedienung {

    async verdrahten(modellwahlId) {
        await this.modellwahl(modellwahlId);
        this._neuLaden('footCorrection', 'change', feld => {
            state.enableFootCorrection = feld.checked;
        });
        this._neuLaden('deltaNormSelect', 'change', feld => {
            // 'auto' heißt: die BVH-Erkennung entscheidet selbst.
            state.deltaNormMode = feld.value === 'auto' ? undefined
                                                       : feld.value === '1';
        });
        this.haarknopf();
        return this;
    }

    /**
     * Element, dessen Änderung den Zustand setzt und die BVH neu lädt. Neu
     * geladen wird nur, wenn schon ein Skelett steht — sonst gäbe es nichts,
     * worauf die Animation wirken könnte.
     */
    _neuLaden(id, ereignis, setzen) {
        const feld = document.getElementById(id);
        feld?.addEventListener(ereignis, () => {
            setzen(feld);
            if (state.isSkinned) loadBVH();
        });
    }

    /** Modellauswahl der Kopfzeile — dieselbe Liste wie im Seitenfeld. */
    async modellwahl(id) {
        if (!id) return;
        await modellwahlFuellen(document.getElementById(id),
                                name => reloadForPreset(name), true);
    }

    haarknopf() {
        const knopf = document.getElementById('btnToggleHair');
        knopf?.addEventListener('click', () => {
            if (!state.hairMesh) return;
            state.hairMesh.visible = !state.hairMesh.visible;
            knopf.classList.toggle('active', state.hairMesh.visible);
        });
    }
}
