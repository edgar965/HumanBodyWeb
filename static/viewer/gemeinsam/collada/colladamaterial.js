import { xmlEsc, reinerName } from './colladaxml.js';
import { Werkstoffbild } from '../werkstoffbild.js';

/**
 * Colladamaterial — `<library_images>`, `<library_effects>`,
 * `<library_materials>` zu den Werkstoffen einer Objektliste.
 *
 * Ein Werkstoff kommt EINMAL in die Bibliothek, auch wenn ihn mehrere Teile
 * teilen (HumanBody-Haut hängt oft an Körper UND Detailnetzen). Zurück kommt
 * je Netz die Liste seiner Material-IDs IN DER REIHENFOLGE SEINES
 * `material`-Arrays — `Colladaknoten` bindet sie darüber an die
 * `sym0`/`sym1`/… Symbole aus `Colladageometrie`.
 */
export class Colladamaterial {

    /**
     * @param praefix   vor jeden Bilddateinamen gesetzt (siehe `ObjMtl.bauen` —
     *                  derselbe Grund: der Server benennt Export-Dateien nur
     *                  um, wenn sie mit dem Platzhalter beginnen)
     * @param maxSeite  0 = Originalauflösung, sonst längere Seite begrenzt
     *                  (siehe `Werkstoffbild.png`)
     * @returns {xml, idProMesh: Map<mesh, string[]>, bilder, warnungen}
     */
    static async bauen(objekte, textur, praefix = '', maxSeite = 0) {
        const idVonMaterial = new Map();
        const idProMesh = new Map();
        const bilder = [];
        const bildnamen = new Set();
        const warnungen = [];
        let images = '';
        let effects = '';
        let materials = '';
        let zaehler = 0;

        for (const obj of objekte) {
            const liste = Array.isArray(obj.material) ? obj.material : [obj.material];
            const ids = [];
            for (const mat of liste) {
                if (!mat) { ids.push(null); continue; }
                if (!idVonMaterial.has(mat)) {
                    const basis = reinerName(mat.name, `mat${zaehler++}`);
                    let id = basis;
                    let n = 2;
                    while ([...idVonMaterial.values()].includes(id)) id = `${basis}_${n++}`;
                    idVonMaterial.set(mat, id);
                    const eintrag = await Colladamaterial._eintrag(
                        mat, id, textur, praefix, maxSeite, bilder, bildnamen, warnungen
                    );
                    images += eintrag.images;
                    effects += eintrag.effects;
                    materials += eintrag.materials;
                }
                ids.push(idVonMaterial.get(mat));
            }
            idProMesh.set(obj, ids);
        }
        return { images, effects, materials, idProMesh, bilder, warnungen };
    }

    static async _eintrag(mat, id, textur, praefix, maxSeite, bilder, bildnamen, warnungen) {
        const farbe = mat.color || { r: 1, g: 1, b: 1 };
        const deckkraft = mat.opacity !== undefined ? mat.opacity : 1;
        let images = '';
        let texturKanal = '';
        if (textur && mat.map && mat.map.image) {
            const blob = await Werkstoffbild.png(mat.map.image, maxSeite);
            if (blob) {
                const dateiname = `${praefix}${id}.png`;
                if (!bildnamen.has(dateiname)) { bildnamen.add(dateiname); bilder.push({ dateiname, blob }); }
                images = `<image id="${id}-img"><init_from>${xmlEsc(dateiname)}</init_from></image>`;
                texturKanal = `<texture texture="${id}-sampler" texcoord="UVSET0"/>`;
            } else {
                warnungen.push(`Bildkarte von „${id}" nicht exportierbar — nur Grundfarbe.`);
            }
        } else if (textur && mat.isShaderMaterial) {
            warnungen.push(`„${id}" ist ein eigener Shader — nur die Grundfarbe wird exportiert.`);
        }
        const diffus = texturKanal || `<color sid="diffuse">${farbe.r} ${farbe.g} ${farbe.b} 1</color>`;
        const effects = '<effect id="' + id + '-fx"><profile_COMMON>'
            + (texturKanal ? `<newparam sid="${id}-sampler"><sampler2D><source>${id}-surface</source></sampler2D></newparam>`
                + `<newparam sid="${id}-surface"><surface type="2D"><init_from>${id}-img</init_from></surface></newparam>` : '')
            + `<technique sid="common"><lambert><diffuse>${diffus}</diffuse>`
            + `<transparency><float>${deckkraft}</float></transparency>`
            + '</lambert></technique></profile_COMMON></effect>';
        const materials = `<material id="${id}" name="${xmlEsc(mat.name || id)}"><instance_effect url="#${id}-fx"/></material>`;
        return { images, effects, materials };
    }
}
