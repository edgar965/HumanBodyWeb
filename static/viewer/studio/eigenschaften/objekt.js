/**
 * Objekteigenschaften — Maske und Bedienung eines importierten 3D-Objekts
 * (scene_object/custom).
 *
 * Aus properties.js herausgeloest (Umbau 16.08.2026). Das Ersetzen von Textur,
 * MTL und Mesh liegt in objekt_dateien.js.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { Objektdateien } from './objekt_dateien.js';
import { Maskenbausteine as M } from './bausteine.js';

/** Hoechstzahl gezeigter Texturvorschauen. */
const MAX_VORSCHAU = 4;

export class Objekteigenschaften {
    static maske(track) {
        const m = track.mesh;
        const pos = m?.position || { x: 0, y: 0, z: 0 };
        const rot = m?.rotation || { x: 0, y: 0, z: 0 };
        const scl = m?.scale || { x: 1, y: 1, z: 1 };
        const zeile = (id, wert, schritt) =>
            `<div class="prop-row"><label>${id[id.length - 1].toUpperCase()}:</label><input type="number"
                step="${schritt}" value="${wert}" id="prop-obj-${id}"></div>`;
        const lage = ['x', 'y', 'z'].map(a => zeile('p' + a, pos[a].toFixed(2), 0.1)).join('');
        const drehung = ['x', 'y', 'z'].map(a =>
            zeile('r' + a, (rot[a] * 180 / Math.PI).toFixed(1), 1)).join('');

        return `<div class="prop-group">
            <div class="prop-row"><label>Typ:</label><span
                class="marke-akzent">3D-Objekt (${track.objectExt || '?'})</span></div>
            <div class="prop-row"><label>Tönung:</label><input type="color" value="${track.objectTint || '#ffffff'}"
                id="prop-obj-tint"></div>
            <h3 class="gruppentitel">Position</h3>${lage}
            <h3 class="gruppentitel">Rotation (Grad)</h3>${drehung}
            <h3 class="gruppentitel">Größe</h3>
            <div class="prop-row"><label>Scale:</label><input type="number" step="0.05" min="0.01" max="100"
                value="${scl.x.toFixed(2)}" id="prop-obj-scale"></div>
            <div class="prop-row"><label>Modus:</label>
                <select id="prop-obj-gizmo"><option value="translate" selected>Verschieben</option><option
                    value="rotate">Rotieren</option><option value="scale">Skalieren</option></select>
            </div>
            <h3 class="studio-abschnittstitel">Material</h3>
            ${Objekteigenschaften._texturvorschau(track)}
            <div class="prop-row"><label>Textur:</label>
                <button id="prop-obj-tex-replace" class="knopf-akzent-schmal"><i
                    class="fas fa-image"></i> Ersetzen…</button>
                <button id="prop-obj-tex-remove" class="knopf-schmal-grau">Entfernen</button>
            </div>
            <div class="prop-row"><label>MTL:</label>
                <button id="prop-obj-mtl-replace" class="knopf-akzent-schmal"><i
                    class="fas fa-file-code"></i> Ersetzen…</button>
                ${track.objectMtlUrl
                    ? `<span class="dateiname-hinweis">${track.objectMtlUrl.split('/').pop()}</span>`
                    : '<span class="dateiname-fehlt">fehlt</span>'}
            </div>
            <div class="prop-row"><label>Mesh:</label>
                <button id="prop-obj-mesh-replace" class="knopf-akzent-schmal"><i
                    class="fas fa-cube"></i> Ersetzen…</button>
                ${track.objectUrl ? `<span class="dateiname-hinweis">${track.objectUrl.split('/').pop()}</span>` : ''}
            </div>
            <div
                class="fussnote">Tipp: Beim Import OBJ + MTL + alle Texturen gleichzeitig auswählen (Ctrl+Klick im
                    Datei-Dialog). Sonst werden sie nicht im selben Bundle-Ordner abgelegt und MTL→Textur-Referenzen
                        schlagen fehl.</div>
        </div>`;
    }

    /** Zeigt die Texturen, die tatsaechlich am Netz haengen (.map.image.src). */
    static _texturvorschau(track) {
        const aktiv = new Set();
        track.mesh?.traverse?.(o => {
            if (!o.isMesh || !o.material) return;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            for (const m of mats) {
                const src = m.map?.image?.src || m.map?.source?.data?.src;
                if (src) aktiv.add(src);
            }
        });
        if (aktiv.size === 0) {
            return '<div class="prop-row texturfehler">'
                 + '<label>&nbsp;</label>Keine Textur geladen</div>';
        }
        return Array.from(aktiv).slice(0, MAX_VORSCHAU).map(src => `
            <div class="prop-row zeile-oben">
                <label>Aktiv:</label>
                <div class="texturspalte">
                    <img src="${src}" class="texturbild" />
                    <span class="texturname">${(src.split('/').pop() || '?').slice(0, 40)}</span>
                </div>
            </div>`).join('');
    }

    static binden(track) {
        M.an('prop-obj-tint', 'input', (e) => fn.setObjectTint?.(track, e.target.value));
        for (const achse of ['x', 'y', 'z']) {
            M.an(`prop-obj-p${achse}`, 'change', (e) => {
                track.mesh.position[achse] = parseFloat(e.target.value) || 0;
            });
            M.an(`prop-obj-r${achse}`, 'change', (e) => {
                track.mesh.rotation[achse] = (parseFloat(e.target.value) || 0) * Math.PI / 180;
            });
        }
        M.an('prop-obj-scale', 'change', (e) => {
            track.mesh.scale.setScalar(Math.max(0.01, parseFloat(e.target.value) || 1));
        });
        M.an('prop-obj-gizmo', 'change', (e) => fn.setTransformMode?.(e.target.value));
        M.an('prop-obj-tex-replace', 'click', () => Objektdateien.texturErsetzen(track));
        M.an('prop-obj-tex-remove', 'click', () => Objektdateien.texturEntfernen(track));
        M.an('prop-obj-mtl-replace', 'click', () => Objektdateien.mtlErsetzen(track));
        M.an('prop-obj-mesh-replace', 'click', () => Objektdateien.meshErsetzen(track));
    }
}
