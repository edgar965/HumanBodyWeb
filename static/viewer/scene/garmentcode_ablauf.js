import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeSchnitt } from './garmentcode_schnitt.js';
import { GarmentcodeDrapierung } from './garmentcode_drapieren.js';
import { GarmentcodePanels } from './garmentcode_panels.js';
import { GarmentcodeVorschau3d } from './garmentcode_vorschau3d.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { Laufwache } from '../gemeinsam/laufwache.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeSchritte } from './garmentcode_schritte.js';

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
    /**
     * EINE Quelle: `GarmentcodeSchritte` entscheidet ebenfalls daran, ob ein
     * Schnittschritt in den Plan kommt. Zwei Listen desselben Inhalts laufen
     * beim naechsten neuen Modus auseinander — dann baut der eine Weg einen
     * Schnitt, den der andere nicht erwartet.
     */
    static NUR3D = GarmentcodeSchritte.NUR3D;
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
            meldung.textContent = GarmentcodeAblauf.warumNicht(reiter, figur,
                                                               vorlage);
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
            // WAS gebaut wird, steht ab jetzt im Reiter (09.09.2026). An
            // diesem Tag hat der Server „sommerkleid" gebaut, waehrend Edgar
            // eine Hose erwartete: Die Deutung eines Bibliotheksstuecks hatte
            // die Auswahl still umgestellt. Der Name im Meldungsfeld macht
            // einen solchen Zustand sofort sichtbar — vorher stand dort bis
            // zum Ende des Schnitts gar nichts.
            //
            // Der Hinweis auf einen VERLORENEN Vorlauf bleibt stehen — er ist
            // das einzige Wort darueber, dass hier etwas haengengeblieben war.
            if (wache.grund !== 'verloren') {
                meldung.textContent = `Baue „${GarmentcodeAblauf.titel(vorlage)}" …`;
            }
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

    /** Die Beschriftung der Vorlage — der Nutzer kennt „Hose", nicht `hose`. */
    static titel(vorlage) {
        const auswahl = document.getElementById('gc-vorlage');
        const eintrag = [...(auswahl?.options || [])]
            .find((o) => o.value === vorlage);
        return eintrag ? eintrag.textContent.trim() : vorlage;
    }

    /**
     * Warum der vorhandene Schnitt nicht genommen wird.
     *
     * Der veraltete Schnitt ist der häufigere Fall und braucht eine andere
     * Auskunft als „gar keiner da" — sonst sucht man den Fehler bei der
     * Figur, während nur ein Regler seit dem letzten Schnitt bewegt wurde.
     */
    static warumNicht(reiter, figur, vorlage) {
        if (reiter.spezifikation && reiter.schnittVon
                && reiter.schnittVon.figur === figur.id
                && reiter.schnittVon.vorlage === vorlage) {
            return 'Die Einstellungen haben sich seit dem letzten Schnitt '
                + 'geändert — erst „2D", dann „3D". (Sonst würde der alte '
                + 'Schnitt drapiert.)';
        }
        return 'Für diese Figur und dieses Stück liegt kein Schnitt bereit '
            + '— erst „2D", dann „3D".';
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
        reiter.schnittVon = { figur: figur.id, vorlage,
                              regler: GarmentcodeAblauf.reglerstand() };
        return true;
    }

    /**
     * Gehört der gemerkte Schnitt zu dieser Figur, diesem Stück UND diesen
     * Reglerwerten?
     *
     * Der dritte Teil kam am 08.09.2026 dazu (Edgar: „ich habe das T-shirt
     * länger eingestellt, warum wird es in 3D nicht länger gemacht, im 2D
     * war es länger?"). Der Schnitt liegt als Ordner auf der Platte, und
     * „3D" baut ihn nicht neu. Normalerweise zieht `GarmentcodeLive` bei
     * jedem Reglerzug nach — aber nicht, während ein Bau läuft: Dann wird
     * der Zug verworfen (`angestossen` steigt bei `reiter.laeuft` aus), und
     * der Ordner enthält weiter den Schnitt von vorher. Wer danach „3D"
     * drückt, drapiert die alte Länge, ohne dass irgendwo ein Fehler
     * entsteht — die Panels im Bild zeigen längst die neue.
     */
    static schnittPasst(reiter, figur, vorlage) {
        return Boolean(reiter.spezifikation && reiter.schnittVon
            && reiter.schnittVon.figur === figur.id
            && reiter.schnittVon.vorlage === vorlage
            && reiter.schnittVon.regler === GarmentcodeAblauf.reglerstand());
    }

    /**
     * Ein Fingerabdruck der eingestellten Reglerwerte.
     *
     * Verglichen wird die Zeichenkette, nicht Wert für Wert: Sie ist billig
     * zu bilden und zu speichern, und ein Unterschied irgendwo genügt schon
     * als Antwort. Sortiert, weil die Reihenfolge der Schlüssel sonst zwei
     * gleiche Stände verschieden aussehen liesse.
     */
    static reglerstand() {
        const werte = garmentcodeRegler.werte || {};
        return Object.keys(werte).sort()
            .map((pfad) => `${pfad}=${werte[pfad]}`).join('|');
    }

    /** Der Schrittplan steht in `garmentcode_schritte.js`. */
    static schritte(reiter, modus) {
        return GarmentcodeSchritte.fuer(reiter, modus);
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
