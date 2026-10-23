/**
 * Mesh3daibewegungsfigur — Messungen am Skelett der Genesis-Figur, die die Standardanimation von Mesh3D-AI bewegt (22.10.2026, aus `Mesh3daifigurbewegung` gelöst).
 *
 * `rahmen`: die Stücke aus der KI liegen in der Ruhelage der Kinematik ihrer Figur (`kinematik.json`, Ruhegelenke). Ist die gebaute Genesis-Figur dieselbe, liegen ihre Knochen auf diesen Gelenken; ein Unterschied der
 * Rahmen (Lage, Drehung) wird starr gemessen (`Mesh3daiausrichtung.starr`) und nur dann ausgeglichen, wenn es ihn gibt. `hoehe`: Körperhöhe über die Knochen wie `Eigenanimation.hoehe` der Charakter-Seite —
 * derselbe Schlüssel im Retarget-Vorrat für dieselbe Figur.
 */
import * as THREE from 'three';
import { Mesh3daiausrichtung } from './mesh3daiausrichtung.js';

export class Mesh3daibewegungsfigur {
    /** Name → Weltlage [x, y, z] je Knochen (der Gruppe in Ruhe). */
    static knochenlagen(modell) {
        const je = new Map();
        const p = new THREE.Vector3();
        modell.group.updateMatrixWorld(true);
        for (const b of modell.skelett?.bones || []) if (!je.has(b.name)) je.set(b.name, b.getWorldPosition(p).toArray());
        return je;
    }

    /** → `{abbildung: {quaternion, verschiebung} | null, rest_mm: number | null}` (Ruhegelenke `ruhezentren` in der Reihenfolge `knochen` → Knochen der Figur). */
    static rahmen(modell, knochen, ruhezentren) {
        if (!ruhezentren?.length || !knochen?.length) return { abbildung: null, rest_mm: null };
        const je = Mesh3daibewegungsfigur.knochenlagen(modell);
        const a = [], b = [];
        knochen.forEach((name, i) => { if (je.has(name) && ruhezentren[i]) { a.push(ruhezentren[i]); b.push(je.get(name)); } });
        if (a.length < 3) return { abbildung: null, rest_mm: null };
        const r = Mesh3daiausrichtung.starr(a, b);
        // Nur ausgleichen, was wirklich verschoben ist — liegen die Rahmen aufeinander, bleibt das Stück unberührt.
        const verschoben = r.verschiebung.length() > 1e-4 || 2 * Math.acos(Math.min(1, Math.abs(r.quaternion.w))) > 1e-3;
        return { abbildung: verschoben ? r : null, rest_mm: r.rest_mm };
    }

    static hoehe(modell) {
        let unten = Infinity, oben = -Infinity;
        for (const [, p] of Mesh3daibewegungsfigur.knochenlagen(modell)) { unten = Math.min(unten, p[1]); oben = Math.max(oben, p[1]); }
        return oben > unten ? oben - unten : (modell.hoehe || 1.68);
    }
}
