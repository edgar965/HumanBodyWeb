import { getSkinMat, syncSkinUI } from './scene_settings.js';

/**
 * Hautbedienung — Farbe, Rauheit und Metallgrad der Haut auf der Viewer-Seite.
 *
 * Aus viewer/morphs.js herausgeloest (Umbau 16.08.2026): Rauheit und
 * Metallgrad waren zwei gleich gebaute Blöcke (Regler holen, Anzeige holen,
 * Wert durch 100, ins Material) — jetzt eine Tabelle.
 */
export class Hautbedienung {

    /** Regler: Kennung, Materialfeld, Vorgabestellung in Prozent. */
    static REGLER = [
        ['skin-roughness-viewer', 'roughness', 55],
        ['skin-metalness-viewer', 'metalness', 0],
    ];

    static verdrahten() {
        document.getElementById('skin-color-viewer')
            ?.addEventListener('input', ereignis => {
                const material = getSkinMat();
                if (material) material.color.set(ereignis.target.value);
            });
        for (const [id, feld] of Hautbedienung.REGLER) {
            Hautbedienung._regler(id, feld);
        }
    }

    static _regler(id, feld) {
        const regler = document.getElementById(id);
        if (!regler) return;
        const anzeige = document.getElementById(id + '-val');
        regler.addEventListener('input', () => {
            const wert = parseFloat(regler.value) / 100;
            if (anzeige) anzeige.textContent = wert.toFixed(2);
            const material = getSkinMat();
            if (material) material[feld] = wert;
        });
    }

    /** Regler auf die Vorgabe stellen — beim Zurücksetzen. */
    static zuruecksetzen(material) {
        for (const [id, feld, vorgabe] of Hautbedienung.REGLER) {
            const regler = document.getElementById(id);
            if (!regler) continue;
            regler.value = vorgabe;
            const anzeige = document.getElementById(id + '-val');
            if (anzeige) anzeige.textContent = (vorgabe / 100).toFixed(2);
            if (material) material[feld] = vorgabe / 100;
        }
        if (material) syncSkinUI(material);
    }
}
