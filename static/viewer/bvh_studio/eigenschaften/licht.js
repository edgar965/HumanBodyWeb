/**
 * Lichteigenschaften — Maske und Bedienung der Lichtspur im Eigenschaftsfeld.
 *
 * WARUM Maske und Bedienung in EINER Klasse (Umbau 16.08.2026): properties.js
 * hatte eine einzige Funktion mit 751 Zeilen, in der erst 200 Zeilen HTML
 * zusammengebaut und danach 300 Zeilen Ereignisbindungen registriert wurden. Wer
 * ein Feld aenderte, musste an zwei weit entfernten Stellen suchen — die
 * Element-Kennungen (`prop-light-penumbra`) sind die Klammer zwischen beidem.
 * Darum wird nicht nach HTML/Logik getrennt, sondern nach Fachlichkeit.
 */
import * as THREE from 'three';
import { state } from '../state.js';
import { Schaltknopf } from '../schaltknopf.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { createLightHelper } from '../spur_lichter.js';
import { Maskenbausteine as M } from './bausteine.js';

const ARTEN = [
    { v: 'spot', label: 'SpotLight' },
    { v: 'directional', label: 'Directional' },
    { v: 'point', label: 'PointLight' },
    { v: 'ambient', label: 'Ambient' },
];

export class Lichteigenschaften {
    static maske(track) {
        const L = track.light;
        const art = track.lightType || 'spot';
        const ambient = art === 'ambient';
        const lp = L?.position || { x: 0, y: 0, z: 0 };
        const tg = L?.target?.position || { x: 0, y: 0, z: 0 };
        const farbe = L ? L.color : new THREE.Color(0xffffff);
        const R = Math.round(farbe.r * 255), G = Math.round(farbe.g * 255),
              B = Math.round(farbe.b * 255);
        const auswahl = `<select id="prop-light-type" class="dehnen">${ARTEN.map(o =>
            `<option value="${o.v}" ${o.v === art ? 'selected' : ''}>${o.label}</option>`
        ).join('')}</select>`;
        const schieber = (kanal,
            wert) => `<div class="prop-row"><label>${kanal.toUpperCase()}:</label><input type="range" min="0"
                max="255" value="${wert}" id="prop-light-${kanal}" class="dehnen"><span id="prop-light-${kanal}-val"
                    class="kanalwert">${wert}</span></div>`;
        const knopf = (id, an) => Schaltknopf.bauen(id, an, true);
        const achsen = (praefix, p) => ['x', 'y', 'z'].map(a =>
            `<div class="prop-row"><label>${a.toUpperCase()}:</label><input type="number" step="0.1"
                value="${p[a].toFixed(2)}" id="prop-light-${praefix}${a}"></div>`
        ).join('');

        return `<div class="prop-group">
            <div
                class="prop-row"><label>Licht-Typ:</label>${auswahl}${track._sceneLight ? '<span class="szenenmarke">(Szene)</span>' : ''}</div>
            <div class="prop-row"><label>Farbe:</label><input type="color"
                value="${L ? '#' + L.color.getHexString() : '#ffffff'}" id="prop-light-color"></div>
            ${schieber('r', R)}${schieber('g', G)}${schieber('b', B)}
            <div class="prop-row"><label>Intensität:</label><input type="number" value="${L?.intensity || 2}"
                id="prop-light-intensity" min="0" max="20" step="0.1"></div>
            ${ambient ? '' : `<div class="prop-row"><label>Winkel:</label><input type="number"
                value="${((L?.angle ?? Math.PI / 6) * 180 / Math.PI).toFixed(1)}" id="prop-light-angle" min="1" max="170" step="1"> °</div>
            <div class="prop-row"><label>Penumbra:</label><input type="number" value="${(L?.penumbra ?? 0.3).toFixed(2)}" id="prop-light-penumbra" min="0" max="1" step="0.05"></div>
            <div class="prop-row"><label>Reichweite:</label><input type="number" value="${(L?.distance ?? 50).toFixed(1)}" id="prop-light-distance" min="0" max="200" step="1"></div>`}
            ${!track.lightHelper ? '' : `
            <div class="prop-row"><label>Lichtkegel:</label>${knopf('prop-light-cone-toggle', track.coneVisible
                !== false)}</div>
            <div class="prop-row"><label>Helferlinien:</label>${knopf('prop-light-lines-toggle',
                track.lightVisible)}</div>`}
            ${ambient ? '' : `<h3 class="gruppentitel">Position</h3>${achsen('', lp)}`}
            ${!L?.target ? '' : `<h3 class="gruppentitel">Ziel (Blickrichtung)</h3>${achsen('t', tg)}`}
            <div class="abstand-6">
                <button id="prop-light-add-kf" class="knopf-akzent"><i class="fas fa-key"></i> Keyframe setzen</button>
            </div>
            ${!track._sceneLight ? '' : '<div class="fussnote">Szenen-Licht — wird immer geladen, kann nicht gelöscht werden.</div>'}
        </div>`;
    }

    static binden(track) {
        const nachziehen = () => {
            if (!track.light) return;
            track.light.target?.updateMatrixWorld();
            track.lightHelper?.update?.();
        };

        M.an('prop-light-type', 'change',
           (e) => Lichteigenschaften.artWechseln(track, e.target.value));
        M.an('prop-light-color', 'input', (e) => {
            if (!track.light) return;
            track.light.color.set(e.target.value);
            Lichteigenschaften._reglerNachziehen(track);
            nachziehen();
        });
        for (const kanal of ['r', 'g', 'b']) {
            M.an(`prop-light-${kanal}`, 'input', (e) => {
                if (!track.light) return;
                track.light.color[kanal] = parseInt(e.target.value) / 255;
                document.getElementById(`prop-light-${kanal}-val`).textContent = e.target.value;
                const feld = document.getElementById('prop-light-color');
                if (feld) feld.value = '#' + track.light.color.getHexString();
                nachziehen();
            });
        }
        const zahl = (id, feld, umrechnen) => M.an(id, 'change', (e) => {
            if (!track.light) return;
            track.light[feld] = umrechnen(parseFloat(e.target.value));
            nachziehen();
        });
        zahl('prop-light-intensity', 'intensity', v => v || 2);
        zahl('prop-light-angle', 'angle', v => (v || 30) * Math.PI / 180);
        zahl('prop-light-penumbra', 'penumbra', v => Math.max(0, Math.min(1, v || 0)));
        zahl('prop-light-distance', 'distance', v => v || 50);

        M.an('prop-light-cone-toggle', 'click', () => {
            track.coneVisible = !(track.coneVisible !== false);  // undefined→true→false
            fn.updateProperties();
        });
        M.an('prop-light-lines-toggle', 'click', () => {
            track.lightVisible = !track.lightVisible;
            fn.updateProperties();
        });
        for (const achse of ['x', 'y', 'z']) {
            M.an(`prop-light-${achse}`, 'change', (e) => {
                if (!track.light) return;
                track.light.position[achse] = parseFloat(e.target.value) || 0;
                nachziehen();
            });
            M.an(`prop-light-t${achse}`, 'change', (e) => {
                if (!track.light?.target) return;
                track.light.target.position[achse] = parseFloat(e.target.value) || 0;
                nachziehen();
            });
        }
        M.an('prop-light-add-kf', 'click',
           () => fn.addLightKeyframe(state.selectedTrackIdx));
    }

    /** Farbwaehler und RGB-Schieber auf den Lichtwert nachziehen. */
    static _reglerNachziehen(track) {
        if (!track.light) return;
        const c = track.light.color;
        for (const kanal of ['r', 'g', 'b']) {
            const wert = Math.round(c[kanal] * 255);
            const regler = document.getElementById(`prop-light-${kanal}`);
            if (regler) regler.value = wert;
            const zahl = document.getElementById(`prop-light-${kanal}-val`);
            if (zahl) zahl.textContent = wert;
        }
        const feld = document.getElementById('prop-light-color');
        if (feld) feld.value = '#' + c.getHexString();
    }

    /**
     * Three.js-Lichtart einer Spur tauschen und den Helfer neu bauen.
     * Position, Farbe, Intensitaet, Winkel, Penumbra und Reichweite bleiben.
     */
    static artWechseln(track, neueArt) {
        const alt = track.light;
        if (!alt) return;
        const pos = alt.position?.clone?.();
        const ziel = alt.target?.position?.clone?.();
        const farbe = alt.color.clone();
        const intensitaet = alt.intensity ?? 3;
        const winkel = alt.angle ?? Math.PI / 6;
        const penumbra = alt.penumbra ?? 0.3;
        const reichweite = alt.distance ?? 50;

        if (alt.target) state.scene.remove(alt.target);
        state.scene.remove(alt);
        alt.dispose?.();
        if (track.lightHelper) {
            state.scene.remove(track.lightHelper);
            track.lightHelper.traverse?.(o => {
                o.geometry?.dispose?.();
                o.material?.dispose?.();
            });
            track.lightHelper = null;
        }

        let neu;
        if (neueArt === 'spot') {
            neu = new THREE.SpotLight(farbe, intensitaet, reichweite, winkel, penumbra, 1);
        } else if (neueArt === 'directional') {
            neu = new THREE.DirectionalLight(farbe, intensitaet);
        } else if (neueArt === 'point') {
            neu = new THREE.PointLight(farbe, intensitaet, reichweite);
        } else if (neueArt === 'ambient') {
            neu = new THREE.AmbientLight(farbe, intensitaet);
        } else {
            return;
        }
        if (pos && neu.position) neu.position.copy(pos);
        if (ziel && neu.target) {
            neu.target.position.copy(ziel);
            state.scene.add(neu.target);
        }
        state.scene.add(neu);
        track.light = neu;
        track.lightType = neueArt;
        track.lightHelper = createLightHelper(neu);
        if (track.lightHelper) state.scene.add(track.lightHelper);
        fn.syncLightVisibility?.();
        fn.updateProperties();
    }
}
