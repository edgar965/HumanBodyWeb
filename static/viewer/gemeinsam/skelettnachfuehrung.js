/**
 * Skelettnachfuehrung — die Knochen dem gemorphten Koerper nachziehen.
 *
 * DER BEFUND (05.09.2026): `def_skeleton.json` ist eine feste Datei. Am
 * Groessenregler wuchs der Koerper von 110 cm auf 228 cm, das Skelett blieb
 * bei 168 cm stehen — sichtbar als Netz, das aus seinem Rig herauswaechst.
 * Gerechnet wird die neue Lage auf dem Server (`Gelenkanpassung`), hier
 * kommt sie nur an.
 *
 * DIE NACHRICHT IST VOLLSTAENDIG: `bones` enthaelt die BEWEGTEN Knochen.
 * Was fehlt, gehoert in die Ruhelage — deshalb setzt `anwenden` immer ALLE
 * Knochen, nicht nur die genannten. Sonst bliebe beim Zurueckdrehen des
 * Reglers stehen, was einmal verschoben war.
 *
 * WARUM NEU GEBUNDEN WERDEN MUSS: Three.js merkt sich beim Binden je Knochen
 * die Umkehrmatrix seiner Ruhelage (`boneInverses`). Wer einen Knochen
 * verschiebt und das unterlaesst, verschiebt damit das ganze Netz — der
 * Koerper zerreisst, ohne dass etwas geworfen wird.
 *
 * UND WARUM DABEI DIE RUHEDREHUNGEN GELTEN MUESSEN: `calculateInverses()`
 * liest die AKTUELLEN Weltmatrizen. Laeuft gerade eine Animation, stehen die
 * Knochen in der Pose des aktuellen Bildes; die wuerde dann als Ruhelage
 * einbrennen. Also: Ruhedrehungen setzen, binden, Pose zurueckschreiben.
 */
export class Skelettnachfuehrung {

    /**
     * @param {Object} skelettDaten die Antwort von `/api/character/rigify-skeleton/`
     */
    constructor(skelettDaten) {
        this.ruhe = new Map();
        for (const knochen of (skelettDaten?.bones || [])) {
            const p = knochen.local_position;
            const q = knochen.local_quaternion;
            this.ruhe.set(knochen.name, {
                // Blender (x,y,z) -> Three.js (x,z,-y), wie im Skelettbauer.
                lage: [p[0], p[2], -p[1]],
                // Blender [w,x,y,z] -> Three.js (x,z,-y,w).
                drehung: [q[1], q[3], -q[2], q[0]],
            });
        }
    }

    /** Gibt es ueberhaupt eine Ruhelage zum Nachfuehren? */
    get brauchbar() {
        return this.ruhe.size > 0;
    }

    /**
     * `THREE` steht hier NICHT als Typ (`{THREE.SkinnedMesh}`): Dieses Modul
     * importiert Three.js nicht, und der Typpruefer meldete den Namen als
     * `TS2503: Cannot find namespace 'THREE'`. Ein Typ, den niemand aufloest,
     * beschreibt auch nichts.
     *
     * @param netz das gebundene Koerpernetz (`THREE.SkinnedMesh`)
     * @param {Object} skelett {skeleton, boneByName} aus `buildRigifySkeleton`
     * @param {Object} bewegte {Knochenname: [x,y,z]} in Blender-Koordinaten
     * @returns {boolean} ob etwas gesetzt wurde
     */
    anwenden(netz, skelett, bewegte) {
        if (!netz || !skelett?.skeleton || !this.brauchbar) return false;

        const pose = this._poseSichern(skelett);
        for (const [name, knochen] of Object.entries(skelett.boneByName || {})) {
            const ruhe = this.ruhe.get(name);
            if (!ruhe) continue;
            const neu = bewegte?.[name];
            if (neu) {
                knochen.position.set(neu[0], neu[2], -neu[1]);
            } else {
                knochen.position.set(ruhe.lage[0], ruhe.lage[1], ruhe.lage[2]);
            }
            knochen.quaternion.set(ruhe.drehung[0], ruhe.drehung[1],
                                   ruhe.drehung[2], ruhe.drehung[3]);
        }

        // Ueber das NETZ, nicht ueber den Wurzelknochen: die Knochen haengen
        // unter dem SkinnedMesh, und dessen eigene Weltmatrix geht in
        // `boneInverses` ein. Sie muss also zuerst stimmen.
        netz.updateMatrixWorld(true);
        skelett.skeleton.calculateInverses();
        this._poseZurueck(skelett, pose);
        return true;
    }

    /**
     * Die laufende Pose merken — nur die Drehungen.
     *
     * Die Lagen werden bewusst NICHT zurueckgeschrieben: Sie sind ja gerade
     * das, was sich aendern soll. Der einzige Knochen, dessen Lage eine
     * Animation ueberhaupt beschreibt, ist die Wurzel, und die bekommt ihren
     * Wert im naechsten Bild ohnehin neu.
     */
    _poseSichern(skelett) {
        const pose = new Map();
        for (const knochen of skelett.skeleton.bones) {
            pose.set(knochen, knochen.quaternion.clone());
        }
        return pose;
    }

    _poseZurueck(skelett, pose) {
        for (const knochen of skelett.skeleton.bones) {
            const gemerkt = pose.get(knochen);
            if (gemerkt) knochen.quaternion.copy(gemerkt);
        }
        skelett.skeleton.bones[0]?.parent?.updateMatrixWorld(true);
    }
}
