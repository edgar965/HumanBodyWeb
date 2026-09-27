import * as THREE from 'three';
import { Werkstoffbild } from './werkstoffbild.js';

/**
 * ObjMtl — MTL-Text und Bildkarten zu einer Menge von Objekten.
 *
 * Three.js' `OBJExporter` schreibt KEINE MTL-Datei und keine Bilder. Diese
 * Klasse liefert das Fehlende dazu, damit MeshLab/Blender die Figur nicht
 * einfarbig grau öffnen.
 *
 * ACHTUNG, oft falsch erinnert (`OBJExporter.js:46-49`): der Exporter liest
 * `mesh.material.name` OHNE Index und schreibt EIN `usemtl` je Netz. Bei einem
 * Material-Array ist `.name` undefiniert — dann schreibt er gar keins, und die
 * Flächen laufen unter dem Material des vorigen Netzes weiter. Netze mit
 * Material-Array müssen darum vorher zerlegt werden (`Gruppennetze`).
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
        const vergeben = new Map();
        const bilder = [];
        const bildnamen = new Set();
        const warnungen = [];
        let zaehler = 0;
        let text = '';
        for (const obj of objekte) {
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            for (const mat of mats) {
                if (!mat) continue;
                if (vergeben.has(mat)) continue;
                if (!mat.name) mat.name = `mat_${zaehler++}`;
                vergeben.set(mat, mat.name);
                text += await ObjMtl._eintrag(mat, textur, praefix, maxSeite, bilder, bildnamen, warnungen);
            }
        }
        return { mtl: text, bilder, warnungen };
    }

    static async _eintrag(mat, textur, praefix, maxSeite, bilder, bildnamen, warnungen) {
        const farbe = mat.color || new THREE.Color(1, 1, 1);
        const hatKarte = !!(textur && mat.map && mat.map.image);
        let text = `newmtl ${mat.name}\n`;
        // GRUNDFARBE STECKT IN DER KARTE, wenn es eine gibt: Blender und
        // MeshLab ERSETZEN `Kd` durch `map_Kd`, three multipliziert beides.
        // Darum wird die Farbe beim Schreiben in die Bilddatei gerechnet
        // (`Werkstoffbild.einfaerben`) und hier die Eins geschrieben — dann
        // stimmt das Ergebnis bei beiden Lesarten. Ohne das waren die Brauen
        // weiß (Kd 0,0395) und das Haar ein Drittel zu hell (Kd 0,6444).
        text += hatKarte
            ? 'Kd 1.0000 1.0000 1.0000\n'
            : `Kd ${farbe.r.toFixed(4)} ${farbe.g.toFixed(4)} ${farbe.b.toFixed(4)}\n`;
        text += `d ${mat.opacity !== undefined ? mat.opacity.toFixed(4) : '1.0000'}\n`;
        if (hatKarte) {
            const datei = await ObjMtl._bilddatei(
                mat.map, praefix + mat.name, maxSeite, bilder, bildnamen, warnungen, farbe
            );
            if (datei) text += `map_Kd ${datei}\n`;
        } else if (textur && mat.isShaderMaterial) {
            warnungen.push(
                `„${mat.name}" ist ein eigener Shader (kein Standard-Werkstoff) — nur die Grundfarbe `
                + 'wird exportiert, keine Bildkarte.'
            );
        }
        // Deckkraftmaske als `map_d` (FUND 26.09.2026, Edgar: „die Haare im
        // Export haben nicht die richtige Textur, und sind zum Teil
        // fehlerhaft"): Haarkarten, Wimpern und Brauen tragen ihre Form NICHT
        // in der Geometrie, sondern in einer `alphaMap` — ohne sie wird aus
        // jeder Strähnenkarte ein volles, undurchsichtiges Rechteck. Wimpern
        // haben überhaupt nur diese Maske und gar keine Farbkarte.
        if (textur && mat.alphaMap && mat.alphaMap.image) {
            // `alphaTest` mitgeben: der Leser kennt ihn nicht, also wird die
            // Maske daran geschnitten (`Werkstoffbild.schneiden`).
            const datei = await ObjMtl._bilddatei(
                mat.alphaMap, `${praefix}${mat.name}_alpha`, maxSeite, bilder, bildnamen,
                warnungen, null, mat.alphaTest
            );
            if (datei) text += `map_d ${datei}\n`;
        }
        return text;
    }

    /**
     * @param karte die `THREE.Texture` — ihr `flipY` entscheidet die Zeilenrichtung.
     * @param farbe nur für FARBkarten; eine Deckkraftmaske bleibt ungefärbt.
     * @param schwelle nur für MASKEN; `material.alphaTest`.
     */
    static async _bilddatei(karte, matName, maxSeite, bilder, bildnamen, warnungen,
                            farbe = null, schwelle = 0) {
        const blob = await Werkstoffbild.png(karte.image, maxSeite, karte.flipY, farbe, schwelle);
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
