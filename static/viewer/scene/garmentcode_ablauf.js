import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeSchnitt } from './garmentcode_schnitt.js';
import { GarmentcodeDrapierung } from './garmentcode_drapieren.js';
import { GarmentcodePanels } from './garmentcode_panels.js';
import { GarmentcodeVorschau3d } from './garmentcode_vorschau3d.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { Laufwache } from '../gemeinsam/laufwache.js';

/**
 * GarmentcodeAblauf — was auf einen Knopfdruck hin passiert.
 *
 * DREI KNOEPFE, EIN ABLAUF (Edgar, 07.09.2026: „insgesamt dann 3 Buttons:
 * Einmal 2D, einmal 3D und einmal alles komplett (2d + 3d)").
 *
 * Herausgeloest aus `garmentcode.js`, die dabei auf 329 Zeilen gewachsen
 * waere — die Regel ist, dass eine Datei beim Anfassen nicht ueber ihre
 * Grenze waechst (`~/.claude/rules/struktur.md`). Im Reiter bleibt, was
 * die Oberflaeche betrifft: Knoepfe, Auswahl, Zustand. Hier steht der
 * Ablauf, und er nimmt den Reiter als Gegenueber entgegen.
 */
export class GarmentcodeAblauf {

    /**
     * Drei Wege, ein Ablauf (Edgar, 07.09.2026: „insgesamt dann 3 Buttons:
     * Einmal 2D, einmal 3D und einmal alles komplett (2d + 3d)").
     *
     *     '2d'        Schnitt konstruieren und die Panels an die Figur legen
     *     '3d'        den vorhandenen Schnitt drapieren, Panels wieder weg
     *     'komplett'  beides hintereinander
     *
     * `'3d'` baut den Schnitt NICHT neu. Es prüft aber, ob der vorhandene
     * zu dieser Figur und dieser Vorlage gehört: Ein Schnitt liegt als
     * Ordner auf der Platte, und wer die Figur wechselt und dann 3D
     * drückt, drapierte sonst den Schnitt der vorigen — dieselbe Falle wie
     * am 06.09.2026, als ein Bau ohne Morphs den Ergebnisordner
     * überschrieb und eine Stunde Messläufe auf dem falschen Schnitt
     * rechneten.
     */
    /**
     * Die fuenf Wege (Edgar, 08.09.2026: fuenf Knoepfe, Vorschau 2D
     * und 3D neben Bauen 2D, 3D und 2D+3D).
     *
     *   vorschau2d   Schnitt, Panels an die Figur gelegt     ~0,4 s
     *   vorschau3d   Panels an den Koerper gelegt            0,4-1,0 s
     *   2d           wie vorschau2d, aber mit allen Dateien  ~0,4 s
     *   3d           echte Warp-Simulation                    ~23 s
     *   komplett     2d + 3d                                  ~31 s
     *
     * Gemessen ist der 2D-Schritt mit 364-391 ms schon Vorschau-
     * Geschwindigkeit. Genau deshalb ist der Vorschau-Knopf dafuer
     * wieder entfallen: Zwei Knoepfe fuer dieselbe Rechnung, die sich
     * nur darin unterscheiden, was danach gezeigt wird, sind einer zu
     * viel.
     */
    static NUR3D = ['3d', 'vorschau3d'];
    static VORSCHAU = ['vorschau2d', 'vorschau3d'];

    static async bauen(reiter, modus = 'komplett') {
        const meldung = document.getElementById('gc-meldung');
        const wache = GarmentcodeAblauf.frei(reiter, meldung);
        if (!wache.darf) return;
        const figur = reiter.figur();
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt — bitte links in der '
                + 'Charakterliste eine anklicken. Der Schnitt wird aus ihren '
                + 'Maßen gebaut.';
            return;
        }
        const vorlage = document.getElementById('gc-vorlage').value;
        // Beide 3D-Wege setzen einen Schnitt voraus, der zu DIESER Figur
        // und DIESEM Stueck gehoert. Ohne die Pruefung wuerde der Schnitt
        // der vorigen Figur drapiert — die Falle vom 06.09.2026.
        if (GarmentcodeAblauf.NUR3D.includes(modus)
                && !GarmentcodeAblauf.schnittPasst(reiter, figur, vorlage)) {
            meldung.textContent = 'Für diese Figur und dieses Stück liegt '
                + 'kein Schnitt bereit — erst „2D", dann „3D".';
            return;
        }
        const knoepfe = ['gc-vorschau-2d', 'gc-vorschau-3d',
                         'gc-bauen-2d', 'gc-bauen-3d',
                         'gc-bauen-beides']
            .map(k => document.getElementById(k)).filter(Boolean);

        // Der Lauf wird SOFORT abgesichert: Zwischen dem Setzen von
        // `laeuft` und dem `try` darf nichts stehen, was werfen kann —
        // sonst bliebe der Reiter besetzt und alle drei Knoepfe grau,
        // ohne dass je ein `finally` liefe.
        const lauf = GarmentcodeAblauf.beginnen(reiter, knoepfe);
        try {
            // Der Hinweis auf einen VERLORENEN Vorlauf bleibt stehen — er ist
            // das einzige Wort darueber, dass hier etwas haengengeblieben war.
            if (wache.grund !== 'verloren') meldung.textContent = '';
            // Gesagt, nicht verhindert: Ein Grundkoerper ist auch eine Figur.
            reiter.ohneMorphs = GarmentcodeFigur.ohneMorphs(figur);
            garmentcodeFortschritt.starten(
                GarmentcodeAblauf.schritte(reiter, modus));
            if (!GarmentcodeAblauf.NUR3D.includes(modus)
                    && !await GarmentcodeAblauf.schnittteil(reiter, figur, meldung, vorlage)) {
                return;
            }
            await GarmentcodeAblauf.dreid(reiter, modus, figur, meldung, vorlage);
            garmentcodeFortschritt.beenden();
        } catch (fehler) {
            // Nur der AKTUELLE Lauf darf melden. Ein alter, laengst
            // aufgegebener Lauf, dessen Anfrage doch noch zurueckkommt,
            // ueberschriebe sonst die Meldung des neuen.
            if (Laufwache.aktuell(reiter, lauf)) {
                garmentcodeFortschritt.gescheitert(
                    GarmentcodeAblauf.NUR3D.includes(modus) ? 'drape' : 'schnitt',
                    String(fehler.message || fehler));
                meldung.textContent = `Fehler: ${fehler.message || fehler}`;
            }
        } finally {
            GarmentcodeAblauf.beenden(reiter, knoepfe, lauf);
        }
    }

    /**
     * Ist der Reiter frei — und wenn nicht, sagt er es.
     *
     * @returns den Stand der `Laufwache` (`{darf, grund, seit}`)
     *
     * Die Entscheidung trifft `Laufwache` (ohne DOM, deshalb pruefbar);
     * hier steht nur, was der Nutzer davon zu sehen bekommt. Frueher stand
     * an dieser Stelle `if (reiter.laeuft) return;` — stumm, und damit die
     * Ursache des Befundes vom 08.09.2026.
     */
    static frei(reiter, meldung) {
        const stand = Laufwache.pruefen(reiter);
        if (stand.grund === 'besetzt' && meldung) {
            meldung.textContent = `Es läuft noch ein Bau (seit ${stand.seit} s) `
                + '— bitte abwarten, die Knöpfe kommen von selbst zurück.';
        } else if (stand.grund === 'verloren' && meldung) {
            meldung.textContent = `Der vorige Bau meldet sich seit ${stand.seit} s `
                + 'nicht mehr — er gilt als verloren, dieser Klick übernimmt.';
        }
        return stand;
    }

    /** Den Reiter besetzen und die Knoepfe sperren. */
    static beginnen(reiter, knoepfe) {
        const lauf = Laufwache.beginnen(reiter);
        knoepfe.forEach(k => { k.disabled = true; });
        return lauf;
    }

    /** Freigeben — nur, wenn dieser Lauf noch der aktuelle ist. */
    static beenden(reiter, knoepfe, lauf) {
        if (!Laufwache.beenden(reiter, lauf)) return false;
        knoepfe.forEach(k => { k.disabled = false; });
        garmentcodeFortschritt.beenden();
        return true;
    }

    /**
     * Schnitt bauen, merken, und bei `2d` gleich an die Figur legen.
     *
     * @returns `false`, wenn der Schnitt nicht baut (die Meldung steht
     *          dann schon im Feld)
     */
    static async schnittteil(reiter, figur, meldung, vorlage) {
        const ergebnis = await GarmentcodeSchnitt.bauen(reiter, figur, meldung);
        if (!ergebnis) {
            garmentcodeFortschritt.entfallen('panels');
            garmentcodeFortschritt.entfallen('drape');
            garmentcodeFortschritt.entfallen('rig');
            return false;
        }
        reiter.spezifikation = ergebnis.spezifikation || null;
        // Der Ergebnisordner: „Vorschau 3D" liest daraus die Panels. Die
        // Spezifikation allein reicht dort nicht — sie ist ein Pfad auf
        // eine Datei, der Ordner enthaelt auch das Boxmesh.
        reiter.ordner = ergebnis.ordner || '';
        // Woher der Schnitt stammt — die Probe für den 3D-Knopf.
        reiter.schnittVon = { figur: figur.id, vorlage };
        return true;
    }

    /** Gehört der gemerkte Schnitt zu dieser Figur und diesem Stück? */
    static schnittPasst(reiter, figur, vorlage) {
        return Boolean(reiter.spezifikation && reiter.schnittVon
            && reiter.schnittVon.figur === figur.id
            && reiter.schnittVon.vorlage === vorlage);
    }

    /**
     * Die Schritte im Voraus — dann weiss der Nutzer, was kommt und dass die
     * Drapierung der lange Teil ist. Die erwarteten Dauern sind gemessene
     * Werte (Schnitt 4 s und Panels unter 1 s am 07.09.2026, Drapierung
     * 22 s im Browser und Anziehen 3 s am 06.09.2026).
     */
    static schritte(reiter, modus) {
        const schritte = [];
        if (modus === 'vorschau3d') {
            return [{ schluessel: 'vorschau3d', erwartet: 1,
                      titel: 'Am Körper anlegen' }];
        }
        if (!GarmentcodeAblauf.NUR3D.includes(modus)) {
            schritte.push({ schluessel: 'schnitt', erwartet: 4,
                            titel: 'Schnitt konstruieren' });
        }
        if (modus === '2d' || modus === 'vorschau2d') {
            schritte.push({ schluessel: 'panels', erwartet: 1,
                            titel: 'Panels an die Figur' });
        }
        if (reiter.drapierbereit && modus !== '2d'
                && modus !== 'vorschau2d') {
            schritte.push({ schluessel: 'drape', erwartet: 22,
                            titel: 'Stoff drapieren' });
            schritte.push({ schluessel: 'rig', erwartet: 3,
                            titel: 'Anziehen' });
        }
        return schritte;
    }

    /**
     * Der 3D-Teil — oder bei `2d` die flachen Panels an der Figur.
     *
     * Die Panels fliegen weg, sobald drapiert wird: Der simulierte Stoff
     * liegt an derselben Stelle, und beide zusammen sähen aus wie ein
     * Fehler.
     */
    static async dreid(reiter, modus, figur, meldung, vorlage) {
        if (modus === 'vorschau3d') {
            await GarmentcodeVorschau3d.zeigen(reiter, figur, meldung, vorlage);
            return;
        }
        if (modus === '2d' || modus === 'vorschau2d') {
            garmentcodeFortschritt.laeuft('panels');
            const anzahl = await GarmentcodePanels.zeigen(
                figur, reiter.spezifikation, vorlage);
            garmentcodeFortschritt.fertig('panels', `${anzahl} Panels`);
            meldung.textContent += anzahl
                ? ` — ${anzahl} Panels liegen an der Figur. „Vorschau 3D" `
                  + 'legt sie an den Körper, „Bauen 3D" simuliert den Stoff.'
                : ' — die Panels liessen sich nicht anlegen.';
            return;
        }
        GarmentcodePanels.entfernen(figur);
        // Auch das Vorschaunetz weicht: Es liegt an derselben Stelle wie der
        // simulierte Stoff, und beide zusammen saehen aus wie ein Fehler.
        GarmentcodeVorschau3d.entfernen(figur);
        if (reiter.drapierbereit && reiter.spezifikation) {
            await GarmentcodeDrapierung.drapieren(
                reiter, figur, reiter.spezifikation, meldung, vorlage);
            return;
        }
        garmentcodeFortschritt.entfallen('drape');
        garmentcodeFortschritt.entfallen('rig');
        if (!reiter.drapierbereit) {
            meldung.textContent += ' — nur Schnittmuster, die '
                + 'Simulationsumgebung fehlt.';
        }
    }
}
