import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeSchnitt } from './garmentcode_schnitt.js';
import { GarmentcodeDrapierung } from './garmentcode_drapieren.js';
import { GarmentcodePanels } from './garmentcode_panels.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';

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
    static async bauen(reiter, modus = 'komplett') {
        if (reiter.laeuft) return;
        const meldung = document.getElementById('gc-meldung');
        const figur = reiter.figur();
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt — bitte links in der '
                + 'Charakterliste eine anklicken. Der Schnitt wird aus ihren '
                + 'Maßen gebaut.';
            return;
        }
        const vorlage = document.getElementById('gc-vorlage').value;
        if (modus === '3d' && !GarmentcodeAblauf.schnittPasst(reiter, figur, vorlage)) {
            meldung.textContent = 'Für diese Figur und dieses Stück liegt '
                + 'kein Schnitt bereit — erst „2D", dann „3D".';
            return;
        }
        const knoepfe = ['gc-erzeugen', 'gc-schnitt', 'gc-drapieren']
            .map(k => document.getElementById(k)).filter(Boolean);

        reiter.laeuft = true;
        knoepfe.forEach(k => { k.disabled = true; });
        meldung.textContent = '';
        // Gesagt, nicht verhindert: Ein Grundkörper ist auch eine Figur.
        reiter.ohneMorphs = GarmentcodeFigur.ohneMorphs(figur);
        garmentcodeFortschritt.starten(GarmentcodeAblauf.schritte(reiter, modus));

        try {
            if (modus !== '3d' && !await GarmentcodeAblauf.schnittteil(reiter, figur, meldung, vorlage)) {
                return;
            }
            await GarmentcodeAblauf.dreid(reiter, modus, figur, meldung, vorlage);
            garmentcodeFortschritt.beenden();
        } catch (fehler) {
            garmentcodeFortschritt.gescheitert(
                modus === '3d' ? 'drape' : 'schnitt',
                String(fehler.message || fehler));
            meldung.textContent = `Fehler: ${fehler.message || fehler}`;
        } finally {
            reiter.laeuft = false;
            knoepfe.forEach(k => { k.disabled = false; });
            garmentcodeFortschritt.beenden();
        }
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
        if (modus !== '3d') {
            schritte.push({ schluessel: 'schnitt', erwartet: 4,
                            titel: 'Schnitt konstruieren' });
        }
        if (modus === '2d') {
            schritte.push({ schluessel: 'panels', erwartet: 1,
                            titel: 'Panels an die Figur' });
        }
        if (reiter.drapierbereit && modus !== '2d') {
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
        if (modus === '2d') {
            garmentcodeFortschritt.laeuft('panels');
            const anzahl = await GarmentcodePanels.zeigen(
                figur, reiter.spezifikation, vorlage);
            garmentcodeFortschritt.fertig('panels', `${anzahl} Panels`);
            meldung.textContent += anzahl
                ? ` — ${anzahl} Panels liegen an der Figur. „3D" simuliert `
                  + 'den Stoff.'
                : ' — die Panels liessen sich nicht anlegen.';
            return;
        }
        GarmentcodePanels.entfernen(figur);
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
