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
import { garmentcodeRegler } from './garmentcode_regler.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeDrapierung } from './garmentcode_drapieren.js';
import { GarmentcodeSchnitt } from './garmentcode_schnitt.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { GarmentcodeMasse } from './garmentcode_masse.js';

class GarmentcodeReiter {
    constructor() {
        this.laeuft = false;
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

    einhaengen() {
        const reiter = document.querySelector('.panel-tab[data-tab="garmentcode"]');
        if (!reiter) return;
        reiter.addEventListener('click', () => this.oeffnen());

        const knopf = document.getElementById('gc-erzeugen');
        if (knopf) knopf.addEventListener('click', () => this.bauen());
        // Nur der 2D-Teil (Edgar, 07.09.2026). Gemessen 6,12 s gegen 31 s
        // fuer den ganzen Weg — wer am Schnitt schraubt, wartet ein
        // Fuenftel.
        const nur2d = document.getElementById('gc-schnitt');
        if (nur2d) nur2d.addEventListener('click', () => this.bauen(true));

        // Ein anderes Kleidungsstück hat andere Einstellungen — eine Hose
        // hat keinen Kragen. Deshalb bei jedem Wechsel neu holen.
        const auswahl = document.getElementById('gc-vorlage');
        if (auswahl) {
            auswahl.addEventListener('change',
                () => garmentcodeRegler.laden(auswahl.value));
        }

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
        for (const schluessel of ['gc_bauen', 'gc_regler']) {
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

    /**
     * Bauen — mit `nurSchnitt` endet es beim Schnittmuster.
     *
     * Der 2D-Knopf ist kein zweiter Weg, sondern derselbe ohne die beiden
     * langen Schritte: Der Balken zeigt dann nur „Schnitt konstruieren",
     * und `spezifikation` bleibt stehen, sodass ein anschliessendes
     * „Fuer diese Figur bauen" ohne Neubau weitermachen koennte.
     */
    async bauen(nurSchnitt = false) {
        if (this.laeuft) return;
        const meldung = document.getElementById('gc-meldung');
        const figur = this.figur();
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt — bitte links in der '
                + 'Charakterliste eine anklicken. Der Schnitt wird aus ihren '
                + 'Maßen gebaut.';
            return;
        }
        const knoepfe = [document.getElementById('gc-erzeugen'),
                         document.getElementById('gc-schnitt')].filter(Boolean);

        this.laeuft = true;
        knoepfe.forEach(k => { k.disabled = true; });
        meldung.textContent = '';
        // Gesagt, nicht verhindert: Ein Grundkörper ist auch eine Figur.
        this.ohneMorphs = GarmentcodeFigur.ohneMorphs(figur);
        garmentcodeFortschritt.starten(this.schritte(nurSchnitt));

        try {
            const ergebnis = await GarmentcodeSchnitt.bauen(this, figur, meldung);
            if (!ergebnis) {
                garmentcodeFortschritt.entfallen('drape');
                garmentcodeFortschritt.entfallen('rig');
                return;
            }
            this.spezifikation = ergebnis.spezifikation || null;
            await this.dreid(nurSchnitt, figur, meldung);
            garmentcodeFortschritt.beenden();
        } catch (fehler) {
            garmentcodeFortschritt.gescheitert('schnitt',
                                               String(fehler.message || fehler));
            meldung.textContent = `Fehler: ${fehler.message || fehler}`;
        } finally {
            this.laeuft = false;
            knoepfe.forEach(k => { k.disabled = false; });
            garmentcodeFortschritt.beenden();
        }
    }

    /**
     * Die Schritte im Voraus — dann weiss der Nutzer, was kommt und dass die
     * Drapierung der lange Teil ist. Die erwarteten Dauern sind gemessene
     * Werte (06.09.2026: Schnitt 4 s, Drapierung 22 s im Browser, Anziehen
     * 3 s) und gewichten den Balken.
     */
    schritte(nurSchnitt) {
        const schritte = [
            { schluessel: 'schnitt', titel: 'Schnitt konstruieren', erwartet: 4 },
        ];
        if (this.drapierbereit && !nurSchnitt) {
            schritte.push({ schluessel: 'drape', erwartet: 22,
                            titel: 'Stoff drapieren' });
            schritte.push({ schluessel: 'rig', erwartet: 3,
                            titel: 'Anziehen' });
        }
        return schritte;
    }

    /**
     * Und jetzt ohne weiteres Zutun an die Figur (Edgar, 06.09.2026: „bei
     * Bauen soll das Garment gleich auf den Körper gebracht werden, ohne
     * extra Klick").
     */
    async dreid(nurSchnitt, figur, meldung) {
        if (nurSchnitt) {
            meldung.textContent += ' — nur der Schnitt. „Für diese Figur '
                + 'bauen" legt ihn auf die Figur.';
            return;
        }
        if (this.drapierbereit && this.spezifikation) {
            await GarmentcodeDrapierung.drapieren(
                this, figur, this.spezifikation, meldung,
                document.getElementById('gc-vorlage').value);
            return;
        }
        garmentcodeFortschritt.entfallen('drape');
        garmentcodeFortschritt.entfallen('rig');
        if (!this.drapierbereit) {
            meldung.textContent += ' — nur Schnittmuster, die '
                + 'Simulationsumgebung fehlt.';
        }
    }


    // --------------------------------------------------------------- Maße

    /** Die Maßliste steht in `garmentcode_masse.js`. */
    async masseLaden() {
        return GarmentcodeMasse.laden(this);
    }
}

export const garmentcodeReiter = new GarmentcodeReiter();
garmentcodeReiter.starten();
