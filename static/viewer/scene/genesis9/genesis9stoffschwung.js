/**
 * Genesis9stoffschwung — dForce-Kleidung eines Daz-Stücks schwingt in der
 * Bewegung nach (Edgar, 18.09.2026: „dForce-Stoff … kannst du das einbauen").
 *
 * WAS DFORCE IST: Daz' Stoffsimulation — Kleidung mit dem Modifikator
 * `dForce Simulation` wird in Daz Studio über die Animation vorab simuliert
 * (Sekunden je Bild), das Ergebnis ist eine Punktfolge. Hier läuft eine
 * NÄHERUNG live in einem Web Worker (`gemeinsam/stoffarbeiter.js` mit
 * `gemeinsam/stoffpendel.js`: Verlet auf dem Käfig, Kantenlängen, Anker,
 * Feder zur gehäuteten Lage, Schwerkraft, Kapseln um die Knochen und seit
 * dem 20.09.2026 die Haut selbst als Körper, `gemeinsam/stoffoberflaeche.js`
 * - eine Stichprobe des Körpernetzes, je Bild mit dessen Knochenmatrizen
 * gehäutet). Der Server gibt je
 * Reglerzug Freiheit und Lage des Käfigs mit dem Netz (`teil.stoff` →
 * `userData.stoff`, `Genesis9/stoff.py`) und einmal je Stück den Bauplan
 * (Kanten, Unterteilungsmatrix, Käfighaut — `garderobe/<kennung>/stoff/<n>/`).
 *
 * WIE ES GEZEICHNET WIRD: Das Stück bleibt eine `SkinnedMesh` (die GPU
 * häutet). Beim Abspielen wird sie unsichtbar, und ein zweites, ungehäutetes
 * Netz mit derselben Geometrie und demselben Material zeigt die Punkte des
 * Workers — je Bild schickt der Hauptfaden die Knochenmatrizen (dieselbe
 * Rechnung wie der Shader, `Stoffhaut.matrizen`) und die Kapseln, der Worker
 * antwortet mit Punkten und Normalen, sobald er fertig ist; ist er noch
 * beschäftigt, sammelt sich die Zeit fürs nächste Bild. Steht die Animation,
 * kommt die `SkinnedMesh` zurück; ein neues Skelett (`neuFormen`) oder ein
 * ausgezogenes Stück beendet seinen Worker.
 *
 * Läuft nach Mixer und Zopfschwung, vor dem Weichgewebe. Gemessen wird mit
 * `await __stoffschwung.probe(n, dt)` im versteckten Tab.
 *
 * JCMs (18.09.2026 abends): je Stück holt `_laden` die Käfigfelder der
 * Gelenkkorrekturen (`Genesis9felder.holenStueck(…, 'kaefig')`) und gibt sie
 * dem Worker; `_bild` schickt die Werte des Graphen dieses Bildes mit
 * (`Genesis9gelenke.werte(inst)`), der Worker verformt den Käfig vor der
 * Häutung (`gemeinsam/stofffelder.js`).
 */
import { THREE, state } from '../state.js';
import { Eigenhaut } from '../../gemeinsam/eigenhaut.js';
import { base64ToFloat32, base64ToUint32 } from '../../gemeinsam/kodierung.js';
import { Stoffkapseln, Stoffhaut } from './stoffkapseln.js';
import { Genesis9felder } from '../../gemeinsam/genesis9felder.js';
import { Genesis9gelenke } from '../../gemeinsam/genesis9gelenke.js';
import { Stoffwache } from '../../gemeinsam/stoffwache.js';

export class Genesis9stoffschwung {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    static _figuren = new Map();      // inst -> {skelett, kapseln, stuecke: Map(netz -> eintrag)}
    static _inv = new THREE.Matrix4();

    /** Aus der Szenenschleife: nach `mixer.update(dt)` und dem Zopfschwung. */
    static takt(dt) {
        for (const inst of state.characters.values()) {
            const netze = Genesis9stoffschwung.stoffnetze(inst);
            let figur = Genesis9stoffschwung._figuren.get(inst);
            if (!netze.length) {
                if (figur) { Genesis9stoffschwung._abraeumen(figur); Genesis9stoffschwung._figuren.delete(inst); }
                continue;
            }
            if (!figur || figur.skelett !== inst.skelett) {
                if (figur) Genesis9stoffschwung._abraeumen(figur);
                figur = { skelett: inst.skelett, kapseln: null, stuecke: new Map() };
                Genesis9stoffschwung._figuren.set(inst, figur);
            }
            for (const [netz, e] of [...figur.stuecke]) {
                if (!netze.includes(netz)) { Genesis9stoffschwung._entfernen(e); figur.stuecke.delete(netz); }
            }
            if (!state.playing || dt <= 0) { Genesis9stoffschwung._ruhe(figur); continue; }
            inst.group.updateMatrixWorld(true);
            if (!figur.kapseln) figur.kapseln = Stoffkapseln.anlegen(inst);
            const kapseln = Stoffkapseln.bild(figur.kapseln);
            // Die Haut je Bild: Knochenmatrizen des Körpernetzes (einmal je Figur, alle Stücke teilen sie).
            const haut = inst.bodyMesh?.isSkinnedMesh
                ? { Mk: Stoffhaut.matrizen(inst.bodyMesh), Wk: Float32Array.from(inst.bodyMesh.matrixWorld.elements) } : null;
            for (const netz of netze) {
                let e = figur.stuecke.get(netz);
                if (!e) { e = Genesis9stoffschwung._anlegen(inst, netz); figur.stuecke.set(netz, e); }
                Genesis9stoffschwung._bild(e, dt, kapseln, haut);
            }
        }
        const lebend = new Set(state.characters.values());
        for (const [inst, figur] of [...Genesis9stoffschwung._figuren]) {
            if (!lebend.has(inst)) { Genesis9stoffschwung._abraeumen(figur); Genesis9stoffschwung._figuren.delete(inst); }
        }
    }

    /** Die gehäuteten Stücke einer Figur, die Käfigdaten tragen. */
    static stoffnetze(inst) {
        if (!inst?.clothMeshes || !inst.skelett) return [];
        return Object.values(inst.clothMeshes).filter(n => n?.isSkinnedMesh && n.userData?.stoff?.kaefig);
    }

    /** Anzeigenetz anlegen, Bauplan holen, Worker starten. */
    static _anlegen(inst, netz) {
        const anzeige = new THREE.Mesh(netz.geometry.clone(), netz.material);
        anzeige.name = `${netz.name}_stoff`;
        anzeige.frustumCulled = false;
        anzeige.castShadow = netz.castShadow;
        anzeige.receiveShadow = netz.receiveShadow;
        anzeige.userData.stoffanzeige = true;
        // Ein Klick auf das Simulationsnetz trifft das STÜCK (`teilnetz_auswahl._findSubMeshForObject`) —
        // vorher wählte er die Figur, und Entf löschte die ganze Person (Edgar, 18.09.2026).
        anzeige.userData.stueckVon = netz;
        anzeige.visible = false;
        anzeige.position.copy(netz.position); anzeige.quaternion.copy(netz.quaternion); anzeige.scale.copy(netz.scale);
        netz.parent.add(anzeige);
        const e = { netz, anzeige, worker: null, bereit: false, beschaeftigt: false, dtSumme: 0,
                    bilder: 0, auslenkung: 0, warten: null, inst, felder: false };
        Genesis9stoffschwung._laden(inst, e).catch(fehler => console.warn('[Stoffschwung]', netz.name, fehler));
        return e;
    }

    static async _laden(inst, e) {
        // `genesis9_kleid_<kennung>_<n>` auf Genesis, `daz_<kennung>_<n>` auf HumanBody
        // (`Dazkleidung.PRAEFIX`) - beide tragen denselben Daz-Käfig.
        const treffer = /^(?:genesis9_kleid|daz)_(.+)_(\d+)$/.exec(e.netz.name);
        if (!treffer) return;
        const stoff = e.netz.userData.stoff;
        // Mit Länge/Weite trägt der Käfig die Haut des verschobenen Stücks (20.09.2026).
        const passform = Genesis9felder.passform(inst.kleidung?.[treffer[1]]?.regler);
        const antwort = await fetch(`${Genesis9stoffschwung.ADRESSE}${encodeURIComponent(treffer[1])}/stoff/${treffer[2]}/?stufen=${stoff.stufen}${Genesis9felder.passformAnfrage(passform)}`);
        if (!antwort.ok) throw new Error(`Bauplan ${antwort.status}`);
        const plan = await antwort.json();
        if (!e.anzeige.parent) return;                  // inzwischen ausgezogen
        // Auf HumanBody bringt das Stück die Käfighaut mit Rigify-Namen mit
        // (`G9kleidhumanbody`); der Bauplan nennt Daz-Knochen. Die Namen stehen
        // wie in Blender (`DEF-breast.L`), Three kennt `DEF-breast_L` - `boneByName`
        // übersetzt (wie `Dazkleidung.mitThreeNamen`).
        const nach = inst.skelett.boneByName || null;
        let haut = stoff.hautgewichte || plan.hautgewichte;
        if (nach) haut = { ...haut, knochen: (haut.knochen || []).map(n => nach[n]?.name ?? n) };
        const spalte = Eigenhaut.spaltenNummern(haut.knochen, inst.skelett);
        if (!spalte) throw new Error('Käfighaut nennt Knochen, die das Skelett nicht hat');
        const { index: roh, gewicht: hautGewicht } = Eigenhaut.gewichte(haut);
        const hautIndex = new Float32Array(roh.length);
        for (let i = 0; i < roh.length; i++) hautIndex[i] = spalte[roh[i]] ?? 0;
        const worker = new Worker(Genesis9stoffschwung.arbeiterpfad(), { type: 'module' });
        worker.onmessage = (ereignis) => Genesis9stoffschwung._angekommen(e, ereignis.data);
        // Nur merken — `_bild` nimmt das Stück dann zurück auf die GPU-Häutung (`Stoffwache`).
        worker.onerror = (ereignis) => { console.warn('[Stoffschwung] Worker:', ereignis.message); e.fehler = ereignis.message || 'Worker'; };
        worker.postMessage({
            typ: 'bauen', kaefig: stoff.kaefig, frei: stoff.frei, kanten: base64ToUint32(plan.kanten),
            indptr: base64ToUint32(plan.indptr), indices: base64ToUint32(plan.indices), data: base64ToFloat32(plan.data),
            zeilen: plan.zeilen, hautIndex, hautGewicht,
            dreiecke: Uint32Array.from(e.netz.geometry.index.array),
        });
        // Die Haut der Figur als Körper (`Stoffoberflaeche`): eine Stichprobe des Körpernetzes,
        // einmal je Stück - der Rock fiel sonst ins Becken, wo keine Kapsel ist (20.09.2026).
        const probe = Stoffhaut.stichprobe(inst.bodyMesh);
        if (probe) worker.postMessage({ typ: 'koerper', ...probe });
        e.worker = worker;
        e.bereit = true;
        // Die Käfigfelder der JCMs gehören zu Daz' Gelenken - auf HumanBody (eigene
        // Käfighaut mit Rigify-Namen) gibt es sie nicht.
        if (!stoff.hautgewichte) Genesis9stoffschwung._felder(e, treffer[1], Number(treffer[2]), passform);
    }

    /** Die Käfigfelder der JCMs dieses Teils an den Worker geben (asynchron, einmal je Stück). */
    static async _felder(e, kennung, nummer, passform = null) {
        const teile = await Genesis9felder.holenStueck(Genesis9gelenke.GRUPPE, kennung, 'kaefig', passform);
        const eigene = teile?.[nummer];
        if (!eigene || !Object.keys(eigene).length || !e.worker || !e.anzeige.parent) return;
        e.worker.postMessage({ typ: 'felder', felder: eigene });
        e.felder = true;
    }

    /**
     * Der Worker liegt außerhalb des Szenenbündels (`/buendel/<fassung>/scene.js`,
     * dort zeigt `import.meta.url` ins Leere): die Vorlage nennt seinen Pfad
     * mit Fassung (`<meta name="stoffarbeiter">`, `{% fassungspfad %}`).
     */
    static arbeiterpfad() {
        const meta = document.querySelector('meta[name="stoffarbeiter"]')?.content;
        return meta || new URL('../../gemeinsam/stoffarbeiter.js', import.meta.url).href;
    }

    static _bild(e, dt, kapseln, haut = null) {
        e.dtSumme += dt;
        // Ein toter oder stummer Worker ließe das Anzeigenetz mit seinen letzten
        // Punkten stehen, während der Körper weitertanzt („hose animiert nicht").
        if (!e.ausgefallen && Stoffwache.ausgefallen(e, performance.now())) {
            console.warn('[Stoffschwung]', e.netz.name, 'ohne Stoffschwung weiter:', e.fehler || 'keine Antwort');
            Stoffwache.zurueck(e);
        }
        if (!e.bereit || e.beschaeftigt) return;
        const { netz, anzeige } = e;
        anzeige.updateMatrixWorld(true);
        e.worker.postMessage({
            typ: 'bild', M: Stoffhaut.matrizen(netz), W: Float32Array.from(netz.matrixWorld.elements),
            inv: Float32Array.from(Genesis9stoffschwung._inv.copy(anzeige.matrixWorld).invert().elements),
            kapseln, Mk: haut?.Mk || null, Wk: haut?.Wk || null,
            dt: e.dtSumme, werte: e.felder ? (Genesis9gelenke.werte(e.inst) || null) : null,
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
        if (!e.anzeige.visible && state.playing) { e.anzeige.visible = true; e.netz.visible = false; }
        e.bilder++;
        e.auslenkung = d.auslenkung;
        e.zeiten = d.zeiten;
        if (e.warten) { e.warten(); e.warten = null; }
    }

    static _ruhe(figur) {
        for (const e of figur.stuecke.values()) {
            if (e.anzeige.visible) { e.anzeige.visible = false; e.netz.visible = true; }
        }
    }

    static _entfernen(e) {
        e.netz.visible = true;
        e.worker?.terminate();
        e.anzeige.parent?.remove(e.anzeige);
        e.anzeige.geometry.dispose();
    }

    static _abraeumen(figur) {
        for (const e of figur.stuecke.values()) Genesis9stoffschwung._entfernen(e);
        figur.stuecke.clear();
    }

    /**
     * Für Sichtproben aus der Konsole (kein `requestAnimationFrame` im
     * versteckten Fenster): `schritte` Bilder zu `dt` Sekunden — Mixer,
     * Stoff — jedes Bild wartet auf den Worker; zurück kommen ms je Bild und
     * je Stück Punkte, Auslenkung (m).
     */
    static async probe(schritte = 30, dt = 1 / 30) {
        if (!state.mixer) return null;
        const war = state.playing;
        state.playing = true;
        const t0 = performance.now();
        for (let i = 0; i < schritte; i++) {
            state.mixer.update(dt);
            Genesis9stoffschwung.takt(dt);
            const offen = [];
            for (const figur of Genesis9stoffschwung._figuren.values()) {
                for (const e of figur.stuecke.values()) {
                    if (e.beschaeftigt) offen.push(new Promise(res => { e.warten = res; }));
                    else if (!e.bereit) offen.push(new Promise(res => setTimeout(res, 200)));
                }
            }
            await Promise.all(offen);
        }
        const ms = (performance.now() - t0) / schritte;
        state.playing = war;
        const aus = { ms: +ms.toFixed(1), stuecke: [] };
        for (const figur of Genesis9stoffschwung._figuren.values()) {
            for (const e of figur.stuecke.values()) {
                aus.stuecke.push({ name: e.netz.name, bereit: e.bereit, bilder: e.bilder,
                                   auslenkung: +e.auslenkung.toFixed(3), kapseln: figur.kapseln?.length,
                                   zeiten: e.zeiten, felder: e.felder });
            }
        }
        return aus;
    }
}

window.__stoffschwung = Genesis9stoffschwung;
