/**
 * Bodeneigenschaften — Maske und Bedienung der Bodenspur (scene_object/floor).
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026).
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Maskenbausteine as M } from './bausteine.js';
import { Schaltknopf } from '../schaltknopf.js';
import { Auswahlfeld } from '../../gemeinsam/auswahlfeld.js';

/** Kleinste zulaessige Kantenlaenge in Metern. */
const MINDESTMASS = 0.2;

export class Bodeneigenschaften {
    static maske(track) {
        const mitte = track.mesh?.position || { x: 0, y: 0, z: 0 };
        // Legacy: floorSize (quadratisch) → Vorgabe fuer Breite/Laenge
        const w = track.floorWidth ?? track.floorSize ?? 6;
        const l = track.floorLength ?? track.floorSize ?? 6;
        const cx = mitte.x ?? 0, cz = mitte.z ?? 0;
        const raster = state.gridVisible !== false;
        const kante = (id, wert, achse) =>
            `<div class="prop-row"><label>${id.startsWith('s') ? 'Start' : 'Ende'} ${achse}:</label><input
                type="number" value="${wert}" id="prop-floor-${id}" step="0.1"> m</div>`;

        return `<div class="prop-group">
            <div class="prop-row"><label>Typ:</label><span class="marke-akzent">Boden (Szene)</span></div>
            <div class="prop-row"><label>Farbe:</label><input type="color" value="${track.floorColor || '#3a3a4a'}"
                id="prop-floor-color"></div>
            <div class="prop-row"><label>Textur:</label><select id="prop-floor-texture" class="dehnen"><option
                value="">(Lade...)</option></select></div>
            <div class="prop-row"><label>Rauheit:</label><input type="number"
                value="${(track.floorRoughness ?? 0.9).toFixed(2)}" id="prop-floor-roughness" min="0" max="1" step="0.05"></div>
            <div class="prop-row"><label>Metall:</label><input type="number"
                value="${(track.floorMetalness ?? 0.05).toFixed(2)}" id="prop-floor-metalness" min="0" max="1" step="0.05"></div>
            <h3 class="gruppentitel">Abmessungen (Mittelpunkt-bezogen)</h3>
            <div class="prop-row"><label>Breite X:</label><input type="number" value="${w.toFixed(2)}"
                id="prop-floor-width" min="0.2" max="200" step="0.1"> m</div>
            <div class="prop-row"><label>Länge Z:</label><input type="number" value="${l.toFixed(2)}"
                id="prop-floor-length" min="0.2" max="200" step="0.1"> m</div>
            <h3 class="gruppentitel">Kanten-Positionen</h3>
            ${kante('sx', (cx - w / 2).toFixed(2), 'X')}
            ${kante('ex', (cx + w / 2).toFixed(2), 'X')}
            ${kante('sz', (cz - l / 2).toFixed(2), 'Z')}
            ${kante('ez', (cz + l / 2).toFixed(2), 'Z')}
            <div class="prop-row"><label>Raster:</label>
                ${Schaltknopf.bauen('prop-floor-grid', raster)}
            </div>
            <div
                class="fussnote">Breite/Länge wachsen um den aktuellen Mittelpunkt. Start/Ende-Kanten editieren
                    verschiebt nur die jeweilige Kante (Gegen-Kante bleibt fix).</div>
        </div>`;
    }

    static binden(track) {
        const material = (feld, vorgabe) => (e) => {
            track[feld] = parseFloat(e.target.value) || vorgabe;
            fn.updateFloorMaterial?.(track);
        };
        M.an('prop-floor-color', 'input', (e) => {
            track.floorColor = e.target.value;
            fn.updateFloorMaterial?.(track);
        });
        M.an('prop-floor-roughness', 'change', material('floorRoughness', 0.9));
        M.an('prop-floor-metalness', 'change', material('floorMetalness', 0.05));

        // Breite/Laenge wachsen zentriert um den aktuellen Mittelpunkt.
        M.an('prop-floor-width', 'change', (e) => {
            const w = Math.max(MINDESTMASS, parseFloat(e.target.value) || 6);
            fn.setFloorGeometry?.(track, w, track.floorLength ?? track.floorSize ?? 6);
            fn.updateProperties();
        });
        M.an('prop-floor-length', 'change', (e) => {
            const l = Math.max(MINDESTMASS, parseFloat(e.target.value) || 6);
            fn.setFloorGeometry?.(track, track.floorWidth ?? track.floorSize ?? 6, l);
            fn.updateProperties();
        });
        for (const [id, achse, seite] of [['sx', 'x', 'start'], ['ex', 'x', 'end'],
                                          ['sz', 'z', 'start'], ['ez', 'z', 'end']]) {
            M.an(`prop-floor-${id}`, 'change', (e) => Bodeneigenschaften._kanteSetzen(
                track, achse, seite, parseFloat(e.target.value) || 0));
        }
        M.an('prop-floor-grid', 'click', () => {
            state.gridVisible = state.gridVisible === false;
            state.scene?.traverse(o => {
                if (o.type === 'GridHelper' || o.isGridHelper) o.visible = state.gridVisible;
            });
            fn.updateProperties();
        });
        Bodeneigenschaften._texturlisteFuellen(track);
    }

    /**
     * Eine Kante verschieben: die Gegenkante bleibt fix, daraus ergeben sich
     * neue Kantenlaenge UND neuer Mittelpunkt.
     */
    static _kanteSetzen(track, achse, seite, wert) {
        const mitte = track.mesh.position;
        const w = track.floorWidth ?? track.floorSize ?? 6;
        const l = track.floorLength ?? track.floorSize ?? 6;
        if (achse === 'x') {
            const gegen = seite === 'start' ? mitte.x + w / 2 : mitte.x - w / 2;
            fn.setFloorGeometry?.(track, Math.max(MINDESTMASS, Math.abs(gegen - wert)),
                                  l, (wert + gegen) / 2, mitte.z);
        } else {
            const gegen = seite === 'start' ? mitte.z + l / 2 : mitte.z - l / 2;
            fn.setFloorGeometry?.(track, w,
                                  Math.max(MINDESTMASS, Math.abs(gegen - wert)),
                                  mitte.x, (wert + gegen) / 2);
        }
        fn.updateProperties();
    }

    /** Texturliste vom Server nachladen — die Maske steht da schon. */
    static _texturlisteFuellen(track) {
        const auswahl = document.getElementById('prop-floor-texture');
        if (!auswahl || !fn.getFloorTextures) return;
        fn.getFloorTextures().then(texturen => {
            auswahl.innerHTML = '';
            Auswahlfeld.fuellen(auswahl, texturen.map((t) => ({
                wert: t.url || '', text: t.label,
                gewaehlt: (track.floorTexture || 'none') === t.name,
            })));
            auswahl.addEventListener('change',
                (e) => fn.applyFloorTexture?.(track, e.target.value));
        });
    }
}
