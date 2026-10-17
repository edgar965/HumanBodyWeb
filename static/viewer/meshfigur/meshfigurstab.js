import * as THREE from 'three';
import { Meshfighaltungspose } from './meshfighaltungspose.js';
import { Meshfighaut } from './meshfighaut.js';

/**
 * Meshfigurstab — ein gehaltener Gegenstand (Stab) bleibt in der Faust und weicht dem Körper aus (14.10.2026).
 *
 * Edgar (Zauberer im Tanz): „Der Stab geht einmal DURCH die Hand, einmal liegt er außerhalb" — „beim letzten Screenshot durch den Körper!!". Beides sind die zwei Seiten einer Aufgabe: Bindet man den Stab
 * starr an die Hand in der Lage, in der die Faust ihn greift (`Meshfighaltungspose`), steckt er in jedem Bild in der Faust — und durchsticht den Körper, sobald der Arm quer vor den Rumpf kommt (gemessen am
 * Zauberer, DanceKurz: in 51 % der Bilder der Rumpf, in 37 % der eigene Arm, in 10 % der Kopf). Bindet man ihn dagegen an die Ruhelage der Hand, liegt er zwar frei, aber neben der Faust.
 *
 * Ein Stab in einer Faust darf sich um die Faust drehen: die Finger umschließen ihn nicht fest, und das Handgelenk gibt nach. Je Bild sucht diese Klasse den KLEINSTEN Schwenk um die Faust (Drehpunkt = die
 * Stelle der Stabachse, die den Knöcheln am nächsten liegt), bei dem die Stabachse genug Abstand zu Körperpunkten hat. Die Stabachse liegt in der Hand-Lage der Haltung (Hauptachse der Stabpunkte um die
 * Faust). Körper = jeder `STRIDE`-te Punkt des Körpernetzes in der gerade gestellten Pose (CPU-Häutung), ohne die Hand und Finger der haltenden Seite (der Stab steckt ja in ihr); ein Raster mit `KORN_M` Zellen.
 * Prüfpunkte entlang der Achse fern der Faust (`GRIFFNAH_M`); Schwenkwinkel bis `MAX_WINKEL`, kleinster zuerst. Die Kosten sind der Winkel plus ein Anteil der Richtungsänderung gegen das letzte Bild
 * (`BEWEGUNG`), damit der Stab nicht springt; ist nichts frei, gewinnt die Lage mit den wenigsten Treffern.
 *
 * Wirkt nur, wo der Stab abgelöst an die Haltung gebunden ist (`Meshfighaut._an_die_haltung` mit `beweglich`): seine eigene Matrix ist dann der Schwenk nach der Häutung.
 */
export class Meshfigurstab {

    static STRIDE = 12;
    static KORN_M = 0.06;
    static ABSTAND_M = 0.055;
    static GRIFFNAH_M = 0.12;
    static SCHRITT_M = 0.07;
    static WINKEL = [0, 2, 4, 6, 8, 10, 12, 15, 18, 21, 25, 30, 35, 40];
    static MAX_WINKEL = 40;
    static AZIMUT = 12;
    static BEWEGUNG = 0.6;
    static KNOECHEL = ['index1', 'mid1', 'ring1', 'pinky1'];

    constructor(buehne) {
        this.buehne = buehne;
        this._stab = new Map();             // Name des Bestandteils -> {objekt, seite, lokal, letzte}
        this._koerper = null;               // {netz, seite, ids, rest, aus}
        this._raster = { zellen: 0, start: null, punkte: null };
    }

    /** Ein Bestandteil ist (neu) gebunden: gehaltene, abgelöst gebundene Gegenstände werden vermerkt, alles andere vergessen. */
    gebunden(name, objekt) {
        const netz = objekt.objekt ? Meshfighaut.netze(objekt.objekt)[0] : null;
        const seite = (this.buehne.teile.eintraege.get(name) || {}).haelt;
        if (!objekt.beweglich || !netz?.userData?.haltungsbindung || !seite) { this._stab.delete(name); return; }
        this._stab.set(name, { objekt, seite, lokal: this._lokal(objekt, netz, seite), letzte: null });
    }

    /** Ein Bild: jeden gehaltenen Stab in der Faust lassen und dem Körper ausweichen lassen. */
    takt() {
        const inst = this.buehne.modell;
        if (!inst?.bodyMesh?.isSkinnedMesh || !this._stab.size) return;
        inst.group.updateMatrixWorld(true);
        for (const e of this._stab.values()) {
            const netz = e.objekt.objekt ? Meshfighaut.netze(e.objekt.objekt)[0] : null;
            if (!netz?.userData?.haltungsbindung || !e.lokal) continue;
            const hand = inst.skelett.skeleton.bones.find(b => b.name === `${e.seite}_hand`);
            if (!hand) continue;
            const punkte = this._koerperPunkte(inst, e.seite);
            const schwenk = this._waehlen(e, hand.matrixWorld, punkte);
            netz.matrix.copy(schwenk).multiply(netz.userData.hebung);
            netz.matrixWorldNeedsUpdate = true;
        }
        this.buehne.wach?.();
    }

    // ------------------------------------------------------------------ Stab in der Hand-Lage der Haltung

    /** `{achse, griff, von, bis}` im Raum der Hand in der Haltung (m): Hauptachse der Stabpunkte um die Faust, Drehpunkt an der Achse neben den Knöcheln, Ausdehnung des Stabs entlang der Achse relativ zum Drehpunkt. */
    _lokal(objekt, netz, seite) {
        const modell = objekt.modell;
        const pose = modell && objekt._drehung ? Meshfighaltungspose.gemerkt(modell, objekt._drehung) : null;
        if (!pose) return null;
        const bones = modell.skelett.skeleton.bones;
        const nummer = name => bones.findIndex(b => b.name === name);
        const h = nummer(`${seite}_hand`);
        if (h < 0) return null;
        const invHand = pose.inverse[h];
        const heb = netz.userData.hebung, roh = netz.geometry.getAttribute('position');
        const v = new THREE.Vector3(), alle = [];
        for (let i = 0; i < roh.count; i += 10) alle.push(v.fromBufferAttribute(roh, i).applyMatrix4(heb).applyMatrix4(invHand).clone());
        const nah = alle.filter(p => p.length() < 0.25);
        if (nah.length < 20) return null;
        const mitte = nah.reduce((s, p) => s.add(p), new THREE.Vector3()).multiplyScalar(1 / nah.length);
        const achse = Meshfigurstab._hauptachse(nah, mitte);
        const knoechel = new THREE.Vector3();
        let n = 0;
        for (const k of Meshfigurstab.KNOECHEL) {
            const i = nummer(`${seite}_${k}`);
            if (i < 0) continue;
            const welt = pose.inverse[i].clone().invert();                     // der Knochen in der Haltung (Lage der Figurgruppe)
            knoechel.add(new THREE.Vector3().setFromMatrixPosition(welt).applyMatrix4(invHand));
            n++;
        }
        if (!n) return null;
        knoechel.multiplyScalar(1 / n);
        const griff = mitte.clone().addScaledVector(achse, knoechel.clone().sub(mitte).dot(achse));
        const t = alle.map(p => p.clone().sub(griff).dot(achse)).sort((a, b) => a - b);
        return { achse, griff, von: t[Math.floor(0.01 * t.length)], bis: t[Math.floor(0.99 * t.length)] };
    }

    static _hauptachse(punkte, mitte) {
        const c = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
        for (const p of punkte) {
            const d = [p.x - mitte.x, p.y - mitte.y, p.z - mitte.z];
            for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) c[a][b] += d[a] * d[b];
        }
        let v = [1, 1, 1];
        for (let k = 0; k < 60; k++) {
            const w = [0, 1, 2].map(a => c[a][0] * v[0] + c[a][1] * v[1] + c[a][2] * v[2]);
            const l = Math.hypot(...w) || 1;
            v = w.map(x => x / l);
        }
        const achse = new THREE.Vector3(...v);
        if (achse.y < 0) achse.negate();
        return achse;
    }

    // ------------------------------------------------------------------ Körper

    /** Jeder `STRIDE`-te Körperpunkt in der gestellten Pose als `{n, p: Float32Array}`; Hand und Finger der haltenden Seite fehlen. */
    _koerperPunkte(inst, seite) {
        const netz = inst.bodyMesh;
        let k = this._koerper;
        if (!k || k.netz !== netz || k.seite !== seite || k.skeleton !== netz.skeleton) k = this._koerper = this._koerperVorbereiten(netz, seite);
        netz.skeleton.update();
        const b = netz.skeleton.boneMatrices, n = k.ids.length, aus = k.aus;
        for (let i = 0; i < n; i++) {
            const x = k.rest[3 * i], y = k.rest[3 * i + 1], z = k.rest[3 * i + 2];
            let ax = 0, ay = 0, az = 0;
            for (let j = 0; j < 4; j++) {
                const w = k.gewicht[4 * i + j];
                if (w === 0) continue;
                const o = 16 * k.knochen[4 * i + j];
                ax += w * (b[o] * x + b[o + 4] * y + b[o + 8] * z + b[o + 12]);
                ay += w * (b[o + 1] * x + b[o + 5] * y + b[o + 9] * z + b[o + 13]);
                az += w * (b[o + 2] * x + b[o + 6] * y + b[o + 10] * z + b[o + 14]);
            }
            aus[3 * i] = ax; aus[3 * i + 1] = ay; aus[3 * i + 2] = az;
        }
        this._rasterBauen(aus, n);
        return n;
    }

    _koerperVorbereiten(netz, seite) {
        const pos = netz.geometry.getAttribute('position'), si = netz.geometry.getAttribute('skinIndex'), sw = netz.geometry.getAttribute('skinWeight');
        const hand = new RegExp(`^${seite}_(hand|thumb|index|mid|ring|pinky|carpal|metacarpal)`);
        const bones = netz.skeleton.bones;
        const ids = [];
        for (let v = 0; v < pos.count; v += Meshfigurstab.STRIDE) {
            let best = 0, bw = -1;
            for (let j = 0; j < 4; j++) { const w = sw.getComponent(v, j); if (w > bw) { bw = w; best = si.getComponent(v, j); } }
            if (!hand.test(bones[best]?.name || '')) ids.push(v);
        }
        const n = ids.length, rest = new Float32Array(3 * n), knochen = new Uint16Array(4 * n), gewicht = new Float32Array(4 * n);
        const m = netz.bindMatrix.elements;
        ids.forEach((v, i) => {
            const x = pos.getX(v), y = pos.getY(v), z = pos.getZ(v);
            rest[3 * i] = m[0] * x + m[4] * y + m[8] * z + m[12];
            rest[3 * i + 1] = m[1] * x + m[5] * y + m[9] * z + m[13];
            rest[3 * i + 2] = m[2] * x + m[6] * y + m[10] * z + m[14];
            for (let j = 0; j < 4; j++) { knochen[4 * i + j] = si.getComponent(v, j); gewicht[4 * i + j] = sw.getComponent(v, j); }
        });
        return { netz, seite, skeleton: netz.skeleton, ids, rest, knochen, gewicht, aus: new Float32Array(3 * n) };
    }

    /** Ein Raster (Zählsortierung) über die Körperpunkte: je Zelle die Punkte darin. */
    _rasterBauen(p, n) {
        const korn = Meshfigurstab.KORN_M, r = Meshfigurstab.ABSTAND_M;
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i < n; i++) for (let a = 0; a < 3; a++) { const w = p[3 * i + a]; if (w < lo[a]) lo[a] = w; if (w > hi[a]) hi[a] = w; }
        const dim = [0, 1, 2].map(a => Math.ceil((hi[a] - lo[a] + 2 * r) / korn) + 1);
        const g = this._raster;
        g.lo = lo.map(x => x - r); g.dim = dim;
        const zellen = dim[0] * dim[1] * dim[2];
        if (!g.start || g.start.length < zellen + 1) g.start = new Int32Array(zellen + 1);
        else g.start.fill(0, 0, zellen + 1);
        if (!g.punkte || g.punkte.length < n) g.punkte = new Int32Array(n);
        const zelle = i => {
            const x = Math.floor((p[3 * i] - g.lo[0]) / korn), y = Math.floor((p[3 * i + 1] - g.lo[1]) / korn), z = Math.floor((p[3 * i + 2] - g.lo[2]) / korn);
            return (x * dim[1] + y) * dim[2] + z;
        };
        for (let i = 0; i < n; i++) g.start[zelle(i) + 1]++;
        for (let c = 0; c < zellen; c++) g.start[c + 1] += g.start[c];
        const fuell = g.start.slice(0, zellen);
        for (let i = 0; i < n; i++) g.punkte[fuell[zelle(i)]++] = i;
        g.zellen = zellen; g.p = p;
    }

    /** Liegt ein Körperpunkt näher als `ABSTAND_M` an `q`? */
    _beruehrt(q) {
        const g = this._raster, korn = Meshfigurstab.KORN_M, r2 = Meshfigurstab.ABSTAND_M ** 2, dim = g.dim, p = g.p;
        const cx = Math.floor((q.x - g.lo[0]) / korn), cy = Math.floor((q.y - g.lo[1]) / korn), cz = Math.floor((q.z - g.lo[2]) / korn);
        for (let x = Math.max(0, cx - 1); x <= Math.min(dim[0] - 1, cx + 1); x++) {
            for (let y = Math.max(0, cy - 1); y <= Math.min(dim[1] - 1, cy + 1); y++) {
                for (let z = Math.max(0, cz - 1); z <= Math.min(dim[2] - 1, cz + 1); z++) {
                    const c = (x * dim[1] + y) * dim[2] + z;
                    for (let k = g.start[c]; k < g.start[c + 1]; k++) {
                        const i = g.punkte[k];
                        const dx = p[3 * i] - q.x, dy = p[3 * i + 1] - q.y, dz = p[3 * i + 2] - q.z;
                        if (dx * dx + dy * dy + dz * dz < r2) return true;
                    }
                }
            }
        }
        return false;
    }

    // ------------------------------------------------------------------ Schwenk wählen

    /** Treffer der Stabachse mit Richtung `d` um den Drehpunkt `g`. */
    _treffer(e, g, d, tmp) {
        let n = 0;
        const { von, bis } = e.lokal;
        for (let t = von; t <= bis; t += Meshfigurstab.SCHRITT_M) {
            if (Math.abs(t) < Meshfigurstab.GRIFFNAH_M) continue;
            tmp.copy(g).addScaledVector(d, t);
            if (this._beruehrt(tmp)) n++;
        }
        return n;
    }

    /** Die Matrix des kleinsten Schwenks um die Faust (Welt), der die Stabachse frei vom Körper hält; `handMatrix` = Welt der Handknochen. */
    _waehlen(e, handMatrix, n) {
        const g = e.lokal.griff.clone().applyMatrix4(handMatrix);
        const d0 = e.lokal.achse.clone().transformDirection(handMatrix);
        const e1 = new THREE.Vector3(1, 0, 0).addScaledVector(d0, -d0.x);
        if (e1.lengthSq() < 1e-6) e1.set(0, 1, 0).addScaledVector(d0, -d0.y);
        e1.normalize();
        const e2 = new THREE.Vector3().crossVectors(d0, e1).normalize();
        const tmp = new THREE.Vector3(), d = new THREE.Vector3(), q = new THREE.Quaternion(), u = new THREE.Vector3();
        let beste = null;
        const kosten = (w, dd) => w + (e.letzte ? Meshfigurstab.BEWEGUNG * THREE.MathUtils.radToDeg(dd.angleTo(e.letzte)) : 0);
        for (const w of Meshfigurstab.WINKEL) {
            if (beste && beste.treffer === 0 && w > beste.kosten) break;
            const schritte = w === 0 ? 1 : Meshfigurstab.AZIMUT;
            for (let k = 0; k < schritte; k++) {
                const phi = 2 * Math.PI * k / schritte;
                u.copy(e1).multiplyScalar(Math.cos(phi)).addScaledVector(e2, Math.sin(phi));
                q.setFromAxisAngle(u, THREE.MathUtils.degToRad(w));
                d.copy(d0).applyQuaternion(q);
                const treffer = this._treffer(e, g, d, tmp);
                const c = kosten(w, d);
                if (!beste || treffer < beste.treffer || (treffer === beste.treffer && c < beste.kosten)) beste = { treffer, kosten: c, q: q.clone(), d: d.clone() };
            }
        }
        e.letzte = beste.d;
        const schwenk = new THREE.Matrix4().makeTranslation(g.x, g.y, g.z);
        schwenk.multiply(new THREE.Matrix4().makeRotationFromQuaternion(beste.q));
        schwenk.multiply(new THREE.Matrix4().makeTranslation(-g.x, -g.y, -g.z));
        return schwenk;
    }
}
