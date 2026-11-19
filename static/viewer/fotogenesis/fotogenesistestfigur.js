/**
 * Fotogenesistestfigur — die Figur eines Mesh-Genesis-Tests auf der Foto-Genesis-Seite: Feld „Genesis-Ergebnis“ (`Fotogenesisgenesiszeile`) und Feld 3 eines Tests aus echten Fotos
 * (`Fotogenesisseite`, die eigene Figur `<Job>/figur/`).
 *
 * Seit 19.11.2026 mit dem Code der Charakter-Seite (Edgar: „merge beide anzeigen zu einem Code. nimm die schnellste lösung von beiden“): der Körper ist ein `Genesis9Modell` in der Haltung
 * der KI (`drehung_genesis`, Daz-Winkel vom Server, `Meshgenesisgenesishaltung`) bzw. in der A-Pose (`apose`, die Ruhelage), starr auf das Rig der Probe gelegt wie auf der Mesh-Genesis-Jobseite
 * (`Meshgenesisgenesisfigur._ausrichten`); Kleider und Haar aus der KI, wie die Testseite sie gewählt hat (`Meshgenesiskikleiderfeld`), Haut darunter weg (`Hautverdeckung`, wie in Charakter).
 * Bis dahin: vorab gerechnetes Anzeigenetz (`Meshgenesisflaechennetz`, Netzstufe 1) mit eigener Häutung (`Meshgenesistestnetzbau`) und Augäpfeln aus der KI. Gemessen im Chrome (frischer Tab,
 * Goldprinzessin _57, Körper, Augen und 7 Stücke, je dreimal): Anzeigenetz 2.258–2.921 ms, Genesis9Modell 2.305–2.803 ms — gleich schnell; die Abspielleiste und der Export bauen die Figur
 * ohnehin als Genesis9Modell (`Fotogenesisexportfigur`). Nicht übernommen (nur der alte Job mit eigener Figur und Zeile 1 nutzte sie): die Vorlage der Zeile 1 auf dem Anzeigenetz
 * (`Fotogenesiszeile1`) und die Haltung je Foto in den Seitenbildern (`inHaltung`) — `Fotogenesisseitenbild` nimmt dann die gemeinsame Haltung.
 * Dieselbe Schnittstelle wie `Fotogenesisgenesis` (`bereit`, `probe`, `auftrag`, `fertig`, `zeichnen`, `rahmen`).
 */
import * as THREE from 'three';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Genesis9vorrat } from '../gemeinsam/genesis9vorrat.js';
import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';
import { Meshgenesisgenesisfigur } from '../meshgenesis/meshgenesisgenesisfigur.js';
import { Meshgenesiskikleiderfeld } from '../meshgenesis/meshgenesiskikleiderfeld.js';
import { Meshgenesisrigzeichner } from '../meshgenesis/meshgenesisrigzeichner.js';
import { Fotogenesisnetz } from './fotogenesisnetz.js';

export class Fotogenesistestfigur {
    static _nummer = 0;
    static WACHE_MS = 500;

    /** @param {{kennung: string, adresse: string, apose?: boolean, eigen?: boolean}} test aus den Seitendaten @param seite `Fotogenesisseite` oder null */
    constructor(test, seite = null) {
        this.test = test;
        this.seite = seite;
        this.probe = null;           // die Antwort der Testschnittstelle, sobald die Figur gebaut ist
        this.modell = null;          // Genesis9Modell
        this.figur = null;           // THREE.Group: Körper (modell.group) und Stücke
        this.kleider = null;
        this.fehler = '';
        this.text = '';
        // Ein Bild, eine Maske oder die feinere Netzstufe kommt nach: `nachgeladen` (Vergleich der Seite, `Fotogenesisseite`) und `beiAenderung` (Feld neu zeichnen, `Fotogenesisgenesiszeile`)
        this.nachgeladen = null;
        this.beiAenderung = null;
        this.bereit = this._bauen();
    }

    async _bauen() {
        try {
            const antwort = await fetch(this.test.adresse);
            const daten = await antwort.json();
            if (!antwort.ok) throw new Error(daten.error || `HTTP ${antwort.status}`);
            if (!daten.figur_genesis) throw new Error('der Test hat keine Genesis-Figur');
            // A-Pose (10.11.2026, Edgar: „mach doch das pshuman mesh und die genesis ausgabe in allen jobs auf die A-Pose, damit man das besser vergleichen kann“): die Ruhelage von Genesis 9 —
            // Körper, Kleider und Rig in derselben Haltung
            if (this.test.apose) Object.assign(daten, { dreh: daten.dreh.map(() => [0, 0, 0, 1]), ausgabe: daten.ruhezentren.map(p => [...p]) });
            // Die Figur steht hier allein (nicht über dem Fotonetz): Standhaltung der Fußregel, wenn der Server sie liefert (19.11.2026 abends,
            // `Meshgenesishaltungwahl`) — Körper (`drehung_genesis`), Stücke und Rig in derselben Haltung
            else if (daten.ausgabe_stand && daten.dreh_stand) Object.assign(daten, { ausgabe: daten.ausgabe_stand, dreh: daten.dreh_stand });
            const geschlecht = daten.info?.geschlecht || String(daten.figur_netz).split('/').filter(Boolean).pop();
            // Körper und Stücke zugleich (08.11.2026, Ladezeit)
            this._kleiderQuelle = { liste: `${this.test.adresse}kleider/${geschlecht}/`, dreh: daten.dreh, rig: daten.ausgabe, ruhezentren: daten.ruhezentren };
            const kleiderAbruf = Meshgenesiskikleiderfeld.laden(this._kleiderQuelle)
                .catch(fehler => { console.warn(`Fotogenesistestfigur: Kleider nicht geladen (${fehler.message})`); return null; });
            const ohneWinkel = !this.test.apose && !daten.drehung_genesis;
            const figur = { ...daten.figur_genesis, pose: '', drehung: this.test.apose ? null : (daten.drehung_genesis || null) };
            const modell = new Genesis9Modell(`fotogenesis_test_${++Fotogenesistestfigur._nummer}`, figur);
            await modell.bauen();
            this.modell = modell;
            this.kleider = await kleiderAbruf;
            this.figur = new THREE.Group();
            this.figur.add(modell.group);
            if (this.kleider) this.figur.add(this.kleider.gruppe);
            this.figur.userData.meshgenesisFremd = true;          // gehört nicht dem Feld (`Meshgenesisansicht._leeren` gibt es dann nicht frei)
            this.probe = daten;
            this._ausrichten();
            this._hautStuecke();
            this._textKopf = this.test.eigen ? `Genesis-Modell dieses Jobs (<Job>/figur/, ${daten.info?.name ?? ''}) in der Haltung aus den Fotos`
                : `Ausgabe des Mesh-Genesis-Tests ${this.test.kennung} (${daten.info?.name ?? ''}) ${this.test.apose ? 'in der A-Pose' : ohneWinkel ? 'in der Ruhelage (Winkel der Haltung fehlen)' : daten.haltung === 'stand' ? 'in der Haltung aus dem Netz, Füße flach (Fußregel)' : 'in der Haltung aus dem Netz'}`;
            this._textSetzen();
            this._wachen();
            // Alle Stufen bis zur Einstellung dauerhaft ablegen lassen, wie in Charakter nach dem Laden
            Genesis9vorrat.fuellen(modell).catch(f => console.warn(`Genesis9vorrat: ${f.message}`));
        } catch (fehler) {
            // „fehlt“ ausdrücklich (13.11.2026, Edgar: „dann mach hinweis, dass es fehlt!!“)
            this.fehler = `Genesis-Ergebnis fehlt: Figur des Tests ${this.test.kennung} nicht geladen (${fehler.message}).`;
            console.warn(`Fotogenesistestfigur: ${this.fehler}`);
        }
    }

    /** Text des Felds: Figur und Stücke. `Meshgenesiskikleiderfeld` beschriftet Weg k als „aus dem Netz geschnitten“ — bei der eigenen Figur sind sie aus den Fotos (`Fotoschale`). */
    _textSetzen() {
        const namen = (this.kleider?.namen ?? []).map(n => (this.test.eigen ? n.replace('aus dem Netz geschnitten', 'aus den Fotos geschnitten') : n));
        this.text = `${this._textKopf}${namen.length ? `, ${namen.join(', ')}` : ''}.`;
    }

    /**
     * Methode der Kleider (19.11.2026, Edgar: „Kleiderbibliothek (ehemals Garderobe) und Drapieren … toggle für beide Ergebnisse im genesis view“, `Fotogenesiskleidermethode`):
     * derselbe Körper, nur die Stücke wechseln. 'drapieren' nimmt je Zeile das drapierte Stück (Weg f), wo es ein Netz hat, sonst das wirksame (Kleiderbibliothek); geladen beim
     * ersten Umschalten. → {drapiert, versucht} (Zeilen mit drapiertem Netz / Zeilen, für die Drapieren gerechnet wurde) oder null.
     */
    async methodeSetzen(methode) {
        await this.bereit;
        if (!this.modell || !this._kleiderQuelle) return null;
        this._saetze ??= { bibliothek: this.kleider };
        if (!(methode in this._saetze)) {
            // „drapieren“ nur die drapierten Stücke, „gemischt“ drapiert, wo es eins gibt, sonst die Kleiderbibliothek (19.11.2026, Edgar: „sehe ich nicht, welches was ist,
            // mach einen dritten Button der mir entweder das eine oder das andere zeigt“) — null fällt in `Meshgenesiskikleiderfeld.laden` heraus
            const weg = methode === 'gemischt' ? st => (st.f?.netz ? 'f' : st.wahl) : st => (st.f?.netz ? 'f' : null);
            this._saetze[methode] = await Meshgenesiskikleiderfeld.laden({ ...this._kleiderQuelle, daten: this._saetze.bibliothek?.liste, weg })
                .catch(fehler => { console.warn(`Fotogenesistestfigur: Drapieren nicht geladen (${fehler.message})`); return undefined; });
            if (this._saetze[methode] === undefined) { delete this._saetze[methode]; return null; }
        }
        const neu = this._saetze[methode];
        if (neu !== this.kleider) {
            const an = this.kleider?.kleiderAn ?? true;
            if (this.kleider) this.figur.remove(this.kleider.gruppe);
            this.kleider = neu;
            if (neu) {
                this.figur.add(neu.gruppe);
                Meshgenesiskikleiderfeld.kleiderZeigen(neu, an);
                this._ausrichten();
                this._hautStuecke();
            } else {
                this.modell.hautStuecke = {};
                Hautverdeckung.planen(this.modell);
            }
            this._textSetzen();
        }
        const liste = (this._saetze.bibliothek ?? neu)?.liste?.stuecke ?? [];
        return { drapiert: (neu?.stuecke ?? []).filter(st => st.weg === 'f').length, versucht: liste.filter(st => st.quelle === 'ki' && st.f).length };
    }

    /** Körper starr auf das Rig der Probe (dieselben Punkte, mit denen die Stücke gehäutet sind) — nach jeder feineren Stufe neu, sie ersetzt Netze und Skelett. */
    _ausrichten() {
        Meshgenesisgenesisfigur._ausrichten(this.modell.group, this.probe.rig?.knochen ?? [], this.probe.ausgabe, null);
        this.figur.traverse(o => { o.layers.set(1); o.frustumCulled = false; });
    }

    /**
     * Haut und Anatomie-Stück unter den Stücken weg wie in Charakter und Studio (`Hautverdeckung`) — mit den Stücken in der Lage, in der sie gezeigt werden, im Rahmen des Körpers.
     * Der Server rechnet die Haltung in das Netz des Körpers ein (`drehung`; gehäutete Punkte = Rohpunkte, gemessen 19.11.2026), `Meshgenesiskikleiderfeld.hautStuecke` nimmt aber
     * die Ruhelage der Stücke: die Maske verglich den gestellten Körper mit Stücken in Ruhelage, und an der Brust der Goldprinzessin stand Haut vor dem Kostüm.
     */
    _hautStuecke() {
        const ki = this.kleider;
        if (!ki) return;
        this.figur.updateMatrixWorld(true);
        const umkehr = this.modell.group.matrixWorld.clone().invert(), v = new THREE.Vector3();
        const gestellt = { ...ki, stuecke: ki.stuecke.map(st => {
            const lage = st.mesh?.geometry?.getAttribute('position');
            if (!lage) return st;
            const ruhe = new Float32Array(lage.count * 3);
            for (let p = 0; p < lage.count; p++) {
                v.fromBufferAttribute(lage, p).applyMatrix4(umkehr);
                ruhe[p * 3] = v.x; ruhe[p * 3 + 1] = v.y; ruhe[p * 3 + 2] = v.z;
            }
            return { ...st, ruhe };
        }) };
        this.modell.hautStuecke = Meshgenesiskikleiderfeld.hautStuecke(gestellt);
        ki.haut = gestellt.haut;          // der Schalter „Kleider“ blendet diese Stoffe mit aus (`Meshgenesiskikleiderfeld.kleiderZeigen`)
        Hautverdeckung.planen(this.modell);
    }

    /** Was nach `bauen()` noch kommt (Bilder, Masken, feinere Stufe), zeichnet sonst niemand: dieselbe Wache wie `Meshgenesisgenesisfigur` (Stände vergleichen, nur bei Änderung melden). */
    _wachen() {
        let stand = Meshgenesisgenesisfigur._stand(this.modell);
        clearInterval(this._wache);
        this._wache = setInterval(() => {
            if (document.hidden || !this.modell) return;
            const neu = Meshgenesisgenesisfigur._stand(this.modell);
            if (neu.bau === stand.bau && neu.rest === stand.rest) return;
            if (neu.bau !== stand.bau) this._ausrichten();
            stand = neu;
            this.beiAenderung?.();
            this.nachgeladen?.();
        }, Fotogenesistestfigur.WACHE_MS);
    }

    /** Die Materialien des Körpers (für „Haut angleichen“, `Fotogenesishautangleich`). */
    materialien() {
        return this.modell?.bodyMesh ? [this.modell.bodyMesh.material].flat() : [];
    }

    auftrag(quelle, modus, kleider, rig = false) {
        return { echt: true, zeile: 'test', quelle, modus, kleider, rig };
    }

    /** Zeichner von `Meshgenesisansicht`: `d` aus `auftrag` — Kleider (mit Haar) ein/aus, Ansichtsart als Ersatzmaterial, Rig (Knopf „Rig“) darüber. */
    zeichnen(inhalt, _art, d) {
        if (!this.figur || !this.modell) {
            inhalt.userData.hinweis = this.fehler || 'Figur des Tests wird gebaut …';
            return;
        }
        // Schalter „Kleider“: ausgeblendet zeigt die Figur die Haut darunter wieder (die Maske rechnet ohne die Stücke neu)
        if (this.kleider && Meshgenesiskikleiderfeld.kleiderZeigen(this.kleider, d?.kleider !== false)) Hautverdeckung.planen(this.modell);
        inhalt.add(this.figur);
        inhalt.userData.genesisErsatz = Fotogenesisnetz.ersatz(d?.modus ?? 'textur');
        if (d?.rig) inhalt.add(this.rigZeichnen());
    }

    /** Das Skelett der Testfigur: die Punkte `ausgabe`, auf die Körper und Stücke gelegt sind, Zeichnung wie auf der Mesh-Genesis-Testseite (`Meshgenesisrigzeichner`).
     *  Als `nurAnsicht` markiert: Hülle und Rendering für Feld 3 und den Vergleich lassen es aus (`Fotogenesiskamera.huelle`, `Fotogenesisvergleich.rendern`). */
    rigZeichnen() {
        const beschr = this.probe.rig;
        const gruppe = Meshgenesisrigzeichner.zeichnen(beschr, beschr.knochen.map((_k, j) => j), this.probe.ausgabe);
        gruppe.traverse(o => { o.userData.nurAnsicht = true; });
        return gruppe;
    }

    fertig() {
        return !!this.figur;
    }

    /** Echte Fotos haben keinen gemessenen Rahmen. */
    rahmen() {
        return null;
    }
}
