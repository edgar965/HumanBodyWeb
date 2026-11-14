import * as THREE from 'three';
import { base64ToFloat32, base64ToUint32 } from './kodierung.js';
import { Bauart } from './bauart.js';
import { Dqhaut } from './dqhaut.js';
import { Eigenhaut } from './eigenhaut.js';
import { Genesis9felder } from './genesis9felder.js';
import { Stoffglaettung } from './stoffglaettung.js';
import { Stoffhaut } from './stoffkapseln.js';

/**
 * Genesis9glaettung — die Glättung je Bild (`Stoffglaettung`) an den anliegenden Stücken einer Genesis-Figur (12.11.2026).
 *
 * Edgar, 12.11.2026: „mach“ zu „Daz glättet den Stoff an solchen Stellen in jedem Bild nach“ (Olesia1, Spagat, Riss der Jeans im Schritt).
 *
 * WER: jedes gehäutete Stück mit Käfig (`userData.glaettung`, Server `G9koerpernetz` für Kleidung mit Körperhaut), Bauart „anliegend“,
 * nicht starr gebunden, nicht im Stoffschwung. Der Bauplan (Kanten, Unterteilungsmatrix, Käfighaut) kommt einmal je Stück vom selben
 * Endpunkt wie der des Stoffschwungs (`…/stoff/<n>/?glaetten=1`).
 *
 * WIE ES GEZEICHNET WIRD: Das Stück bleibt eine `SkinnedMesh`. Der Versatz geglättet − gehäutet liegt je Browserpunkt im Attribut
 * `glaettung`; der Shader addiert ihn am Ende von `skinning_vertex` (nach der Dual-Quaternion-Mischung), also VOR der Hautbindung, die den
 * Stoff aus dem Körper schiebt. CPU-Häutungen, die messen, was gezeichnet ist (`Stoffhaut.welt`, `Netzpose`), lesen denselben Puffer
 * (`userData.glaettVersatz`). Gerechnet wird nur, wenn sich eine Knochenmatrix des Stücks geändert hat.
 *
 * Aufgerufen je Bild aus der Szenenschleife (nach den Gelenkkorrekturen) und aus der `Kleidungsprobe`. Abschalten zur Gegenprobe:
 * `__glaettung.an = false` (der Versatz geht im nächsten Takt auf null).
 */
export class Genesis9glaettung {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    /**
     * AUS bis zur Kollision gegen die gehäutete Haut (12.11.2026, Olesia1, Spagat, im Chrome gemessen und angesehen): Shirt aufreißende
     * Kanten 22 → 0, Jeans 231 → 99 (in 4 statt 18 von 25 Bildern) — aber in Bild 50 steht im Schritt ein Hautfleck vor der Jeans, den es
     * ohne Glättung nicht gibt. Ohne Körper gezeichnet ist die Jeans dort geschlossen: Der geglättete Stoff gleitet auf der gekrümmten
     * Innenseite des Oberschenkels seitlich, die Hautbindung misst die Tiefe aber gegen das Körperdreieck aus der Ruhe. Mit 2 cm Grenze für
     * den Versatz blieb der Fleck. Gegenprobe in der Konsole: `__glaettung.an = true`.
     */
    static an = false;
    static _stuecke = new WeakMap();      // netz -> Eintrag
    static _aktiv = new Set();            // Einträge mit Versatz (für `an = false`)

    static PARS = `
#ifdef STOFF_GLAETTUNG
attribute vec3 glaettung;
#endif
`;
    static LAGE = `
#if defined( USE_SKINNING ) && defined( STOFF_GLAETTUNG )
	transformed += glaettung;
#endif
`;

    /** Die Chunks einmal erweitern — NACH `Dqhaut` (der Versatz gehört hinter die Mischung, vor das schließende `#endif`). */
    static chunksErweitern() {
        Dqhaut.chunksErweitern();
        const C = THREE.ShaderChunk;
        if (!C.skinning_pars_vertex.includes('attribute vec3 glaettung')) C.skinning_pars_vertex += Genesis9glaettung.PARS;
        if (!C.skinning_vertex.includes('transformed += glaettung')) {
            const ende = C.skinning_vertex.lastIndexOf('#endif');
            C.skinning_vertex = C.skinning_vertex.slice(0, ende) + Genesis9glaettung.LAGE + C.skinning_vertex.slice(ende);
        }
    }

    /** Kleinteile (Nieten, Knöpfe: 145–193 Punkte an der Angie Jeans) reißen nicht — kein Bauplan für sie. */
    static MINDESTPUNKTE = 500;

    /** Gilt die Glättung für dieses Netz? Nur Kleidung: Haar trägt an Olesia1 auch die Bauart „anliegend“. */
    static gilt(netz) {
        const u = netz?.userData;
        return !!(netz?.isSkinnedMesh && u?.glaettung?.kaefig && u.art === 'kleidung' && !u.starrbindung && !u.stoff
                  && Bauart.von(netz) === 'anliegend' && netz.geometry?.attributes?.position?.count >= Genesis9glaettung.MINDESTPUNKTE);
    }

    /** Je Bild: alle Figuren. */
    static takt(figuren) {
        if (!Genesis9glaettung.an) { Genesis9glaettung._ausschalten(); return; }
        for (const inst of figuren) {
            if (!inst?.clothMeshes || !inst.skelett) continue;
            let frisch = false;
            for (const netz of Object.values(inst.clothMeshes)) {
                if (!Genesis9glaettung.gilt(netz)) continue;
                let e = Genesis9glaettung._stuecke.get(netz);
                if (!e) { e = Genesis9glaettung._anlegen(inst, netz); Genesis9glaettung._stuecke.set(netz, e); }
                if (!e.bereit) continue;
                if (!frisch) { inst.group?.updateMatrixWorld(true); frisch = true; }
                Genesis9glaettung._bild(e);
            }
        }
    }

    static _anlegen(inst, netz) {
        const e = { netz, inst, bereit: false, fehler: null, M: null, ms: 0, stand: null };
        Genesis9glaettung._laden(e).catch(f => { e.fehler = String(f?.message || f); console.warn('[Glättung]', netz.name, e.fehler); });
        return e;
    }

    static async _laden(e) {
        const { netz, inst } = e;
        const treffer = /^(?:genesis9_kleid|daz)_(.+)_(\d+)$/.exec(netz.name);
        if (!treffer) throw new Error('kein Garderobenstück');
        const kennung = treffer[1], nummer = Number(treffer[2]);
        const passform = Genesis9felder.passform(inst.kleidung?.[kennung]?.regler);
        const adresse = `${Genesis9glaettung.ADRESSE}${encodeURIComponent(kennung)}/stoff/${nummer}/?stufen=${netz.userData.glaettung.stufen}`
            + `&glaetten=1${Genesis9felder.passformAnfrage(passform)}`;
        const antwort = await fetch(adresse);
        if (!antwort.ok) throw new Error(`Bauplan ${antwort.status}`);
        const plan = await antwort.json();
        const geo = netz.geometry, n = geo.attributes.position.count;
        if (plan.zeilen !== n) throw new Error(`Bauplan ${plan.zeilen} Zeilen, Netz ${n} Punkte`);
        const kaefig = netz.userData.glaettung.kaefig;
        if (plan.punkte * 3 !== kaefig.length) throw new Error(`Käfig ${kaefig.length / 3} Punkte, Bauplan ${plan.punkte}`);
        const haut = plan.hautgewichte;
        const spalte = haut ? Eigenhaut.spaltenNummern(haut.knochen, netz.skeleton) : null;
        if (!spalte) throw new Error('Käfighaut fehlt oder nennt Knochen, die das Skelett nicht hat');
        const { index: roh, gewicht } = Eigenhaut.gewichte(haut);
        const index = new Uint16Array(roh.length);
        for (let i = 0; i < roh.length; i++) index[i] = spalte[roh[i]] ?? 0;
        e.index = index; e.gewicht = gewicht;
        e.glaettung = new Stoffglaettung(kaefig, base64ToUint32(plan.kanten), {
            indptr: base64ToUint32(plan.indptr), indices: base64ToUint32(plan.indices), data: base64ToFloat32(plan.data), zeilen: plan.zeilen,
        }, geo.attributes.normal?.array || null);
        Genesis9glaettung.chunksErweitern();
        const attribut = new THREE.BufferAttribute(e.glaettung.versatz, 3);
        attribut.setUsage(THREE.DynamicDrawUsage);
        geo.setAttribute('glaettung', attribut);
        netz.userData.glaettVersatz = e.glaettung.versatz;
        for (const mat of Array.isArray(netz.material) ? netz.material : [netz.material]) {
            if (!mat || mat.defines?.STOFF_GLAETTUNG !== undefined) continue;
            mat.defines = { ...(mat.defines || {}), STOFF_GLAETTUNG: '' };
            mat.needsUpdate = true;
        }
        e.bereit = true;
    }

    static _bild(e) {
        const { netz, index, gewicht } = e;
        const M = Stoffhaut.matrizen(netz);
        if (e.M && Genesis9glaettung._gleich(e.M, M)) return;
        e.M = M;
        const a = netz.userData.dqMisch || 0, Q = a > 0 ? Dqhaut.tafel(M, netz.skeleton.bones.length) : null, dq = [0, 0, 0];
        const haeuten = (i, x, y, z, aus) => {
            let sx = 0, sy = 0, sz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
            }
            if (Q) {
                Dqhaut.punkt(Q, index, gewicht, i, x, y, z, dq);
                sx += a * (dq[0] - sx); sy += a * (dq[1] - sy); sz += a * (dq[2] - sz);
            }
            aus[0] = sx; aus[1] = sy; aus[2] = sz;
        };
        const t0 = performance.now();
        const r = e.glaettung.bild(haeuten);
        e.ms = performance.now() - t0;
        e.stand = { zone: r.zone, risse: r.risse, groesste: +r.groesste.toFixed(2) };
        if (r.geaendert) { netz.geometry.attributes.glaettung.needsUpdate = true; Genesis9glaettung._aktiv.add(e); }
    }

    static _gleich(a, b) {
        for (let i = 0; i < a.length; i++) if (Math.abs(a[i] - b[i]) > 1e-7) return false;
        return true;
    }

    /** `an = false`: jeden Versatz auf null, einmal. */
    static _ausschalten() {
        for (const e of Genesis9glaettung._aktiv) {
            e.glaettung.versatz.fill(0);
            e.glaettung._beruehrt.length = 0;
            e.glaettung._markiert?.fill(0);
            e.netz.geometry.attributes.glaettung.needsUpdate = true;
            e.M = null;
        }
        Genesis9glaettung._aktiv.clear();
    }

    /** Für die Konsole: je Stück einer Figur Stand und Zeit des letzten Bildes. */
    static stand(inst) {
        const aus = {};
        for (const netz of Object.values(inst?.clothMeshes || {})) {
            const e = Genesis9glaettung._stuecke.get(netz);
            if (e) aus[netz.name] = { bereit: e.bereit, fehler: e.fehler, ms: +e.ms.toFixed(2), ...(e.stand || {}) };
        }
        return aus;
    }
}

if (typeof window !== 'undefined') window.__glaettung = Genesis9glaettung;
