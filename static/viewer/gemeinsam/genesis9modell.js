import * as THREE from 'three';
import { Serverabruf } from './serverabruf.js';
import { Netzentsorgung } from './netzentsorgung.js';
import { Protokoll } from './protokoll.js';
import { Eigenhaut } from './eigenhaut.js';
import { Genesis9hautmischung } from './genesis9hautmischung.js';
import { Oberflaechenbindung } from './oberflaechenbindung.js';
// Nebenwirkung des Imports: die Hautverdeckung hoert auf Stueck- und Skelettereignis —
// damit bekommt JEDE Seite, die eine Genesis-9-Figur baut (Szene, Studio, Theatre,
// Ergebnisseite), die Maske unter der Kleidung (21.09.2026, Konzept Fitting, Schicht 1).
import './hautverdeckung.js';
import { Genesis9netz } from './genesis9netz.js';
import { Genesis9aufbau } from './genesis9aufbau.js';
import { Genesis9kleidung } from './genesis9kleidung.js';
import { Modell } from './modell.js';
import { Skelettereignis } from './skelettereignis.js';

/**
 * Genesis9Modell — die Daz-Figur Genesis 9 als `Modell` für jede Seite.
 *
 * WARUM (Edgar, 17.09.2026: „baue das Genesis9 Modell als zusätzliches neues
 * Modell ein, mit allem drum und dran"): Genesis 9 ist das dichteste
 * Figurnetz im Haus (25.182 Punkte, 4K-Haut je Kachel, 138 Knochen, 1.486
 * Morphkanäle) und liegt installiert auf diesem Rechner. Der Server liest
 * die Daz-Dateien direkt (`Genesis9/`, ohne Daz Studio); nichts davon geht
 * ins Repo (EULA — `Genesis9/HERKUNFT.md`).
 *
 * WAS EINE FIGUR HIER IST: ein Katalogeintrag (`figur`: basis, feminine,
 * masculine, amala, …) — das ist eine REGLERSTELLUNG plus Haut, kein
 * eigenes Netz — dazu `regler` (Daz' Morphkanäle, 0..1 oder −2..2), `haut`
 * (Preset, leer = das des Eintrags), `augen` (Bild 01–15) und `kleidung`
 * (Kennung → {variante, stil, stile, regler, griff}). Ein Stück mit `griff`
 * ist ein Prop mit Griffpose (Dolch): der Körper bekommt die Kennungen als
 * `griffe`, damit sich die Finger schließen (18.09.2026). Der Server liefert
 * in EINER Antwort Körper, Skelett (gerechnet auf dieser Stellung — die
 * Gelenke wandern mit den Morphs), Haut und die Anhänge (Augen, Mund,
 * Wimpern, Träne, Brauen); alle hängen am selben Skelett über Knochennamen
 * (`Eigenhaut`). ERST DAS SKELETT, DANN DIE NETZE — `Eigenhaut.binden` löst
 * die Knochennamen gegen das Skelett in der Gruppe auf. Bei jedem Reglerzug
 * wird alles neu gebaut, auch die Kleidung (sie sitzt auf projizierten
 * Körperpunkten). Der ERSTE Bau kommt in zwei Zügen — Käfig sofort, volle
 * Stufe nach (`Genesis9aufbau`, 18.09.2026 nachts); `_lauf` verwirft
 * Antworten eines überholten Zugs.
 */
export class Genesis9Modell extends Modell {

    static QUELLE = 'genesis9';
    static ADRESSE = '/api/character/genesis9-figur/';

    constructor(id, daten = {}) {
        super(id, Genesis9Modell.QUELLE);
        this.figur = daten.figur || 'basis';
        this.presetName = daten.presetName || `Genesis 9 · ${this.figur}`;
        this.bodyType = 'Genesis 9';
        /** Daz-Morphkanäle: `{Amala_figure_ctrl_Character: 1}`; null = Vorgabe des Eintrags. */
        this.regler = daten.regler ? { ...daten.regler } : null;
        /** Hautpreset (`G9 Feminine Skin 02 MAT`); leer = das des Eintrags. */
        this.haut = daten.haut || '';
        /** Augenbild 01–15. */
        this.augen = daten.augen || '01';
        /** Farbe der Brauen (`Brown`, `omni:Ruby`, `charakter:…`); leer = Vorgabe des Servers. */
        this.brauen = daten.brauen || '';
        /** Brauenstil `card01`..`card12`, `fiber01`..`fiber09`; leer = Karte 01. */
        this.brauenstil = daten.brauenstil || '';
        /** Wimpern, Nagellack, Rouge, Lidschatten, Eyeliner, Lippen, Bemalung: Kategorie → Preset-Id. */
        this.praesets = { ...(daten.praesets || {}) };
        /** Texturmischung (21.09.2026): weitere Hautsätze mit Prozent über der Haut (`Genesis9hautmischung`). */
        this.hautmischung = { ...(daten.hautmischung || {}) };
        /** Daz-Posenpreset (Standbild: Netz UND Skelett stehen in der Pose) und Ausdruck (FACS). */
        this.pose = daten.pose || '';
        this.ausdruck = daten.ausdruck || '';
        /** Getragene Stücke in Anziehreihenfolge: Kennung → `{variante}`; Netze in `clothMeshes`,
         *  Lagen (`{innen, aussen}`, `Genesis9kleidung`) in `lagen`. */
        this.kleidung = { ...(daten.kleidung || {}) }; this.lagen = {};
        /** Die Anhänge: Schlüssel → Netz. */
        this.anhangNetze = {};
        this.hoehe = 0;
        /** Punkte des Daz-Käfigs (25.182); `browserpunkte` und `stufen` sagen, was gezeichnet wird. */
        this.punktzahl = 0; this.browserpunkte = 0; this.stufen = 0;
        this.morphwerte = {}; this.gelenkregler = {};
    }

    // ------------------------------------------------------------- Bauen

    async bauen() {
        if (this.regler === null) await this._vorgabeUebernehmen();
        return Genesis9aufbau.progressiv(this);
    }

    /** Die Reglerstellung des Katalogeintrags — vom Server, nicht geraten. */
    static async vorgabe(figur) {
        return { ...((await Genesis9Modell.eintrag(figur))?.regler || {}) };
    }

    /** Der Katalogeintrag (Bibliothek oder gespeichertes Modell) — oder null. */
    static async eintrag(figur) {
        const daten = await Serverabruf.json(Genesis9Modell.ADRESSE);
        return (daten.figuren || []).find(f => f.name === figur) || null;
    }

    /**
     * Regler des Eintrags übernehmen — und bei einem GESPEICHERTEN Modell
     * (Studio, Theatre: dort ist nur der Name bekannt, 17.09.2026) auch Haut,
     * Augen, Brauen und Kleidung, soweit hier nichts gesetzt ist.
     */
    async _vorgabeUebernehmen() {
        const eintrag = await Genesis9Modell.eintrag(this.figur);
        this.regler = { ...(eintrag?.regler || {}) };
        if (!eintrag?.gespeichert) return;
        if (!this.haut) this.haut = eintrag.haut || '';
        if (this.augen === '01' && eintrag.augen) this.augen = eintrag.augen;
        if (!this.brauen) this.brauen = eintrag.brauen || '';
        if (!this.brauenstil) this.brauenstil = eintrag.brauenstil || '';
        if (!Object.keys(this.praesets).length) this.praesets = { ...(eintrag.praesets || {}) };
        if (!Object.keys(this.hautmischung).length) this.hautmischung = { ...(eintrag.hautmischung || {}) };
        if (!this.pose) this.pose = eintrag.pose || '';
        if (!this.ausdruck) this.ausdruck = eintrag.ausdruck || '';
        if (!Object.keys(this.kleidung).length) this.kleidung = { ...(eintrag.kleidung || {}) };
    }

    /**
     * Körper, Skelett und Anhänge holen und neu einhängen (`stufen`: null = Stufe des
     * Browsers).
     *
     * `skelettFrisch`: Regler- und Posenzüge (`neuFormen`) können Gelenke verschieben —
     * das ganze `THREE.Skeleton` muss neu; ein reiner Material-/Presetwechsel (Haut,
     * Augen, Brauen, Makeup: `hautSetzen` & Co.) bewegt KEINEN Knochen. Trotzdem riss
     * `koerperAufbauen` bis 22.09.2026 bei JEDEM Aufruf das Skelett ab und neu auf und
     * feuerte `Skelettereignis` — das stößt Hautverdeckung (2,4 s je Umbau,
     * `genesis9-passform.md`) und die GarmentCode-Nachbindung neu an, für eine reine
     * Augenfarbe (Edgar, 22.09.2026: „nicht immer Skelett umbauen, das dauert auch ewig
     * im UI"). Jetzt bleibt das Skelett stehen, wenn der Aufrufer weiß, dass er es nicht
     * bewegt hat — `!this.skelett` erzwingt den ersten Bau trotzdem.
     */
    async koerperAufbauen(stufen = null, skelettFrisch = true) {
        const lauf = this._lauf = (this._lauf || 0) + 1;
        const daten = await Serverabruf.senden(Genesis9aufbau.adresse(
            `${Genesis9Modell.ADRESSE}${encodeURIComponent(this.figur)}/netz/`, stufen), {
                regler: this.regler || {}, haut: this.haut, augen: this.augen,
                brauen: this.brauen, brauenstil: this.brauenstil, praesets: this.praesets,
                pose: this.pose, ausdruck: this.ausdruck, griffe: this.griffe(),
                kleidung: this.kleidungsliste(),
            });
        if (daten.fehler) throw new Error(daten.fehler);
        if (lauf !== this._lauf) return this;          // überholt: ein neuer Zug läuft
        this._altesWeg();
        const neuesSkelett = skelettFrisch || !this.skelett;
        if (neuesSkelett) {
            // Mit den eigenen Knochen der getragenen Stücke (Eirgrid: 14 Zöpfe an
            // `spine4`); ihre Namen bekommt der Zopfschwung (`genesis9zopfschwung.js`).
            this.skelettBauen(daten.skelett);
            this.eigeneKnochen = daten.skelett?.eigene || [];
        }
        this.bodyMesh = this._einhaengen(
            Genesis9netz.bauen(daten, `genesis9_koerper_${this.id}`), daten.hautgewichte);
        this.isSkinned = !!this.bodyMesh.isSkinnedMesh;
        for (const anhang of daten.anhaenge || []) {
            this.anhangNetze[anhang.schluessel] = this._einhaengen(
                Genesis9netz.bauen(anhang, `genesis9_${anhang.schluessel}_${this.id}`),
                anhang.hautgewichte);
        }
        this.hoehe = daten.hoehe || 0;
        this.punktzahl = daten.punktzahl || 0;
        this.browserpunkte = daten.browserpunkte || daten.vertex_count || 0;
        this.stufen = daten.stufen || 0;
        this.morphwerte = daten.morphwerte || {};
        this.gelenkregler = daten.gelenkregler || {};   // JCM-Schalter (`genesis9gelenke.js`)
        /** Wirksame HD-Morphkanäle (`Genesis9/hdmorphe.py`) — auf Stufe 1, mit Strg+Alt+H auch 2. */
        this.hdkanaele = daten.hdkanaele || [];
        this._kleiderBinden(neuesSkelett);
        // Frische Materialien: die Texturmischung neu einhängen (Bilder aus dem Vorrat).
        if (Object.keys(this.hautmischung).length) Genesis9hautmischung.anwenden(this);
        Protokoll.debug('Genesis9Modell',
            `${this.figur}: ${this.punktzahl} Punkte, Stufe ${this.stufen} `
            + `(${this.browserpunkte}), ${(this.hoehe * 100).toFixed(1)} cm, `
            + `${Object.keys(this.morphwerte).length} Morphs wirksam`);
        return this;
    }

    /** Ein Netz binden (wenn Gewichte da sind) und in die Gruppe hängen. */
    _einhaengen(netz, haut) {
        const gebunden = (this.skelett && haut) ? Eigenhaut.binden(netz, this.skelett, haut) : netz;
        gebunden.userData.hautgewichte = haut || null;
        Eigenhaut.einhaengen(this.group, gebunden, this.skelett);
        // Anliegende Kleidung folgt der Oberflaeche je Bild (Attribute aus `Genesis9kleidung`).
        Oberflaechenbindung.verdrahten(this, gebunden);
        return gebunden;
    }

    _altesWeg() {
        if (this.bodyMesh) Netzentsorgung.entfernen(this.group, this.bodyMesh);
        this.bodyMesh = null;
        for (const netz of Object.values(this.anhangNetze)) {
            Netzentsorgung.entfernen(this.group, netz);
        }
        this.anhangNetze = {};
    }

    /**
     * Die getragenen Stücke an das FRISCHE Skelett binden — `skelettBauen` räumt je Aufruf
     * ab; eine alte Bindung zeigte auf Knochen außerhalb der Szene (MakeHuman, 07.09.2026).
     * GarmentCode-Stücke bindet die Szene nach dem `Skelettereignis` um (19.09.2026).
     *
     * `skelettNeu = false` (22.09.2026): das Skelett-OBJEKT ist dasselbe geblieben (reiner
     * Material-/Presetwechsel, siehe `koerperAufbauen`) — die bestehende Bindung der
     * Stücke gilt weiter, ein Umbinden und das `Skelettereignis` (GarmentCode-Nachbindung,
     * Hautverdeckung) wären hier reine Verschwendung.
     */
    _kleiderBinden(skelettNeu = true) {
        if (!this.skelett || !skelettNeu) return;
        for (const [schluessel, altes] of Object.entries(this.clothMeshes)) {
            const haut = altes?.userData?.hautgewichte; if (!haut) continue;
            this.group.remove(altes);
            const roh = new THREE.Mesh(altes.geometry, altes.material);
            roh.name = altes.name; roh.userData = altes.userData;
            // Stranghaar prüft Klicks selbst (`Genesis9strangtreffer`, eigene Eigenschaft
            // des Netzes) — ohne das war Viola nach dem ersten Reglerzug wieder unwählbar.
            if (Object.hasOwn(altes, 'raycast')) roh.raycast = altes.raycast;
            this.clothMeshes[schluessel] = this._einhaengen(roh, haut);
        }
        Skelettereignis.melden(this);
    }

    // ------------------------------------------------------------ Regler

    /** Nach einem Reglerzug: Körper, Anhänge UND Kleidung neu — gleichzeitig. */
    async neuFormen() {
        return Genesis9aufbau.alles(this, null);
    }

    async reglerSetzen(name, wert) {
        this.regler = this.regler || {};
        if (Math.abs(wert) < 1e-6) delete this.regler[name];
        else this.regler[name] = wert;
        return this.neuFormen();
    }

    // Haut, Augen, Brauen und Makeup-Presets bewegen keinen Knochen — `koerperAufbauen`
    // bekommt `skelettFrisch = false` und lässt das Skelett unangetastet (siehe dort).

    async hautSetzen(preset) {
        this.haut = preset || '';
        return this.koerperAufbauen(null, false);
    }

    async augenSetzen(nummer) {
        this.augen = nummer || '01';
        return this.koerperAufbauen(null, false);
    }

    async brauenSetzen(farbe) {
        this.brauen = farbe || '';
        return this.koerperAufbauen(null, false);
    }

    async brauenstilSetzen(stil, farbe = undefined) {
        this.brauenstil = stil || '';
        if (farbe !== undefined) this.brauen = farbe || '';
        return this.koerperAufbauen(null, false);
    }

    /** Ein Preset einer Kategorie wählen (leer = keins). */
    async praesetSetzen(kategorie, kennung) {
        if (kennung) this.praesets[kategorie] = kennung;
        else delete this.praesets[kategorie];
        return this.koerperAufbauen(null, false);
    }

    /** Ein Hautsatz der Texturmischung auf Prozent (0 = raus) — ohne Neubau des Körpers:
     *  Gewichte sind Uniforms; nur eine neue oder verschwundene Schicht baut die Programme um. */
    async hautmischungSetzen(id, prozent) {
        if (prozent > 0) this.hautmischung[id] = Math.min(100, Math.round(prozent));
        else delete this.hautmischung[id];
        if (!Genesis9hautmischung.gewichte(this)) await Genesis9hautmischung.anwenden(this);
        return this;
    }

    /** Pose oder Ausdruck (leer = Ruhelage) — die Kleidung sitzt auf der Pose, also alles neu. */
    async poseSetzen(feld, kennung) {
        this[feld === 'ausdruck' ? 'ausdruck' : 'pose'] = kennung || '';
        return this.neuFormen();
    }

    // ---------------------------------------------------------- Kleidung

    /**
     * Ein Stück der Daz-Garderobe anziehen — alle seine Teile, über den getragenen
     * Stücken darunter (`Genesis9kleidung`; `kaskade`: die Stücke darüber neu holen).
     * `werte`: `{variante, stil, stile: {pose, laenge}, regler, griff}` — die
     * Stile gehen als Liste (`Genesis9garderobe.werte`), je Art eine Wahl.
     */
    anziehen(kennung, werte = null, stufen = null, kaskade = true) {
        return Genesis9kleidung.anziehen(this, kennung, werte, stufen, kaskade);
    }

    static stilliste(werte) { return Genesis9kleidung.stilliste(werte); }

    /**
     * Anziehen — und die Figur neu, wenn das Stück das Skelett ändert: ein
     * Prop mit Griffpose (Finger), ein Haar mit eigenen Knochen (Zöpfe — sie
     * hängen im Browser-Skelett, ihre Pose steckt in dessen Stellung).
     */
    async anziehenMitGriff(kennung, werte = null) {
        if (!werte?.griff && !werte?.knochen) return this.anziehen(kennung, werte);
        this.kleidung[kennung] = { ...werte };
        return this.neuFormen();
    }

    /** Ausziehen — Griffpose öffnet die Finger, eigene Knochen verlassen das Skelett (Figur neu);
     *  sonst holt `Genesis9kleidung` die Stücke neu, die über dem ausgezogenen lagen. */
    ausziehen(kennung) {
        return Genesis9kleidung.ausziehen(this, kennung,
            Boolean(this.kleidung[kennung]?.griff || this.kleidung[kennung]?.knochen));
    }

    /** Kennungen der getragenen Props mit Griffpose. */
    griffe() {
        return Object.keys(this.kleidung).filter(k => this.kleidung[k]?.griff);
    }

    /** `[{kennung, stil}]` aller getragenen Stücke — der Server hängt deren eigene Knochen ins Skelett. */
    kleidungsliste() {
        return Object.entries(this.kleidung).map(([kennung, werte]) => ({
            kennung, stil: Genesis9Modell.stilliste(werte),
        }));
    }

    _stueckWeg(kennung) {
        for (const schluessel of Object.keys(this.clothMeshes)) {
            if (schluessel.split('/')[0] === kennung) {
                Netzentsorgung.ausAblage(this.group, this.clothMeshes, schluessel);
            }
        }
    }

    getragen() {
        return Object.keys(this.kleidung);
    }

    // ------------------------------------------------------------- Größe

    sichtbareHoehe() {
        return this.hoehe * (this.group.scale.y || 1);
    }

    aufHoehe(meter) {
        if (!(meter > 0) || !(this.hoehe > 0)) return;
        this.group.scale.setScalar(meter / this.hoehe);
        this.group.updateMatrixWorld(true);
    }

    dispose() {
        // Erst das Skelett abhängen (`Knochenbau.abraeumen`), dann Netze und Gruppe.
        this.skelettBauen(null);
        super.dispose();
        this.bodyMesh = null;
        this.anhangNetze = {};
        this.clothMeshes = {};
    }
}
