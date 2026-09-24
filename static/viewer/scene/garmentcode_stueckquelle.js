import { fn } from '../gemeinsam/registrierung.js';
import { garmentcodePreset } from './garmentcode_preset.js';

/**
 * GarmentcodeStueckquelle — nach einem Klick auf ein GarmentCode-Stück in
 * der Szene die Toolbox GENAU dorthin springen lassen: das Vorbild in der
 * Kleiderbibliothek markieren, oder die Formcheckbox ankreuzen.
 *
 * Edgar, 24.09.2026: „wenn ich ein Garment Code anklicke, soll die Toolbox
 * links exakt zu dem hinspringen, also z.B: in der Kleiderbibliothek das
 * Garment Code selektieren, oder die Checkboxen aktivieren falls keine
 * Kleiderbibliothek." Der Vorlagenwechsel (`garmentcode_titel.js`,
 * `Stueckmarkierung`) sprang bis dahin nur zum KATALOGSTÜCK („Schuh") — die
 * Kleiderbibliothek und die Häkchen blieben, wo sie zufällig standen.
 *
 * WARUM POLLING: Der Vorlagenwechsel setzt `#gc-vorlage` und feuert nur ein
 * `change`-Ereignis (`GarmentcodeReiter.vorlageZeigen`) — die Vorbild-Knöpfe
 * und Formcheckboxen holt `GarmentcodeVorbilder`/die Reglerantwort danach
 * ASYNCHRON vom Server. Ohne Warten träfe die Suche ins Leere.
 *
 * NUR ANZEIGEN, NICHT NEU BAUEN: Ein Klick auf den Vorbild-Knopf stellt laut
 * `garmentcode_vorbilder.js` nur die Regler — gebaut wird erst mit „Bauen
 * 2D+3D". Für die Form genügt das Häkchen (`garmentcodePreset.anhaken`,
 * OHNE Werte zu ändern) — die Regler stehen am Stück schon so, wie gebaut.
 *
 * DIE KENNUNG KOMMT VOM BAU, NICHT VOM ANZEIGETEXT (`garmentcode_titel.js`
 * `quelle()`, gemerkt in `garmentcode_ablage.js`) — ein Stück ohne bekannte
 * Herkunft (freie Regler) lässt die Toolbox einfach beim Katalogstück stehen.
 */
export class GarmentcodeStueckquelle {

    static WARTEN_MS = 100;
    static VERSUCHE = 20;

    /** Vorlage wechseln und, wenn bekannt, die Herkunft des Stücks zeigen. */
    static zeigen(vorlage, quelle) {
        if (!fn.garmentcodeVorlageZeigen?.(vorlage) || !quelle?.schluessel) return;
        if (quelle.art === 'vorbild') {
            GarmentcodeStueckquelle._warten(
                () => document.querySelector(
                    `#gc-vorbilder .vorbild-knopf[data-schluessel="${CSS.escape(quelle.schluessel)}"]`),
                (knopf) => knopf.click());
        } else if (quelle.art === 'form') {
            GarmentcodeStueckquelle._warten(
                () => document.querySelector(
                    `#gc-passform input[data-preset="${CSS.escape(quelle.schluessel)}"]`),
                () => garmentcodePreset.anhaken([quelle.schluessel]));
        }
    }

    /** Bis zu `VERSUCHE`-mal alle `WARTEN_MS` nach dem Element suchen. */
    static async _warten(suchen, anwenden, versuch = 0) {
        const element = suchen();
        if (element) { anwenden(element); return; }
        if (versuch >= GarmentcodeStueckquelle.VERSUCHE) return;
        await new Promise((weiter) => setTimeout(weiter, GarmentcodeStueckquelle.WARTEN_MS));
        GarmentcodeStueckquelle._warten(suchen, anwenden, versuch + 1);
    }
}

fn.garmentcodeQuelleZeigen = (vorlage, quelle) => GarmentcodeStueckquelle.zeigen(vorlage, quelle);
