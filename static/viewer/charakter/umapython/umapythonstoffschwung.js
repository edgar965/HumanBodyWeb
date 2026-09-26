/**
 * Umapythonstoffschwung — lose UMA-Kleidung (Robe, Rock, Kleid) schwingt in der
 * Bewegung nach (Edgar, 25.09.2026: „UMAs ClothHelper ungenutzt - warum? Baue das ein").
 *
 * WARUM NICHT UMAS EIGENER WEG: Unity-`Cloth` braucht je Slot
 * `clothSkinningSerialized` und je Renderer `ClothProperties`; im Bestand hat
 * kein einziger der 254 Slots die Koeffizienten, und beide Renderer-Assets
 * lassen `ClothProperties` leer — Unity baut hier nie Stoff (`UMA_Python/stoffschwung.py`).
 * Der Server liefert deshalb je losem Kleidungsslot eine Freiheit je Punkt
 * (UMAs maxDistance, wo vorhanden, sonst der Hautabstand wie bei Genesis 9),
 * und derselbe Worker wie beim Daz-Stoff rechnet das Pendel
 * (`gemeinsam/stoffarbeiter.js`, Protokoll `bauen`/`koerper`/`bild`).
 *
 * WAS ANDERS IST ALS BEI GENESIS: Eine UMA-Figur ist EIN Netz mit einer
 * Materialgruppe je Slot. Beim Abspielen wird die Gruppe des Slots im Körper
 * auf 0 Einträge gesetzt, und ein eigenes, ungehäutetes Netz aus seinen Punkten
 * zeigt, was der Worker rechnet; steht die Animation, kommt die Gruppe zurück.
 * Der Käfig sind die geschweißten Orte des Slots (`zuordnung`, UV-Nahtkopien),
 * die Browserpunkte zeigen über eine Eins-Matrix darauf. Kapseln und Hautprobe
 * nehmen nur die KÖRPERslots (`stoff.koerper`) — mit den Stoffpunkten darin
 * stünde der Rock in seiner eigenen Kollision.
 *
 * Probe im versteckten Tab: `await __umastoffschwung.probe(30, 1/30)`.
 */
import { THREE, state } from '../state.js';
import { base64ToFloat32, base64ToUint32 } from '../../gemeinsam/kodierung.js';
import { Stoffkapseln, Stoffhaut } from '../../gemeinsam/stoffkapseln.js';
import { Stoffwache } from '../../gemeinsam/stoffwache.js';
import { Genesis9stoffschwung } from '../genesis9/genesis9stoffschwung.js';

export class Umapythonstoffschwung {

    static _figuren = new Map();      // inst -> {netz, kapseln, probe, teile: [eintrag]}
    static _inv = new THREE.Matrix4();

    /** Aus der Szenenschleife, nach dem Mixer — wie `Genesis9stoffschwung.takt`. */
    static takt(dt) {
        const lebend = new Set();
        for (const inst of state.characters.values()) {
            const netz = inst.bodyMesh;
            const stoff = netz?.isSkinnedMesh ? netz.userData?.umastoff : null;
            let figur = Umapythonstoffschwung._figuren.get(inst);
            if (!stoff?.teile?.length) {
                if (figur) Umapythonstoffschwung._abraeumen(inst, figur);
                continue;
            }
            lebend.add(inst);
            // Jeder Reglerzug baut das Körpernetz neu — dann auch die Stücke.
            if (!figur || figur.netz !== netz) {
                if (figur) Umapythonstoffschwung._abraeumen(inst, figur);
                figur = Umapythonstoffschwung._figur(inst, netz, stoff);
            }
            if (!state.playing || dt <= 0) { Umapythonstoffschwung._ruhe(figur); continue; }
            inst.group.updateMatrixWorld(true);
            if (!figur.kapseln) figur.kapseln = Stoffkapseln.anlegen({ bodyMesh: figur.koerper });
            const kapseln = Stoffkapseln.bild(figur.kapseln);
            const haut = { Mk: Stoffhaut.matrizen(netz), Wk: Float32Array.from(netz.matrixWorld.elements) };
            for (const e of figur.teile) Umapythonstoffschwung._bild(e, dt, kapseln, haut);
        }
        for (const [inst, figur] of [...Umapythonstoffschwung._figuren]) {
            if (!lebend.has(inst)) Umapythonstoffschwung._abraeumen(inst, figur);
        }
    }

    static _figur(inst, netz, stoff) {
        const koerper = Umapythonstoffschwung.koerpernetz(netz, stoff.koerper);
        const figur = { netz, koerper, kapseln: null, teile: [] };
        const probe = Stoffhaut.stichprobe(koerper);
        for (const teil of stoff.teile) {
            try {
                figur.teile.push(Umapythonstoffschwung._anlegen(netz, teil, probe));
            } catch (fehler) {
                console.warn('[UMA-Stoff]', teil.name, fehler);
            }
        }
        Umapythonstoffschwung._figuren.set(inst, figur);
        return figur;
    }

    /**
     * Nur die Körperslots als eigene `SkinnedMesh` (nicht in der Szene) — für
     * Kapseln und Hautprobe. Gleiches Skelett, gleiche Bindung wie der Körper.
     */
    static koerpernetz(netz, bereiche) {
        const quelle = netz.geometry.attributes;
        const geo = new THREE.BufferGeometry();
        for (const [name, breite] of [['position', 3], ['normal', 3], ['skinIndex', 4], ['skinWeight', 4]]) {
            if (!quelle[name]) continue;
            const teile = bereiche.map(([ab, n]) => quelle[name].array.subarray(ab * breite, (ab + n) * breite));
            const feld = new quelle[name].array.constructor(teile.reduce((s, t) => s + t.length, 0));
            let o = 0;
            for (const t of teile) { feld.set(t, o); o += t.length; }
            geo.setAttribute(name, new THREE.BufferAttribute(feld, breite));
        }
        const koerper = new THREE.SkinnedMesh(geo, netz.material);
        koerper.bind(netz.skeleton, netz.bindMatrix);
        koerper.matrixWorld = netz.matrixWorld;     // lebt mit dem Körper, wird nicht gezeichnet
        return koerper;
    }

    /** Anzeigenetz des Slots bauen, Worker starten. */
    static _anlegen(netz, teil, probe) {
        const a = netz.geometry.attributes;
        const ab = teil.punkt_ab, n = teil.punktzahl;
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(a.position.array.slice(3 * ab, 3 * (ab + n)), 3));
        if (a.normal) geo.setAttribute('normal', new THREE.BufferAttribute(a.normal.array.slice(3 * ab, 3 * (ab + n)), 3));
        if (a.uv) geo.setAttribute('uv', new THREE.BufferAttribute(a.uv.array.slice(2 * ab, 2 * (ab + n)), 2));
        const index = Uint32Array.from(netz.geometry.index.array.subarray(teil.index_ab, teil.index_ab + teil.index_anzahl),
                                       (i) => i - ab);
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        const gruppe = netz.geometry.groups.find(g => g.start === teil.index_ab);
        const material = Array.isArray(netz.material) ? netz.material[gruppe?.materialIndex ?? 0] : netz.material;
        const anzeige = new THREE.Mesh(geo, material);
        anzeige.name = `${netz.name}_stoff_${teil.name}`;
        anzeige.frustumCulled = false;
        anzeige.visible = false;
        anzeige.userData.stoffanzeige = true;
        anzeige.userData.stueckVon = netz;
        anzeige.position.copy(netz.position); anzeige.quaternion.copy(netz.quaternion); anzeige.scale.copy(netz.scale);
        netz.parent.add(anzeige);
        const e = { name: teil.name, netz, anzeige, gruppe, anzahl: gruppe?.count ?? 0, worker: null,
                    bereit: false, beschaeftigt: false, dtSumme: 0, bilder: 0, auslenkung: 0, warten: null };
        const worker = new Worker(Genesis9stoffschwung.arbeiterpfad(), { type: 'module' });
        worker.onmessage = (ereignis) => Umapythonstoffschwung._angekommen(e, ereignis.data);
        worker.onerror = (ereignis) => { console.warn('[UMA-Stoff] Worker:', ereignis.message); e.fehler = ereignis.message || 'Worker'; };
        worker.postMessage({ typ: 'bauen', ...Umapythonstoffschwung.bauplan(a, teil), dreiecke: index });
        if (probe) worker.postMessage({ typ: 'koerper', ...probe });
        e.worker = worker;
        e.bereit = true;
        return e;
    }

    /**
     * Käfig, Haut und Eins-Matrix aus dem Körpernetz: je Käfigpunkt Lage und
     * Gewichte seines Vertreters (dieselbe Häutung wie der Shader).
     */
    static bauplan(a, teil) {
        const ab = teil.punkt_ab, n = teil.punktzahl;
        const vertreter = base64ToUint32(teil.vertreter), zuordnung = base64ToUint32(teil.zuordnung);
        const k = vertreter.length;
        const kaefig = new Float32Array(3 * k), hautIndex = new Float32Array(4 * k), hautGewicht = new Float32Array(4 * k);
        for (let j = 0; j < k; j++) {
            const i = ab + vertreter[j];
            for (let c = 0; c < 3; c++) kaefig[3 * j + c] = a.position.array[3 * i + c];
            for (let c = 0; c < 4; c++) {
                hautIndex[4 * j + c] = a.skinIndex.array[4 * i + c];
                hautGewicht[4 * j + c] = a.skinWeight.array[4 * i + c];
            }
        }
        const indptr = new Uint32Array(n + 1);
        for (let r = 0; r <= n; r++) indptr[r] = r;
        return { kaefig, frei: base64ToFloat32(teil.frei), kanten: base64ToUint32(teil.kanten),
                 indptr, indices: zuordnung, data: new Float32Array(n).fill(1), zeilen: n, hautIndex, hautGewicht };
    }

    static _bild(e, dt, kapseln, haut) {
        e.dtSumme += dt;
        if (!e.ausgefallen && Stoffwache.ausgefallen(e, performance.now())) {
            console.warn('[UMA-Stoff]', e.name, 'ohne Stoffschwung weiter:', e.fehler || 'keine Antwort');
            Stoffwache.zurueck(e);
            Umapythonstoffschwung._zeigen(e, false);
        }
        if (!e.bereit || e.beschaeftigt || e.ausgefallen) return;
        e.anzeige.updateMatrixWorld(true);
        e.worker.postMessage({
            typ: 'bild', M: haut.Mk, W: haut.Wk,
            inv: Float32Array.from(Umapythonstoffschwung._inv.copy(e.anzeige.matrixWorld).invert().elements),
            kapseln, Mk: haut.Mk, Wk: haut.Wk, dt: e.dtSumme, werte: null,
        });
        e.beschaeftigt = true;
        e.gesendet = performance.now();
        e.dtSumme = 0;
    }

    static _angekommen(e, d) {
        e.beschaeftigt = false;
        if (d.typ !== 'punkte' || !e.anzeige.parent) return;
        const geo = e.anzeige.geometry;
        geo.attributes.position.array.set(d.pos);
        geo.attributes.position.needsUpdate = true;
        if (geo.attributes.normal) { geo.attributes.normal.array.set(d.nrm); geo.attributes.normal.needsUpdate = true; }
        if (state.playing && !e.ausgefallen) Umapythonstoffschwung._zeigen(e, true);
        e.bilder++;
        e.auslenkung = d.auslenkung;
        e.zeiten = d.zeiten;
        if (e.warten) { e.warten(); e.warten = null; }
    }

    /** Simulationsnetz an und die Slotgruppe im Körper aus — oder umgekehrt. */
    static _zeigen(e, simuliert) {
        e.anzeige.visible = simuliert;
        if (e.gruppe) e.gruppe.count = simuliert ? 0 : e.anzahl;
    }

    static _ruhe(figur) {
        for (const e of figur.teile) if (e.anzeige.visible) Umapythonstoffschwung._zeigen(e, false);
    }

    static _abraeumen(inst, figur) {
        for (const e of figur.teile) {
            Umapythonstoffschwung._zeigen(e, false);
            e.worker?.terminate();
            e.anzeige.parent?.remove(e.anzeige);
            e.anzeige.geometry.dispose();
        }
        figur.koerper?.geometry.dispose();
        Umapythonstoffschwung._figuren.delete(inst);
    }

    /** Sichtprobe ohne `requestAnimationFrame`: `schritte` Bilder, jedes wartet auf die Worker. */
    static async probe(schritte = 30, dt = 1 / 30) {
        if (!state.mixer) return null;
        const war = state.playing;
        state.playing = true;
        const t0 = performance.now();
        for (let i = 0; i < schritte; i++) {
            state.mixer.update(dt);
            Umapythonstoffschwung.takt(dt);
            const offen = [];
            for (const figur of Umapythonstoffschwung._figuren.values()) {
                for (const e of figur.teile) if (e.beschaeftigt) offen.push(new Promise(res => { e.warten = res; }));
            }
            await Promise.all(offen);
        }
        const ms = (performance.now() - t0) / schritte;
        state.playing = war;
        const aus = { ms: +ms.toFixed(1), stuecke: [] };
        for (const figur of Umapythonstoffschwung._figuren.values()) {
            for (const e of figur.teile) {
                aus.stuecke.push({ name: e.name, bilder: e.bilder, auslenkung: +e.auslenkung.toFixed(3),
                                   kapseln: figur.kapseln?.length, zeiten: e.zeiten, ausgefallen: !!e.ausgefallen });
            }
        }
        return aus;
    }
}

window.__umastoffschwung = Umapythonstoffschwung;
