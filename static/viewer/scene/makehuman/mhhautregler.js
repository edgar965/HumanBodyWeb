import { markDirty } from '../undo.js';
import { Mhreglerzeile } from './mhreglerzeile.js';

/**
 * Mhhautregler — die Haut des MakeHuman-Körpers.
 *
 * MakeHuman legt hier eine `.mhmat`-Haut auf (Textur, Rauheit, Durchschein).
 * Solche Dateien bringt das Projekt nicht mit — der Ordner
 * `Dokumente/makehuman2/data/skins` ist leer —, deshalb steht hier das, was
 * ohne sie geht: Farbe und die drei Materialwerte. Ein Hautbild vorzugaukeln,
 * das es nicht gibt, wäre schlechter als keines.
 *
 * Die Werte gehen ohne Neuladen ins Material (`MhFigur.hautAngleichen`); das
 * Netz bleibt, wie es ist.
 */
export class Mhhautregler {

    static REGLER = [
        { schluessel: 'rauheit', name: 'Rauheit', min: 0, max: 100,
          titel: 'Matt (100) bis spiegelnd (0)' },
        { schluessel: 'metall', name: 'Metallanteil', min: 0, max: 100,
          titel: 'Haut ist 0 — höhere Werte nur für Effekte' },
        { schluessel: 'deckkraft', name: 'Deckkraft', min: 10, max: 100,
          titel: 'Durchsichtig machen, um Kleidung von innen zu sehen' },
    ];

    static fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        behaelter.appendChild(Mhreglerzeile.farbe('Hautfarbe', inst.haut.farbe,
            (wert) => {
                inst.haut.farbe = wert;
                inst.hautAngleichen();
            }));
        for (const angabe of Mhhautregler.REGLER) {
            behaelter.appendChild(Mhreglerzeile.schieber(
                { ...angabe, wert: inst.haut[angabe.schluessel] },
                (wert) => {
                    inst.haut[angabe.schluessel] = wert;
                    inst.hautAngleichen();
                },
                () => markDirty('MakeHuman-Haut')));
        }
    }
}
