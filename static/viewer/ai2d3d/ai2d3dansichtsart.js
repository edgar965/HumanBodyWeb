/**
 * Ai2d3dansichtsart — die Ansichten der Zeilenleisten (04.11.2026, Edgar: „in jeder Zeile ab Zeile 3 diese ansichten plus die Rig, Kleider Toggle buttons“): dieselben fünf wie die
 * Leiste der PSHuman-Eingabe (`ai2d3d_pshumaneingabe.html`, `Ai2d3dpshumannetzbilder`), dort für Bilder, hier für die 3D-Felder einer Zeile.
 *
 *   textur       die Figur mit ihren Materialien — Ansichtsart „Textur“ der Felder
 *   normale      Normalen im Kamera-Raum als Farbe MIT den Normalenkarten der Materialien (Feinrelief) — wie PSHumans Normalenbilder; ohne Karte gleich „Netz-Normale“
 *   netz         grau, beleuchtet — Ansichtsart „Oberfläche“ (PSHuman: grau, Umgebungslicht + Licht aus der Kamera)
 *   netzfarbe    die Farben der Materialien (Farbbild bzw. Punktfarben) auf dem Netz, ohne Relief- und Rauheitskarten, beleuchtet — wie PSHumans „Netz farbig“
 *   netznormale  Normalen des Netzes im Kamera-Raum als Farbe (`MeshNormalMaterial`) — Ansichtsart „Normalen“, wie PSHuman
 *
 * Die Zeichner der Felder kennen nur ihre Ansichtsarten (`modus`): „Normale“ und „Netz farbig“ zeichnen sie als „Textur“, das Feld tauscht beim Rendern die Materialien jedes Netzes
 * gegen abgeleitete (`malen`, je Originalmaterial einmal angelegt) und legt sie danach zurück — die Materialien der Figuren werden nicht verändert. Ausgenommen: Überlagerungen nur für die
 * Ansicht (`userData.nurAnsicht`, z. B. das Rig).
 */
import * as THREE from 'three';

export class Ai2d3dansichtsart {
    static ARTEN = [
        { wert: 'textur', text: 'Textur', modus: 'textur', titel: 'Die Figur mit ihren Materialien (Farbbild, Relief, Rauheit)' },
        { wert: 'normale', text: 'Normale', modus: 'textur', titel: 'Normalen im Kamera-Raum als Farbe, mit den Normalenkarten der Figur (Feinrelief) — wie PSHumans Normalenbilder' },
        { wert: 'netz', text: 'Netz', modus: 'oberflaeche', titel: 'Das Netz grau, beleuchtet' },
        { wert: 'netzfarbe', text: 'Netz farbig', modus: 'textur', titel: 'Das Netz mit seinen Farben (Farbbild oder Punktfarben), ohne Relief- und Rauheitskarten, beleuchtet' },
        { wert: 'netznormale', text: 'Netz-Normale', modus: 'normalen', titel: 'Normalen des Netzes im Kamera-Raum als Farbe, ohne Normalenkarten — zum Vergleich mit „Normale“' },
    ];
    static _vorrat = new WeakMap();
    static _weiss = new THREE.Color(1, 1, 1);

    /** Die Ansichtsart, mit der die Zeichner das Feld füllen. */
    static modus(art) {
        return (Ai2d3dansichtsart.ARTEN.find(a => a.wert === art) ?? Ai2d3dansichtsart.ARTEN[0]).modus;
    }

    /** Tauscht das Feld beim Rendern die Materialien? */
    static getauscht(art) {
        return art === 'normale' || art === 'netzfarbe';
    }

    /** Das Feld `ansicht` (`Mesh3daiansicht`) in der Art `art` rendern: alle Ebenen in einem Durchgang, Materialien nur für diesen Durchgang getauscht. */
    static malen(ansicht, renderer, art) {
        const zurueck = [];
        ansicht.inhalt.traverse(o => {
            if (!o.isMesh || !o.material || o.userData.nurAnsicht) return;
            zurueck.push([o, o.material]);
            o.material = Array.isArray(o.material) ? o.material.map(m => Ai2d3dansichtsart.material(m, art)) : Ai2d3dansichtsart.material(o.material, art);
        });
        try {
            ansicht.kamera.layers.enableAll();
            renderer.render(ansicht.szene, ansicht.kamera);
        } finally {
            for (const [o, m] of zurueck) o.material = m;
        }
    }

    /** Das abgeleitete Material zu `m` — angelegt beim ersten Mal, danach nachgeführt (Karten kommen bei den Genesis-Figuren erst nach dem Netz, `Mesh3daiflaechennetz`). */
    static material(m, art) {
        let je = Ai2d3dansichtsart._vorrat.get(m);
        if (!je) Ai2d3dansichtsart._vorrat.set(m, je = {});
        let d = je[art], neu = false;
        if (art === 'normale') {
            d ??= je[art] = new THREE.MeshNormalMaterial();
            if (d.normalMap !== (m.normalMap ?? null)) { d.normalMap = m.normalMap ?? null; neu = true; }
            if (m.normalScale) d.normalScale.copy(m.normalScale);
        } else {
            d ??= je[art] = new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0 });
            if (d.map !== (m.map ?? null) || d.vertexColors !== !!m.vertexColors || d.alphaMap !== (m.alphaMap ?? null)) {
                d.map = m.map ?? null; d.vertexColors = !!m.vertexColors; d.alphaMap = m.alphaMap ?? null; neu = true;
            }
            d.color.copy(m.color ?? Ai2d3dansichtsart._weiss);
        }
        if (d.side !== m.side) { d.side = m.side; neu = true; }
        d.transparent = m.transparent; d.opacity = m.opacity ?? 1; d.alphaTest = m.alphaTest ?? 0; d.depthWrite = m.depthWrite; d.visible = m.visible;
        if (neu) d.needsUpdate = true;
        return d;
    }
}
