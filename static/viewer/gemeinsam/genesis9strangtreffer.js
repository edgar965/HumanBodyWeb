import * as THREE from 'three';

/**
 * Genesis9strangtreffer — ein Klick trifft Stranghaar.
 *
 * Edgar, 20.09.2026: „HS Viola Haar ist nicht auswählbar (wenn ich im Modell
 * view darauf klicke, ist das Modell ausgewählt)". Die Strähnen sind entartete
 * Dreiecke `[a, b, b]` (`Genesis9strang`: Drahtgitter, damit das SkinnedMesh
 * sie häutet). Three prüft einen Klick je Dreieck (`Ray.intersectTriangle`) —
 * ein Dreieck ohne Fläche trifft nie. Der Strahl ging durch das Haar hindurch
 * auf die Kopfhaut, und die gehört der Figur. Violas Kappe ist in Daz
 * unsichtbar und kommt gar nicht mit (`G9garderobe.teile`), es gab also
 * nichts zu treffen.
 *
 * Hier gilt jedes Dreieck als STRECKE a–b: getroffen, wenn der Strahl ihr
 * näher als TREFFERBREITE kommt (`Ray.distanceSqToSegment`, wie
 * `Line.raycast`) — aber mit der Häutung des Netzes (`getVertexPosition`
 * liefert bei einem SkinnedMesh die gestellte Lage).
 *
 * WAS ES KOSTET (gemessen im Chrome, Viola auf Ursula, 264.144 + 213.576
 * Punkte): das Häuten aller Punkte 360 ms je Prüfung — und die Schwebeanzeige
 * prüft JEDES Bild, in dem sich die Maus bewegt. Deshalb liegen die
 * gehäuteten Weltpunkte im Netz (`userData._strangwelt`) mit einem Stempel
 * aus Knochenmatrizen, Weltmatrix und Punktfassung: solange die Figur so
 * steht, kostet eine Prüfung nur die Streckenschleife. Vorher eine Grobprobe
 * mit jedem 64. Punkt (GROB_RAND): ein Klick an den Fuß fragt das Haar nicht.
 * Die Streckenschleife überspringt, was schon am Anfangspunkt weiter weg ist
 * als Trefferbreite plus längste Strecke — die meisten Strähnen.
 */
export class Genesis9strangtreffer {

    /** Wie nah der Strahl einer Strähne kommen muss (m) — Strähnen sind 1 px breit. */
    static TREFFERBREITE = 0.006;
    static GROB_SCHRITT = 64;
    static GROB_RAND = 0.15;

    /** Dem Netz die Strecken-Prüfung geben (überlebt `Eigenhaut.binden`). */
    static anbringen(netz) {
        netz.raycast = function (raycaster, intersects) {
            Genesis9strangtreffer.pruefen(this, raycaster, intersects);
        };
        return netz;
    }

    static pruefen(netz, raycaster, intersects) {
        const geo = netz.geometry;
        const index = geo?.index;
        const lage = geo?.attributes?.position;
        if (!index || !lage || !netz.visible) return;
        const strahl = raycaster.ray;
        const { welt, laengste } = Genesis9strangtreffer._weltpunkte(netz, lage, index);
        if (!Genesis9strangtreffer._inDerNaehe(welt, strahl)) return;

        const a = new THREE.Vector3(), b = new THREE.Vector3();
        const aufStrahl = new THREE.Vector3(), aufStrecke = new THREE.Vector3();
        const grenze = Genesis9strangtreffer.TREFFERBREITE ** 2;
        const grob = (Genesis9strangtreffer.TREFFERBREITE + laengste) ** 2;
        const idx = index.array;
        let bester = null;
        for (let i = 0; i + 1 < idx.length; i += 3) {
            a.fromArray(welt, idx[i] * 3);
            if (strahl.distanceSqToPoint(a) > grob) continue;
            b.fromArray(welt, idx[i + 1] * 3);
            if (strahl.distanceSqToSegment(a, b, aufStrahl, aufStrecke) > grenze) continue;
            const abstand = aufStrahl.distanceTo(strahl.origin);
            if (abstand < raycaster.near || abstand > raycaster.far) continue;
            if (!bester || abstand < bester.distance) {
                bester = { distance: abstand, point: aufStrecke.clone(), object: netz, index: i / 3 };
            }
        }
        if (bester) intersects.push(bester);
    }

    /** Grobprobe: kommt der Strahl irgendeinem 64. Punkt auf GROB_RAND nah? */
    static _inDerNaehe(welt, strahl) {
        const grenze = Genesis9strangtreffer.GROB_RAND ** 2;
        const p = new THREE.Vector3();
        for (let i = 0; i < welt.length; i += 3 * Genesis9strangtreffer.GROB_SCHRITT) {
            if (strahl.distanceSqToPoint(p.fromArray(welt, i)) < grenze) return true;
        }
        return false;
    }

    /** Die gehäuteten Weltpunkte — aus dem Netz, solange der Stempel stimmt. */
    static _weltpunkte(netz, lage, index) {
        const stempel = Genesis9strangtreffer._stempel(netz, lage);
        const alt = netz.userData._strangwelt;
        if (alt && alt.stempel === stempel && alt.welt.length === lage.count * 3) return alt;
        const welt = new Float32Array(lage.count * 3);
        const p = new THREE.Vector3();
        for (let i = 0; i < lage.count; i++) {
            netz.getVertexPosition(i, p).applyMatrix4(netz.matrixWorld);
            p.toArray(welt, i * 3);
        }
        const a = new THREE.Vector3(), b = new THREE.Vector3();
        const idx = index.array;
        let laengste = 0;
        for (let i = 0; i + 1 < idx.length; i += 3) {
            const d = a.fromArray(welt, idx[i] * 3).distanceToSquared(b.fromArray(welt, idx[i + 1] * 3));
            if (d > laengste) laengste = d;
        }
        const frisch = { stempel, welt, laengste: Math.sqrt(laengste) };
        netz.userData._strangwelt = frisch;
        return frisch;
    }

    /**
     * Was die Lage der Punkte ändert: die Knochenmatrizen des Skeletts (Three
     * schreibt sie je Bild in `boneMatrices`), die Weltmatrix des Netzes und
     * die Fassung des Punktattributs. Eine gewichtete Summe reicht als Stempel.
     */
    static _stempel(netz, lage) {
        let h = lage.version * 31 + 17;
        const w = netz.matrixWorld.elements;
        for (let i = 0; i < 16; i++) h += w[i] * (i + 1);
        const bm = netz.skeleton?.boneMatrices;
        if (bm) for (let i = 0; i < bm.length; i += 4) h += bm[i] * ((i & 63) + 1);
        return h;
    }
}
