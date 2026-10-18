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
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daihaeutung } from './mesh3daihaeutung.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';
import { Mesh3daitestkleider } from './mesh3daitestkleider.js';
import { Mesh3daitestnetzbau } from './mesh3daitestnetzbau.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

export class Mesh3daitestseite {
    static async starten(wurzel) {
        const seite = new Mesh3daitestseite(wurzel);
        window.__mesh3daitest = seite;
        // Der Rig-Knopf ist derselbe Eintrag wie auf den Jobseiten (17.10.2026, Edgar: „Die Einstellung des Rig Buttons merkst du dir immer noch nicht, die soll für alle Jobs gelten“) —
        // bis dahin hatte die Testseite einen eigenen Zustand, der beim Öffnen immer „an“ war.
        const stand = await Mesh3daiansichtgedaechtnis.laden();
        if (typeof stand.rig === 'boolean') seite.rigSetzen(stand.rig, false);
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
        this.figurNetz = null;     // ihr Anzeigenetz (für den Neubau ohne die verdeckten Dreiecke, `figurNeu`)
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = ['eingabe', 'ausgabe'].map(art => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="${art}"]`), art, zeichner, KAMERA));
        Mesh3daiansicht.koppeln(this.ansichten);
        this.rigknopf = wurzel.querySelector('#mesh3dai-test-rig');
        this.rigknopf.addEventListener('click', () => {
            Mesh3daiansichtgedaechtnis.merken({ rig: !this.rig });
            this.rigSetzen(!this.rig);
        });
        Mesh3daiflaechennetz.nachLaden = () => this.zeigen();
        // Geschlecht der Figur (16.10.2026 abends): der Server nimmt unter den Figuren dieses Geschlechts die mit dem kleinsten Rest — gerechnet ist schon alles, die Seite lädt nur neu.
        this.wahl = wurzel.querySelector('#mesh3dai-test-geschlecht');
        this.wahl?.addEventListener('change', () => this.geschlechtSetzen(this.wahl.value));
        // Kleider und Bestandteile (17.10.2026 nachts): je Stück Katalog (a) oder aus dem Netz (b), dazu „Übernehmen und speichern“.
        const karte = document.getElementById('mesh3dai-kleider');
        this.kleider = karte ? new Mesh3daitestkleider(karte, this) : null;
        this.matrizen = null;
    }

    rigSetzen(an, zeichnen = true) {
        this.rig = an;
        this.rigknopf.classList.toggle('active', an);
        this.rigknopf.setAttribute('aria-pressed', String(an));
        if (zeichnen) this.zeigen();
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

    /** Woher die Haltung der vorhergesagten Form kommt (`test.json` → `form.<geschlecht>.haltung`, seit 17.10.2026 spätabends der gewählte Weg; davor die Stimmen des Netzes in der Pose). */
    _formHaltung(i) {
        const haltung = i.form?.[i.geschlecht]?.haltung;
        return haltung === 'rig' ? 'die Gelenke der Rig-Figur aus „Mesh to 3D“ (Weg: Rig allein)'
            : haltung === 'vorstufe' ? 'die Gelenke der Vorstufe (Netz auf der A-Pose, mit dem Rig zurück in die Haltung)'
                : 'die Gelenke, die das Netz in der Pose stimmt';
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
            // Seit 18.10.2026 kann das Rig auch von Make-It-Animatable kommen (Kette ohne Mesh-3D-Auftrag: `mesh3d` leer); Namen der Methoden seit dem Abend: MeshToRigToPose_MIA / MeshToRigToPose.
            const rig = i.mesh3d ? `MeshToRigToPose: Mesh-3D-Figur, Auftrag ${i.mesh3d}` : 'MeshToRigToPose_MIA: Make-It-Animatable';
            const weg = i.weg === 'vorstufe' ? ` Weg: A-Pose über ${rig} → Netz der Vorstufe → zurück in die Haltung.`
                : i.weg === 'rig' ? ` Weg: Rig allein (${rig}) — ${i.weg_grund}.` : '';
            // Einstellungen → Mesh3D-AI, „Zwischenschritt A-Pose“ (`Mesh3daiaposewahl`): bei „aus“ das gesicherte Ergebnis ohne Vorstufe.
            const zs = i.zwischenschritt;
            const schritt = zs?.ohne_vorstufe ? ' Zwischenschritt A-Pose: aus (Einstellungen → Mesh3D-AI) — gezeigt wird das Ergebnis des Netzes direkt auf der Pose.'
                : zs?.fehlt ? ' Zwischenschritt A-Pose ist ausgeschaltet, für diesen Test liegt aber kein Ergebnis ohne Vorstufe vor — gezeigt wird das mit Vorstufe.'
                : zs?.andere_methode ? ` Eingestellt ist ${zs.eingestellt} — dieses Testnetz ist nur mit ${zs.methode} gerechnet; gezeigt wird das.` : '';
            info.textContent = `Netz ohne Trainingsdaten (${i.quelle}) — gerechnet mit dem Netz des Laufs ${form ? i.form?.lauf : i.lauf} (trainiert an ${trainiert}).${weg}${schritt}${wahl} Es gibt kein Ziel, darum keine Fehlerzahl.`;
            this._text('eingabe', `Das Netz, auf ${de(i.hoehe_m, 3)} m Höhe gebracht (Maßstab ${de(i.massstab, 3)}${i.weg ? ' aus der Höhe der Rig-Figur' : ''}, Mitte des Umrisses auf die Achse, Boden auf 0)${i.weg ? '' : ' — so sieht es das Netz von Mesh3D-AI'}; `
                + `${de(i.netz_punkte)} Punkte, hier auf ${de(i.vorschau_dreiecke)} Dreiecke verkleinert. Das Netz bekommt davon 16.384 Punkte mit ihren Texturfarben (im Training: 5 flache Teilfarben).\n`
                + 'Rig (Knopf „Rig“): das Rig, das Mesh3D-AI in dieses Netz legt.');
            if (form) {
                const regler = Object.entries(daten.form_regler || {});
                const charaktere = regler.filter(([n]) => n.includes('figure_ctrl')).sort((a, b) => b[1] - a[1]).map(([n, w]) => `${n.split('_')[0]} ${de(w, 2)}`);
                this._text('ausgabe', `Genesis-Figur aus den vorhergesagten Formreglern (${de(regler.length)} gesetzt von ${daten.form_regler_gesamt ? de(daten.form_regler_gesamt) : '?'}, Charaktere: ${charaktere.join(' · ') || 'keiner'}), Kleider und Bestandteile nach der Wahl in der Karte darunter, `
                    + `in der vorhergesagten Haltung (Daz-Winkel in den Grenzen von Genesis 9, Knochenlängen dieser Figur). Höhe ${de(i.hoehe_m, 3)} m. `
                    + `Anpassung der Winkel an ${this._formHaltung(i)}: Rest ${de(i.ik_rest_mm, 1)} mm. Geschlecht „${daten.geschlechter[i.geschlecht]}“: Charaktere des anderen Geschlechts sind auf dieses umgelegt.`);
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
        // Die Kleider gehören zur vorhergesagten Figur dieses Geschlechts (`kleider_<g>/`): mit derselben Haltung gehäutet.
        if (this.kleider && this.daten.figur_netz) {
            if (this.kleider.geschlecht === this.daten.info.geschlecht) await this.kleider.neuHaeuten(this.matrizen);
            else await this.kleider.laden(this.daten.info.geschlecht, this.matrizen, `${this.daten.info.name} Mesh3D-AI`);
        }
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
            const d = this.daten;
            // Die Matrizen bleiben gemerkt: die Kleider der Karte werden mit denselben gehäutet (`Mesh3daitestkleider`).
            this.matrizen = Mesh3daihaeutung.ausDrehungen(d.dreh, d.ausgabe, d.ruhezentren);
            this.figurNetz = netz;
            this.figur = Mesh3daitestnetzbau.mesh(netz, this.matrizen);
        } catch (fehler) {
            this._text('ausgabe', `Ausgabe nicht gebaut: ${fehler.message}`);
        }
    }

    /**
     * Die Figur nach der Wahl der Karte neu bauen (gerufen nach jeder Wahl): Haut der Figur oder die Haut aus dem Netz (`Mesh3daitestkleider.hautNetz`, dieselben Dreiecke),
     * ohne die Dreiecke unter den gewählten Stücken (`Mesh3daitestkleider.verdeckt`) — wie die Hautverdeckung in Charakter und Studio.
     */
    async figurNeu() {
        const netz = (await this.kleider?.hautNetz()) || this.figurNetz;
        if (netz && this.matrizen) {
            this.figur?.geometry.dispose();          // nur die Geometrie: Materialien und Attribute teilt sie mit dem Anzeigenetz
            this.figur = Mesh3daitestnetzbau.mesh(netz, this.matrizen, this.kleider?.verdeckt(netz.material.length));
        }
        this.zeigen();
    }

    _zeichnen(inhalt, art) {
        const objekt = art === 'eingabe' ? this.netz : this.figur;
        if (objekt) inhalt.add(objekt);
        if (art === 'ausgabe' && this.figur && this.kleider) for (const o of this.kleider.sichtbare()) inhalt.add(o);
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
