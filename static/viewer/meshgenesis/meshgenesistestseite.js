/**
 * Meshgenesistestseite — die Seite EINES Tests von Mesh-Genesis (16.10.2026, Reiter „Test“: Netze ohne Trainingsdaten).
 * Edgar: „darin auch eine Jobliste, aber nur Mesh und Ausgabe … testen, wie das bei Meshes ausschaut, wo wir keine Trainingsdaten haben“.
 * Zwei gekoppelte Felder (`Meshgenesisansicht`): Mesh = das Netz im Rahmen des Datensatzes (`…/netz/`, GLB mit Farbe je Punkt), Ausgabe = Ursula1 in der vorhergesagten Haltung — aus der Ruhelage mit den
 * Drehungen des Netzes gehäutet (`Meshgenesishaeutung.ausDrehungen`, dasselbe Anzeigenetz und dieselbe Hautmischung wie das Ergebnis auf der Jobseite). Der Knopf „Rig“ legt das vorhergesagte Rig über beide Felder.
 * Kein Ziel, also keine Fehlerfarben: das Rig trägt die Gruppenfarben. Seit 24.10.2026 dieselben Ansichtsarten und der Knopf „Kleider“ wie auf den Jobseiten (`Meshgenesistestansicht`, `Meshgenesisansichtart`).
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Meshgenesisansicht } from './meshgenesisansicht.js';
import { Meshgenesisansichtart } from './meshgenesisansichtart.js';
import { Meshgenesisansichtgedaechtnis } from './meshgenesisansichtgedaechtnis.js';
import { Meshgenesisanatomiehuelle } from './meshgenesisanatomiehuelle.js';
import { Meshgenesisfigurbewegung } from './meshgenesisfigurbewegung.js';
import { Meshgenesisfigurbewegungsleiste } from './meshgenesisfigurbewegungsleiste.js';
import { Meshgenesisflaechennetz } from './meshgenesisflaechennetz.js';
import { Meshgenesishaeutung } from './meshgenesishaeutung.js';
import { Meshgenesisrigzeichner } from './meshgenesisrigzeichner.js';
import { Meshgenesistestfaelle } from './meshgenesistestfaelle.js';
import { Meshgenesisohneglieder } from './meshgenesisohneglieder.js';
import { Meshgenesistestansicht } from './meshgenesistestansicht.js';
import { Meshgenesistestkleider } from './meshgenesistestkleider.js';
import { Meshgenesistestnetzbau } from './meshgenesistestnetzbau.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const de = (n, s = 0) => Number(n).toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });
const KAMERA = { position: [1.7, 1.5, 3.4], ziel: [0, 0.95, 0], boden: true };

export class Meshgenesistestseite {
    static async starten(wurzel) {
        const seite = new Meshgenesistestseite(wurzel);
        window.__meshgenesistest = seite;
        // Rig, Ansichtsart und Kleider sind derselbe Eintrag wie auf den Jobseiten (17.10.2026, Edgar: „Die Einstellung des Rig Buttons merkst du dir immer noch nicht, die soll für alle Jobs gelten“) —
        // bis dahin hatte die Testseite einen eigenen Zustand, der beim Öffnen immer „an“ war.
        seite.ansicht.gemerktSetzen(await Meshgenesisansichtgedaechtnis.laden());
        await seite.laden();
        seite._bereit();
        return seite;
    }

    constructor(wurzel) {
        this.wurzel = wurzel;
        this.kennung = wurzel.dataset.kennung;
        this.bereit = new Promise(fertig => { this._bereit = fertig; });
        this.daten = null;
        this.netz = null;          // das Netz des Tests (GLB-Szene)
        this.figur = null;         // Ursula1 in der vorhergesagten Haltung
        this.figurNetz = null;     // ihr Anzeigenetz (für den Neubau ohne die verdeckten Dreiecke, `figurNeu`)
        const zeichner = { zeichnen: (inhalt, art) => this._zeichnen(inhalt, art) };
        this.ansichten = ['eingabe', 'ausgabe'].map(art => new Meshgenesisansicht(wurzel.querySelector(`.meshgenesis-leinwand[data-art="${art}"]`), art, zeichner, KAMERA));
        Meshgenesisansicht.koppeln(this.ansichten);
        // Standardanimation der Ausgabe (22.10.2026, wie Mesh-3D): die vorhergesagte Figur als Genesis-Modell in Bewegung, mit Leertaste, Pfeilen, Pos1, Ende.
        const leiste = wurzel.querySelector('[data-figurbewegung]');
        const feld = this.ansichten.find(a => a.art === 'ausgabe');
        if (leiste && feld) {
            this.bewegung = new Meshgenesisfigurbewegung(feld, () => this._bewegungsquelle());
            new Meshgenesisfigurbewegungsleiste(leiste, this.bewegung, { tasten: true }).wahlLaden(leiste.dataset.adresse);
        }
        // „Kleider“ baut die Figur neu (die Haut unter den Stücken kommt zurück), Rig und Ansichtsart zeichnen nur neu.
        this.ansicht = new Meshgenesistestansicht(wurzel.querySelector('.meshgenesis-ansichtwahl'), was => (was === 'kleider' || was === 'ohneGlieder' ? this.figurNeu() : this.zeigen()));
        Meshgenesisflaechennetz.nachLaden = () => this.zeigen();
        // Geschlecht der Figur (16.10.2026 abends): der Server nimmt unter den Figuren dieses Geschlechts die mit dem kleinsten Rest — gerechnet ist schon alles, die Seite lädt nur neu.
        this.wahl = wurzel.querySelector('#meshgenesis-test-geschlecht');
        this.wahl?.addEventListener('change', () => this.geschlechtSetzen(this.wahl.value));
        // Kleider und Bestandteile (17.10.2026 nachts): je Stück Katalog (a) oder aus dem Netz (b), dazu „Übernehmen und speichern“.
        const karte = document.getElementById('meshgenesis-kleider');
        this.kleider = karte ? new Meshgenesistestkleider(karte, this) : null;
        // Testfälle der Kleider-KI (22.10.2026): FEHLER von Prüfungen je Prio, je Geschlecht neben den Stücken
        const testfaelle = document.getElementById('meshgenesis-testfaelle');
        this.testfaelle = testfaelle ? new Meshgenesistestfaelle(testfaelle) : null;
        this.matrizen = null;
    }

    /** Das Feld Ausgabe für „Haut angleichen“ (`Fotogenesishautangleich`). */
    get hautort() {
        return { ansicht: this.ansichten.find(a => a.art === 'ausgabe'), bereit: this.bereit, materialien: () => (this.figur ? [this.figur.material].flat() : []) };
    }

    async geschlechtSetzen(wert) {
        const vorher = this.daten?.info?.geschlecht;
        this.wahl.disabled = true;
        try {
            await Serverabruf.senden(`/api/meshgenesis/test/${encodeURIComponent(this.kennung)}/geschlecht/`, { geschlecht: wert });
            await this.laden();
        } catch (fehler) {
            alert(`Geschlecht nicht gespeichert: ${fehler.message}`);
            if (vorher) this.wahl.value = vorher;
            this.wahl.disabled = false;
        }
    }

    /** Gerechnet wird nur das eingestellte Geschlecht: Nach dem Umstellen sagt die Seite, dass die Kleider nicht aus dem letzten Lauf stammen (`Meshgenesistestgeschlechtstand`). */
    _geschlechtstand(text) {
        const feld = this.wurzel.querySelector('#meshgenesis-test-geschlechtstand');
        if (!feld) return;
        feld.hidden = !text;
        feld.textContent = text || '';
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
            if (!this.ansicht.kleider) break;          // Knopf „Kleider“ aus: kein Stück bewegt sich mit, auch das Haar nicht (30.10.2026, Edgar: „die Haare werden nicht deaktiviert“)
            const netz = st.art !== 'haut' && st.wahl !== 'aus' ? this.kleider.netze.get(`${st.wahl}/${st.id}`) : null;
            if (netz) stuecke.push({ id: st.id, art: st.art, netz: await netz.catch(() => null) });
        }
        const ohneKnochen = this._ohneKnochen();
        return { schluessel: `${this.kennung}|${d.info.geschlecht}|${ohneKnochen.join(',')}`, figur: d.figur_genesis, stuecke: stuecke.filter(s => s.netz), knochen: d.rig.knochen.map(k => k.name),
                 ruhezentren: d.ruhezentren, ohneKnochen, kapseln: d.kapseln, anatomieGetragen: Meshgenesisanatomiehuelle.getragen(this.kleider?.liste) };
    }

    /** Knopf „Ohne fehlende Glieder“ an: die Knochen, die der Eingang nicht hat (Kleiderliste, `ohne_eingang`), sonst keine. */
    _ohneKnochen() {
        return this.ansicht.ohneGlieder ? (this.kleider?.liste?.ohne_eingang?.knochen || []) : [];
    }

    async laden() {
        this.bewegung?.verwerfen();         // anderes Geschlecht: andere Figur
        const info = this.wurzel.querySelector('#meshgenesis-test-info');
        try {
            const antwort = await fetch(`/api/meshgenesis/test/${encodeURIComponent(this.kennung)}/`);
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
            // Einstellungen → Mesh-Genesis, „Zwischenschritt A-Pose“ (`Meshgenesisaposewahl`): bei „aus“ das gesicherte Ergebnis ohne Vorstufe.
            const zs = i.zwischenschritt;
            const schritt = zs?.ohne_vorstufe ? ' Zwischenschritt A-Pose: aus (Einstellungen → Mesh-Genesis) — gezeigt wird das Ergebnis des Netzes direkt auf der Pose.'
                : zs?.fehlt ? ' Zwischenschritt A-Pose ist ausgeschaltet, für diesen Test liegt aber kein Ergebnis ohne Vorstufe vor — gezeigt wird das mit Vorstufe.'
                : zs?.andere_methode ? ` Eingestellt ist ${zs.eingestellt} — dieses Testnetz ist nur mit ${zs.methode} gerechnet; gezeigt wird das.` : '';
            // Form aus der Regler-KI (27.10.2026, `meshgenesis_reglerki_test.py`): trainiert an den Formvarianten, nicht an den vier Jobs; mit Wahrheit (Tripo-Job) die echte Prüfung dazu
            const rk = form && i.form?.reglerki_lauf ? i.form.reglerki : null;
            const ziel = rk?.wahrheit_echt_mm ? ` Gegen die Wahrheit (G9formung, ohne Ausrichtung; der Eingang steht auf der mittleren Höhe ${de(rk.hoehe_m, 3)} m, nicht auf der wahren): `
                + ['Grundfigur', 'Regler-KI'].map(z => `${z === 'Regler-KI' ? 'Regler-KI (Ausgabe vor dem Umlegen aufs Geschlecht)' : z} Körper ${de(rk.wahrheit_echt_mm[z].koerper, 1)} · Kopfform ${de(rk.wahrheit_echt_mm[z].kopf_form, 1)} · Gelenke ${de(rk.wahrheit_echt_mm[z].gelenke, 1)} mm`).join('; ')
                + `. Eingang zur Figur (Median): Grundfigur ${de(rk.abstand_wolke_figur_mm['Grundfigur'], 1)}, Regler-KI ${de(rk.abstand_wolke_figur_mm['Regler-KI'], 1)} mm.` : ' Es gibt kein Ziel, darum keine Fehlerzahl.';
            info.textContent = rk ? `Netz ohne Trainingsdaten (${i.quelle}) — Form aus der Regler-KI (Lauf ${i.form.reglerki_lauf}, trainiert an den Trainingsformen, dieses Netz nie gesehen), Haltung aus dem Netz des Laufs ${i.lauf}.${weg}${schritt}${ziel}`
                : `Netz ohne Trainingsdaten (${i.quelle}) — gerechnet mit dem Netz des Laufs ${form ? i.form?.lauf : i.lauf} (trainiert an ${trainiert}).${weg}${schritt}${wahl} Es gibt kein Ziel, darum keine Fehlerzahl.`;
            this._text('eingabe', `Das Netz, auf ${de(i.hoehe_m, 3)} m Höhe gebracht (Maßstab ${de(i.massstab, 3)}${i.weg ? ' aus der Höhe der Rig-Figur' : ''}, Mitte des Umrisses auf die Achse, Boden auf 0)${i.weg ? '' : ' — so sieht es das Netz von Mesh-Genesis'}; `
                + `${de(i.netz_punkte)} Punkte, hier auf ${de(i.vorschau_dreiecke)} Dreiecke verkleinert. Das Netz bekommt davon 16.384 Punkte mit ihren Texturfarben (im Training: 5 flache Teilfarben).\n`
                + 'Rig (Knopf „Rig“): das Rig, das Mesh-Genesis in dieses Netz legt.');
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
            this.testfaelle?.laden(`/api/meshgenesis/test/${encodeURIComponent(this.kennung)}/testfaelle/${encodeURIComponent(i.geschlecht)}/?t=${Date.now()}`);
            const figurText = this.wurzel.querySelector('#meshgenesis-test-figur');
            if (figurText) figurText.textContent = `Ausgabe: ${form ? 'vorhergesagte Form' : figur}${daten.figur_hinweis ? ' — ' + daten.figur_hinweis : ''}`;
            this._geschlechtstand(i.geschlecht_stand);
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
            else await this.kleider.laden(this.daten.info.geschlecht, this.matrizen, `${this.daten.info.name} Mesh-Genesis`);
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
            // Netzstufe 1 (09.11.2026, Edgar: „das ganze Anzeigenetz in Stufe 1“) — wie die Charakter-Seite; der Server gibt den Käfig, wo der Körper keiner ist
            const netz = await Meshgenesisflaechennetz.holen(this.daten.job, this.daten.figur_netz, { stufe: 1 });
            const d = this.daten;
            // Die Matrizen bleiben gemerkt: die Kleider der Karte werden mit denselben gehäutet (`Meshgenesistestkleider`).
            this.matrizen = Meshgenesishaeutung.ausDrehungen(d.dreh, d.ausgabe, d.ruhezentren);
            this.figurNetz = netz;
            this.figur = Meshgenesistestnetzbau.mesh(netz, this.matrizen);
        } catch (fehler) {
            this._text('ausgabe', `Ausgabe nicht gebaut: ${fehler.message}`);
        }
    }

    /**
     * Die Figur nach der Wahl der Karte neu bauen (gerufen nach jeder Wahl): Haut der Figur oder die Haut aus dem Netz (`Meshgenesistestkleider.hautNetz`, dieselben Dreiecke),
     * ohne die Dreiecke unter den gewählten Stücken (`Meshgenesistestkleider.verdeckt`) — wie die Hautverdeckung in Charakter und Studio.
     */
    async figurNeu() {
        this.bewegung?.verwerfen();         // neue Wahl der Stücke: die bewegte Figur trägt die alten
        const netz = (await this.kleider?.hautNetz()) || this.figurNetz;
        if (netz && this.matrizen) {
            this.figur?.geometry.dispose();          // nur die Geometrie: Materialien und Attribute teilt sie mit dem Anzeigenetz
            // die Masken der Stücke sind auf dem Käfig gerechnet — auf Stufe 1 gelten sie für die Kinder jedes Käfigdreiecks (`dreieckmaske`)
            let weg = this.ansicht.kleider ? netz.dreieckmaske(this.kleider?.verdeckt(netz.kaefigDreiecke)) : null;
            const ohne = Meshgenesisohneglieder.dreiecke(netz, this.daten?.rig?.knochen?.map(k => k.name) || [], this._ohneKnochen());
            if (ohne) weg = weg ? weg.map((v, i) => v | ohne[i]) : ohne;
            this.figur = Meshgenesistestnetzbau.mesh(netz, this.matrizen, weg);
        }
        this.zeigen();
    }

    _zeichnen(inhalt, art) {
        const modus = this.ansicht.modus;
        const objekt = art === 'eingabe' ? this.netz : this.figur;
        if (objekt) inhalt.add(Meshgenesisansichtart.anwenden(objekt, modus));
        if (art === 'ausgabe' && this.figur && this.kleider && this.ansicht.kleider) for (const o of this.kleider.sichtbare()) inhalt.add(Meshgenesisansichtart.anwenden(o, modus));
        if (this.ansicht.rig && this.daten) {
            const beschr = this.daten.rig;
            inhalt.add(Meshgenesisrigzeichner.zeichnen(beschr, beschr.knochen.map((_k, j) => j), this.daten.ausgabe));
        }
    }

    zeigen() {
        const d = this.daten ? { echt: true } : null;
        for (const a of this.ansichten) a.zeigen(d, this.daten ? null : 'wird geladen …');
    }
}
