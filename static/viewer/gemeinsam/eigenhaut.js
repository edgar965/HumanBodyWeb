import * as THREE from 'three';
import { base64ToFloat32, base64ToUint16, base64ToBytes } from './kodierung.js';
import { Protokoll } from './protokoll.js';

/**
 * Eigenhaut — ein Netz an SEIN eigenes Skelett binden, über Knochennamen.
 *
 * WARUM (Edgar, 07.09.2026: „Das Rigging funktioniert wohl nicht für die
 * neuen Modelle SMPL, MakeHuman. Wenn ich auf Play klicke … funktioniert das
 * nicht"): Die SMPL- und die MakeHuman-Figur waren reine `THREE.Mesh`. Die
 * Szene hängte ihnen beim Abspielen ersatzweise das Rigify-Skelett samt
 * HumanBody-Hautgewichten an — 176 Knochen und 18.210 Punkte für ein Netz
 * mit 6.890. Gemessen bewegte sich danach nichts: Die Spuren hießen
 * `DEF-spine.quaternion`, die Knochen der Figur `Pelvis`.
 *
 * DER UNTERSCHIED ZU `hautnetz.js`
 * ================================
 * Dort sind die Knochennummern schon die Nummern IM SKELETT — die Gewichte
 * und das Skelett stammen aus derselben Datei und derselben Reihenfolge.
 * Hier nicht: Der Server schickt die Gewichte als Spalten einer NAMENSLISTE
 * (`haut.knochen`), und welche Nummer ein Knochen im `THREE.Skeleton` hat,
 * entscheidet erst der Bauplan — die Endknochen hängen hinten dran, und ein
 * Rig darf umsortiert werden. Würde man die Spaltennummer direkt als
 * Knochennummer nehmen, bewegte sich der Arm, wenn das Bein tritt: kein
 * Fehler, keine Meldung, nur eine Figur, die falsch läuft.
 *
 * Deshalb: Namen auflösen, und was sich nicht auflösen lässt, kommt in die
 * Meldung statt still auf Knochen 0 zu zeigen.
 */
export class Eigenhaut {

    /** So viele Knochen trägt ein Punkt in einem `SkinnedMesh`. */
    static JE_PUNKT = 4;

    /**
     * Ein `SkinnedMesh` aus Netz und Hautdaten — oder das Netz unverändert.
     *
     * @param {THREE.Mesh} netz    das fertige Netz (Geometrie + Material)
     * @param {Object} skelett     `{skeleton, bones, boneByName}` aus `Knochenbau`
     * @param {Object} haut        `{knochen:[Namen], skin_indices, skin_weights}`
     * @returns {THREE.Mesh|THREE.SkinnedMesh}
     */
    static binden(netz, skelett, haut) {
        if (!netz || !skelett?.skeleton || !haut?.knochen
            || !haut.skin_indices || !haut.skin_weights) return netz;
        const spalte = Eigenhaut.spaltenNummern(haut.knochen, skelett);
        if (!spalte) return netz;

        const { index: roh, gewicht } = Eigenhaut.gewichte(haut);
        const index = new Float32Array(roh.length);
        for (let i = 0; i < roh.length; i++) index[i] = spalte[roh[i]] ?? 0;

        const geo = netz.geometry;
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(index, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(gewicht, 4));

        const gebunden = new THREE.SkinnedMesh(geo, netz.material);
        gebunden.name = netz.name;
        gebunden.visible = netz.visible;
        // Eine animierte Figur verlässt ihre Ruhe-Box; ohne das verschwindet
        // sie mitten in der Bewegung, sobald die Box aus dem Bild rutscht.
        gebunden.frustumCulled = false;
        gebunden.castShadow = netz.castShadow;
        gebunden.receiveShadow = netz.receiveShadow;
        // `userData` MUSS mit: Dort liegen die Rohgewichte, aus denen ein
        // Stueck nach einem Skelettneubau wieder gebunden wird
        // (`MhFigur._kleiderBinden`). Ohne sie ist die zweite Bindung
        // nicht mehr moeglich, und das Stueck bleibt still starr.
        gebunden.userData = netz.userData;
        // Eine eigene Trefferprüfung (Stranghaar: Strecken statt Dreiecke,
        // `Genesis9strangtreffer`) gehört zum Netz, nicht zur Klasse — sie zieht mit.
        if (Object.hasOwn(netz, 'raycast')) gebunden.raycast = netz.raycast;
        return gebunden;
    }

    /**
     * Rohe Spalten und Gewichte einer Hautantwort — float32 (Vorgabe) oder
     * kompakt `kodierung: 'u16u8'` (Genesis 9 seit 18.09.2026: uint16-Spalten,
     * uint8-Gewichte × 1/255 — ein Viertel der Bytes auf 410.202 Punkten).
     * @returns {{index: Float32Array|Uint16Array, gewicht: Float32Array}}
     */
    static gewichte(haut) {
        if (haut?.kodierung === 'u16u8') {
            const roh = base64ToBytes(haut.skin_weights);
            const gewicht = new Float32Array(roh.length);
            // Je Punkt auf Summe 1: Three normiert nicht, und 4 × 1/255 Rundung
            // hiesse bis zu 0,4 % Skalierung je Punkt — die Haut sah gekräuselt aus.
            for (let p = 0; p + 3 < roh.length; p += 4) {
                const summe = (roh[p] + roh[p + 1] + roh[p + 2] + roh[p + 3]) || 255;
                for (let k = 0; k < 4; k++) gewicht[p + k] = roh[p + k] / summe;
            }
            return { index: base64ToUint16(haut.skin_indices), gewicht };
        }
        return { index: base64ToFloat32(haut.skin_indices), gewicht: base64ToFloat32(haut.skin_weights) };
    }

    /**
     * Spaltennummer der Gewichte → Knochennummer im Skelett.
     *
     * `null`, wenn ein Name im Skelett fehlt: Dann ist die Zuordnung als
     * Ganzes fraglich, und ein halb gebundenes Netz reißt an der Stelle auf,
     * die niemand sucht.
     */
    static spaltenNummern(namen, skelett) {
        const nummer = new Map(skelett.bones.map((k, i) => [k.name, i]));
        const aus = new Int32Array(namen.length);
        const fehlend = [];
        for (let i = 0; i < namen.length; i++) {
            const gefunden = nummer.get(namen[i]);
            if (gefunden === undefined) fehlend.push(namen[i]);
            else aus[i] = gefunden;
        }
        if (fehlend.length) {
            Protokoll.warnung('Eigenhaut',
                `Hautgewichte nennen ${fehlend.length} Knochen, die das Skelett `
                + `nicht hat — nicht gebunden: ${fehlend.slice(0, 6).join(', ')}`);
            return null;
        }
        return aus;
    }

    /**
     * Das Netz an die Figur hängen und binden.
     *
     * `bindMatrix` ist die Lage des Netzes IN DER FIGURGRUPPE, nicht in der
     * Welt: Die Umkehrmatrizen des Skeletts stehen ebenfalls dort
     * (`Knochenbau.ruhelagen`), und beide müssen im selben Bezug liegen.
     * Mit der Weltmatrix wäre ein Stück, das gebunden wird, während die
     * Figur schon 90 cm weiter steht, um genau diese 90 cm doppelt
     * verrechnet — gemessen 1,92 m weit wandernde Stoffpunkte, im Bild ein
     * zerrissenes Kleidungsstück (07.09.2026).
     *
     * `netz.matrix` und nicht die Einheitsmatrix: Ein Netz mit eigener
     * Verschiebung in der Gruppe soll sie behalten. Bei den Körper- und
     * Kleidernetzen hier ist sie die Einheit.
     */
    static einhaengen(gruppe, netz, skelett) {
        gruppe.add(netz);
        if (!netz.isSkinnedMesh) return netz;
        netz.updateMatrix();
        netz.bind(skelett.skeleton, netz.matrix);
        return netz;
    }
}
