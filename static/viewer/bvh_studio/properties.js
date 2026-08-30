/**
 * Eigenschaftsfeld des BVH-Studios — baut die Maske zur ausgewaehlten Spur bzw.
 * zum ausgewaehlten Clip und haengt die Bedienung daran.
 *
 * WARUM diese Datei jetzt klein ist (Umbau 16.08.2026): `updateProperties` war
 * EINE Funktion mit 751 Zeilen — erst 200 Zeilen HTML fuer sechs Spurarten, dann
 * 300 Zeilen Ereignisbindungen fuer dieselben sechs. Aufgeteilt ist sie nach
 * Fachlichkeit, nicht nach HTML/Logik: Jede Klasse bringt `maske(track)` und
 * `binden(track)` mit, weil die Element-Kennungen beides verbinden.
 *
 *   eigenschaften/licht.js    Lichtspur (inkl. Lichtart wechseln)
 *   eigenschaften/boden.js    Bodenspur
 *   eigenschaften/objekt.js   importiertes 3D-Objekt
 *   eigenschaften/klip.js     ausgewaehlter Clip / Schluesselbild
 */
import { state, TRACK_ICONS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Lichteigenschaften } from './eigenschaften/licht.js';
import { Bodeneigenschaften } from './eigenschaften/boden.js';
import { Objekteigenschaften } from './eigenschaften/objekt.js';
import { Klipeigenschaften } from './eigenschaften/klip.js';
import { Maskenbausteine as M } from './eigenschaften/bausteine.js';
import { Schaltknopf } from './schaltknopf.js';

export class Eigenschaftsfeld {
    static neuzeichnen() {
        const feld = document.getElementById('props-content');
        if (!feld) return;
        const spuren = state.project.tracks;
        if (state.selectedTrackIdx < 0 || state.selectedTrackIdx >= spuren.length) {
            feld.innerHTML = '<div class="gedaempft-klein">'
                           + 'Animation oder Clip auswählen</div>';
            return;
        }
        const track = spuren[state.selectedTrackIdx];
        const clip = state.selectedClipIdx >= 0 ? track.clips[state.selectedClipIdx] : null;

        feld.innerHTML = Eigenschaftsfeld._kopf(track)
                       + Eigenschaftsfeld._spurmaske(track)
                       + Eigenschaftsfeld._klipliste(track)
                       + (clip ? Klipeigenschaften.maske(clip) : '');

        Eigenschaftsfeld._kopfBinden(track);
        Eigenschaftsfeld._spurBinden(track);
        if (clip) Klipeigenschaften.binden(track, clip);
    }

    static _kopf(track) {
        const symbol = TRACK_ICONS[track.type] || 'fa-running';
        let html = `<div class="prop-group">
        <h3 class="spurtitel"><i class="fas ${symbol}"></i> ${track.name}</h3>
        <div class="prop-row"><label>Name:</label><input type="text" value="${track.name}" id="prop-track-name"></div>`;
        if (track.type === 'light' || track.type === 'scene_object') {
            // Licht und Szenenobjekt: An/Aus statt "Muted"
            const an = !track.muted;
            const id = track.type === 'light' ? 'prop-light-toggle' : 'prop-obj-toggle';
            html += `<div class="prop-row"><label>Sichtbar:</label>
            ${Schaltknopf.bauen(id, an)}
        </div>`;
        } else {
            html += `<div class="prop-row"><label>Muted:</label><input type="checkbox" ${track.muted ? 'checked' : ''}
                id="prop-track-mute"></div>`;
        }
        return html + '</div>';
    }

    static _spurmaske(track) {
        if (track.type === 'bvh') {
            return `<div class="prop-group">
            <div class="prop-row"><label>Modell:</label><span class="marke-akzent">${track.preset}</span></div>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${track.position[0]}"
                id="prop-pos-x"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${track.position[2]}"
                id="prop-pos-z"></div>
        </div>`;
        }
        if (track.type === 'camera') {
            return `<div class="prop-group">
            <div class="prop-row"><label>Aktiv:</label><input type="checkbox" ${track.cameraActive ? 'checked' : ''}
                id="prop-cam-active"></div>
            <div class="abstand-6">
                <button id="prop-cam-add-kf" class="knopf-akzent"><i
                    class="fas fa-key"></i> Keyframe setzen (K)</button>
            </div>
            <div class="fussnote">Setzt aktuelle Kamera-Position als Keyframe am Playhead.</div>
        </div>`;
        }
        if (track.type === 'light') return Lichteigenschaften.maske(track);
        if (track.type === 'model') {
            const verbunden = state.project.getLinkedAnimation(track);
            return `<div class="prop-group">
            <div class="prop-row"><label>Verknüpft:</label><span
                class="marke-akzent">${verbunden ? verbunden.name : '(keiner)'}</span></div>
        </div>`;
        }
        if (track.type === 'audio') {
            return `<div class="prop-group">
            <div class="abstand-unten-6">
                <button id="prop-audio-load" class="knopf-akzent"><i
                    class="fas fa-folder-open"></i> Audio laden</button>
            </div>
        </div>`;
        }
        if (track.type === 'scene_object') {
            return track.subtype === 'floor' ? Bodeneigenschaften.maske(track)
                                             : Objekteigenschaften.maske(track);
        }
        return '';
    }

    static _klipliste(track) {
        const titel = (track.type === 'camera' || track.type === 'light')
            ? 'Keyframes' : 'Clips';
        const eintraege = track.clips.map((c, i) => {
            const dauer = (c.type === 'camera_kf' || c.type === 'light_kf')
                ? `F${c.startFrame}` : `${c.duration.toFixed(1)}s`;
            const gewaehlt = i === state.selectedClipIdx;
            return `<div class="prop-clip-item${gewaehlt ? ' gewaehlt' : ''}"
                data-clip="${i}">${c.name} (${dauer})</div>`;
        }).join('');
        return `<div class="prop-group">
        <h3 class="clipliste-titel">${titel} (${track.clips.length})</h3>
        ${eintraege}
    </div>`;
    }

    static _kopfBinden(track) {
        M.an('prop-track-name', 'change', (e) => {
            track.name = e.target.value;
            fn.updateTrackHeaders();
        });
        M.an('prop-track-mute', 'change', (e) => { track.muted = e.target.checked; });
        M.an('prop-light-toggle', 'click', () => {
            track.muted = !track.muted;
            if (track.light) {
                track.light.visible = !track.muted;
                if (track.lightHelper) {
                    track.lightHelper.visible = !track.muted && track.lightVisible;
                }
            }
            fn.updateProperties();   // neu zeichnen: Beschriftung und Farbe des Knopfs
        });
        M.an('prop-obj-toggle', 'click', () => {
            track.muted = !track.muted;
            if (track.mesh) track.mesh.visible = !track.muted;
            fn.updateProperties();
        });
        document.querySelectorAll('.prop-clip-item').forEach(el => {
            el.addEventListener('click', () => {
                state.selectedClipIdx = parseInt(el.dataset.clip);
                fn.updateProperties();
                fn.renderTimeline();
            });
        });
    }

    static _spurBinden(track) {
        if (track.type === 'bvh') {
            for (const [id, i] of [['prop-pos-x', 0], ['prop-pos-z', 2]]) {
                M.an(id, 'change', (e) => {
                    track.position[i] = parseFloat(e.target.value) || 0;
                    track.group.position[i === 0 ? 'x' : 'z'] = track.position[i];
                });
            }
        } else if (track.type === 'camera') {
            M.an('prop-cam-active', 'change', (e) => { track.cameraActive = e.target.checked; });
            M.an('prop-cam-add-kf', 'click',
               () => fn.addCameraKeyframe(state.selectedTrackIdx));
        } else if (track.type === 'light') {
            Lichteigenschaften.binden(track);
        } else if (track.type === 'audio') {
            M.an('prop-audio-load', 'click', () => fn.loadAudioFile(state.selectedTrackIdx));
        } else if (track.type === 'scene_object') {
            if (track.subtype === 'floor') Bodeneigenschaften.binden(track);
            else if (track.mesh) Objekteigenschaften.binden(track);
        }
    }

    /** Reiter des Eigenschaftsfelds umschalten (Eigenschaften/Tools/Export). */
    static reiterWechseln(name) {
        document.querySelectorAll('.props-tab')
            .forEach(t => t.classList.toggle('active', t.dataset.tab === name));
        document.querySelectorAll('.props-tab-content')
            .forEach(c => c.classList.toggle('active', c.id === `props-tab-${name}`));
    }
}

fn.updateProperties = Eigenschaftsfeld.neuzeichnen;
fn.switchPropsTab = Eigenschaftsfeld.reiterWechseln;
