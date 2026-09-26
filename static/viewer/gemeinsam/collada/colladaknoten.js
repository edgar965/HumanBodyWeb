import { xmlEsc, zahlen, zeilenMajor } from './colladaxml.js';
import { Colladaskin } from './colladaskin.js';

/**
 * Colladaknoten — der Gelenkbaum (`<node type="JOINT">`) EINES Skeletts.
 *
 * Baut auf der BINDEPOSE auf (`Colladaskin.bindLokalMatrix`, siehe dessen
 * Docstring) — die aktuelle Pose kommt, wenn gewählt, über
 * `<library_animations>` (`Colladaanimation`) als Zeitspur oben drauf.
 */
export class Colladaknoten {

    /** @returns der XML-Text — ein `<node>` je Wurzelknochen (meist einer). */
    static gelenkbaum(skeleton, sids) {
        const kinder = new Map();
        const wurzeln = [];
        skeleton.bones.forEach((bone, i) => {
            const elternIndex = bone.parent && bone.parent.isBone ? skeleton.bones.indexOf(bone.parent) : -1;
            if (elternIndex < 0) wurzeln.push(i);
            else {
                if (!kinder.has(elternIndex)) kinder.set(elternIndex, []);
                kinder.get(elternIndex).push(i);
            }
        });
        const knoten = (i) => {
            const matrix = zahlen(zeilenMajor(Colladaskin.bindLokalMatrix(skeleton, i)));
            const nachkommen = (kinder.get(i) || []).map(knoten).join('');
            return `<node id="${sids[i]}" name="${xmlEsc(skeleton.bones[i].name)}" sid="${sids[i]}" type="JOINT">`
                + `<matrix sid="matrix">${matrix}</matrix>${nachkommen}</node>`;
        };
        return wurzeln.map(knoten).join('');
    }
}
