import * as THREE from 'three';
import { base64ToFloat32 } from '../gemeinsam/kodierung.js';

/**
 * Smplxrig — das Skelett eines SMPL-X-Netzes in einer Three.js-Szene.
 *
 * Edgar (20.09.2026): „mach ein ausgabefenster in 3D mit dem SMPL modell dazu
 * inkl. Rig". Der Runner legt die 55 Skelettgelenke (Körper 22, Kiefer, Augen,
 * 2 × 15 Finger) in derselben Lage wie das Netz ab, der Endpunkt `gvhmr3d/`
 * liefert sie als `gelenke` (base64 float32 J×3) mit `eltern` (Baum). Hier:
 * eine Kugel je Gelenk (Körper größer als Finger) und ein Strich je Knochen
 * zum Elternteil — vor dem Netz gezeichnet (`depthTest` aus), damit das Rig
 * durch die Haut sichtbar bleibt.
 */
export class Smplxrig {

    static KOERPER = 22;
    static FARBE_GELENK = 0xffb347;
    static FARBE_KNOCHEN = 0xff7b1c;

    constructor(szene) {
        this.szene = szene;
        this.gruppe = new THREE.Group();
        this.gruppe.name = 'smplxrig';
        this.gruppe.renderOrder = 10;
        this.szene.add(this.gruppe);
        this.anzahl = 0;
    }

    get da() { return this.anzahl > 0; }

    get visible() { return this.gruppe.visible; }
    set visible(an) { this.gruppe.visible = !!an; }

    /** Aus der Antwort von `gvhmr3d/` bauen; ohne `gelenke` bleibt die Szene leer. */
    setzen(antwort) {
        this.leeren();
        if (!antwort || !antwort.gelenke || !Array.isArray(antwort.eltern)) return;
        const g = base64ToFloat32(antwort.gelenke);
        const n = Math.min(g.length / 3, antwort.eltern.length);
        if (n < 2) return;
        const punkte = [];
        for (let i = 0; i < n; i++) punkte.push(new THREE.Vector3(g[i * 3], g[i * 3 + 1], g[i * 3 + 2]));
        const striche = [];
        for (let i = 1; i < n; i++) {
            const e = antwort.eltern[i];
            if (e < 0 || e >= n) continue;
            striche.push(punkte[i].x, punkte[i].y, punkte[i].z, punkte[e].x, punkte[e].y, punkte[e].z);
        }
        const knochen = new THREE.BufferGeometry();
        knochen.setAttribute('position', new THREE.Float32BufferAttribute(striche, 3));
        this.gruppe.add(new THREE.LineSegments(knochen, new THREE.LineBasicMaterial({
            color: Smplxrig.FARBE_KNOCHEN, depthTest: false, transparent: true, opacity: 0.95,
        })));
        const hoehe = Math.max(0.5, Math.max(...punkte.map(p => p.y)) - Math.min(...punkte.map(p => p.y)));
        const stoff = new THREE.MeshBasicMaterial({ color: Smplxrig.FARBE_GELENK, depthTest: false });
        const gross = new THREE.SphereGeometry(hoehe * 0.011, 10, 8);
        const klein = new THREE.SphereGeometry(hoehe * 0.004, 6, 5);
        for (let i = 0; i < n; i++) {
            const kugel = new THREE.Mesh(i < Smplxrig.KOERPER ? gross : klein, stoff);
            kugel.position.copy(punkte[i]);
            this.gruppe.add(kugel);
        }
        this.anzahl = n;
    }

    leeren() {
        for (const kind of [...this.gruppe.children]) {
            this.gruppe.remove(kind);
            kind.geometry?.dispose?.();
        }
        this.anzahl = 0;
    }

    dispose() {
        this.leeren();
        this.szene.remove(this.gruppe);
    }
}
