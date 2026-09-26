import { Morphliste } from '../gemeinsam/morphliste.js';
import { Morphgruppen } from '../gemeinsam/morphgruppen.js';
import { Metaregler } from '../gemeinsam/metaregler.js';
import { Gemeinsameregler } from './gemeinsameregler.js';
import { Umamasse } from './uma/umamasse.js';

/**
 * Formbedienung — alles, womit man die FORM einer Figur stellt.
 *
 * Drei Ebenen, die sich gegenseitig nachziehen müssen:
 *
 *   1. Metaregler (Alter, Masse, Muskeln, Größe) in ihrer eigenen Einheit,
 *   2. der gemeinsame Block, den es für UMA und HumanBody gleichermaßen gibt
 *      (`gemeinsameregler.js`, 06.09.2026),
 *   3. die 216 Einzelmorphs.
 *
 * HERAUSGELÖST aus `properties.js` (06.09.2026): Mit dem gemeinsamen Block
 * wäre die Datei von 291 auf 313 Zeilen gewachsen. Der Teil, der angefasst
 * wurde, gehört damit hierher — die Nachführung zwischen Ebene 2 und 3 ist
 * der eigentliche Grund: Ein gemeinsamer Regler stellt mehrere Morphs, und
 * ohne Nachführung zeigten zwei Bedienelemente verschiedene Zahlen für
 * dieselbe Figur.
 */
export class Formbedienung {

    /** Unter diesem Betrag gilt ein Morph als aus und wird aus der Figur entfernt. */
    static SCHWELLE = 0.005;

    /**
     * Die drei Ebenen für eine HumanBody-Figur bauen.
     *
     * @param inst       Figur
     * @param morphDefs  `/api/character/morphs/`
     * @param neuLaden   holt das Netz vom Server (jede Änderung braucht es)
     */
    static async humanbody(inst, morphDefs, neuLaden) {
        Formbedienung._meta(inst, morphDefs, neuLaden);
        Formbedienung._morphs(inst, morphDefs, neuLaden);
        await Gemeinsameregler.fuellen(inst, {
            morphDefs,
            nachAenderung: () => {
                Morphliste.angleichen(document.getElementById('prop-morphs-panel'),
                                      inst.morphs || {});
                neuLaden(inst);
            },
        });
    }

    /**
     * Der gemeinsame Block für eine UMA-Figur — dieselben Regler, nur stellen
     * sie hier Knochen. Die Zentimeter der Größe werden gemessen, nicht
     * gerechnet (`Umamasse.cm`).
     */
    static async uma(inst, nachAenderung) {
        await Gemeinsameregler.fuellen(inst, { nachAenderung, cm: Umamasse.cm });
    }

    static leeren() {
        Gemeinsameregler.leeren();
    }

    /**
     * Metaregler der Figur. Die Werte stehen in der Figur als -1..1 und im
     * Regler in ihrer Einheit — die Umrechnung kommt aus `Metaregler`, wo sie
     * einmal steht (war vorher an fünf Stellen ausgeschrieben).
     */
    static _meta(inst, morphDefs, neuLaden) {
        const behaelter = document.getElementById('prop-meta-sliders');
        behaelter.innerHTML = '';
        for (const [name, meta] of Object.entries(morphDefs?.meta_sliders || {})) {
            const angezeigt = Math.round(
                Metaregler.aussen(inst.meta[name] || 0, meta.min, meta.max));
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            const beschriftung = document.createElement('label');
            beschriftung.textContent = meta.label || name;
            const schieber = document.createElement('input');
            Object.assign(schieber, { type: 'range', min: meta.min, max: meta.max,
                                      step: 1, value: angezeigt });
            schieber.dataset.meta = name;
            const feld = document.createElement('span');
            feld.className = 'slider-val';
            feld.textContent = String(angezeigt);
            schieber.addEventListener('input', () => { feld.textContent = schieber.value; });
            // Erst beim Loslassen, weil danach das Netz neu geholt wird.
            schieber.addEventListener('change', () => {
                inst.meta[name] = Metaregler.innen(parseFloat(schieber.value),
                                                   meta.min, meta.max);
                neuLaden(inst);
            });
            zeile.append(beschriftung, schieber, feld);
            behaelter.appendChild(zeile);
        }
    }

    /**
     * Morphregler der Figur — dieselben Kategorien wie auf den anderen Seiten,
     * deshalb aus `Morphliste`; hier in drei klappbaren Bereichen (Gesicht,
     * Körper, Fantasie — `Morphgruppen`, 12.09.2026). Eigen ist: Meldung
     * erst beim Loslassen, Pfeil vor dem Kategorienamen, und Werte unter der
     * Schwelle werden ganz entfernt, damit die Figur keine Nullwerte mitschleppt.
     */
    static _morphs(inst, morphDefs, neuLaden) {
        const behaelter = document.getElementById('prop-morphs-panel');
        behaelter.innerHTML = '';
        if (!morphDefs?.morphs || !morphDefs?.categories) return;
        const liste = new Morphliste({
            ereignis: 'change',
            chevron: true,
            startwert: name => inst.morphs[name],
            geaendert: (name, wert) => {
                if (Math.abs(wert) < Formbedienung.SCHWELLE) delete inst.morphs[name];
                else inst.morphs[name] = wert;
                // Ein Einzelmorph bewegt den gemeinsamen Regler mit.
                Gemeinsameregler.angleichen(inst);
                neuLaden(inst);
            },
        });
        const nach = Morphliste.nachKategorie(morphDefs.morphs, morphDefs.categories);
        for (const [bereich, namen] of Morphgruppen.aufteilen(nach.map(([n]) => n))) {
            const eintraege = nach.filter(([n]) => namen.includes(n));
            const anzahl = eintraege.reduce((summe, [, morphs]) => summe + morphs.length, 0);
            const { block, koerper } = Morphgruppen.bereich(bereich, anzahl);
            for (const [name, morphs] of eintraege) koerper.appendChild(liste.kategorie(name, morphs));
            behaelter.appendChild(block);
        }
    }
}
