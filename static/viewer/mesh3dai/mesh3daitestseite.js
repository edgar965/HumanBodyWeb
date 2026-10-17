/**
 * Mesh3daitestseite — die Seite EINES Tests von Mesh3D-AI (16.10.2026, Reiter „Test“: Netze ohne Trainingsdaten).
 * Edgar: „darin auch eine Jobliste, aber nur Mesh und Ausgabe … testen, wie das bei Meshes ausschaut, wo wir keine Trainingsdaten haben“.
 * Zwei gekoppelte Felder (`Mesh3daiansicht`): Mesh = das Netz im Rahmen des Datensatzes (`…/netz/`, GLB mit Farbe je Punkt), Ausgabe = Ursula1 in der vorhergesagten Haltung — aus der Ruhelage mit den
 * Drehungen des Netzes gehäutet (`Mesh3daihaeutung.ausDrehungen`, dasselbe Anzeigenetz und dieselbe Hautmischung wie das Ergebnis auf der Jobseite). Der Knopf „Rig“ legt das vorhergesagte Rig über beide Felder.
 * Kein Ziel, also keine Fehlerfarben: das Rig trägt die Gruppenfarben.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { Mesh3daiflaechen } from './mesh3daiflaechen.js';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daihaeutung } from './mesh3daihaeutung.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

export class Mesh3daitestseite {
    static async starten(wurzel) {
        const seite = new Mesh3daitestseite(wurzel);
        window.__mesh3daitest = seite;
        await seite.laden();
        return seite;
    }

    constructor(wurzel) {
        this.wurzel = wurzel;
        this.kennung = wurzel.dataset.kennung;
        this.rig = true;
        this.daten = null;
        this.netz = null;          // das Netz des Tests (GLB-Szene)
        this.figur = null;         // Ursula1 in der vorhergesagten Haltung
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = ['eingabe', 'ausgabe'].map(art => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="${art}"]`), art, zeichner, KAMERA));
        Mesh3daiansicht.koppeln(this.ansichten);
        this.rigknopf = wurzel.querySelector('#mesh3dai-test-rig');
        this.rigknopf.addEventListener('click', () => {
            this.rig = !this.rig;
            this.rigknopf.classList.toggle('active', this.rig);
            this.rigknopf.setAttribute('aria-pressed', String(this.rig));
            this.zeigen();
        });
        Mesh3daiflaechennetz.nachLaden = () => this.zeigen();
        // Geschlecht der Figur (16.10.2026 abends): der Server nimmt unter den Figuren dieses Geschlechts die mit dem kleinsten Rest — gerechnet ist schon alles, die Seite lädt nur neu.
        this.wahl = wurzel.querySelector('#mesh3dai-test-geschlecht');
        this.wahl?.addEventListener('change', () => this.geschlechtSetzen(this.wahl.value));
    }

    async geschlechtSetzen(wert) {
        const vorher = this.daten?.info?.geschlecht;
        this.wahl.disabled = true;
        try {
            await Serverabruf.senden(`/api/mesh3dai/test/${encodeURIComponent(this.kennung)}/geschlecht/`, { geschlecht: wert });
            await this.laden();
        } catch (fehler) {
            alert(`Geschlecht nicht gespeichert: ${fehler.message}`);
            if (vorher) this.wahl.value = vorher;
            this.wahl.disabled = false;
        }
    }

    _text(art, text) {
        const feld = this.wurzel.querySelector(`[data-info="${art}"]`);
        if (feld) feld.textContent = text;
    }

    async laden() {
        const info = this.wurzel.querySelector('#mesh3dai-test-info');
        try {
            const antwort = await fetch(`/api/mesh3dai/test/${encodeURIComponent(this.kennung)}/`);
            const daten = await antwort.json();
            if (!antwort.ok) throw new Error(daten.error || `HTTP ${antwort.status}`);
            this.daten = daten;
            const i = daten.info;
            // Figur der Ausgabe (16.10.2026 abends, Edgar: „bei Edgar erscheint ja noch Ursula“): die trainierte Figur mit dem kleinsten Rest der Anpassung (`test.json` → `figur`, `figuren`).
            const figur = i.figur || 'Ursula1';
            const form = figur === 'Form';
            const trainiert = (i.training_daten || [i.lauf_daten || 'Ursula1']).join(', ');
            const wahl = form ? ` Figur der Ausgabe: vorhergesagt aus den Formreglern (Lauf ${i.form?.lauf}).`
                : i.figuren ? ` Figur der Ausgabe: ${figur} — von ${Object.keys(i.figuren).length} trainierten die mit dem kleinsten Rest der Anpassung (${Object.entries(i.figuren).map(([n, r]) => `${n} ${de(r.rest_mm ?? r, 1)} mm`).join(' · ')}).` : '';
            // Seit 17.10.2026 rechnet die Vorstufe (Rig → A-Pose → Netz); ist das Netz der Vorstufe zu weit von der Rig-Figur, gilt das Rig allein (`weg`, `weg_grund` in test.json).
            const weg = i.weg === 'vorstufe' ? ` Weg: Rig (Mesh-3D ${i.mesh3d}) → A-Pose → Netz der Vorstufe → zurück in die Haltung.`
                : i.weg === 'rig' ? ` Weg: Rig allein (Mesh-3D ${i.mesh3d}) — ${i.weg_grund}.` : '';
            info.textContent = `Netz ohne Trainingsdaten (${i.quelle}) — gerechnet mit dem Netz des Laufs ${form ? i.form?.lauf : i.lauf} (trainiert an ${trainiert}).${weg}${wahl} Es gibt kein Ziel, darum keine Fehlerzahl.`;
            this._text('eingabe', `Das Netz, auf ${de(i.hoehe_m, 3)} m Höhe gebracht (Maßstab ${de(i.massstab, 3)}${i.weg ? ' aus der Höhe der Rig-Figur' : ''}, Mitte des Umrisses auf die Achse, Boden auf 0)${i.weg ? '' : ' — so sieht es das Netz von Mesh3D-AI'}; `
                + `${de(i.netz_punkte)} Punkte, hier auf ${de(i.vorschau_dreiecke)} Dreiecke verkleinert. Das Netz bekommt davon 16.384 Punkte mit ihren Texturfarben (im Training: 5 flache Teilfarben).\n`
                + 'Rig (Knopf „Rig“): das Rig, das Mesh3D-AI in dieses Netz legt.');
            if (form) {
                const regler = Object.entries(daten.form_regler || {});
                const charaktere = regler.filter(([n]) => n.includes('figure_ctrl')).sort((a, b) => b[1] - a[1]).map(([n, w]) => `${n.split('_')[0]} ${de(w, 2)}`);
                this._text('ausgabe', `Genesis-Figur aus den vorhergesagten Formreglern (${regler.length} gesetzt von 815; Charaktere: ${charaktere.join(' · ') || 'keiner'}), ohne Kleider und Haar, `
                    + `in der vorhergesagten Haltung (Daz-Winkel in den Grenzen von Genesis 9, Knochenlängen dieser Figur). Höhe ${de(i.hoehe_m, 3)} m. `
                    + `Anpassung der Winkel an die gestimmten Gelenke: Rest ${de(i.ik_rest_mm, 1)} mm. Geschlecht „${daten.geschlechter[i.geschlecht]}“: Charaktere des anderen Geschlechts sind auf dieses umgelegt.`);
            } else {
                const quelle = i.weg === 'rig' ? 'die Gelenke der Rig-Figur aus „Mesh to 3D“' : i.weg === 'vorstufe' ? 'die Gelenke der Vorstufe (Netz auf der A-Pose, mit dem Rig zurück in die Haltung)' : 'die gestimmten Gelenke';
                this._text('ausgabe', `${figur} in der erkannten Haltung (Daz-Winkel in den Grenzen von Genesis 9, Knochenlängen von ${figur}) — die Form bleibt ${figur}, erkannt wird nur die Haltung. `
                    + `Anpassung der Winkel an ${quelle}: Rest ${de(i.ik_rest_mm, 1)} mm.${daten.figur_hinweis ? '\n' + daten.figur_hinweis : ''}`);
            }
            if (this.wahl) {
                this.wahl.value = i.geschlecht;
                this.wahl.disabled = false;
            }
            const figurText = this.wurzel.querySelector('#mesh3dai-test-figur');
            if (figurText) figurText.textContent = `Ausgabe: ${form ? 'vorhergesagte Form' : figur}${daten.figur_hinweis ? ' — ' + daten.figur_hinweis : ''}`;
        } catch (fehler) {
            info.textContent = `Test nicht lesbar: ${fehler.message}`;
            return;
        }
        this.figur = null;
        this.zeigen();
        await Promise.all([this.netz ? null : this._netzLaden(), this._figurBauen()]);
        // Der Rahmen ist eine Streckung um den Fußpunkt der Mitte: dieselbe Vorschau passt auf jede Figurhöhe (`netz_skala` = Höhe der Figur / Höhe der Vorschau).
        this.netz?.scale.setScalar(this.daten.netz_skala ?? 1);
        this.zeigen();
    }

    async _netzLaden() {
        try {
            const gltf = await new GLTFLoader().loadAsync(this.daten.netz);
            gltf.scene.traverse(o => {
                if (!o.isMesh) return;
                // Die Vorschau (trimesh-Export) trägt keine Normalen — ohne sie zeichnet ein beleuchtetes Material schwarz (gesehen 16.10.2026).
                if (!o.geometry.getAttribute('normal')) o.geometry.computeVertexNormals();
                o.geometry.userData.gemeinsam = true;         // die Felder geben ihren Inhalt bei jedem Zeichnen frei — dieses Netz bleibt
                o.material = new THREE.MeshStandardMaterial({ vertexColors: !!o.geometry.getAttribute('color'), roughness: 0.8, side: THREE.DoubleSide });
                o.material.userData.gemeinsam = true;
            });
            this.netz = gltf.scene;
        } catch (fehler) {
            this._text('eingabe', `Netz nicht geladen: ${fehler.message}`);
        }
    }

    async _figurBauen() {
        try {
            // Vorhergesagte Form (16.10.2026 abends): eigenes Anzeigenetz unter der Adresse des Tests (`figur_netz`), sonst das des Jobs der gewählten Figur.
            const netz = await Mesh3daiflaechennetz.holen(this.daten.job, this.daten.figur_netz);
            if (!netz.ruhe) throw new Error('Anzeigenetz ohne Ruhelage');
            const d = this.daten;
            const lage = Mesh3daihaeutung.verformen(netz.ruhe, netz.knochen, netz.gewicht, netz.kopf.haut, Mesh3daihaeutung.ausDrehungen(d.dreh, d.ausgabe, d.ruhezentren));
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
            geo.setAttribute('uv', netz.uvAttribut);
            netz.farbe ??= Mesh3daiflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
            geo.setAttribute('color', netz.farbe);
            // Dreiecke nach Material sortiert (eine Gruppe je Material, −1 = Farbe je Punkt = das letzte Material).
            const materialien = netz.materialien();
            const letzter = materialien.length - 1;
            const je = Array.from({ length: materialien.length }, () => []);
            for (let t = 0; t < netz.material.length; t++) {
                const m = netz.material[t] < 0 ? letzter : netz.material[t];
                je[m].push(netz.dreiecke[t * 3], netz.dreiecke[t * 3 + 1], netz.dreiecke[t * 3 + 2]);
            }
            const index = new Uint32Array(je.reduce((s, l) => s + l.length, 0));
            let ab = 0;
            je.forEach((l, m) => {
                if (!l.length) return;
                index.set(l, ab);
                geo.addGroup(ab, l.length, m);
                ab += l.length;
            });
            geo.setIndex(new THREE.BufferAttribute(index, 1));
            geo.computeVertexNormals();
            geo.userData.gemeinsam = true;
            for (const m of materialien) m.userData.gemeinsam = true;
            this.figur = new THREE.Mesh(geo, materialien);
        } catch (fehler) {
            this._text('ausgabe', `Ausgabe nicht gebaut: ${fehler.message}`);
        }
    }

    _zeichnen(inhalt, art) {
        const objekt = art === 'eingabe' ? this.netz : this.figur;
        if (objekt) inhalt.add(objekt);
        if (this.rig && this.daten) {
            const beschr = this.daten.rig;
            inhalt.add(Mesh3dairigzeichner.zeichnen(beschr, beschr.knochen.map((_k, j) => j), this.daten.ausgabe));
        }
    }

    zeigen() {
        const d = this.daten ? { echt: true } : null;
        for (const a of this.ansichten) a.zeigen(d, this.daten ? null : 'wird geladen …');
    }
}
