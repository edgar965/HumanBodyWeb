import * as THREE from 'three';
import { state } from './state.js';
import { Stoffhaut } from '../gemeinsam/stoffkapseln.js';
import { Genesis9stoffschwung } from './genesis9/genesis9stoffschwung.js';
import { Kleidungsmass } from '../gemeinsam/kleidungsmass.js';
import { Posenabsatz } from './posenabsatz.js';
import { Genesis9glaettung } from '../gemeinsam/genesis9glaettung.js';

/**
 * Kleidungsprobe — eine Animation im laufenden Chrome Bild für Bild messen:
 * Kantendehnung der Stücke (Streifen, zerrissene Falten), Abstand zum Körper
 * (die Hose bleibt am Bein), Körper hinter dem Stoff (Haut sticht durch) und
 * Armpunkte hinter dem Oberteil (Arme ragen ins Kleid).
 *
 * WARUM (Edgar, 19.09.2026 nachts: „teste mit der ganzen Animation … die Arme
 * sollen nicht in die Kleider hineinragen, die Hose soll am Körper bleiben"
 * und „teste nur in chrome"): gemessen werden die gehäuteten Punkte, die der
 * Shader zeichnet (`Stoffhaut.welt`), bei dynamischen Stücken das Netz des
 * Stoffschwungs — dieselbe Szene, die Edgar sieht, ohne Nachrechnung in Python.
 *
 * Aufruf in der Konsole, Animation geladen:
 *     await __kleidungsprobe.laufen({ inst: __characters.get('…'), schritte: 25, sprung: 5 })
 * Ergebnis je Stück mit `urteil` gegen `ERWARTUNG`; `bilder` = gemessene Bilder.
 *
 * SCHUHE (12.11.2026, Edgar mit Bild vom Fallout Ranger: „schuhe falsch gerigged / sitzen
 * nicht“, „erkennst du das in deinem Tanztest?“ — nein: der Modell-Check prüft „Fuß im Schuh“
 * nur in der Ruhelage, diese Probe ließ Schuhe aus): je Schuh und Fuß der Knick am Knöchel
 * gegen die Haltung, in der der Schuh gebaut ist — die Drehung Elternknochen → Fußknochen,
 * verglichen mit der Bindpose. Geht die Fußhaltung des Schuhs in der Animation verloren,
 * steht der Knöchel in jedem Bild daneben (Median), der Stiefel kippt gegen das Bein.
 * Die erste Fassung (in Ruhe umschlossene Haut ohne Schuhpunkt in 6 cm) war blind: Haut und
 * Schuh hängen an denselben Knochen und kippen gemeinsam, die Gegenprobe blieb grün.
 * Ergebnis unter `schuhe`, Urteil `am_fuss`. `nur` (RegExp auf den Stücknamen) misst nur
 * einen Teil der Stücke: ein Modell mit zehn großen Stücken braucht sonst Minuten.
 */
export class Kleidungsprobe {

    /** Rasterweite (m): Abstände darüber gelten als „fern"; in Ruhe weiter, damit „eng" entscheidbar ist. */
    static WEITE = 0.04;
    static WEITE_RUHE = 0.12;
    /** Höchstens so viele Punkte je Stück werden gegen den Körper gemessen (Schrittweite darüber). */
    static HOECHSTENS = 20000;
    /** Haar, Schuhe und Kleinteile (Nieten) sind keine Kleidung für diese Probe. */
    static AUSSEN = /hair|frisur|sneaker|schuh|shoe|sandal|boot/i;
    static MINDESTPUNKTE = 500;
    // `(?!\w*toe)` (23.09.2026): Genesis9 nennt die Zehen wie die Finger
    // (`l_indextoe1`, `l_midtoe1`, `l_ringtoe1`, `l_pinkytoe1`) — ohne die
    // Ausnahme zählte diese Probe Zehenpunkte als Armpunkte. Dieselbe Falle
    // wie in `Koerperzuordnung.gruppenindex`, dort mit Bild belegt.
    static ARM = /hand|palm|thumb|f_index|f_middle|f_ring|f_pinky|forearm|upper_arm|upperarm|carpal|^[lr]_(?!\w*toe)(index|mid|ring|pinky)/i;
    static OBERTEIL = /^(DEF-spine\.00[1-5]|DEF-breast|DEF-shoulder|spine[1-4]|[lr]_pectoral|[lr]_shoulder|neck)/;
    /**
     * Schwellen, gemessen an Dance1_smplx auf Ursula (Tagebuch 19.09.2026, Abschnitt 12):
     * Jeans und T-Shirt gehäutet: Dehnung p99 2,31 / 1,87 — mit 3 % der Jeanspunkte an
     * `l_hand` (der Fehler vom Abend) 649. Abstand p95 in Ruhe 2,4 cm, im Tanz 2,4;
     * Haut im Stoff p1 −3,6 / −4,2 mm; Armpunkte hinter dem Oberteil 0 / 124 von 44.202.
     */
    static ERWARTUNG = { dehnung_p99: 3.0, am_koerper_cm: 3.0, eng_cm: 5.0, tiefe_p1_mm: -15, arme_anteil: 0.01, risse: 0 };
    /**
     * Riss (12.11.2026, Edgar zum hellen Streifen im Schritt der Jeans im Spagat: „die Hose, die gleich zerreisst“): eine Kante, die um mehr
     * als `RISS_M` UND auf mehr als das `RISS_FAKTOR`-fache länger wird. Die Perzentile sehen ihn nicht (Olesia1, Jeans, Spagat: p99 2,14,
     * die Kanten der Schrittnaht 11- bis 13-fach). Zeile `kein_riss`: in keinem Bild eine solche Kante.
     */
    static RISS_M = 0.010;
    static RISS_FAKTOR = 3;
    /** Größte Kantendehnung eines starren Teils (Verhältnis zur Ruhe): eine reine Drehung um einen Knochen gibt 1 (bis auf Rundung). */
    static STARR_DEHNUNG = 1.01;
    /** Schuhe: wie der Modell-Check (`Modellpruefung.SCHUH`). */
    static SCHUH = /schuh|stiefel|shoe|boot|sneaker|sandal|heel|pump/i;
    /** Fußknochen (Genesis `l_foot`, Rigify `DEF-foot_L`), nicht Zehen und Mittelfuß. Nur an Genesis 9 geprüft. */
    static FUSS = /(^|[_\-.]|left|right)foot([_\-.][lr])?$/i;
    /**
     * Höchstens so weit (Grad, Median über die gemessenen Bilder) darf der Knöchel von der Bauhaltung des Schuhs stehen. Setzung zwischen
     * den Messwerten vom 12.11.2026 (Fallout Ranger, DanceKurz, 251 Bilder im Abstand 4, im Chrome): mit Fußhaltung Median 13,4° / 16,2°
     * (links / rechts, höchstens 39,7° / 44,7°), ohne (`inst.absatzDeltas = null`) Median 62,6° / 58,5°. Eine verlorene Fußhaltung
     * unter etwa 30° sieht die Zeile nicht.
     */
    static KNOECHEL_MEDIAN_MAX = 30;

    static async laufen({ inst = null, schritte = 25, sprung = 5, dt = 1 / 30, nur = null } = {}) {
        inst = inst || [...state.characters.values()].find(c => Object.keys(c.clothMeshes || {}).length);
        if (!inst?.bodyMesh?.isSkinnedMesh || !state.mixer) return { fehler: 'keine gehäutete Figur oder keine Animation' };
        const t0 = performance.now();
        await Kleidungsprobe._aufwaermen(inst, dt, nur);
        const koerper = Kleidungsprobe._netz(inst.bodyMesh);
        koerper.arm = Kleidungsprobe._klasse(inst.bodyMesh, Kleidungsprobe.ARM);
        const schuhe = Kleidungsprobe._schuhe(inst, nur);
        const stuecke = Object.entries(inst.clothMeshes)
            .filter(([name, m]) => m?.isSkinnedMesh && m.geometry?.index && !Kleidungsprobe.AUSSEN.test(name)
                                   && (!nur || nur.test(name))
                                   && m.geometry.attributes.position.count >= Kleidungsprobe.MINDESTPUNKTE)
            .map(([name, m]) => ({ name, netz: m, ...Kleidungsprobe._netz(m), werte: [],
                                   oberteil: Kleidungsprobe._klasse(m, Kleidungsprobe.OBERTEIL),
                                   dynamisch: !!Kleidungsprobe._anzeige(inst, m) }));
        const dynamisch = stuecke.some(s => s.dynamisch) || schuhe.some(s => !!Kleidungsprobe._anzeige(inst, s.netz));
        // Von vorn, und nicht pausiert — `mixer.update` bewegt eine pausierte Aktion nicht (gemessen:
        // 125 Bilder mit denselben Zahlen wie 20). Danach steht die Szene wieder, wie sie war.
        const aktion = state.currentAction, war = { paused: aktion?.paused, playing: state.playing };
        if (aktion) { aktion.time = 0; aktion.paused = false; }
        for (let bild = 0; bild < schritte; bild++) {
            if (dynamisch) await Genesis9stoffschwung.probe(sprung, dt);
            else { state.mixer.update(sprung * dt); Posenabsatz.nachMixer(); }
            inst.group.updateMatrixWorld(true);
            Genesis9glaettung.takt([inst]);   // wie die Szenenschleife: Glättung je Bild (12.11.2026)
            if (stuecke.length) {             // nur Schuhe gefragt (`nur`): die Haut des Körpers wird nicht gebraucht
                const kw = Stoffhaut.welt(inst.bodyMesh);
                const raster = Kleidungsmass.raster(kw, koerper.n, Kleidungsprobe.WEITE);
                const kn = Kleidungsmass.normalen(kw, koerper.index, koerper.n);
                Kleidungsmass.auswaerts(kw, kn, koerper.n);   // HumanBody: Flächen nach innen gewickelt
                const arm = Kleidungsprobe._arm(kw, koerper);
                for (const s of stuecke) s.werte.push(Kleidungsprobe._messen(inst, s, raster, kn, arm));
            }
            for (const s of schuhe) Kleidungsprobe._knoechel(s);
            // Zwischen den Bildern die Schleife freigeben (MessageChannel: auch im versteckten Tab ungedrosselt).
            await new Promise(r => { const c = new MessageChannel(); c.port1.onmessage = () => r(); c.port2.postMessage(0); });
        }
        if (aktion) aktion.paused = war.paused;
        state.playing = war.playing;
        const aus = { bilder: schritte * sprung, ms: Math.round(performance.now() - t0), stuecke: {} };
        for (const s of stuecke) aus.stuecke[s.name] = Kleidungsprobe._zusammen(s, koerper);
        aus.schuhe = {};
        for (const s of schuhe) {
            const fuesse = {};
            for (const f of s.fuesse) {
                const z = [...f.grad].sort((a, b) => a - b);
                fuesse[f.name] = { median_grad: z.length ? +z[z.length >> 1].toFixed(1) : 0, max_grad: z.length ? +z[z.length - 1].toFixed(1) : 0 };
            }
            const werte = Object.values(fuesse);
            // Kein Fußknochen am Schuh gefunden: nicht messbar (`null`), weder grün noch rot.
            aus.schuhe[s.name] = { fuesse, dynamisch: !!Kleidungsprobe._anzeige(inst, s.netz),
                                   am_fuss: werte.length ? werte.every(w => w.median_grad <= Kleidungsprobe.KNOECHEL_MEDIAN_MAX) : null };
        }
        return aus;
    }

    /** Die Schuhe der Figur, je Schuh die Fußknochen, an denen er hängt, mit Elternknochen und der Drehung Elternknochen → Fuß in der Bindpose. */
    static _schuhe(inst, nur) {
        return Object.entries(inst.clothMeshes)
            .filter(([name, m]) => m?.isSkinnedMesh && Kleidungsprobe.SCHUH.test(name) && (!nur || nur.test(name)))
            .map(([name, m]) => {
                const sk = m.skeleton, a = m.geometry.attributes, si = a.skinIndex.array, sw = a.skinWeight.array;
                const traegt = new Set();
                for (let i = 0; i < si.length; i++) if (sw[i] > 0) traegt.add(si[i]);
                const fuesse = [];
                for (const k of traegt) {
                    const fuss = sk.bones[k], eltern = fuss?.parent, e = sk.bones.indexOf(eltern);
                    if (!fuss || e < 0 || !Kleidungsprobe.FUSS.test(fuss.name)) continue;
                    // Bindpose: Weltlage eines Knochens = Inverse seiner `boneInverse`, also Eltern → Fuß = boneInverse(Eltern) · boneInverse(Fuß)⁻¹.
                    const ruhe = new THREE.Matrix4().copy(sk.boneInverses[e]).multiply(new THREE.Matrix4().copy(sk.boneInverses[k]).invert());
                    fuesse.push({ name: fuss.name, fuss, eltern, ruheInvers: new THREE.Quaternion().setFromRotationMatrix(ruhe).invert(), grad: [] });
                }
                return { name, netz: m, fuesse };
            });
    }

    /** Je Fuß des Schuhs: wie weit (Grad) der Knöchel in diesem Bild von der Bindpose steht. */
    static _knoechel(s) {
        for (const f of s.fuesse) {
            const jetzt = new THREE.Matrix4().copy(f.eltern.matrixWorld).invert().multiply(f.fuss.matrixWorld);
            const q = new THREE.Quaternion().setFromRotationMatrix(jetzt).premultiply(f.ruheInvers);
            f.grad.push(2 * Math.acos(Math.min(1, Math.abs(q.w))) * 180 / Math.PI);
        }
    }

    /** Ruhe (Weltlage der Bindpose), Index, Kanten und Punktzahl eines Netzes. */
    static _netz(netz) {
        const a = netz.geometry.attributes.position, n = a.count, W = netz.matrixWorld.elements;
        const ruhe = new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
            const x = a.array[3 * i], y = a.array[3 * i + 1], z = a.array[3 * i + 2];
            ruhe[3 * i] = W[0] * x + W[4] * y + W[8] * z + W[12];
            ruhe[3 * i + 1] = W[1] * x + W[5] * y + W[9] * z + W[13];
            ruhe[3 * i + 2] = W[2] * x + W[6] * y + W[10] * z + W[14];
        }
        const index = netz.geometry.index ? netz.geometry.index.array : new Uint32Array(0);
        return { n, ruhe, index, kanten: Kleidungsmass.kanten(index) };
    }

    /** Je Punkt: passt der Name seines stärksten Knochens auf `muster`? */
    static _klasse(netz, muster) {
        const a = netz.geometry.attributes, si = a.skinIndex.array, sw = a.skinWeight.array;
        const namen = netz.skeleton.bones.map(b => muster.test(b.name));
        const aus = new Uint8Array(a.position.count);
        for (let i = 0; i < aus.length; i++) {
            let beste = 0, w = -1;
            for (let k = 0; k < 4; k++) if (sw[4 * i + k] > w) { w = sw[4 * i + k]; beste = si[4 * i + k]; }
            aus[i] = namen[beste] ? 1 : 0;
        }
        return aus;
    }

    /**
     * Der Stoffschwung legt seine Stücke erst in der Szenenschleife an (`takt`, nur beim
     * Abspielen) — im versteckten Tab läuft die nicht. Einmal anstoßen und warten, bis
     * jeder Worker bereit ist (Bauplan geholt), höchstens eine Minute. Mit `nur` nur
     * die gefragten Stücke: eine Probe der Schuhe wartete sonst die volle Minute auf den
     * Mantel (gemessen 12.11.2026 im versteckten Tab: 60,4 s, davon 0,4 s Messung).
     */
    static async _aufwaermen(inst, dt, nur = null) {
        const kandidaten = Object.entries(inst.clothMeshes)
            .filter(([name, m]) => m?.isSkinnedMesh && m.userData?.stoff?.kaefig && (!nur || nur.test(name)))
            .map(([, m]) => m);
        if (!kandidaten.length) return;
        const war = state.playing;
        state.playing = true;
        Genesis9stoffschwung.takt(dt);
        for (const bis = performance.now() + 60000; performance.now() < bis;) {
            const figur = Genesis9stoffschwung._figuren.get(inst);
            if (figur && kandidaten.every(m => figur.stuecke.get(m)?.bereit)) break;
            await new Promise(r => setTimeout(r, 250));
        }
        state.playing = war;
    }

    /** Das Anzeigenetz des Stoffschwungs, wenn das Stück dort läuft. */
    static _anzeige(inst, netz) {
        const e = Genesis9stoffschwung._figuren.get(inst)?.stuecke.get(netz);
        return e?.bereit && e.anzeige ? e.anzeige : null;
    }

    /** Die Weltpunkte eines Stücks in diesem Bild — Stoffschwung oder Häutung. */
    static _welt(inst, s) {
        const anzeige = Kleidungsprobe._anzeige(inst, s.netz);
        if (!anzeige) return Stoffhaut.welt(s.netz);
        anzeige.updateMatrixWorld(true);
        const a = anzeige.geometry.attributes.position.array, W = anzeige.matrixWorld.elements, aus = new Float32Array(s.n * 3);
        for (let i = 0; i < s.n; i++) {
            const x = a[3 * i], y = a[3 * i + 1], z = a[3 * i + 2];
            aus[3 * i] = W[0] * x + W[4] * y + W[8] * z + W[12];
            aus[3 * i + 1] = W[1] * x + W[5] * y + W[9] * z + W[13];
            aus[3 * i + 2] = W[2] * x + W[6] * y + W[10] * z + W[14];
        }
        return aus;
    }

    /** Die Armpunkte des Körpers in diesem Bild (flach). */
    static _arm(kw, koerper) {
        const arm = [];
        for (let i = 0; i < koerper.n; i++) if (koerper.arm[i]) arm.push(kw[3 * i], kw[3 * i + 1], kw[3 * i + 2]);
        return Float32Array.from(arm);
    }

    static _messen(inst, s, raster, kn, arm) {
        const sw = Kleidungsprobe._welt(inst, s), schritt = Math.max(1, Math.ceil(s.n / Kleidungsprobe.HOECHSTENS));
        const dehnung = Kleidungsmass.kennzahlen(Kleidungsmass.dehnung(s.ruhe, sw, s.kanten));
        const risse = Kleidungsmass.risse(s.ruhe, sw, s.kanten, Kleidungsprobe.RISS_M, Kleidungsprobe.RISS_FAKTOR);
        const abstand = Kleidungsmass.kennzahlen(Kleidungsmass.abstaende(sw, s.n, raster, schritt));
        const tiefe = Kleidungsmass.kennzahlen(Kleidungsmass.tiefen(sw, s.n, raster, kn, null, schritt));
        // Armpunkte des Körpers hinter dem Oberteil des Stücks (mehr als 5 mm innen), jeder zweite
        let drin = 0;
        if (s.oberteil.some(v => v === 1)) {
            const sr = Kleidungsmass.raster(sw, s.n, Kleidungsprobe.WEITE), sn = Kleidungsmass.normalen(sw, s.index, s.n);
            const t = Kleidungsmass.tiefen(arm, arm.length / 3, sr, sn, j => s.oberteil[j] === 1, 2);
            for (const v of t) if (v < -0.005) drin += 2;
        }
        return { dehnung, risse, abstand, tiefe, arme_drin: drin, arme: arm.length / 3 };
    }

    static _zusammen(s, koerper) {
        const w = s.werte, max = (f) => Math.max(...w.map(f)), min = (f) => Math.min(...w.map(f));
        const ruheRaster = Kleidungsmass.raster(koerper.ruhe, koerper.n, Kleidungsprobe.WEITE_RUHE);
        const ruhe = Kleidungsmass.kennzahlen(Kleidungsmass.abstaende(s.ruhe, s.n, ruheRaster));
        const E = Kleidungsprobe.ERWARTUNG, eng = ruhe.p95 < E.eng_cm / 100;
        const aus = {
            punkte: s.n, eng, dynamisch: s.dynamisch,
            dehnung_p99: +max(v => v.dehnung.p99).toFixed(2), dehnung_max: +max(v => v.dehnung.max).toFixed(2),
            risse_max: max(v => v.risse), risse_bilder: w.filter(v => v.risse > 0).length,
            ruhe_abstand_p95_cm: +(ruhe.p95 * 100).toFixed(1),
            abstand_p95_cm: +(max(v => v.abstand.p95) * 100).toFixed(1), abstand_max_cm: +(max(v => v.abstand.max) * 100).toFixed(1),
            tiefe_p1_mm: +(min(v => v.tiefe.p1) * 1000).toFixed(1), tiefe_min_mm: +(min(v => v.tiefe.min) * 1000).toFixed(1),
            arme_drin_max: max(v => v.arme_drin), arme: w[0]?.arme || 0,
            verlauf: w.map(v => [+v.dehnung.p99.toFixed(2), +(v.tiefe.p1 * 1000).toFixed(0), v.arme_drin]),
        };
        aus.urteil = {
            keine_streifen: aus.dehnung_p99 <= E.dehnung_p99,
            kein_riss: aus.risse_max <= E.risse,
            am_koerper: !eng || aus.abstand_p95_cm <= aus.ruhe_abstand_p95_cm + E.am_koerper_cm,
            haut_bleibt_drunter: aus.tiefe_p1_mm >= E.tiefe_p1_mm,
            arme_nicht_im_oberteil: aus.arme_drin_max <= E.arme_anteil * Math.max(1, aus.arme),
        };
        // Bauart starr (12.11.2026, `Starrbindung`): das Teil behält seine Form — keine Kante länger oder kürzer als `STARR_DEHNUNG` gegen die Ruhe.
        // Gegenprobe: die Laserwaffe des Fallout Rangers im Stoffschwung lag bei p99 je Bild 1,31 bis 1,71.
        if (s.netz?.userData?.starrbindung) {
            aus.starr = true;
            aus.urteil.behaelt_form = aus.dehnung_max <= Kleidungsprobe.STARR_DEHNUNG;
        }
        aus.ok = Object.values(aus.urteil).every(Boolean);
        return aus;
    }
}

window.__kleidungsprobe = Kleidungsprobe;
