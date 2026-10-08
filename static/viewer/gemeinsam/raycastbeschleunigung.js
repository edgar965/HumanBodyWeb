import * as THREE from 'three';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';

THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;

/**
 * Raycastbeschleunigung — three-mesh-bvh je Geometrie EINMAL aufbauen, danach
 * läuft ihr Raycast an der Bounding-Hierarchie entlang statt an jedem Dreieck.
 *
 * Befund 08.10.2026 (Edgar: „Bedienung sehr holprig … drehen, verschieben hakt",
 * Seite Charakter, Modell „cute girl"): Schwebeanzeige (`schwebeanzeige.js`,
 * ein Treffertest je Bild bei jeder Mausbewegung) und der Klick-Raycast
 * (`interaction.js`) prüften mit Three.js' eigenem, unbeschleunigten Raycaster
 * gegen die GANZE Szene. Gemessen in der Konsole (`A:\3DTools\ProjektTemp\
 * _wegwerf\edgar\raycast_messung.md`): 297 ms für EINEN `intersectObjects`-Aufruf
 * gegen 68 Netze / 335.025 Dreiecke, ohne Suchbaum (`hatBVH: false`) — bei fast
 * jeder Mausbewegung während des Drehens oder Verschiebens blockierte das den
 * Hauptfaden fast eine drittel Sekunde. Blender nutzt dafür eine eigene,
 * beschleunigte Struktur und spürt das nicht — daher der Unterschied, nicht die
 * höhere Auflösung dort.
 *
 * DER SUCHBAUM KENNT KEINE HÄUTUNG (Edgar, 08.10.2026 abends: „wenn ich auf das T-Shirt
 * klicke, wird es nicht angezeigt im Tab links"): Er steht über den Punkten der
 * RUHEHALTUNG. Gemessen am Modell „Edgar" (G9 Base Shirt, 196 Strahlen, Spine und Oberarme
 * gedreht): `acceleratedRaycast` 121 Treffer bei mittlerem z 0,074 — unverändert gegenüber der
 * Ruhe —, der Raycast von Three.js, der die Häutung rechnet, 77 Treffer bei z 0,235. Ist die
 * Figur animiert (die letzte Animation läuft nach dem Laden wieder), traf der Klick die
 * Ruhehaltung statt das sichtbare Stück: keine Auswahl, keine Markierung im Reiter, und die
 * Schwebeanzeige nannte das falsche Stück. Darum gilt der Suchbaum nur für ein gehäutetes
 * Netz, dessen Skelett in Ruhe steht (`ruhend`); sonst rechnet `Mesh.raycast` wie vor dem
 * Umbau — langsamer, aber richtig. Netze ohne Skelett nehmen den Suchbaum immer.
 *
 * Seiten, die dieses Modul einbinden, brauchen `mesh_bvh=1` in ihrer
 * `_importmap.html` (sonst löst der Browser den Namen `three-mesh-bvh` nicht auf).
 */
export class Raycastbeschleunigung {
    /** Geometrien, deren Suchbaum schon steht — ein zweiter Aufruf ist billig. */
    static _fertig = new WeakSet();

    /** Wie weit eine Knochenmatrix von der Einheitsmatrix abweichen darf und noch „Ruhe" heißt (Meter / Bogenmaß). */
    static TOLERANZ = 5e-4;

    /** `meshes` beschleunigen, bevor gegen sie geraycastet wird. */
    static sicherstellen(meshes) {
        for (const mesh of meshes) {
            const geo = mesh?.geometry;
            if (!geo || Raycastbeschleunigung._fertig.has(geo)) continue;
            Raycastbeschleunigung._fertig.add(geo);
            try {
                geo.computeBoundsTree();
                mesh.raycast = mesh.isSkinnedMesh ? Raycastbeschleunigung._gehaeutet : acceleratedRaycast;
            } catch {
                // Leere oder sonst untaugliche Geometrie — bleibt beim normalen (langsamen) Raycast.
            }
        }
    }

    /** `Mesh.raycast` eines gehäuteten Netzes: Suchbaum nur in Ruhe, sonst der Raycast mit Häutung. */
    static _gehaeutet(raycaster, intersects) {
        const verfahren = Raycastbeschleunigung.ruhend(this) ? acceleratedRaycast : THREE.Mesh.prototype.raycast;
        verfahren.call(this, raycaster, intersects);
    }

    /**
     * Steht das Skelett des Netzes in der Bindehaltung? Dann ist jede Knochenmatrix
     * (`Welt des Knochens × Umkehrung der Bindehaltung`) die Einheitsmatrix und die Punkte der
     * Geometrie sind die sichtbaren. Ohne Skelett: nicht gehäutet, also ja.
     */
    static ruhend(mesh) {
        const skelett = mesh.skeleton;
        if (!skelett) return true;
        skelett.update();
        const m = skelett.boneMatrices;
        for (let i = 0; i < m.length; i += 1) {
            const soll = (i % 16) % 5 === 0 ? 1 : 0;      // Spalten-Hauptdiagonale: 0, 5, 10, 15
            if (Math.abs(m[i] - soll) > Raycastbeschleunigung.TOLERANZ) return false;
        }
        return true;
    }
}
