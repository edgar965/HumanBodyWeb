import * as THREE from 'three';
import { state } from './state.js';
import { base64ToFloat32, base64ToUint32 } from './utils.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Smpllicht } from './smpl_licht.js';
import { Smpleinstellungen } from './smpl_einstellungen.js';

/**
 * Smplkoerper — der SMPL-Körper des Reiters, seine zehn Formregler und
 * seine gespeicherten Einstellungen.
 *
 * Herausgelöst aus `smpl.js` (393 Zeilen). Zwei Dinge sind wichtig:
 *
 * 1. **Reglerbewegungen werden gesammelt** (`Zeiten.SAMMELN_MS`). Jeder Zwischen-
 *    schritt wäre sonst eine eigene Serveranfrage für ein 10.475-Punkte-Netz.
 * 2. **Das Netz wird nur EINMAL gebaut.** Danach werden nur noch die Punkte und
 *    Normalen überschrieben — ein neues Netz je Reglerbewegung ließe den alten
 *    Grafikspeicher liegen und würde die Materialeinstellungen verwerfen.
 */
export class Smplkoerper {

    static FORMNAMEN = ['Height', 'Weight', 'Proportions', 'Torso', 'Chest',
                        'Hips', 'Waist', 'Limbs', 'Arms', 'Legs'];
    /** Unter dieser Auslenkung gilt ein Formwert als „nicht gesetzt". */
    static SCHWELLE = 0.005;
    static ERSATZFARBE = 0x88aaff;

    static _sammler = null;

    // --------------------------------------------------------------- Ablesen

    static formwerte() {
        const werte = [];
        document.querySelectorAll('.smpl-beta-slider').forEach(regler => {
            werte[parseInt(regler.dataset.index)] = regler.value / 100;
        });
        return werte;
    }

    static geschlecht() {
        return document.getElementById('smpl-body-gender')?.value || 'female';
    }

    // ----------------------------------------------------------------- Aufbau

    static async aufbauen() {
        if (!document.getElementById('smpl-body-panel')) return;
        Smplkoerper._formreglerBinden();
        Smplkoerper._werkstoffBinden();
        await Smplkoerper.einstellungenLaden();
        Smpllicht.bedienungBinden();
        document.getElementById('smpl-save-settings')
            ?.addEventListener('click', () => Smplkoerper.einstellungenSpeichern());
        Smplkoerper.laden();
    }

    static _formreglerBinden() {
        const regler = document.querySelectorAll('.smpl-beta-slider');
        const anzeigen = document.querySelectorAll('.smpl-beta-val');
        regler.forEach((einer, i) => {
            einer.addEventListener('input', () => {
                anzeigen[i].textContent = (einer.value / 100).toFixed(2);
                Smplkoerper._sammeln();
            });
        });
        document.getElementById('smpl-body-gender')
            ?.addEventListener('change', () => Smplkoerper.laden());
        document.getElementById('smpl-beta-reset')?.addEventListener('click', () => {
            regler.forEach((einer, i) => {
                einer.value = 0;
                anzeigen[i].textContent = '0.00';
            });
            Smplkoerper._sammeln();
        });
    }

    /** Reglerbewegungen sammeln, damit nicht jeder Pixel ein Modell nachlaedt. */
    static _sammeln() {
        if (Smplkoerper._sammler) clearTimeout(Smplkoerper._sammler);
        Smplkoerper._sammler = setTimeout(() => {
            Smplkoerper._sammler = null;
            Smplkoerper.laden();
        }, Zeiten.SAMMELN_MS);
    }

    static _werkstoffBinden() {
        Smplkoerper._reglerBinden('smpl-body-opacity', 100,
                                  wert => { Smplkoerper._netz(n => {
                                      n.material.opacity = wert; }); },
                                  wert => wert.toFixed(2));
        const farbe = document.getElementById('smpl-body-color');
        farbe?.addEventListener('input', () => Smplkoerper._netz(
            netz => netz.material.color.set(farbe.value)));
        const gitter = document.getElementById('smpl-body-wireframe');
        gitter?.addEventListener('change', () => Smplkoerper._netz(netz => {
            netz.material.wireframe = gitter.checked;
            // Ohne `depthWrite = false` verdeckt das Gitternetz sich selbst.
            netz.material.depthWrite = !gitter.checked;
        }));
        Smplkoerper._reglerBinden('smpl-body-xoffset', 100, wert => {
            Smplkoerper._netz(netz => { netz.position.x = wert; });
            for (const netz of Object.values(state.smplGarmentMeshes)) {
                netz.position.x = wert;
            }
        }, wert => wert.toFixed(2) + ' m');
        document.getElementById('smpl-body-toggle')
            ?.addEventListener('click', () => Smplkoerper.umschalten());
    }

    static _reglerBinden(kennung, teiler, setzen, formatieren) {
        const regler = document.getElementById(kennung);
        if (!regler) return;
        regler.addEventListener('input', () => {
            const wert = regler.value / teiler;
            setzen(wert);
            const anzeige = document.getElementById(`${kennung}-val`);
            if (anzeige) anzeige.textContent = formatieren(wert);
        });
    }

    static _netz(tun) {
        if (state.smplBodyMesh) tun(state.smplBodyMesh);
    }

    static umschalten() {
        if (!state.smplBodyMesh) return;
        state.smplBodyVisible = !state.smplBodyVisible;
        state.smplBodyMesh.visible = state.smplBodyVisible;
        document.getElementById('smpl-body-toggle')
            ?.classList.toggle('active', state.smplBodyVisible);
    }

    // ------------------------------------------------------------------ Laden

    static async laden() {
        let daten;
        try {
            daten = await Serverabruf.json(
                `/api/smpl/body/?gender=${Smplkoerper.geschlecht()}`
                + `&betas=${Smplkoerper.formwerte().join(',')}`);
        } catch (fehler) {
            Protokoll.fehler('smpl', 'Körper nicht ladbar', fehler);
            return;
        }
        if (daten.error) {
            Protokoll.warnung('smpl', 'SMPL body error:', daten.error);
            return;
        }
        const punkte = base64ToFloat32(daten.vertices);
        const normalen = base64ToFloat32(daten.normals);
        if (state.smplBodyMesh) {
            Smplkoerper._auffrischen(punkte, normalen);
        } else {
            Smplkoerper._aufbauenNetz(daten, punkte, normalen);
        }
        Smplkoerper.angabenAuffrischen();
    }

    static _auffrischen(punkte, normalen) {
        const geometrie = state.smplBodyMesh.geometry;
        const stellen = geometrie.getAttribute('position');
        stellen.array.set(punkte);
        stellen.needsUpdate = true;
        const normale = geometrie.getAttribute('normal');
        normale.array.set(normalen);
        normale.needsUpdate = true;
        geometrie.computeBoundingSphere();
    }

    static _aufbauenNetz(daten, punkte, normalen) {
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geometrie.setIndex(new THREE.BufferAttribute(
            base64ToUint32(daten.faces), 1));
        geometrie.setAttribute('normal', new THREE.BufferAttribute(normalen, 3));
        const gitter = document.getElementById('smpl-body-wireframe')?.checked
            || false;
        const netz = new THREE.Mesh(geometrie, new THREE.MeshStandardMaterial({
            color: document.getElementById('smpl-body-color')?.value
                ?? Smplkoerper.ERSATZFARBE,
            transparent: true,
            opacity: Smplkoerper._reglerwert('smpl-body-opacity', 100, 1.0),
            wireframe: gitter, side: THREE.DoubleSide, depthWrite: !gitter,
        }));
        netz.name = 'smpl_body';
        netz.rotation.y = Math.PI;      // der Körper schaut sonst nach hinten
        netz.position.x = Smplkoerper._reglerwert('smpl-body-xoffset', 100, 1.0);
        state.smplBodyMesh = netz;
        state.smplBodyVisible = true;
        state.scene.add(netz);
        document.getElementById('smpl-body-toggle')?.classList.add('active');
    }

    static _reglerwert(kennung, teiler, ersatz) {
        const regler = document.getElementById(kennung);
        return regler ? regler.value / teiler : ersatz;
    }

    /** Die Zeile unter dem Körper: Geschlecht, Netzgröße, gesetzte Formwerte. */
    static angabenAuffrischen() {
        const abschnitt = document.getElementById('smpl-body-info-section');
        const zeile = document.getElementById('smpl-body-info');
        if (!abschnitt || !zeile) return;
        if (!state.smplBodyMesh) {
            abschnitt.style.display = 'none';
            return;
        }
        abschnitt.style.display = '';
        const geometrie = state.smplBodyMesh.geometry;
        const punkte = geometrie.getAttribute('position').count;
        const flaechen = geometrie.index ? geometrie.index.count / 3 : 0;
        zeile.innerHTML = `Gender: <b>${Smplkoerper.geschlecht()}</b> | `
            + `Vertices: <b>${punkte.toLocaleString()}</b> | `
            + `Faces: <b>${flaechen.toLocaleString()}</b><br>`
            + Smplkoerper._formtext();
    }

    static _formtext() {
        const gesetzt = Smplkoerper.formwerte()
            .map((wert, i) => Math.abs(wert) > Smplkoerper.SCHWELLE
                ? `${Smplkoerper.FORMNAMEN[i]}=${wert.toFixed(2)}` : null)
            .filter(Boolean);
        return gesetzt.length ? gesetzt.join(', ') : 'Default shape';
    }

    // ---------------------------------------------------------- Einstellungen

    static async einstellungenLaden() {
        return Smpleinstellungen.laden(werte => Smplkoerper._formwerteSetzen(werte));
    }

    static _formwerteSetzen(werte) {
        if (!werte || werte.length !== Smplkoerper.FORMNAMEN.length) return;
        const regler = document.querySelectorAll('.smpl-beta-slider');
        const anzeigen = document.querySelectorAll('.smpl-beta-val');
        regler.forEach((einer, i) => {
            einer.value = Math.round(werte[i] * 100);
            anzeigen[i].textContent = werte[i].toFixed(2);
        });
    }

    /** Der Stand, der gespeichert wird — Körper plus komplette Szene. */
    static einstellungenSpeichern() {
        return Smpleinstellungen.speichern({
            gender: Smplkoerper.geschlecht(),
            betas: Smplkoerper.formwerte(),
            opacity: Smplkoerper._reglerwert('smpl-body-opacity', 100, 1.0),
            color: document.getElementById('smpl-body-color')?.value || '#88aaff',
            wireframe: document.getElementById('smpl-body-wireframe')?.checked
                || false,
            xoffset: Smplkoerper._reglerwert('smpl-body-xoffset', 100, 1.0),
            scene: Smpllicht.einstellungen(),
        });
    }
}
