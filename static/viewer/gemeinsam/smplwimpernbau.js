import * as THREE from 'three';
import { Eigenhaut } from './eigenhaut.js';

/**
 * Smplwimpernbau — obere Wimpern für eine SMPL-X-Figur.
 *
 * WARUM (Edgar, 25.09.2026: „mach auch Augen …"): SMPL-X hat keine Wimpern.
 * Der Augapfel ragt gemessen 4,5 mm vor die Haut (`SMPL/xdetails.py`); wo er
 * aus der Haut tritt, liegt der Lidrand. Hier: je Auge die Augapfelpunkte,
 * die einem Hautpunkt näher als `RAND_M` kommen, der obere Bogen davon
 * (über der Augenmitte), von außen nach innen sortiert — daran ein Streifen,
 * der nach vorn-oben absteht und sich nach oben biegt. Die Härchen sind eine
 * Alphakarte (Canvas, einmal gezeichnet; 64 feine Striche — mit 90 × 2,2 px
 * sahen sie am 25.09.2026 wie eine Bürste aus). Länge = `wimpern_laenge` (Faktor),
 * Farbe = `wimpern`, wie bei HumanBody (`Koerperdetails`).
 * Knochen: `Head` (die Lider haben in SMPL-X keine eigenen Gelenke).
 */
export class Smplwimpernbau {

    /** Augapfelpunkte je Seite (Topologie des SMPL-X-Netzes, `SmplxKopf`). */
    static AUGEN = [[9383, 9929], [9929, 10475]];
    static RAND_M = 0.0016;
    static LAENGE_M = 0.0075;
    static PUNKTE = 28;

    static _karte = null;

    /** Die Härchen als Alphakarte — 64 Striche, zur Mitte länger. */
    static karte() {
        if (Smplwimpernbau._karte) return Smplwimpernbau._karte;
        const leinwand = document.createElement('canvas');
        leinwand.width = 512;
        leinwand.height = 64;
        const g = leinwand.getContext('2d');
        g.fillStyle = '#000';
        g.fillRect(0, 0, 512, 64);
        g.strokeStyle = '#fff';
        g.lineCap = 'round';
        for (let i = 0; i < 64; i++) {
            const x = 4 + (i / 63) * 504 + Math.sin(i * 12.9898) * 3;
            const lang = 34 + 26 * Math.sin((Math.PI * i) / 63) + Math.sin(i * 78.233) * 5;
            g.lineWidth = 1.3;
            g.beginPath();
            g.moveTo(x, 64);
            g.quadraticCurveTo(x + 3, 64 - lang * 0.6, x + 6, 64 - lang);
            g.stroke();
        }
        Smplwimpernbau._karte = new THREE.CanvasTexture(leinwand);
        return Smplwimpernbau._karte;
    }

    /** Der obere Lidrand eines Auges: Punkte (Meter), außen → innen. */
    static lidrand(punkte, von, bis) {
        const auge = [];
        for (let i = von; i < bis; i++) auge.push(new THREE.Vector3(...punkte[i]));
        const mitte = auge.reduce((s, p) => s.add(p), new THREE.Vector3()).divideScalar(auge.length);
        const haut = [];
        for (let i = 0; i < 9383; i++) {
            const p = punkte[i];
            if (Math.abs(p[0] - mitte.x) < 0.025 && Math.abs(p[1] - mitte.y) < 0.02
                && p[2] > mitte.z - 0.005) haut.push(new THREE.Vector3(...p));
        }
        const rand = auge.filter((p) => p.y > mitte.y - 0.0005 && p.z > mitte.z
            && haut.some((h) => h.distanceTo(p) < Smplwimpernbau.RAND_M));
        if (rand.length < 4) return null;
        const aussen = Math.sign(mitte.x) || 1;
        rand.sort((a, b) => (b.x - a.x) * aussen);
        return { mitte, rand };
    }

    /**
     * Beide Wimpernstreifen bauen und an die Figur hängen.
     * @returns {THREE.SkinnedMesh|null}
     */
    static bauen(gruppe, skelett, punkte, laenge = 1) {
        const kopf = skelett?.bones?.findIndex((k) => k.name === 'Head');
        if (kopf === undefined || kopf < 0) return null;
        const lage = [];
        const uv = [];
        const index = [];
        for (const [von, bis] of Smplwimpernbau.AUGEN) {
            const lid = Smplwimpernbau.lidrand(punkte, von, bis);
            if (!lid) continue;
            const kurve = new THREE.CatmullRomCurve3(Smplwimpernbau._glaetten(lid.rand));
            const basis = lage.length / 3;
            const n = Smplwimpernbau.PUNKTE;
            for (let i = 0; i < n; i++) {
                const t = i / (n - 1);
                const p = kurve.getPoint(t);
                const aussen = p.clone().sub(lid.mitte).normalize();
                const richtung = aussen.multiplyScalar(0.55).add(new THREE.Vector3(0, 0.35, 0.45)).normalize();
                const l = Smplwimpernbau.LAENGE_M * laenge * (0.55 + 0.45 * Math.sin(Math.PI * (0.15 + 0.7 * t)));
                const mitteP = p.clone().addScaledVector(richtung, l * 0.5);
                const spitze = p.clone().addScaledVector(richtung, l).add(new THREE.Vector3(0, l * 0.35, 0));
                for (const [q, v] of [[p, 0], [mitteP, 0.5], [spitze, 1]]) {
                    lage.push(q.x, q.y, q.z);
                    uv.push(t, v);
                }
                if (i + 1 < n) {
                    const a = basis + i * 3;
                    index.push(a, a + 3, a + 1, a + 1, a + 3, a + 4, a + 1, a + 4, a + 2, a + 2, a + 4, a + 5);
                }
            }
        }
        if (!lage.length) return null;
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.Float32BufferAttribute(lage, 3));
        geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
        geo.setIndex(index);
        geo.computeVertexNormals();
        const n = lage.length / 3;
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(new Array(n).fill([kopf, 0, 0, 0]).flat(), 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(new Array(n).fill([1, 0, 0, 0]).flat(), 4));
        const netz = new THREE.SkinnedMesh(geo, new THREE.MeshStandardMaterial({
            color: 0x111111, alphaMap: Smplwimpernbau.karte(), alphaTest: 0.5,
            side: THREE.DoubleSide, roughness: 0.6,
        }));
        netz.name = 'smpl_wimpern';
        netz.frustumCulled = false;
        Eigenhaut.einhaengen(gruppe, netz, skelett);
        return netz;
    }

    /** Doppelte und zu dichte Randpunkte ausdünnen, damit die Kurve nicht zittert. */
    static _glaetten(punkte) {
        const aus = [punkte[0]];
        for (const p of punkte.slice(1)) {
            if (p.distanceTo(aus[aus.length - 1]) > 0.0012) aus.push(p);
        }
        return aus.length >= 2 ? aus : punkte.slice(0, 2);
    }
}
