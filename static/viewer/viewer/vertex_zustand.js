/**
 * Vertexzustand — was der Punkteditor gerade bearbeitet.
 *
 * WARUM eine Klasse (Umbau 16.08.2026): vertex_editor.js hatte 386 Zeilen und
 * dreizehn lose Modulvariablen. Siehe Musterzustand — dieselbe Lage.
 */
import * as THREE from 'three';

export class Vertexzustand {
    static veActive = false;
    static veTargetMesh = null;
    static veTargetKey = null;
    /** Punktwolke ueber dem Netz, zeigt Auswahl und Farben. */
    static vePointsOverlay = null;
    static veSelectedIndices = new Set();
    static veOrigPositions = null;
    /** Ziehgriffe und ihr Anzeigeobjekt. */
    static veGizmo = null;
    static veGizmoHelper = null;
    static veGizmoLastPos = new THREE.Vector3();
    /** Kastenauswahl mit der Maus. */
    static veBoxSelecting = false;
    static veBoxStart = { x: 0, y: 0 };
    static veBoxEnd = { x: 0, y: 0 };
    /** Ursprüngliche Raycast-Methode, waehrend BVH-Beschleunigung laeuft. */
    static veOrigRaycast = null;
}
