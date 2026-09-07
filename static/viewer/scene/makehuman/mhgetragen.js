import { markDirty } from '../undo.js';
import { Mhkleidstueck } from './mhkleidstueck.js';
import { Mhreglerzeile } from './mhreglerzeile.js';

/**
 * Mhgetragen — was die MakeHuman-Figur anhat, mit dem Aussehen je Stück.
 *
 * Warum eine zweite Liste neben dem Katalog: Der Katalog hat 181 Zeilen in
 * sieben Ordnern. Wer die Farbe der getragenen Hose ändern will, soll sie
 * nicht suchen müssen.
 *
 * DIE FARBE WIRKT NUR OHNE TEXTUR, und das steht auch dran. Ein Stück mit
 * Diffuse-Bild bekommt ein weißes Material, damit die Textur unverfälscht
 * durchkommt; eine Farbe darauf würde sie einfärben. Ein Regler, der
 * stillschweigend nichts tut, ist schlimmer als ein abgeblendeter.
 */
export class Mhgetragen {

    static REGLER = [
        { schluessel: 'rauheit', name: 'Rauheit', min: 0, max: 100 },
        { schluessel: 'metall', name: 'Metallanteil', min: 0, max: 100 },
        { schluessel: 'deckkraft', name: 'Deckkraft', min: 10, max: 100 },
    ];

    /**
     * @param inst          die MakeHuman-Figur
     * @param behaelter     Zielelement
     * @param nachAenderung () => void, nach dem Ausziehen
     */
    static fuellen(inst, behaelter, nachAenderung) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const kennungen = inst.getragen();
        if (!kennungen.length) {
            behaelter.innerHTML = '<div class="hb-hinweis">Nichts angezogen — '
                + 'unten aus der Garderobe wählen.</div>';
            return;
        }
        for (const kennung of kennungen) {
            behaelter.appendChild(
                Mhgetragen._stueck(inst, kennung, nachAenderung));
        }
    }

    static _stueck(inst, kennung, nachAenderung) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        const kopf = document.createElement('summary');
        kopf.textContent = kennung.split('/').pop().replace(/_/g, ' ');
        kopf.title = kennung;
        kasten.appendChild(kopf);
        // `mitTextur` kommt aus der Antwort, NICHT aus `material.map`: Das
        // Bild wird nachgeladen und ist beim Aufbau der Zeile oft noch nicht
        // da — die Farbzeile wäre dann mal da und mal nicht.
        kasten.appendChild(Mhgetragen._farbe(
            inst, kennung, Boolean(inst.kleidung[kennung].mitTextur)));
        for (const angabe of Mhgetragen.REGLER) {
            kasten.appendChild(Mhreglerzeile.schieber(
                { ...angabe, wert: inst.kleidung[kennung][angabe.schluessel] },
                (wert) => Mhkleidstueck.aussehen(
                    inst, kennung, { [angabe.schluessel]: wert }),
                () => markDirty('MakeHuman-Kleidung')));
        }
        kasten.appendChild(Mhgetragen._ausziehen(inst, kennung, nachAenderung));
        return kasten;
    }

    static _farbe(inst, kennung, mitTextur) {
        if (mitTextur) {
            const hinweis = document.createElement('div');
            hinweis.className = 'hb-font-size-0-72rem';
            hinweis.textContent = 'Farbe kommt aus der Textur des Stücks.';
            return hinweis;
        }
        return Mhreglerzeile.farbe('Farbe', inst.kleidung[kennung].farbe,
            (wert) => Mhkleidstueck.aussehen(inst, kennung, { farbe: wert }));
    }

    static _ausziehen(inst, kennung, nachAenderung) {
        const knopf = document.createElement('button');
        knopf.className = 'btn-toggle hb-volle-breite';
        knopf.innerHTML = '<i class="fas fa-times"></i> Ausziehen';
        knopf.addEventListener('click', () => {
            inst.ausziehen(kennung);
            nachAenderung();
        });
        return knopf;
    }
}
