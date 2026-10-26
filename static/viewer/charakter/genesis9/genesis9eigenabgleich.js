import { Sortenanteile } from './sortenanteile.js';

/**
 * Genesis9eigenabgleich — derselbe Stückregler an zwei Orten zeigt denselben Wert (Stufe K1, 25.10.2026).
 *
 * Ein Regler eines getragenen Stücks steht jetzt bis zu dreimal im Bedienfeld: unter „Einstellungen“ in der Garderobe (Assets-Reiter,
 * `Genesis9garderobe._eintrag`), im Kasten eines Genital-Stücks (`Genesis9genitalien._stueck`) und in Assets → Eigen
 * (`Genesis9eigenstueck`, seit K2a dort statt im Reglerfeld). Alle drei sind Zeilen von `Genesis9stueckregler._zeile` auf demselben Wert (`inst.kleidung[kennung].regler`) —
 * gebaut wird jede mit dem Stand der Figur, nur ein ZUG an der einen Stelle schob die andere nicht mit. Hier hört EIN Zuhörer am Dokument
 * auf `input` an jedem Schieber `.genesis9-stueckregler input[data-regler]` und stellt die anderen Schieber desselben Stücks und Namens
 * auf denselben Wert und dieselbe Anzeige. Er setzt nur `value` (das löst kein Ereignis aus): kein zweiter Lauf, kein Ringschluss.
 *
 * Das Stück eines Kastens: `data-eigen-stueck` (Eigen), `details.g9-genitalstueck[data-stueck]` (Genitalien), sonst die Zeile davor mit
 * dem Häkchen `g9-kleid-<kennung>` (Garderobe — der Kasten steht direkt hinter seiner Zeile).
 */
export class Genesis9eigenabgleich {

    static AUSWAHL = '.genesis9-stueckregler input[data-regler]';
    static HAKEN = 'g9-kleid-';
    static _verdrahtet = false;

    static verdrahten() {
        if (Genesis9eigenabgleich._verdrahtet) return;
        Genesis9eigenabgleich._verdrahtet = true;
        document.addEventListener('input', (e) => {
            if (e.target instanceof HTMLInputElement && e.target.matches(Genesis9eigenabgleich.AUSWAHL)) Genesis9eigenabgleich.spiegeln(e.target);
        });
    }

    /** Die Kennung des Stücks, zu dem ein Schieber gehört — null, wenn keiner der drei Orte. */
    static kennungVon(schieber) {
        const kasten = schieber.closest('.genesis9-stueckregler');
        if (!kasten) return null;
        if (kasten.dataset.eigenStueck) return kasten.dataset.eigenStueck;
        const genital = kasten.closest('details.g9-genitalstueck');
        if (genital?.dataset.stueck) return genital.dataset.stueck;
        const haken = kasten.previousElementSibling?.querySelector(`input[type="checkbox"][id^="${Genesis9eigenabgleich.HAKEN}"]`);
        return haken ? haken.id.slice(Genesis9eigenabgleich.HAKEN.length) : null;
    }

    /** Den gezogenen Schieber an die anderen Orte übertragen; bei einem Sortenanteil („Haar – Generisch“) alle Anteile, die `_aufteilen` mitzog. */
    static spiegeln(quelle) {
        const kennung = Genesis9eigenabgleich.kennungVon(quelle);
        if (!kennung) return;
        const kasten = quelle.closest('.genesis9-stueckregler');
        const geschwister = Sortenanteile.ist(quelle.dataset.regler)
            ? [...kasten.querySelectorAll('input[data-regler^="sorte."]')] : [quelle];
        const alle = [...document.querySelectorAll(Genesis9eigenabgleich.AUSWAHL)].filter(s => !kasten.contains(s));
        for (const s of geschwister) {
            const text = s.closest('.slider-row')?.querySelector('.slider-value')?.textContent;
            for (const ziel of alle) {
                if (ziel.dataset.regler !== s.dataset.regler || Genesis9eigenabgleich.kennungVon(ziel) !== kennung) continue;
                if (ziel.value !== s.value) ziel.value = s.value;
                const anzeige = ziel.closest('.slider-row')?.querySelector('.slider-value');
                if (anzeige && text != null) anzeige.textContent = text;
            }
        }
    }
}
