/**
 * GarmentCode-Reiter — Kleidung aus Körpermaßen konstruieren.
 *
 * Der Gegenentwurf zum Assets-Reiter: dort wird ein fertiges Netz an den
 * Körper angepasst und sitzt nicht (gemessen am 06.09.2026: 14,3 % der
 * `.mhclo`-Anker fallen auf EINEN Körpervertex, Shrinkwrap liefert bis 36 %
 * Vertices im Körper). Hier wird der Schnitt aus Maßen gebaut — wo nichts
 * angepasst wird, kann nichts verrutschen.
 *
 * BEDIENUNG (Edgar, 06.09.2026: „T-Shirt auswählen, bauen"): Ein Knopf. Die
 * Maße kommen aus der gewählten Figur — mit ihren Reglerwerten, nicht aus dem
 * Grundkörper — und werden im Hintergrund geholt, während der Nutzer schon
 * das Kleidungsstück wählt. Sie sind Anzeige, keine Eingabe.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { fn } from '../gemeinsam/registrierung.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { GarmentcodeMasse } from './garmentcode_masse.js';
import { GarmentcodeAblauf } from './garmentcode_ablauf.js';
import { GarmentcodeLive } from './garmentcode_live.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { garmentcodeKombi } from './garmentcode_kombi.js';

class GarmentcodeReiter {
    constructor() {
        // Der Laufzustand, den `Laufwache` fuehrt: besetzt, seit wann, und
        // die laufende Nummer. Ohne `laeuftSeit` koennte ein haengender Bau
        // nie als verloren erkannt werden.
        this.laeuft = false;
        this.laeuftSeit = 0;
        this.laufnummer = 0;
        this.zustandDa = false;
        this.drapierbereit = false;
        this.aufgeklappt = false;
        /** Für welche Figur die Maße im Panel stehen. */
        this.masseFuer = null;
    }

    /**
     * Einhängen — notfalls erst, wenn das DOM steht.
     *
     * `boot.js` importiert dieses Modul; je nachdem, wann das geschieht,
     * gibt es den Reiter noch nicht. Ein `querySelector` liefert dann null,
     * und ohne diese Weiche bräche `starten()` still ab: kein Klick-Handler,
     * kein Zustand, ein Reiter, in dem nichts passiert.
     */
    starten() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.einhaengen(),
                                      { once: true });
        } else {
            this.einhaengen();
        }
    }

    /** Knopf-Kennung -> Modus von `GarmentcodeAblauf.bauen`. */
    static KNOEPFE = {
        'gc-vorschau-2d': 'vorschau2d',
        'gc-vorschau-3d': 'vorschau3d',
        'gc-bauen-2d': '2d',
        'gc-bauen-3d': '3d',
        'gc-bauen-beides': 'komplett',
    };

    einhaengen() {
        const reiter = document.querySelector('.panel-tab[data-tab="garmentcode"]');
        if (!reiter) return;
        reiter.addEventListener('click', () => this.oeffnen());

        // Fuenf Knoepfe, zwei Zeilen (Edgar, 08.09.2026). Die Tabelle
        // statt einzelner Zeilen: Bei der dritten Aenderung stand hier
        // dreimal dasselbe Muster mit je einem anderen Namen.
        for (const [kennung, modus] of Object.entries(GarmentcodeReiter.KNOEPFE)) {
            document.getElementById(kennung)?.addEventListener(
                'click', () => this.bauen(modus));
        }

        // Ein anderes Kleidungsstück hat andere Einstellungen — eine Hose
        // hat keinen Kragen. Deshalb bei jedem Wechsel neu holen.
        const auswahl = document.getElementById('gc-vorlage');
        if (auswahl) {
            auswahl.addEventListener('change',
                () => garmentcodeRegler.laden(auswahl.value));
        }

        // Die Regler formen das 2D-Modell, sobald eines steht (08.09.2026).
        GarmentcodeLive.einhaengen(this);

        // Farbe, Rauheit und Metallgrad (08.09.2026). Das Material kennt den
        // Reiter nicht — es fragt über diesen Geber nach der Figur, sonst
        // hinge es an der Bedienung und wäre nicht für sich prüfbar.
        GarmentcodeMaterial.figurgeber = () => this.figur();
        GarmentcodeMaterial.einhaengen();

        // Mehrere Stuecke in EINEM Lauf (09.09.2026). Die Liste haengt
        // sich selbst ein und stellt her, was zuletzt darin stand; ohne
        // Knoepfe im DOM kehrt sie von selbst um.
        garmentcodeKombi.einhaengen(this);

        // Vorlagen und Regler brauchen keine Figur — sofort holen, damit im
        // Reiter etwas steht, bevor jemand ihn anklickt.
        this.zustandLaden();
    }

    /**
     * Beim Öffnen: Inhalt zeigen, Maße nebenher holen.
     *
     * Der Inhalt bleibt IMMER sichtbar — Vorlagen und Einstellungen kann man
     * ansehen, ohne eine Figur zu wählen. Ohne Figur ist nur der Bau-Knopf
     * gesperrt, mit Hinweis daneben. (Vorher war der ganze Reiter leer,
     * sobald `state.selectedCharacterId` nicht gesetzt war.)
     */
    oeffnen() {
        const figur = this.figur();
        const inhalt = document.getElementById('gc-content');
        if (inhalt) inhalt.classList.remove('hb-versteckt');
        // Den Knopf NICHT sperren: Ein gesperrter Knopf ohne Erklärung ist
        // das, was "tut nichts" heißt. Fehlt die Figur, sagt der Klick es.
        const hinweis = document.getElementById('gc-empty');
        if (hinweis) hinweis.classList.toggle('hb-versteckt', !!figur);

        this.aufklappen();
        this.zustandLaden();
        if (figur && this.masseFuer !== figur.id) this.masseLaden();
    }

    /**
     * Beim ERSTEN Öffnen die beiden wichtigen Abschnitte aufklappen.
     *
     * Alle `panel-section` starten mit `collapsed` — bei einem eingeführten
     * Reiter ist das richtig, bei einem neuen sieht man dann nur vier
     * Überschriften und hält den Reiter für leer. Danach entscheidet wieder
     * der Nutzer: Wer zuklappt, findet es zugeklappt wieder.
     */
    aufklappen() {
        if (this.aufgeklappt) return;
        this.aufgeklappt = true;
        // `gc_bauen` und `gc_passform` stehen seit dem 09.09.2026
        // ohne Ueberschrift und damit immer offen; hier bleibt
        // nur, was sich noch zuklappen laesst.
        for (const schluessel of ['gc_regler']) {
            const bereich = document.querySelector(
                `#tab-garmentcode [data-panel-key="${schluessel}"]`);
            if (bereich) bereich.classList.remove('collapsed');
        }
    }

    /** Die gewählte Figur — Entscheidung in `GarmentcodeFigur`. */
    figur() {
        return GarmentcodeFigur.gewaehlt();
    }

    /** Was der Server über die Figur bekommt — je Quelle verschieden. */
    figurdaten(figur) {
        return GarmentcodeFigur.formulardaten(figur);
    }

    // ------------------------------------------------------------- Zustand

    async zustandLaden() {
        if (this.zustandDa) return;
        const feld = document.getElementById('gc-status');
        try {
            const zustand = await Serverabruf.json('/api/garmentcode/zustand/');
            this.zustandDa = true;
            if (!zustand.vorhanden) {
                feld.textContent = zustand.hinweis || 'GarmentCode fehlt.';
                return;
            }
            this.drapierbereit = !!zustand.drapierbereit;
            const dreid = this.drapierbereit
                ? '3D-Drapierung bereit'
                : 'nur Schnittmuster (Simulation nicht eingerichtet)';
            feld.textContent = `Bereit — ${zustand.entwuerfe.length} Vorlagen, ${dreid}.`;
            this.vorlagenFuellen(zustand.entwuerfe);
            const auswahl = document.getElementById('gc-vorlage');
            if (auswahl && auswahl.value) garmentcodeRegler.laden(auswahl.value);
        } catch (fehler) {
            feld.textContent = `Status nicht abrufbar: ${fehler.message || fehler}`;
        }
    }

    /**
     * Die Liste kommt aus `GarmentCode/katalog.py` — fertige Kombinationen
     * der drei Bausteine (Oberteil, Bund, Unterteil), unter deutschen Namen.
     * Die zwei Dateien in `design_params` waren nie die Auswahl, sondern nur
     * zwei Beispiele.
     */
    vorlagenFuellen(entwuerfe) {
        const auswahl = document.getElementById('gc-vorlage');
        if (!auswahl || !entwuerfe.length) return;
        auswahl.innerHTML = '';
        for (const stueck of entwuerfe) {
            const eintrag = document.createElement('option');
            eintrag.value = stueck.name;
            eintrag.textContent = stueck.titel || stueck.name;
            auswahl.appendChild(eintrag);
        }
    }

    // ---------------------------------------------------------------- bauen

    // ---------------------------------------------------------------- bauen

    /** Der Ablauf steht in `garmentcode_ablauf.js`. */
    async bauen(modus = 'komplett') {
        return GarmentcodeAblauf.bauen(this, modus);
    }


    // --------------------------------------------------------------- Maße

    /** Die Maßliste steht in `garmentcode_masse.js`. */
    async masseLaden() {
        return GarmentcodeMasse.laden(this);
    }

    /**
     * Eine Vorlage im Reiter wählen — wie ein Klick des Nutzers.
     *
     * WARUM ÜBER DAS EREIGNIS: Am `change` des Auswahlfeldes hängen ZWEI
     * Hörer — das Nachladen der Regler und das `Reitergedaechtnis`. Der
     * Klick auf ein Kleidungsstück in der Szene IST eine Wahl des
     * Nutzers; sie soll beim nächsten Aufruf wieder dastehen.
     *
     * ANDERSWO GILT DAS GEGENTEIL, und das ist gemessen (09.09.2026):
     * `Garmentdeutung` setzt seine Auswahl weiter still. Sie leitet die
     * Vorlage aus einem Bibliotheksstück AB — über diesen Weg gemerkt,
     * stand sie danach in einem fremden Tab, denn der `localStorage` ist
     * über alle Tabs derselben Herkunft geteilt.
     *
     * @returns `true`, wenn es diese Vorlage in der Liste gibt
     */
    vorlageZeigen(vorlage) {
        const auswahl = document.getElementById('gc-vorlage');
        if (!auswahl || !vorlage) return false;
        const gibtes = [...auswahl.options].some(o => o.value === vorlage);
        if (!gibtes) return false;
        if (auswahl.value === vorlage) return true;
        auswahl.value = vorlage;
        auswahl.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    }
}

export const garmentcodeReiter = new GarmentcodeReiter();
garmentcodeReiter.starten();

// Der Klick auf ein Kleidungsstueck in der Szene waehlt seine Vorlage
// (`teilnetz_auswahl.js`). Ueber die Registrierung, damit die Auswahl
// nicht den ganzen Reiter importieren muss.
fn.garmentcodeVorlageZeigen = (vorlage) =>
    garmentcodeReiter.vorlageZeigen(vorlage);
