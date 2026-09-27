import * as THREE from 'three';

/**
 * Vollindex — die GANZE Haut in den Export, nicht nur die sichtbare.
 *
 * FUND 26.09.2026 (Edgar mit Nahaufnahme: „an den Wangen gibt es auch Fehler
 * in den 3D Mesh"): Die Szene nimmt Hautdreiecke, die unter Kleid oder Haaren
 * liegen, aus dem Index — im Viewer sieht sie niemand, und es spart
 * Zeichenzeit (`hautverdeckung.js`, `figurhaut.js`). Den vollen Index hebt
 * sie in `geometry.userData.indexVoll` auf.
 *
 * Im Export ist das falsch: die Datei landet in einem fremden Programm mit
 * anderer Darstellung, und dort klaffen an genau diesen Stellen Löcher —
 * durch die man auf Innenflächen sieht (am Hals der rötliche Mundinnenraum).
 * Bei Damira1 fehlten 12.164 von 804.992 Körperdreiecken.
 *
 * ZWEI WEGE BRAUCHEN DASSELBE, deshalb ein eigenes Modul:
 * - `Netzpose.gebacken` für die Formate ohne Rig (OBJ, PLY, STL, GLB/DAE ohne
 *   Rig) — dort wird ohnehin eine Kopie gebaut;
 * - `Modellexport._glb` für „Rig an": dort gehen die LEBENDEN Netze zum
 *   Exporter, und die tragen den gekürzten Index der Szene. Ohne `tauschen`
 *   hätte ein GLB mit Skelett die Löcher behalten — dieselbe Fehlerklasse
 *   „dieselbe Logik, zweimal geschrieben", nur diesmal: einmal vergessen.
 *
 * Nicht über `Figurhaut.indexSetzen`: das Modul zieht Protokoll und Zustand
 * mit und wäre in einem Knoten-Testlauf nicht ladbar.
 */
export class Vollindex {

    /** Hat die Geometrie einen gemerkten vollen Index, der länger ist als der aktuelle? */
    static noetig(geometrie) {
        const voll = geometrie?.userData?.indexVoll;
        if (!voll?.index) return false;
        return !geometrie.index || voll.index.length > geometrie.index.count;
    }

    /**
     * Den vollen Index samt Materialzonen in DIESE Geometrie setzen.
     * Die Zonen müssen mitwandern — sie sind Abschnitte IM Index.
     * @returns true, wenn etwas gesetzt wurde
     */
    static setzen(geometrie, quelle = null) {
        const voll = (quelle || geometrie)?.userData?.indexVoll;
        if (!voll?.index) return false;
        geometrie.setIndex(new THREE.BufferAttribute(voll.index.slice(), 1));
        geometrie.clearGroups();
        for (const g of voll.gruppen || []) geometrie.addGroup(g.start, g.count, g.materialIndex);
        return true;
    }

    /**
     * Für den LEBENDEN Pfad: je Netz eine Kopie der Geometrie mit vollem
     * Index einhängen. Gibt die Rückstellung zurück — sie MUSS laufen, sonst
     * zeichnet die Szene danach die verdeckte Haut mit.
     * @returns {(() => void)|null}
     */
    static tauschen(objekte) {
        const betroffen = (objekte || []).filter((o) => o?.geometry && Vollindex.noetig(o.geometry));
        if (!betroffen.length) return null;
        const original = betroffen.map((o) => o.geometry);
        betroffen.forEach((o) => {
            const kopie = o.geometry.clone();
            Vollindex.setzen(kopie, o.geometry);
            o.geometry = kopie;
        });
        return () => betroffen.forEach((o, i) => { o.geometry = original[i]; });
    }
}
