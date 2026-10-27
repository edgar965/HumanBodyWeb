/**
 * Mesh3daitestseite — die Seite EINES Tests von Mesh3D-AI (16.10.2026, Reiter „Test“: Netze ohne Trainingsdaten).
 * Edgar: „darin auch eine Jobliste, aber nur Mesh und Ausgabe … testen, wie das bei Meshes ausschaut, wo wir keine Trainingsdaten haben“.
 * Zwei gekoppelte Felder (`Mesh3daiansicht`): Mesh = das Netz im Rahmen des Datensatzes (`…/netz/`, GLB mit Farbe je Punkt), Ausgabe = Ursula1 in der vorhergesagten Haltung — aus der Ruhelage mit den
 * Drehungen des Netzes gehäutet (`Mesh3daihaeutung.ausDrehungen`, dasselbe Anzeigenetz und dieselbe Hautmischung wie das Ergebnis auf der Jobseite). Der Knopf „Rig“ legt das vorhergesagte Rig über beide Felder.
 * Kein Ziel, also keine Fehlerfarben: das Rig trägt die Gruppenfarben. Seit 24.10.2026 dieselben Ansichtsarten und der Knopf „Kleider“ wie auf den Jobseiten (`Mesh3daitestansicht`, `Mesh3daiansichtart`).
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { Mesh3daiansichtart } from './mesh3daiansichtart.js';
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daifigurbewegung } from './mesh3daifigurbewegung.js';
import { Mesh3daifigurbewegungsleiste } from './mesh3daifigurbewegungsleiste.js';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daihaeutung } from './mesh3daihaeutung.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';
import { Mesh3daitestfaelle } from './mesh3daitestfaelle.js';
import { Mesh3daitestansicht } from './mesh3daitestansicht.js';
import { Mesh3daitestkleider } from './mesh3daitestkleider.js';
import { Mesh3daitestnetzbau } from './mesh3daitestnetzbau.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

export class Mesh3daitestseite {
    static async starten(wurzel) {
        const seite = new Mesh3daitestseite(wurzel);
        window.__mesh3daitest = seite;
        // Rig, Ansichtsart und Kleider sind derselbe Eintrag wie auf den Jobseiten (17.10.2026, Edgar: „Die Einstellung des Rig Buttons merkst du dir immer noch nicht, die soll für alle Jobs gelten“) —
        // bis dahin hatte die Testseite einen eigenen Zustand, der beim Öffnen immer „an“ war.
        seite.ansicht.gemerktSetzen(await Mesh3daiansichtgedaechtnis.laden());
        await seite.laden();
        return seite;
    }

    constructor(wurzel) {
        this.wurzel = wurzel;
        this.kennung = wurzel.dataset.kennung;
        this.daten = null;
        this.netz = null;          // das Netz des Tests (GLB-Szene)
        this.figur = null;         // Ursula1 in der vorhergesagten Haltung
        this.figurNetz = null;     // ihr Anzeigenetz (für den Neubau ohne die verdeckten Dreiecke, `figurNeu`)
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = ['eingabe', 'ausgabe'].map(art => new Mesh3daiansicht(wurzel.querySelector(`.mesh3dai-leinwand[data-art="${art}"]`), art, zeichner, KAMERA));
        Mesh3daiansicht.koppeln(this.ansichten);
        // Standardanimation der Ausgabe (22.10.2026, wie Mesh-3D): die vorhergesagte Figur als Genesis-Modell in Bewegung, mit Leertaste, Pfeilen, Pos1, Ende.
        const leiste = wurzel.querySelector('[data-figurbewegung]');
        const feld = this.ansichten.find(a => a.art === 'ausgabe');
        if (leiste && feld) {
            this.bewegung = new Mesh3daifigurbewegung(feld, () => this._bewegungsquelle());
            new Mesh3daifigurbewegungsleiste(leiste, this.bewegung, { tasten: true }).wahlLaden(leiste.dataset.adresse);
        }
        // „Kleider“ baut die Figur neu (die Haut unter den Stücken kommt zurück), Rig und Ansichtsart zeichnen nur neu.
        this.ansicht = new Mesh3daitestansicht(wurzel.querySelector('.mesh3dai-ansichtwahl'), was => (was === 'kleider' ? this.figurNeu() : this.zeigen()));
        Mesh3daiflaechennetz.nachLaden = () => this.zeigen();
        // Geschlecht der Figur (16.10.2026 abends): der Server nimmt unter den Figuren dieses Geschlechts die mit dem kleinsten Rest — gerechnet ist schon alles, die Seite lädt nur neu.
        this.wahl = wurzel.querySelector('#mesh3dai-test-geschlecht');
        this.wahl?.addEventListener('change', () => this.geschlechtSetzen(this.wahl.value));
        // Kleider und Bestandteile (17.10.2026 nachts): je Stück Katalog (a) oder aus dem Netz (b), dazu „Übernehmen und speichern“.
        const karte = document.getElementById('mesh3dai-kleider');
        this.kleider = karte ? new Mesh3daitestkleider(karte, this) : null;
        // Testfälle der Kleider-KI (22.10.2026): FEHLER von Prüfungen je Prio, je Geschlecht neben den Stücken
        const testfaelle = document.getElementById('mesh3dai-testfaelle');
        this.testfaelle = testfaelle ? new Mesh3daitestfaelle(testfaelle) : null;
        this.matrizen = null;
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

    /** Was die Standardanimation bewegt: die vorhergesagte Figur (`figur_genesis`) und die Stücke der wirksamen Wahl der Karte darunter (ihre Anzeigenetze, schon geladen). */
    async _bewegungsquelle() {
        const d = this.daten;
        if (!d?.figur_genesis) return null;
        const stuecke = [];
        for (const st of this.kleider?.liste?.stuecke ?? []) {
            if (!this.ansicht.kleider && st.art !== 'haar') continue;          // Knopf „Kleider“ aus: nur das Haar bewegt sich mit
            const netz = st.art !== 'haut' && st.wahl !== 'aus' ? this.kleider.netze.get(`${st.wahl}/${st.id}`) : null;
            if (netz) stuecke.push({ id: st.id, art: st.art, netz: await netz.catch(() => null) });
        }
        return { schluessel: `${this.kennung}|${d.info.geschlecht}`, figur: d.figur_genesis, stuecke: stuecke.filter(s => s.netz), knochen: d.rig.knochen.map(k => k.name), ruhezentren: d.ruhezentren };
    }

    async laden() {
        this.bewegung?.verwerfen();         // anderes Geschlecht: andere Figur
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
            // Form aus der Regler-KI (27.10.2026, `mesh3dai_reglerki_test.py`): trainiert an den Formvarianten, nicht an den vier Jobs; mit Wahrheit (Tripo-Job) die echte Prüfung dazu
            const rk = form && i.form?.reglerki_lauf ? i.form.reglerki : null;
            const ziel = rk?.wahrheit_echt_mm ? ` Gegen die Wahrheit (G9formung, ohne Ausrichtung; der Eingang steht auf der mittleren Höhe ${de(rk.hoehe_m, 3)} m, nicht auf der wahren): `
                + ['Grundfigur', 'Regler-KI'].map(z => `${z === 'Regler-KI' ? 'Regler-KI (Ausgabe vor dem Umlegen aufs Geschlecht)' : z} Körper ${de(rk.wahrheit_echt_mm[z].koerper, 1)} · Kopfform ${de(rk.wahrheit_echt_mm[z].kopf_form, 1)} · Gelenke ${de(rk.wahrheit_echt_mm[z].gelenke, 1)} mm`).join('; ')
                + `. Eingang zur Figur (Median): Grundfigur ${de(rk.abstand_wolke_figur_mm['Grundfigur'], 1)}, Regler-KI ${de(rk.abstand_wolke_figur_mm['Regler-KI'], 1)} mm.` : ' Es gibt kein Ziel, darum keine Fehlerzahl.';
            info.textContent = rk ? `Netz ohne Trainingsdaten (${i.quelle}) — Form aus der Regler-KI (Lauf ${i.form.reglerki_lauf}, trainiert an den Trainingsformen, dieses Netz nie gesehen), Haltung aus dem Netz des Laufs ${i.lauf}.${weg}${schritt}${ziel}`
                : `Netz ohne Trainingsdaten (${i.quelle}) — gerechnet mit dem Netz des Laufs ${form ? i.form?.lauf : i.lauf} (trainiert an ${trainiert}).${weg}${schritt}${wahl} Es gibt kein Ziel, darum keine Fehlerzahl.`;
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
            this.testfaelle?.laden(`/api/mesh3dai/test/${encodeURIComponent(this.kennung)}/testfaelle/${encodeURIComponent(i.geschlecht)}/?t=${Date.now()}`);
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
        this.bewegung?.verwerfen();         // neue Wahl der Stücke: die bewegte Figur trägt die alten
        const netz = (await this.kleider?.hautNetz()) || this.figurNetz;
        if (netz && this.matrizen) {
            this.figur?.geometry.dispose();          // nur die Geometrie: Materialien und Attribute teilt sie mit dem Anzeigenetz
            this.figur = Mesh3daitestnetzbau.mesh(netz, this.matrizen, this.kleider?.verdeckt(netz.material.length, !this.ansicht.kleider));
        }
        this.zeigen();
    }

    _zeichnen(inhalt, art) {
        const modus = this.ansicht.modus;
        const objekt = art === 'eingabe' ? this.netz : this.figur;
        if (objekt) inhalt.add(Mesh3daiansichtart.anwenden(objekt, modus));
        if (art === 'ausgabe' && this.figur && this.kleider) for (const o of this.kleider.sichtbare(!this.ansicht.kleider)) inhalt.add(Mesh3daiansichtart.anwenden(o, modus));
        if (this.ansicht.rig && this.daten) {
            const beschr = this.daten.rig;
            inhalt.add(Mesh3dairigzeichner.zeichnen(beschr, beschr.knochen.map((_k, j) => j), this.daten.ausgabe));
        }
    }

    zeigen() {
        const d = this.daten ? { echt: true } : null;
        for (const a of this.ansichten) a.zeigen(d, this.daten ? null : 'wird geladen …');
    }
}
