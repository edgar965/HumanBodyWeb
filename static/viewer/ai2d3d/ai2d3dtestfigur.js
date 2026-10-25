/**
 * Ai2d3dtestfigur — Feld 3 „Genesis-Modell“ eines Tests aus echten Fotos (24.10.2026): die Ausgabe des Mesh3D-AI-Tests zum selben Netz (`mesh3dai_test` in der `job.json`).
 *
 * Edgar: „Ich sehe den job nicht mit den bildern“ — bis dahin zeigte ein Fotojob in Feld 3 nur einen Verweis auf die Testseite. Gebaut wird wie auf der Testseite (`Mesh3daitestseite._figurBauen`):
 * Anzeigenetz (`Mesh3daiflaechennetz`) mit den Knochenmatrizen der vorhergesagten Haltung gehäutet (`Mesh3daitestnetzbau`), aus `/api/mesh3dai/test/<kennung>/`. Dazu (24.10.2026 abends):
 *  - Kleider und Haar aus der KI, wie die Testseite sie gewählt hat (`Mesh3daikikleiderfeld`) — Schalter „Kleider“ zeigt sie oder nur den Körper;
 *  - die Augäpfel (`kleider_<g>/k/ki_augen`, `KopfKI.Augenstueck`): die Anzeige der Testfigur hat leere Augenhöhlen, die Bilder der Karte „Kopf“ zeigen Augäpfel — Edgar: „das Genesis
 *    ergebnis und bild ergebnis oben zeigen was anderes als die bilder unten“;
 *  - die Ansichtsart der Leiste (Ersatzmaterial auf Ebene 1 wie `Ai2d3dnetz`; vorher wirkte kein Schalter auf Feld 3).
 * Dieselbe Schnittstelle wie `Ai2d3dgenesis` (`bereit`, `probe`, `auftrag`, `fertig`, `zeichnen`, `rahmen`).
 */
import * as THREE from 'three';
import { Mesh3daiflaechennetz } from '../mesh3dai/mesh3daiflaechennetz.js';
import { Mesh3daigenesisfigur } from '../mesh3dai/mesh3daigenesisfigur.js';
import { Mesh3daihaeutung } from '../mesh3dai/mesh3daihaeutung.js';
import { Mesh3daikikleiderfeld } from '../mesh3dai/mesh3daikikleiderfeld.js';
import { Mesh3dairigzeichner } from '../mesh3dai/mesh3dairigzeichner.js';
import { Mesh3daitestnetzbau } from '../mesh3dai/mesh3daitestnetzbau.js';
import { Ai2d3dnetz } from './ai2d3dnetz.js';

export class Ai2d3dtestfigur {
    /** @param {{kennung: string, adresse: string}} test aus den Seitendaten (`Ai2d3dseitendaten`) */
    constructor(test) {
        this.test = test;
        this.probe = null;           // die Antwort der Testschnittstelle, sobald die Figur gebaut ist
        this.figur = null;
        this.kleider = null;
        this.koerper = null;         // {an, aus}: Körper mit der Haut unter allen Stücken weg bzw. nur unter dem Haar
        this.augen = null;
        this.fehler = '';
        this.text = '';
        // Ein Bild des Anzeigenetzes kommt nach: dieselbe Meldung wie bei einer fertigen Genesis-Figur, die Seite zeichnet neu — und rendert Feld 4 nach (`nachgeladen`, gesetzt von
        // `Ai2d3dseite`): vorher waren die Texturen beim Rendern noch nicht da, die Figur in Feld 4 kam schwarz (gesehen 24.10.2026).
        this.nachgeladen = null;
        Mesh3daiflaechennetz.nachLaden = () => { Mesh3daigenesisfigur.neuZeichnen?.(); this.nachgeladen?.(); };
        this.bereit = this._bauen();
    }

    async _bauen() {
        try {
            const antwort = await fetch(this.test.adresse);
            const daten = await antwort.json();
            if (!antwort.ok) throw new Error(daten.error || `HTTP ${antwort.status}`);
            const matrizen = Mesh3daihaeutung.ausDrehungen(daten.dreh, daten.ausgabe, daten.ruhezentren);
            const netz = await Mesh3daiflaechennetz.holen(daten.job, daten.figur_netz);
            const geschlecht = String(daten.figur_netz).split('/').filter(Boolean).pop();
            this.figur = new THREE.Group();
            // Haut unter den Stücken weglassen wie die Mesh3D-AI-Testseite (`Mesh3daitestkleider.verdeckt` → `Mesh3daitestnetzbau.mesh(…, verdeckt)`). Bis 24.10.2026 20 Uhr fehlte das hier:
            // gemessen im Chrome zeichnete der Körper alle 64.632 Dreiecke, die Haut stach durch Shorts und Socken, das Genital hing unter den Shorts (Abnahme über `Ai2d3dseitenbild`).
            // Zwei Körper: mit allen Stücken verdeckt, und nur unter dem Haar (Schalter „Kleider“ aus).
            const liste = await fetch(`${this.test.adresse}kleider/${geschlecht}/`).then(a => (a.ok ? a.json() : null)).catch(() => null);
            const anzahl = netz.dreiecke.length / 3;
            // Unter einer Hose kein Genital (24.10.2026 abends, Edgar: „fixe!“): das Anatomie-Stück hing unter den Shorts frei — im Foto trägt Edgar es IN den Shorts. Die
            // Anatomieverdeckung von Mesh3D-AI nimmt nur weg, was durch den Stoff sticht; ein Stück, das unter dem Saum heraushängt, bleibt. Abnahme `lauf6_messpunkte`: Oberschenkel
            // innen 33–43 mm zu breit, dort lag das Genital in der Beinlücke.
            const an = Ai2d3dtestfigur.verdeckt(liste, anzahl, false);
            if (an && Ai2d3dtestfigur.hose(liste)) for (const t of Ai2d3dtestfigur.anatomie(netz)) an[t] = 1;
            this.koerper = { an: Mesh3daitestnetzbau.mesh(netz, matrizen, an),
                             aus: Mesh3daitestnetzbau.mesh(netz, matrizen, Ai2d3dtestfigur.verdeckt(liste, anzahl, true)) };
            this.figur.add(this.koerper.an, this.koerper.aus);
            this._bau = { netz, an, aus: Ai2d3dtestfigur.verdeckt(liste, anzahl, true), liste: `${this.test.adresse}kleider/${geschlecht}/`, augen: null };
            this.augen = await Mesh3daiflaechennetz.holen(null, `${this.test.adresse}kleid/${geschlecht}/k/ki_augen`)
                .then(n => { this._bau.augen = n; return Mesh3daitestnetzbau.mesh(n, matrizen); })
                .catch(fehler => { console.warn(`Ai2d3dtestfigur: keine Augäpfel (${fehler.message})`); return null; });
            if (this.augen) this.figur.add(this.augen);
            this.kleider = await Mesh3daikikleiderfeld.laden({ liste: `${this.test.adresse}kleider/${geschlecht}/`, dreh: daten.dreh, rig: daten.ausgabe, ruhezentren: daten.ruhezentren })
                .catch(fehler => { console.warn(`Ai2d3dtestfigur: Kleider nicht geladen (${fehler.message})`); return null; });
            if (this.kleider) this.figur.add(this.kleider.gruppe);
            this.figur.traverse(o => { o.layers.set(1); o.frustumCulled = false; });
            this.figur.userData.mesh3daiFremd = true;          // gehört nicht dem Feld (`Mesh3daiansicht._leeren` gibt es dann nicht frei)
            // `Mesh3daikikleiderfeld` beschriftet Weg k als „aus dem Netz geschnitten“ — hier sind die Stücke aus den Fotos geschnitten (`Fotoschale`)
            if (this.kleider && this.test.eigen) this.kleider.namen = this.kleider.namen.map(n => n.replace('aus dem Netz geschnitten', 'aus den Fotos geschnitten'));
            this.text = (this.test.eigen ? `Genesis-Modell dieses Jobs (<Job>/figur/, ${daten.info?.name ?? ''}) in der Haltung aus den Fotos`
                : `Ausgabe des Mesh3D-AI-Tests ${this.test.kennung} (${daten.info?.name ?? ''}) in der Haltung aus dem Netz`) + (this.augen ? ', mit Augäpfeln' : '')
                + `${this.kleider ? `, ${this.kleider.namen.join(', ')}` : ''}.`;
            this.probe = daten;
        } catch (fehler) {
            this.fehler = `Figur des Tests ${this.test.kennung} nicht gebaut: ${fehler.message}`;
            console.warn(`Ai2d3dtestfigur: ${this.fehler}`);
        }
    }

    /**
     * Dieselbe Figur in einer anderen Haltung (Haltung je Foto, Auftrag EdgarTrip 24.10.2026): Körper, Augen und Kleider mit den Knochenmatrizen dieser Haltung neu gehäutet, sichtbar wie
     * die gezeigte Figur. Für `Ai2d3dseitenbild` — die vier Fotos entstanden nacheinander, jedes in eigener Haltung. @returns {Promise<THREE.Group>}
     */
    async inHaltung(dreh, ausgabe) {
        const b = this._bau, matrizen = Mesh3daihaeutung.ausDrehungen(dreh, ausgabe, this.probe.ruhezentren);
        const gruppe = new THREE.Group();
        const an = Mesh3daitestnetzbau.mesh(b.netz, matrizen, b.an), aus = Mesh3daitestnetzbau.mesh(b.netz, matrizen, b.aus);
        an.visible = this.koerper.an.visible;
        aus.visible = this.koerper.aus.visible;
        gruppe.add(an, aus);
        if (b.augen) gruppe.add(Mesh3daitestnetzbau.mesh(b.augen, matrizen));
        if (this.kleider) {
            const k = await Mesh3daikikleiderfeld.laden({ liste: b.liste, dreh, rig: ausgabe, ruhezentren: this.probe.ruhezentren });
            k.gruppe.visible = this.kleider.gruppe.visible;
            gruppe.add(k.gruppe);
        }
        gruppe.traverse(o => { o.layers.set(1); o.frustumCulled = false; });
        return gruppe;
    }

    /**
     * Die Dreiecke des Körpers unter den Stücken der Kleiderliste (Server: `verdeckt` = Bits je Dreieck, base64, little-endian; dieselbe Lesart wie `Mesh3daitestkleider.verdeckt`).
     * `nurHaar`: nur unter dem Haar. → Uint8Array (1 = weglassen) oder null.
     */
    static verdeckt(liste, anzahl, nurHaar) {
        let aus = null;
        for (const st of liste?.stuecke || []) {
            const bits = st.wahl !== 'aus' && (!nurHaar || st.art === 'haar') ? st[st.wahl]?.verdeckt : null;
            if (!bits) continue;
            aus ??= new Uint8Array(anzahl);
            const bytes = Uint8Array.from(atob(bits), c => c.charCodeAt(0));
            for (let t = 0; t < anzahl; t++) if (bytes[t >> 3] & (1 << (t & 7))) aus[t] = 1;
        }
        return aus;
    }

    /** Trägt die Figur eine Hose (ein gewähltes Stück der Art „hose“)? */
    static hose(liste) {
        return (liste?.stuecke || []).some(st => st.wahl !== 'aus' && st.art === 'hose');
    }

    /** Die Dreiecke des Anatomie-Stücks im Anzeigenetz (Material „daz_anatomie_…“). */
    static anatomie(netz) {
        const m = (netz.kopf?.materialien || []).findIndex(x => /anatomie/i.test(x.name || ''));
        const aus = [];
        if (m >= 0) for (let t = 0; t < netz.material.length; t++) if (netz.material[t] === m) aus.push(t);
        return aus;
    }

    auftrag(quelle, modus, kleider, rig = false) {
        return { echt: true, zeile: 'test', quelle, modus, kleider, rig };
    }

    /** Zeichner von `Mesh3daiansicht`: `d` aus `auftrag` — Kleider (mit Haar) ein/aus, Ansichtsart als Ersatzmaterial, Rig (Knopf „Rig“) darüber. */
    zeichnen(inhalt, _art, d) {
        if (!this.figur) {
            inhalt.userData.hinweis = this.fehler || 'Figur des Tests wird gebaut …';
            return;
        }
        const an = d?.kleider !== false;
        if (this.kleider) this.kleider.gruppe.visible = an;
        this.koerper.an.visible = an;
        this.koerper.aus.visible = !an;
        inhalt.add(this.figur);
        inhalt.userData.genesisErsatz = Ai2d3dnetz.ersatz(d?.modus ?? 'textur');
        if (d?.rig) inhalt.add(this.rigZeichnen());
    }

    /** Das Skelett der Testfigur: dieselben Punkte (`ausgabe`), mit denen die Figur gehäutet ist, Zeichnung wie auf der Mesh3D-AI-Testseite (`Mesh3dairigzeichner`, ohne Tiefentest).
     *  Als `nurAnsicht` markiert: Hülle und Rendering für Feld 3 und den Vergleich lassen es aus (`Ai2d3dkamera.huelle`, `Ai2d3dvergleich.rendern`). */
    rigZeichnen() {
        const beschr = this.probe.rig;
        const gruppe = Mesh3dairigzeichner.zeichnen(beschr, beschr.knochen.map((_k, j) => j), this.probe.ausgabe);
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
