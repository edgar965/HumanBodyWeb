import * as THREE from 'three';
import { Werkstoffbild } from './werkstoffbild.js';

/**
 * ObjMtl — MTL-Text und Bildkarten zu einer Menge von Objekten.
 *
 * Three.js' `OBJExporter` schreibt selbst nur `usemtl <name>` je Geometrie-
 * Gruppe — KEINE MTL-Datei, keine Bilder (siehe `node_modules/three/examples/
 * jsm/exporters/OBJExporter.js`: liest nur `mesh.material[i].name`). Diese
 * Klasse liefert das Fehlende dazu, damit MeshLab/Blender die Figur nicht
 * einfarbig grau öffnen.
 *
 * ALLE Werkstoffe eines `material`-Arrays bekommen einen `newmtl`-Eintrag,
 * nicht nur der erste (Fund 26.09.2026: Genesis-9-Körper hat 10 Zonen —
 * Kopf/Arme/Beine/Nägel/… — als EIN Netz mit 10-teiligem `material`-Array;
 * mit nur dem ersten exportiert blieben 9 Zonen ohne passenden `newmtl`-
 * Eintrag, MeshLab zeigte sie einfarbig/weiß). `ObjMtl.bauen()` muss VOR
 * `OBJExporter().parse()` laufen — es vergibt hier die `mat.name`, die der
 * Exporter danach für die `usemtl`-Zeilen jeder Gruppe liest.
 */
export class ObjMtl {

    /**
     * @param objekte  dieselben Meshes wie an `OBJExporter.parse()`
     * @param textur   `false`: nur Grundfarbe, keine Bildkarten
     * @param praefix   vor jeden Bilddateinamen gesetzt (Modellexport nutzt den
     *                  Platzhalter, damit der Server ihn mit der MTL-Datei
     *                  gemeinsam umbenennt — siehe `Modellexport.PLATZHALTER`)
     * @param maxSeite  0 = Originalauflösung, sonst längere Seite begrenzt
     *                  (siehe `Werkstoffbild.png`)
     * @returns {mtl: string, bilder: [{dateiname, blob}], warnungen: string[]}
     */
    static async bauen(objekte, textur = true, praefix = '', maxSeite = 0) {
        const bekannt = new Set();
        const bilder = [];
        const bildnamen = new Set();
        const warnungen = [];
        let zaehler = 0;
        let text = '';
        for (const obj of objekte) {
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            for (const mat of mats) {
                if (!mat) continue;
                if (!mat.name) mat.name = `mat_${zaehler++}`;
                if (bekannt.has(mat.name)) continue;
                bekannt.add(mat.name);
                text += await ObjMtl._eintrag(mat, textur, praefix, maxSeite, bilder, bildnamen, warnungen);
            }
        }
        return { mtl: text, bilder, warnungen };
    }

    static async _eintrag(mat, textur, praefix, maxSeite, bilder, bildnamen, warnungen) {
        const farbe = mat.color || new THREE.Color(1, 1, 1);
        let text = `newmtl ${mat.name}\n`;
        text += `Kd ${farbe.r.toFixed(4)} ${farbe.g.toFixed(4)} ${farbe.b.toFixed(4)}\n`;
        text += `d ${mat.opacity !== undefined ? mat.opacity.toFixed(4) : '1.0000'}\n`;
        if (textur && mat.map && mat.map.image) {
            const datei = await ObjMtl._bilddatei(mat.map.image, praefix + mat.name, maxSeite, bilder, bildnamen, warnungen);
            if (datei) text += `map_Kd ${datei}\n`;
        } else if (textur && mat.isShaderMaterial) {
            warnungen.push(
                `„${mat.name}" ist ein eigener Shader (kein Standard-Werkstoff) — nur die Grundfarbe `
                + 'wird exportiert, keine Bildkarte.'
            );
        }
        return text;
    }

    static async _bilddatei(image, matName, maxSeite, bilder, bildnamen, warnungen) {
        const blob = await Werkstoffbild.png(image, maxSeite);
        if (!blob) {
            warnungen.push(`Bildkarte von „${matName}" nicht exportierbar.`);
            return null;
        }
        const dateiname = `${matName}.png`;
        if (!bildnamen.has(dateiname)) {
            bildnamen.add(dateiname);
            bilder.push({ dateiname, blob });
        }
        return dateiname;
    }
}
