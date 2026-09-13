import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Knochenbau } from './knochenbau.js';
import { Eigenhaut } from './eigenhaut.js';
import { Umapythonnetz } from './umapythonnetz.js';
import { Modell } from './modell.js';

/**
 * UmapythonModell — eine echte UMA-Figur, in Python gebaut; `Modell` für jede Seite.
 *
 * WARUM DIESE FIGURART (Edgar, 08.09.2026: „Ich möchte doch ein Male,
 * Female, Elf usw. auswählen, genau so wie UMA das macht!")
 * ====================================================================
 * Vorher stand hier ein Prüfstand für die Kleidungs-Anpassung: ein
 * GarmentCode-Referenzkörper mit einem drapierten Stück. Der Name versprach
 * etwas anderes — Edgar hat zu Recht gefragt, warum da ein SMPL-Modell kommt.
 *
 * Jetzt baut sie wirklich. Rasse aus UMAs Katalog (20 Stück, darunter Elf,
 * HalfOrc, Sylvan, Sprite), Netz und Skelett aus den binären Assets, Form
 * über die 62 DNA-Regler — alles in Python, ohne Unity.
 *
 * WAS DAS KOSTET, UND WARUM ES ZWEI WEGE GIBT
 * ===========================================
 * Der erste Bau einer Rasse dauert 6 bis 14 s (acht Slot-Assets, davon fünf
 * über 2 MB). Danach hält der Server die gebaute Figur, und ein Reglerzug
 * kostet nur noch die Knochen- und Hautrechnung — gemessen 0,07 s.
 *
 * Die Felder sind dieselben wie bei `SmplModell` und `UmaModell`, damit Liste,
 * Auswahl, Zählung und Speichern nicht je Quelle unterscheiden.
 *
 * Seit 13.09.2026 in `gemeinsam/`; die Szene erbt als `UmapythonModell` nur das
 * Speichern (siehe dort; ohne es bricht die Undo-Aufnahme).
 */
export class UmapythonModell extends Modell {

    static QUELLE = 'umapython';
    static ADRESSE = '/api/umapython/figur/';
    static RASSEN = '/api/umapython/rassen/';

    /** Hautton — die Overlays (Texturen) rechnet der Port nicht mit. */
    static FARBE = 0xc9a086;

    constructor(id, daten) {
        super(id, UmapythonModell.QUELLE);
        this.rasse = daten.rasse || 'Human Female 3.0';
        this.presetName = daten.presetName || `UMA Python · ${this.rasse}`;
        this.bodyType = this.rasse;
        /** Reglerstellungen, die vom Rezept abweichen. */
        this.dna = { ...(daten.dna || {}) };
        /** Was der Server über die Regler dieser Rasse sagt. */
        this.regler = [];
        this.bilanz = null;
        this.hoehe = 0;
    }

    /** Die Rassen des Katalogs — Male, Female, Elf stehen vorn. */
    static async rassen() {
        const daten = await Serverabruf.json(UmapythonModell.RASSEN);
        return daten?.rassen || [];
    }

    async bauen() {
        await this._holen();
        Protokoll.debug('UmapythonModell',
            `${this.rasse}: ${this.bilanz?.punkte} Punkte, `
            + `${this.bilanz?.knochen} Knochen, ${this.bilanz?.hoehe_m} m`);
        return this;
    }

    /**
     * Einen Regler stellen und die Figur neu rechnen.
     *
     * Der Server hält die gebaute Figur; hier läuft nur die Knochen- und
     * Hautrechnung (gemessen 0,07 s gegen 6–14 s für den Bau).
     */
    async reglerSetzen(name, wert) {
        this.dna[name] = wert;
        return this._holen();
    }

    async _holen() {
        const daten = await Serverabruf.senden(UmapythonModell.ADRESSE, {
            rasse: this.rasse,
            dna: this.dna,
        });
        if (daten.fehler) throw new Error(daten.fehler);
        this._setzen(daten);
        return daten.bilanz;
    }

    /**
     * ERST DAS SKELETT, DANN DAS NETZ, DANN BINDEN.
     *
     * Die Reihenfolge ist kein Geschmack: `Eigenhaut.binden` löst die
     * Knochennamen der Gewichte gegen das Skelett auf, das in der Szene
     * hängt. Wer das Netz zuerst baut und später ein neues Skelett
     * darunterschiebt, bindet gegen Knochen, die nicht mehr da sind — bei
     * MakeHuman war genau das der Grund, warum die Kleider still starr
     * blieben (07.09.2026).
     */
    _setzen(daten) {
        this.bilanz = daten.bilanz || null;
        this.regler = daten.regler || [];
        this.bodyType = daten.rasse || this.rasse;
        this._skelettSetzen(daten.skelett);
        this._netzSetzen(daten.netz, daten.haut);
        this.hoehe = Number(daten.bilanz?.hoehe_m) || 0;
    }

    /**
     * Das Körpernetz austauschen — und an das eigene Skelett binden.
     *
     * Geometrie und Material werden NEU gebaut und die alten freigegeben:
     * Die Punktzahl bleibt je Rasse gleich, aber ein `setAttribute` auf eine
     * noch gezeichnete Geometrie ist die teurere Wette als ein sauberer
     * Tausch bei EINEM Netz je Figur.
     */
    _netzSetzen(netz, haut) {
        if (!netz || !netz.punkte?.length) return;
        const name = `umapython_koerper_${this.id}`;
        Umapythonnetz.entfernen(this.group, name);
        const roh = Umapythonnetz.bauen(netz, name, this.rasse, this.rasse);
        const gebunden = this.skelett
            ? Eigenhaut.binden(roh, this.skelett, haut) : roh;
        // `einhaengen` bindet mit `netz.matrix`, also in der Lage der
        // FIGURGRUPPE — nicht mit deren Weltmatrix. Mit `group.matrix`
        // gemessen: In Ruhe wanderte jeder Punkt um exakt 900 mm, den
        // Gruppenversatz, weil er zweimal verrechnet wurde. Dieselbe
        // Falle wie bei den GarmentCode-Stücken am 07.09.2026.
        Eigenhaut.einhaengen(this.group, gebunden, this.skelett);
        this.bodyMesh = gebunden;
        this.isSkinned = !!gebunden.isSkinnedMesh;
    }

    /**
     * Das Skelett — über `Knochenbau`, wie bei SMPL und MakeHuman.
     *
     * WARUM NICHT MEHR VON HAND (Edgar, 08.09.2026: „UMA Python skeletn
     * fehlt auch")
     * ==========================================================
     * Die frühere Fassung baute die Kette selbst und legte sie als
     * `{wurzel, knochen, halter}` ab. `Rigauswahl` sucht aber
     * `inst.skelett.rootBone` — dieses Feld gab es nicht, und deshalb blieb
     * der Rig-Schalter für diese Figurart wirkungslos, obwohl die Knochen
     * längst in der Szene hingen.
     *
     * `Knochenbau` liefert genau die Form, die Rigauswahl, Skelettanzeige
     * und `Eigenhaut` erwarten — `{skeleton, rootBone, bones, boneByName}` —
     * und setzt die Ruhedrehungen mit, ohne die keine Bewegung richtig
     * ankommt.
     *
     * DAS ALTE SKELETT MUSS WEG, BEVOR DAS NEUE KOMMT: `_holen` läuft bei
     * jedem Reglerzug erneut; ohne Abräumen hängen nach zehn Zügen zehn
     * Skelette ineinander (Befund 07.09.2026).
     */
    _skelettSetzen(daten) {
        if (!daten?.knochen?.length) return;
        this.skelett = Knochenbau.abraeumen(this.skelett);
        this.skelett = Knochenbau.bauen(daten, this.group);
    }

    dispose() {
        // Erst das Skelett abhaengen, dann Netze und Gruppe (Modell).
        this.skelett = Knochenbau.abraeumen(this.skelett);
        super.dispose();
        this.bodyMesh = null;
        this.clothMeshes = {};
    }


}
