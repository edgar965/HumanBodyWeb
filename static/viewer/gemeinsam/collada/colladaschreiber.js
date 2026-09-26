import { xmlEsc } from './colladaxml.js';
import { Colladageometrie } from './colladageometrie.js';
import { Colladamaterial } from './colladamaterial.js';
import { Colladaskin } from './colladaskin.js';
import { Colladaknoten } from './colladaknoten.js';
import { Colladaanimation } from './colladaanimation.js';

/**
 * Colladaschreiber — eine Collada-1.4.1-Datei (.dae) aus Three.js-Objekten.
 *
 * WARUM EIN EIGENER SCHREIBER (26.09.2026, Docu/konzept_modellexport.md):
 * Three.js hat seit einigen Fassungen keinen `ColladaExporter` mehr, Blender
 * 5.0 keinen Collada-Export mehr (`bpy.ops.wm` geprüft: nur noch alembic, obj,
 * ply, stl, usd). Fünf Module — dieses hier fügt die anderen vier
 * (`Colladageometrie`, `Colladamaterial`, `Colladaskin`, `Colladaknoten`,
 * `Colladaanimation`) zu einem Dokument zusammen.
 *
 * ANNAHME, DIE HIER GILT: Der erste Knochen in `skeleton.bones` ist der
 * Wurzelknochen (so baut `Hautbindung`/`buildRigifySkeleton` das Skelett —
 * geprüft, nicht vermutet für den DEF-Skelett-Fall dieses Projekts).
 */
export class Colladaschreiber {

    /**
     * @param objekte  Meshes — rigged Originale ODER von `Netzpose` gebackene
     *                 statische Kopien (der Aufrufer entscheidet das VORHER,
     *                 je nach „Rig"-Häkchen)
     * @param optionen {textur, rig, animation: {wurzel, mixer, action} | null,
     *                  praefix: vor jeden Bilddateinamen gesetzt,
     *                  aufloesung: 0 = Original, sonst längere Bildkartenseite}
     * @returns {xml, bilder: [{dateiname, blob}], warnungen}
     */
    static async bauen(objekte, optionen = {}) {
        const { textur = true, rig = true, animation = null, praefix = '', aufloesung = 0 } = optionen;
        const mat = await Colladamaterial.bauen(objekte, textur, praefix, aufloesung);

        let geometrien = '';
        let controller = '';
        let szeneKnoten = '';
        let gelenkbaeume = '';
        let animationsXml = '';
        const behandelteSkelette = new Set();

        objekte.forEach((obj, i) => {
            const geomId = `geo_${i}`;
            const { xml: geoXml, symbole } = Colladageometrie.bauen(obj, geomId);
            geometrien += geoXml;
            const bindMaterial = Colladaschreiber._bindMaterial(symbole, mat.idProMesh.get(obj));
            const skinFaehig = rig && obj.isSkinnedMesh && obj.skeleton;

            if (!skinFaehig) {
                szeneKnoten += `<node id="node_${i}" name="${xmlEsc(obj.name || geomId)}">`
                    + `<instance_geometry url="#${geomId}">${bindMaterial}</instance_geometry></node>`;
                return;
            }

            const ctrlId = `ctrl_${i}`;
            const { xml: skinXml, sids } = Colladaskin.bauen(obj, geomId, ctrlId);
            controller += skinXml;
            if (!behandelteSkelette.has(obj.skeleton)) {
                behandelteSkelette.add(obj.skeleton);
                gelenkbaeume += Colladaknoten.gelenkbaum(obj.skeleton, sids);
                if (animation) {
                    animationsXml += Colladaanimation.bauen(
                        animation.wurzel, animation.mixer, animation.action, obj.skeleton, sids
                    );
                }
            }
            szeneKnoten += `<node id="node_${i}" name="${xmlEsc(obj.name || geomId)}">`
                + `<instance_controller url="#${ctrlId}"><skeleton>#${sids[0]}</skeleton>${bindMaterial}</instance_controller></node>`;
        });

        const xml = '<?xml version="1.0" encoding="UTF-8"?>'
            + '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">'
            + '<asset><up_axis>Y_UP</up_axis></asset>'
            + `<library_images>${mat.images}</library_images>`
            + `<library_effects>${mat.effects}</library_effects>`
            + `<library_materials>${mat.materials}</library_materials>`
            + `<library_geometries>${geometrien}</library_geometries>`
            + (controller ? `<library_controllers>${controller}</library_controllers>` : '')
            + (animationsXml ? `<library_animations>${animationsXml}</library_animations>` : '')
            + '<library_visual_scenes><visual_scene id="Scene" name="Scene">'
            + (gelenkbaeume ? `<node id="Armature" name="Armature">${gelenkbaeume}</node>` : '')
            + szeneKnoten + '</visual_scene></library_visual_scenes>'
            + '<scene><instance_visual_scene url="#Scene"/></scene>'
            + '</COLLADA>';

        return { xml, bilder: mat.bilder, warnungen: mat.warnungen };
    }

    static _bindMaterial(symbole, matIds) {
        if (!matIds) return '';
        const eintraege = symbole
            .map(s => (matIds[s.materialIndex]
                ? `<instance_material symbol="${s.symbol}" target="#${matIds[s.materialIndex]}"/>` : ''))
            .join('');
        return eintraege ? `<bind_material><technique_common>${eintraege}</technique_common></bind_material>` : '';
    }
}
