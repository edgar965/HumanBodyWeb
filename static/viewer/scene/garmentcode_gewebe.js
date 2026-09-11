import { state } from './state.js';
import { Schieberegler } from '../gemeinsam/schieberegler.js';
import { gewebeart } from '../gemeinsam/gewebearten.js';

/**
 * Die Gewebe-Auswahl unter „Farbe / Material": Art, Fäden je cm, Struktur.
 *
 * AUFTRAG (Edgar, 11.09.2026): „du hast ja jetzt auch die Textur eingebaut,
 * kannst du auswahlmöglichkeiten für Textur bei dem Bereich Farbe/Material
 * hinzufügen".
 *
 * Die drei Felder schreiben in `GarmentcodeMaterial.stand.gewebe` und gehen
 * denselben Weg wie Farbe und Rauheit: auf das GEWÄHLTE Stück, sonst nur
 * gemerkt für das nächste gebaute (`garmentcode_material.js`, Modulkopf —
 * die Begründung steht dort). Das Reitergedächtnis merkt sie von selbst,
 * weil sie eine `id` tragen.
 *
 * DIE ART SETZT VORGABEN, ABER NUR BEI EINEM ECHTEN KLICK. Wer auf „Köper"
 * stellt, bekommt dessen Fadenzahl und Stärke in die beiden Schieber — mit
 * `input`, damit Stand und Gedächtnis mitgehen. Beim Seitenstart stellt das
 * Reitergedächtnis die Art aber mit einem SYNTHETISCHEN `change` her
 * (`isTrusted` false); dort dürfen die Schieber nicht auf die Vorgabe
 * fallen, sonst wären die gemerkten Feinwerte im selben Atemzug weg.
 *
 * Nebenbei bekommen Rauheit und Metallgrad hier ihre Wertanzeige: Die beiden
 * Schieber zeigten bis dahin den Startwert, gleich wo sie standen.
 */
export class GarmentcodeGewebe {

    static ART = 'gc-gewebe';
    static FAEDEN = 'gc-faeden';
    static STRUKTUR = 'gc-struktur';

    /** Alle Felder verdrahten; `material` ist `GarmentcodeMaterial`. */
    static einhaengen(material) {
        const auswahl = document.getElementById(GarmentcodeGewebe.ART);
        if (!auswahl) return false;
        auswahl.addEventListener('change', (ereignis) => {
            if (state._syncingSliders) return;
            material.stand.gewebe = { ...material.stand.gewebe, art: auswahl.value };
            if (ereignis.isTrusted) {
                GarmentcodeGewebe.vorgabenSetzen(auswahl.value);
            } else {
                material.anwenden(material.figur());
            }
        });
        material._schieber(GarmentcodeGewebe.FAEDEN, (wert) => {
            material.stand.gewebe = { ...material.stand.gewebe, faeden: wert };
        });
        material._schieber(GarmentcodeGewebe.STRUKTUR, (wert) => {
            material.stand.gewebe = { ...material.stand.gewebe, staerke: wert / 100 };
        });
        GarmentcodeGewebe._anzeige(GarmentcodeGewebe.FAEDEN, GarmentcodeGewebe.faedenText);
        GarmentcodeGewebe._anzeige(GarmentcodeGewebe.STRUKTUR, GarmentcodeGewebe.prozentText);
        GarmentcodeGewebe._anzeige('gc-roughness', GarmentcodeGewebe.hundertstelText);
        GarmentcodeGewebe._anzeige('gc-metalness', GarmentcodeGewebe.hundertstelText);
        return true;
    }

    /** Fäden und Stärke der Art in die Schieber — mit `input`. */
    static vorgabenSetzen(artname) {
        const art = gewebeart(artname);
        GarmentcodeGewebe._stellen(GarmentcodeGewebe.FAEDEN, art.faedenJeCm);
        GarmentcodeGewebe._stellen(GarmentcodeGewebe.STRUKTUR, Math.round(art.staerke * 100));
    }

    static _stellen(kennung, wert) {
        const feld = document.getElementById(kennung);
        if (!feld) return;
        feld.value = String(wert);
        feld.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /** Die Wertanzeige eines Schiebers nachziehen — jetzt und bei `input`. */
    static _anzeige(kennung, format) {
        const feld = document.getElementById(kennung);
        if (!feld) return;
        const nachziehen = () => Schieberegler.setzen(kennung, feld.value, format);
        feld.addEventListener('input', nachziehen);
        nachziehen();
    }

    static faedenText(wert) {
        return `${wert}`;
    }

    static prozentText(wert) {
        return `${wert} %`;
    }

    static hundertstelText(wert) {
        return (wert / 100).toFixed(2);
    }
}
