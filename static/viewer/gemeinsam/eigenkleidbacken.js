import * as THREE from 'three';
import { Eigenkleidwerte } from './eigenkleidwerte.js';
import { Eigenkleidgeometrie } from './eigenkleidgeometrie.js';
import { Koerperkoordinatenkarte } from './koerperkoordinatenkarte.js';
import { EigenkleidschnittGLSL } from './eigenkleidschnitt.js';
import { Eigenrock } from './eigenrock.js';

/**
 * Eigenkleidbacken — die eigenen Stücke (Oberteil, Hose, Socken, Kleid-Oberteil) als Netz (02.11.2026; vorher `ProjektTemp/_wegwerf/tripo_wahrheit/eigen_backen.js`).
 *
 * Die Stücke entstehen erst im Shader (`EigenkleidGLSL`: Sitz, Brücke, Ärmelform entlang der Ruhenormale; `EigenkleidschnittGLSL`: Saum, Ärmel, Ausschnitt je Pixel).
 * Hier dieselbe Rechnung je PUNKT (Formeln aus beiden Shadern abgeschrieben, Uniforms über `Eigenkleidwerte.shaderwerte`, Attribute der Schale) → ein ungehäutetes
 * Netz je Stück im Raum der Figurgruppe. Geschnitten wird an der Kante f = 0 durch die Dreiecke (`_netz`; der Shader schneidet je Pixel).
 * Nebenbei je Körperpunkt, was die Modellprüfung braucht (`userData`): Kante `stoffseite` (m, > 0 = Stoff), Abstand der Schale `versatz`, Körperkoordinaten
 * `koord`, Saum, Längen, Schultergelenke, umgeklappte Dreiecke `gefaltet` (der Shader verwirft sie: `!gl_FrontFacing && vKkHub > 0.002`).
 * Gilt für die Haltung im Netz (Bindlage = Haltung, gebackene Pose); Morphe nimmt `getVertexPosition` mit. Der Kragen (`Eigenkragen`) wird nicht gebacken.
 * Validiert am 02.11.2026: Umriss gegen die Shader-Schale IoU 0,991–0,994 (vor dem Ärmel- und Brückenumbau).
 */
export class Eigenkleidbacken {

    static KETTEN = { oberteil: 1, hose: 2, socke: 3, kleid: 1 };

    static ss(a, b, x) { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

    static mix(a, b, t) { return a + (b - a) * t; }

    static kkForm(u, form) {
        const v = Math.min(1, Math.max(0, u));
        const s = form < 0.5 ? Math.sqrt(1 - v * v) : (form < 1.5 ? 1 - v : (form < 2.5 ? Math.sqrt(1 - v ** 4) : 1 - v ** 6));
        return u >= 1 ? 0 : s;
    }

    /** Die sichtbaren Schalen der Figur. */
    static schalen(inst) {
        const aus = [];
        inst.group.traverse((o) => { if (o.isMesh && Eigenkleidbacken.KETTEN[o.userData?.eigenkleid] && o.visible) aus.push(o); });
        return aus;
    }

    /** Schultergelenk, Oberarmrichtung und Armlänge je Seite in der Bindlage — wie `Eigenkleid.schultern`. */
    static schultern(koerper) {
        const knochen = koerper.skeleton?.bones || [], inv = koerper.skeleton?.boneInverses || [];
        const gelenk = (name) => {
            const i = knochen.findIndex((b) => b.name === name);
            return i < 0 ? null : new THREE.Vector3().setFromMatrixPosition(new THREE.Matrix4().copy(inv[i]).invert().premultiply(koerper.bindMatrixInverse));
        };
        const aus = {};
        for (const s of ['l', 'r']) {
            const a = gelenk(`${s}_upperarm`), e = gelenk(`${s}_forearm`), h = gelenk(`${s}_hand`);
            aus[s] = a && e && h ? { a, achse: e.clone().sub(a).normalize(), laenge: a.distanceTo(h) } : null;
        }
        return aus;
    }

    /** → `[THREE.Mesh]` je Schale, `userData.eigenGebacken` = Art (siehe Kopf). */
    static async backen(inst) {
        const koerper = inst.bodyMesh;
        const karte = await Koerperkoordinatenkarte.holen();
        const { laengen } = Eigenkleidgeometrie.bauen(koerper.geometry, [koerper.material].flat(), karte);
        const schalen = Eigenkleidbacken.schalen(inst);
        let lage = [0, 0];
        if (schalen.some((s) => s.userData.eigenkleid === 'oberteil') && Eigenkleidwerte.an(inst, 'hose')) {
            const wh = Eigenkleidwerte.shaderwerte('hose', Eigenkleidwerte.alle(inst, 'hose'));
            lage = [Math.max(...wh.sitz) + wh.bruecke[0] + 0.002, wh.saum[0]];         // wie `Eigenkleider.lage`
        }
        const schulter = Eigenkleidbacken.schultern(koerper);
        const bund = {};                                                             // Bundring je Rock (`Eigenrock`, userData.bund): Kleid-Rockteil, eigener Rock
        inst.group.traverse((o) => { const m = /^eigenrock_(kleid|rock)_/.exec(o.name || ''); if (m && o.visible && Number.isFinite(o.userData?.bund)) bund[m[1]] = o.userData.bund; });
        return schalen.map((schale) => {
            const art = schale.userData.eigenkleid;
            const w = Eigenkleidwerte.shaderwerte(art, Eigenkleidwerte.alle(inst, art));
            const ueber = art === 'oberteil' && bund.rock !== undefined && Eigenrock.reichtBisBund(Eigenkleidwerte.alle(inst, 'oberteil'), Eigenkleidwerte.alle(inst, 'rock'));
            const rockBund = (art === 'kleid' ? bund.kleid : ueber ? bund.rock : undefined) ?? EigenkleidschnittGLSL.OHNE_BUND;
            const p = Eigenkleidbacken._punkte(koerper, schale, art, w, laengen, art === 'oberteil' ? lage : [0, 0], schulter, rockBund);
            const netz = Eigenkleidbacken._netz(schale, p, w, art);
            Object.assign(netz.userData, { stoffseite: p.stoff, versatz: p.versatz, koord: p.kk, saum: w.saum.slice(0, 2), laengen, schulter });
            return netz;
        });
    }

    /**
     * Die verschobene Schale eines Stücks in der Bindlage, ohne Häutung und ohne Schnitt unter einem Rock → `{pos: Float32Array 3n, stoff: Float32Array n}` oder null —
     * die Unterlage eines Rocks darüber (`Eigenrock.unterlageSetzen`); Punktreihenfolge der Schale (`Eigenkleidgeometrie`).
     */
    static async unterlage(inst, art) {
        const koerper = inst?.bodyMesh, schale = inst ? Eigenkleidbacken.schalen(inst).find((s) => s.userData.eigenkleid === art) : null;
        if (!koerper || !schale) return null;
        const karte = await Koerperkoordinatenkarte.holen();
        const { laengen } = Eigenkleidgeometrie.bauen(koerper.geometry, [koerper.material].flat(), karte);
        const w = Eigenkleidwerte.shaderwerte(art, Eigenkleidwerte.alle(inst, art));
        const p = Eigenkleidbacken._punkte(koerper, schale, art, w, laengen, [0, 0], Eigenkleidbacken.schultern(koerper), EigenkleidschnittGLSL.OHNE_BUND, true);
        return { pos: p.lage, stoff: p.stoff };
    }

    /** Ärmel in der Haltung wie `EigenkleidschnittGLSL.kkArmAnteil`. */
    static armAnteil(schulter, t, x, y, z) {
        const s = schulter[x >= 0 ? 'l' : 'r'], ss = Eigenkleidbacken.ss;
        if (!s) return t;
        const tp = ((x - s.a.x) * s.achse.x + (y - s.a.y) * s.achse.y + (z - s.a.z) * s.achse.z) / s.laenge;
        return Eigenkleidbacken.mix(t, Math.min(t, tp), (1 - ss(0.15, 0.3, t)) * ss(0, 0.03, s.a.y - y));
    }

    /** Je Körperpunkt: Kante, Hub, Abstand, Körperlage und verschobene Lage (Gruppenraum). */
    static _punkte(koerper, schale, art, w, L, lageArt, schulter, rockBund = EigenkleidschnittGLSL.OHNE_BUND, bindlage = false) {
        const { ss, mix, kkForm } = Eigenkleidbacken;
        const nummer = Eigenkleidwerte.ARTEN[art].nummer, KLEIDNAHT = EigenkleidschnittGLSL.KLEIDNAHT ?? 0, ROCKUNTER = EigenkleidschnittGLSL.ROCKUNTER_M;
        const [saumX, saumY] = w.saum, [sx, sy, sz, sw] = w.sitz, [hf, htv, hth, hbr] = w.hals, kragenX = w.kragen[0], [aw, af, at, naht] = w.aermelform;
        const [bAbst, bAusbr, bGlatt] = w.bruecke;
        const g = schale.geometry, A = g.attributes, pos = A.position.array;
        const kk = A.kkKoord.array, kn = A.kkNormal.array, an = A.kkAnsatz.array, nrm = A.normal.array;
        const b1 = A.kkBruecke.array, b2 = A.kkBrueckeB.array, b3 = A.kkBrueckeC?.array;
        const [ox, oy, oz] = g.userData.oben || [0, 1, 0];          // Rumpfachse der Brücke (`Eigenkleidbruecke.rumpfrahmen`)
        const n = A.position.count, p = new THREE.Vector3();
        const lage = new Float32Array(3 * n), koerperLage = new Float32Array(3 * n), stoff = new Float32Array(n), hubJe = new Float32Array(n), versatz = new Float32Array(n);
        for (let i = 0; i < n; i++) {
            const kette = Math.floor(kk[4 * i] + 0.5);
            let t = kk[4 * i + 1];
            const h = kk[4 * i + 2], vorn = Math.cos(2 * Math.PI * kk[4 * i + 3]);
            const k = [Math.abs(kette - 1) < 0.5 ? 1 : 0, kette > 1.5 && kette < 3.5 ? 1 : 0, kette > 3.5 && kette < 5.5 ? 1 : 0, kette > 5.5 && kette < 7.5 ? 1 : 0];
            if (nummer < 1.5 && kette > 7.5 && kette < 9.5) { k[1] = 1; t = 1.05; }                       // Hände beim Oberteil, Füße bei der Hose (wie der Shader)
            if (nummer > 1.5 && nummer < 2.5 && kette > 9.5 && kette < 11.5) { k[2] = 1; t = 1.05; }
            let nx = nrm[3 * i], ny = nrm[3 * i + 1], nz = nrm[3 * i + 2];             // Ruhenormale, an UV-Nähten verschweißt
            if (kn[3 * i] ** 2 + kn[3 * i + 1] ** 2 + kn[3 * i + 2] ** 2 > 0.25) { nx = kn[3 * i]; ny = kn[3 * i + 1]; nz = kn[3 * i + 2]; }
            const nl = Math.hypot(nx, ny, nz) || 1;
            let hub = 0;                                                                 // kkHub
            if (bAusbr > 0.0005) {
                const a = Math.max(bAusbr, 0.001), seitlich = 1 - ss(0.35, 0.65, (nx * ox + ny * oy + nz * oz) / nl);
                const wH = 1 - ss(0.3 * a, a, b2[4 * i + 2]), wF = 1 - ss(0.3 * a, a, b2[4 * i + 3]), oben = nummer < 1.5 ? 1 : 0;
                const zeltF = Math.max(b1[4 * i + 3] - b1[4 * i + 2], 0) * wF * oben, rundF = Math.max(b2[4 * i + 1] - b2[4 * i], 0) * wF * oben;
                const kkNaht = naht > 0.5 && kette === 1 ? 1 - ss(saumX - 0.08, saumX - 0.01, h) : 1;
                hub = kkNaht * (mix(b1[4 * i + 2], b2[4 * i], bGlatt) * wH * seitlich + mix(zeltF, rundF, bGlatt));
            }
            let sitz;                                                                    // Sitz
            if (nummer < 1.5) {
                sitz = k[1] > 0.5 ? mix(sx, sw, ss(0, 0.15, t)) : (h < 0.5 ? mix(sx, sy, ss(0.1, 0.5, h)) : mix(sy, sz, ss(0.5, 0.95, h)));
                const kA = k[1] > 0.5 ? Math.min(1, Math.max(0, t / Math.max(saumY, 0.05))) : 0;
                sitz += aw * kA * kA + at * kA * (0.5 + 0.5 * Math.sin(2 * Math.PI * af * kk[4 * i + 3]));
            } else if (nummer < 2.5) {
                const rh = mix(sx, sy, ss(saumX, saumX + 0.15, h));
                sitz = k[2] > 0.5 ? mix(rh, sz, ss(0.15, 0.35, t)) : rh;
            } else {
                k[3] = kette > 9.5 && kette < 11.5 ? 1 : 0;
                t = k[3] > 0.5 ? 1.05 : t;
                sitz = mix(sy, sx, ss(0.9, 1, t));
            }
            if (lageArt[0] > 0 && h >= lageArt[1] && k[1] < 0.5) sitz = Math.max(sitz, lageArt[0]);
            const rx = b1[4 * i], rz = b1[4 * i + 1], ry = b3 ? b3[4 * i + 2] : 0, ux = nx / nl, uy = ny / nl, uz = nz / nl;
            const auf = Math.max(Math.max(sitz - hub * Math.max(ux * rx + uy * ry + uz * rz, 0), bAbst * ss(0, 0.003, hub)), 0.001);
            const x = pos[3 * i];                                                        // Kante (> 0 = Stoff)
            let f = 1;
            if (nummer < 1.5) {
                if (k[1] < 0.5) {
                    let fs = (saumX + (naht > 0.5 ? KLEIDNAHT : 0) - h) * L[0];
                    if (rockBund > -100) fs = pos[3 * i + 1] - (rockBund - ROCKUNTER);
                    f = Math.min(f, fs);
                }
                if (k[2] < 0.5) f = Math.min(f, (saumY - Eigenkleidbacken.armAnteil(schulter, t, x, pos[3 * i + 1], pos[3 * i + 2])) * L[1]);
                const u = Math.abs(x) / Math.max(0.5 * hbr, 0.001);
                const tiefe = mix(hth * kkForm(u, 0), htv * kkForm(u, hf), ss(-0.35, 0.35, vorn)), ab = h - an[i];
                f = Math.min(f, hf > 3.5 ? ab * L[0] + kragenX : (ab - tiefe) * L[0]);
                if (k[0] + k[1] + k[2] + k[3] < 0.5) f = -1;
            } else if (nummer < 2.5) {
                f = Math.min(f, (h - saumX) * L[0]);
                if (k[2] > 0.5) f = Math.min(f, (saumY - t) * L[2]);
                if (k[0] + k[2] < 0.5) f = -1;
            } else {
                if (k[2] > 0.5) f = Math.min(f, (t - saumX) * L[2]);
                if (k[2] + k[3] < 0.5) f = -1;
            }
            stoff[i] = f; hubJe[i] = hub; versatz[i] = hub + auf;
            if (bindlage) p.set(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]);            // Bindlage (Raum des Rocks), sonst Körperpunkt mit Morphen und Häutung
            else koerper.getVertexPosition(i, p);                                        // dann wie der Shader verschoben
            koerperLage.set([p.x, p.y, p.z], 3 * i);
            p.x += rx * hub + ux * auf; p.y += ry * hub + uy * auf; p.z += rz * hub + uz * auf;
            if (!bindlage) p.applyMatrix4(koerper.matrixWorld);                         // Weltlage fürs gebackene Netz; die Unterlage bleibt im Raum des Körpers
            lage.set([p.x, p.y, p.z], 3 * i);
        }
        return { kk, stoff, hubJe, versatz, lage, koerperLage };
    }

    /**
     * Dreiecke der sichtbaren Hautgruppen, an der Kante (Stoffseite f = 0, linear über die Kante wie der Shader je Pixel) geschnitten → Netz; umgeklappte zählen
     * (`userData.gefaltet`, wie bisher an Dreiecken mit mindestens zwei Stoffecken). Bis 02.11.2026 abends ganze Dreiecke mit ≥ 2 Stoffecken — Säume als Zacken im
     * GLB und in den Masken (Damira, Rückenansicht der Maske), während das Foto (Shader) glatt schnitt.
     */
    static _netz(schale, p, w, art) {
        const g = schale.geometry, index = g.index.array, sicht = [schale.material].flat().map((m) => m?.visible !== false);
        const gruppen = g.groups.length ? g.groups : [{ start: 0, count: index.length, materialIndex: 0 }];
        const { stoff, hubJe, lage, koerperLage, kk } = p;
        const normale = (L, a, b, c) => {
            const ux = L[3 * b] - L[3 * a], uy = L[3 * b + 1] - L[3 * a + 1], uz = L[3 * b + 2] - L[3 * a + 2];
            const vx = L[3 * c] - L[3 * a], vy = L[3 * c + 1] - L[3 * a + 1], vz = L[3 * c + 2] - L[3 * a + 2];
            return [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx];
        };
        const behalten = [], gefaltet = { dreiecke: 0, flaeche_cm2: 0, ketten: {} };
        const kanten = new Map(), schnittpunkte = [];                  // Schnittpunkt je Kante: negativer Index → [a, b, s] mit f(a + s·(b − a)) = 0
        const schnitt = (a, b) => {
            const k = a < b ? `${a},${b}` : `${b},${a}`;
            let v = kanten.get(k);
            if (v === undefined) { v = -1 - schnittpunkte.length; schnittpunkte.push([a, b, stoff[a] / (stoff[a] - stoff[b])]); kanten.set(k, v); }
            return v;
        };
        for (const gr of gruppen) {
            if (!sicht[gr.materialIndex]) continue;
            for (let j = gr.start; j < gr.start + gr.count; j += 3) {
                const a = index[j], b = index[j + 1], c = index[j + 2];
                const ein = [stoff[a] >= 0, stoff[b] >= 0, stoff[c] >= 0], zahl = ein[0] + ein[1] + ein[2];
                if (!zahl) continue;
                if (zahl === 3) behalten.push(a, b, c);
                else {                                                     // drehen: bei einer Stoffecke steht sie vorn, bei zweien die freie hinten (Umlauf bleibt)
                    let [q0, q1, q2] = [a, b, c], [e0, , e2] = ein;
                    for (let r = 0; r < 2 && !((zahl === 1 && e0) || (zahl === 2 && !e2)); r++) {
                        [q0, q1, q2] = [q1, q2, q0];
                        [e0, e2] = [stoff[q0] >= 0, stoff[q2] >= 0];
                    }
                    if (zahl === 1) behalten.push(q0, schnitt(q0, q1), schnitt(q2, q0));
                    else { const s12 = schnitt(q1, q2), s20 = schnitt(q2, q0); behalten.push(q0, q1, s12, q0, s12, s20); }
                }
                if (zahl < 2 || Math.max(hubJe[a], hubJe[b], hubJe[c]) <= 0.002) continue;
                const n0 = normale(koerperLage, a, b, c), n1 = normale(lage, a, b, c);
                if (n0[0] * n1[0] + n0[1] * n1[1] + n0[2] * n1[2] >= 0) continue;
                gefaltet.dreiecke++;
                gefaltet.flaeche_cm2 += 0.5e4 * Math.hypot(...n0);
                const k = `${Math.floor(kk[4 * a] + 0.5)}@${Math.round(10 * kk[4 * a + 2]) / 10}`;
                gefaltet.ketten[k] = (gefaltet.ketten[k] || 0) + 1;
            }
        }
        gefaltet.flaeche_cm2 = Math.round(gefaltet.flaeche_cm2);
        const neu = new Map(), pos = [], uv = [], idx = [], uvA = g.attributes.uv?.array;
        for (const v of behalten) {
            let m = neu.get(v);
            if (m === undefined) {
                m = neu.size; neu.set(v, m);
                if (v >= 0) {
                    pos.push(lage[3 * v], lage[3 * v + 1], lage[3 * v + 2]);
                    if (uvA) uv.push(uvA[2 * v], uvA[2 * v + 1]);
                } else {
                    const [a, b, s] = schnittpunkte[-1 - v];
                    for (let d = 0; d < 3; d++) pos.push(lage[3 * a + d] + s * (lage[3 * b + d] - lage[3 * a + d]));
                    if (uvA) for (let d = 0; d < 2; d++) uv.push(uvA[2 * a + d] + s * (uvA[2 * b + d] - uvA[2 * a + d]));
                }
            }
            idx.push(m);
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
        if (uvA) geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
        geo.setIndex(idx);
        geo.computeVertexNormals();
        const material = new THREE.MeshStandardMaterial({ color: w.farbe, roughness: w.rauheit, metalness: 0, side: THREE.DoubleSide });
        material.name = `eigen_${art}`;
        const netz = new THREE.Mesh(geo, material);
        netz.name = `eigen_${art}`;
        netz.userData.eigenGebacken = art;
        netz.userData.eigenKategorie = Eigenkleidwerte.ARTEN[art].kategorie;
        netz.userData.gefaltet = gefaltet;
        return netz;
    }

    /** Netze freigeben (nicht in der Szene gebraucht, nur für die Prüfung gerechnet). */
    static weg(netze) {
        for (const n of netze || []) { n.removeFromParent(); n.geometry.dispose(); n.material.dispose(); }
    }
}
