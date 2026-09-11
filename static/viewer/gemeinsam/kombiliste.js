/**
 * Kombiliste — welche Kleidungsstücke gemeinsam angezogen werden sollen.
 *
 * WARUM EINE LISTE UND NICHT MEHRFACHAUSWAHL (09.09.2026): Der Reiter zeigt
 * die Feineinstellungen von GENAU EINEM Stück — beim T-Shirt 71 Regler, bei
 * der Hose andere. Wer zwei Stücke gemeinsam bauen will, muss deshalb erst
 * das eine einstellen, es übernehmen, dann das zweite. Die Liste hält von
 * jedem Stück die Reglerwerte fest, mit denen es übernommen wurde.
 *
 * DIE WERTE WERDEN KOPIERT, nicht verwiesen: `garmentcodeRegler.werte` ist
 * EIN Objekt, das bei jedem Reglerzug weitergeschrieben wird. Ein Verweis
 * darauf hiesse, dass das Einstellen des zweiten Stücks rückwirkend das
 * erste ändert — ohne dass in der Liste etwas anders aussähe.
 *
 * Ohne DOM, deshalb prüfbar (`test_js_kombiliste.py`).
 */
export class Kombiliste {

    /**
     * Muss zu `Garmentgemeinsam.HOECHSTZAHL` passen. Die Grenze ist
     * Vorsicht, keine Physik: Jedes Stück kostet Punkte im gemeinsamen
     * Netz und damit Simulationszeit.
     */
    static HOECHSTZAHL = 4;

    /** Ablage im Browser — je Herkunft, überlebt das Schliessen. */
    static SCHLUESSEL = 'hb_gc_kombination';

    constructor() {
        /** @type {{vorlage: string, titel: string, regler: object, bau: object,
         *           material: object|null}[]} */
        this.eintraege = [];
    }

    get anzahl() {
        return this.eintraege.length;
    }

    /**
     * Ein Stück übernehmen.
     *
     * Dasselbe Stück zweimal ist ERLAUBT (zwei Röcke übereinander, mit
     * verschiedenen Reglern); der Server numeriert die Panels dann durch.
     *
     * @returns {{ok: boolean, grund?: string}}
     */
    hinzufuegen(vorlage, titel, regler, bau = null, material = null) {
        if (!vorlage) return { ok: false, grund: 'Kein Kleidungsstück gewählt.' };
        if (this.eintraege.length >= Kombiliste.HOECHSTZAHL) {
            return { ok: false, grund: `Höchstens ${Kombiliste.HOECHSTZAHL} `
                     + 'Stücke auf einmal.' };
        }
        this.eintraege.push({
            vorlage,
            titel: titel || vorlage,
            // Flache Kopie genügt: Die Werte sind Zahlen, Zeichenketten
            // und Wahrheitswerte, keine verschachtelten Objekte.
            regler: { ...(regler || {}) },
            // Die Bauregler (Hautabstand, Netzfeinheit, Anliegen) gehören
            // zum Stück wie seine Schnittwerte: Die Leggings brauchen ihr
            // Anliegen, das T-Shirt darüber nicht (11.09.2026).
            bau: { ...(bau || {}) },
            // Farbe, Rauheit, Metall, Gewebe — je Stück, tief kopiert (das
            // Gewebe ist ein Objekt). Bleibt im Browser: Der Server baut
            // Geometrie, das Material legt `garmentcode_gemeinsam.js` auf.
            // Ohne das bekam jedes Stück die zuletzt eingestellte Farbe
            // (Edgar, 11.09.2026: „es wurde nur 1 Farbe genommen").
            material: material ? JSON.parse(JSON.stringify(material)) : null,
        });
        return { ok: true };
    }

    entfernen(nummer) {
        if (nummer < 0 || nummer >= this.eintraege.length) return false;
        this.eintraege.splice(nummer, 1);
        return true;
    }

    leeren() {
        this.eintraege = [];
    }

    /** Was der Server bekommt — Titel bleiben im Browser. */
    fuerServer() {
        return this.eintraege.map((e) => ({ vorlage: e.vorlage,
                                            regler: e.regler,
                                            bau: e.bau || {} }));
    }

    /**
     * Darf gebaut werden?
     *
     * Ein einzelnes Stück wird abgelehnt statt still durchgereicht: Der
     * gewöhnliche Weg baut es schneller, und ein „gemeinsamer" Lauf mit
     * einem Stück wäre eine Behauptung, die nicht stimmt.
     */
    darfBauen() {
        if (this.eintraege.length < 2) {
            return { ok: false, grund: 'Mindestens zwei Stücke übernehmen — '
                     + 'ein einzelnes baut „2D + 3D" schneller.' };
        }
        return { ok: true };
    }

    /**
     * Die Liste in den Browser-Speicher schreiben.
     *
     * Jeder Zugriff ist umschlossen: In einem privaten Fenster wirft schon
     * das Lesen, und dann darf die Liste leer starten statt die Seite zu
     * zerlegen.
     */
    sichern(ablage) {
        const speicher = ablage || Kombiliste._speicher();
        if (!speicher) return false;
        try {
            speicher.setItem(Kombiliste.SCHLUESSEL,
                             JSON.stringify(this.eintraege));
            return true;
        } catch (fehler) {
            return false;
        }
    }

    /** Die gemerkte Liste holen; unbrauchbarer Inhalt wird übergangen. */
    laden(ablage) {
        const speicher = ablage || Kombiliste._speicher();
        if (!speicher) return false;
        let roh = null;
        try {
            roh = speicher.getItem(Kombiliste.SCHLUESSEL);
        } catch (fehler) {
            return false;
        }
        if (!roh) return false;
        try {
            const gelesen = JSON.parse(roh);
            if (!Array.isArray(gelesen)) return false;
            this.eintraege = gelesen
                .filter((e) => e && typeof e.vorlage === 'string')
                .slice(0, Kombiliste.HOECHSTZAHL)
                .map((e) => ({ vorlage: e.vorlage, titel: e.titel || e.vorlage,
                               regler: (e.regler && typeof e.regler === 'object')
                                   ? e.regler : {},
                               bau: (e.bau && typeof e.bau === 'object')
                                   ? e.bau : {},
                               material: (e.material && typeof e.material === 'object')
                                   ? e.material : null }));
            return true;
        } catch (fehler) {
            return false;
        }
    }

    static _speicher() {
        try {
            return (typeof localStorage === 'undefined') ? null : localStorage;
        } catch (fehler) {
            return null;
        }
    }
}
