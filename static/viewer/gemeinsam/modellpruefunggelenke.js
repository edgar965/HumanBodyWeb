import * as THREE from 'three';

/**
 * Modellpruefunggelenke — sitzen die Gelenke im Körper? Fünfte Klasse des Modell Checks (`Modellpruefung`, 02.11.2026, Foto-Genesis; Edgar: „Die andere Session hat auch
 * einen Figur-Check eingebaut. Erweitere ihn“). Anlass: Eigenmorphe (Versatz der Zeile 1 im Job Foto-Genesis) verschoben die Haut bis 17 cm, das Skelett blieb stehen —
 * an Kat_EigenShirt_Hose_Gehen lagen der linke Oberschenkel 21 mm, das rechte Schienbein 30 mm außerhalb der Haut (`ProjektTemp/_wegwerf/fotogenesis/ergaenzung/
 * gelenke_ruhe_diag.py`); beim Bewegen verformt sich die Figur dann falsch. Seither tragen die Eigenmorphe Gelenkversatz (`G9eigenmorphe.gelenke`, geschätzt mit
 * `Genesis9/gelenkversatz.py` in `KoerperKI_Fotos/zeile1regler.py`).
 *
 * Je Rumpf- und Gliedknochen (KNOCHEN, ohne Zehen, Fingerglieder, Anker und Gesicht: deren Mitten liegen schon bei der Grundfigur bis 16 mm außen) die verallgemeinerte
 * Windungszahl des Gelenks gegen das gestellte Körpernetz (Van Oosterom/Strackee, trägt auch die Löcher an Augen und Mund): |w| > 0,5 = innen.
 *
 *     const g = Modellpruefunggelenke.pruefen(koerper, lage);    // koerper: SkinnedMesh, lage: Float32Array (3 n) Welt → {geprueft, aussen: [{name, abstand_mm}]}
 */
export class Modellpruefunggelenke {

    static KNOCHEN = /^(hip|pelvis|spine[1-4]|neck[12]|head|(l|r)_(shoulder|upperarm|upperarmtwist[12]|forearm|forearmtwist[12]|hand|thigh|thightwist[12]|shin|foot))$/;

    static pruefen(koerper, lage) {
        // Gegen den VOLLEN Index (12.11.2026): Die Hautmaske nimmt die Haut unter dem Stoff aus dem Index (`Hautverdeckung`, Olesia1: 11.203 von 201.248 Dreiecken
        // unter Shirt und Jeans); durch das Loch fiel die Windungszahl an spine3/spine4 unter 0,5, und die Zeile meldete sie 42 und 58 mm „außen“.
        const M = Modellpruefunggelenke, geo = koerper.geometry, idx = geo.userData?.indexVoll?.index || geo.index?.array;
        if (!idx) return { geprueft: 0, aussen: [] };
        const aus = [], q = new THREE.Vector3();
        const knochen = koerper.skeleton.bones.filter((b) => M.KNOCHEN.test(b.name));
        for (const b of knochen) {
            b.getWorldPosition(q);
            if (Math.abs(M.windung(lage, idx, q)) > 0.5) continue;
            let d = Infinity;
            for (let i = 0; i < lage.length; i += 3) d = Math.min(d, (lage[i] - q.x) ** 2 + (lage[i + 1] - q.y) ** 2 + (lage[i + 2] - q.z) ** 2);
            aus.push({ name: b.name, abstand_mm: Math.round(1000 * Math.sqrt(d)) });
        }
        return { geprueft: knochen.length, aussen: aus };
    }

    /** Windungszahl des Punkts q gegen die Dreiecke `idx` der Punkte `lage`: ≈ ±1 innen, ≈ 0 außen. */
    static windung(lage, idx, q) {
        let s = 0;
        for (let t = 0; t < idx.length; t += 3) {
            const a = 3 * idx[t], b = 3 * idx[t + 1], c = 3 * idx[t + 2];
            const ax = lage[a] - q.x, ay = lage[a + 1] - q.y, az = lage[a + 2] - q.z;
            const bx = lage[b] - q.x, by = lage[b + 1] - q.y, bz = lage[b + 2] - q.z;
            const cx = lage[c] - q.x, cy = lage[c + 1] - q.y, cz = lage[c + 2] - q.z;
            const la = Math.hypot(ax, ay, az), lb = Math.hypot(bx, by, bz), lc = Math.hypot(cx, cy, cz);
            const zaehler = ax * (by * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - by * cx);
            const nenner = la * lb * lc + (ax * bx + ay * by + az * bz) * lc + (bx * cx + by * cy + bz * cz) * la + (cx * ax + cy * ay + cz * az) * lb;
            s += 2 * Math.atan2(zaehler, nenner);
        }
        return s / (4 * Math.PI);
    }
}
