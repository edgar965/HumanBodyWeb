import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';
import { DazschnittGLSL } from './dazschnittglsl.js';
import { Dazschnittwerte } from './dazschnittwerte.js';
import { Dazschnittkoord } from './dazschnittkoord.js';
import { Koerperkoordinatenkarte } from './koerperkoordinatenkarte.js';
import { Hautmaske } from './hautmaske.js';
import { Hautverdeckung } from './hautverdeckung.js';
import { Umfaerbung } from './umfaerbung.js';
import { Stueckereignis } from './stueckereignis.js';
import { Skelettereignis } from './skelettereignis.js';
import { Protokoll } from './protokoll.js';

/**
 * Dazschnitt — Ausschnitt und Säume an einem getragenen Daz-Stück NUR durch Wegschneiden, dazu Saumband, Kragen und Knopfleiste als Abziehbild (Stufe K2c,
 * 25.10.2026; Felder `Dazschnittfelder`, Werte und Kante `Dazschnittwerte`, Shader `DazschnittGLSL`, Körperkoordinaten je Punkt `Dazschnittkoord`).
 *
 * ZWEI SCHNITTE, EINE KANTE: Flächen, deren drei Ecken jenseits liegen, fallen aus dem Index (`_netz`, gerechnet vom Index wie geliefert, `geometry.userData.
 * dazschnitt.voll`); in den Flächen an der Kante verwirft der Shader die Pixel jenseits. Nichts wird angebaut.
 * HAUT DARUNTER: Die Hautverdeckung (`Hautverdeckung`, Haut unter Kleidung wird nicht gezeichnet) rechnet mit dem VOLLEN Index jedes Stücks
 * (`geometry.userData.indexVoll`). Der geschnittene Index wird deshalb auch dort eingetragen, und nach jedem Schnitt wird sie neu geplant — wo der Ausschnitt
 * tiefer wird, liegt kein Stoff mehr über der Haut, sie wird wieder gezeichnet. In den Randflächen bleibt die Haut versenkt gezeichnet (`Saumband`), kein Loch.
 * (Die Lagenverdeckung rechnet ebenfalls vom `indexVoll` und sieht so das geschnittene Stück.)
 *
 * WANN: bei jedem Anziehen/Neubau eines Stücks (`Stueckereignis`) und jedem neuen Körper (`Skelettereignis`), wenn das Stück `schnitt:`-Regler trägt; beim Zug
 * am Schieber nur die Uniforms (`vorschau`), beim Loslassen alles (`anwenden`). Ein Stück ohne Eigen-Werte bleibt unangetastet (kein Eingriff, kein Index).
 */
export class Dazschnitt {

    static uniforms() {
        return { uDkHals: { value: [-1, 0, 0, 0.18] }, uDkSaum: { value: [99, 99, -99, 99] }, uDkBand: { value: [0, 0, 0, 0] },
                 uDkLeiste: { value: [0, 0, 0, 0] }, uDkLaenge: { value: [0.62, 0.6, 0.8] } };
    }

    /**
     * Die Uniforms EINES Materials — einmal je Material, nie neu (`_je`). Three ruft `onBeforeCompile` je Programmschlüssel nur einmal je Material und behält
     * dessen Uniform-Objekte; ein zweites Anhängen mit frischen Objekten (nach `zurueck`) hätte nichts mehr bewegt (im Chrome gesehen: der Ausschnitt blieb
     * auf „V“, obwohl „rund“ in den Uniforms stand — wie bei `Umfaerbung`).
     */
    static _je = new WeakMap();

    static _uniformsVon(material) {
        let u = Dazschnitt._je.get(material);
        if (!u) { u = Dazschnitt.uniforms(); Dazschnitt._je.set(material, u); }
        return u;
    }

    static _uniformsSetzen(netz, s, laengen) {
        for (const material of [netz.material].flat()) {
            if (!material) continue;
            const u = Dazschnitt._uniformsVon(material);
            for (const [name, werte] of [['uDkHals', s.hals], ['uDkSaum', s.saum], ['uDkBand', s.band], ['uDkLeiste', s.leiste], ['uDkLaenge', laengen]]) {
                werte.forEach((w, i) => { u[name].value[i] = w; });
            }
        }
    }

    /** Die Netze eines getragenen Stücks, die geschnitten werden dürfen (Art `kleidung`). */
    static netze(inst, kennung) {
        return Umfaerbung.netze(inst, kennung).map(e => e.netz).filter(n => n?.isMesh && n.geometry?.index && n.userData?.art === 'kleidung');
    }

    /**
     * Die Werte des Stücks auf seine Netze: Attribute, Eingriff, Index; danach die Hautverdeckung neu planen (`masken`). `werte`: statt der Regler (Vorschau).
     * → `{netze, entfernt, ms, quelle}` oder null (keine Genesis-9-Figur, kein Körper).
     */
    static async anwenden(inst, kennung, { werte = null, masken = true } = {}) {
        if (inst?.quelle !== 'genesis9') return null;
        const w = werte || Dazschnittwerte.alle(Dazschnittwerte.regler(inst, kennung));
        const netze = Dazschnitt.netze(inst, kennung);
        let geaendert = false;
        if (!Dazschnittwerte.noetig(w)) {
            for (const netz of netze) geaendert = Dazschnitt.zurueck(netz) || geaendert;
            if (geaendert && masken) Hautverdeckung.planen(inst);
            return { netze: 0, entfernt: 0 };
        }
        const karte = await Koerperkoordinatenkarte.holen();
        const koerper = inst.bodyMesh;
        if (!koerper?.geometry?.attributes?.uv) return null;
        const t0 = performance.now();
        const haut = Dazschnittkoord.haut(koerper, karte);
        const s = Dazschnittwerte.shaderwerte(w);
        const stand = { netze: 0, entfernt: 0, quelle: '' };
        for (const netz of Dazschnitt.netze(inst, kennung)) {              // nach dem Warten neu gelesen: das Stück kann neu gebaut sein
            geaendert = Dazschnitt._netz(inst, netz, haut, s) || geaendert;
            const st = netz.geometry.userData.dazschnitt;
            stand.netze++; stand.entfernt += st.entfernt || 0; stand.quelle = st.quelle;
        }
        stand.ms = Math.round(performance.now() - t0);
        if (geaendert && masken) Hautverdeckung.planen(inst);
        Protokoll.debug('Daz-Schnitt', `${kennung}: ${stand.netze} Netze, ${stand.entfernt} Dreiecke weggeschnitten, Koordinaten aus ${stand.quelle} (${stand.ms} ms)`);
        return stand;
    }

    /** Nur die Uniforms (Schieber im Zug) — false, wenn das Stück noch keinen Eingriff trägt (dann `anwenden`). */
    static vorschau(inst, kennung, werte) {
        const netze = Dazschnitt.netze(inst, kennung);
        if (!netze.length || netze.some(n => !n.geometry.userData.dazschnitt)) return false;
        const s = Dazschnittwerte.shaderwerte(werte);
        for (const netz of netze) Dazschnitt._uniformsSetzen(netz, s, netz.geometry.userData.dazschnitt.haut.laengen);
        return true;
    }

    static _netz(inst, netz, haut, s) {
        const geo = netz.geometry;
        let st = geo.userData.dazschnitt;
        if (!st || st.haut !== haut) {
            const t = Dazschnittkoord.teil(netz, haut);
            geo.setAttribute('dkKoord', new THREE.BufferAttribute(t.koord, 4));
            geo.setAttribute('dkLage', new THREE.BufferAttribute(t.lage, 2));
            st = geo.userData.dazschnitt = { haut, koord: t.koord, lage: t.lage, quelle: t.quelle, voll: st?.voll || Dazschnitt._voll(geo),
                                              schluessel: null, entfernt: 0 };
        }
        Dazschnitt._uniformsSetzen(netz, s, haut.laengen);
        for (const material of [netz.material].flat()) {
            if (!material || Shaderpatch.hat(material, DazschnittGLSL.SCHLUESSEL)) continue;
            const u = Dazschnitt._uniformsVon(material);
            const eingriff = (shader) => {
                const fehlt = DazschnittGLSL.patchen(shader, u);
                if (fehlt.length) Protokoll.warnung('Daz-Schnitt', `${netz.name}: Shader ohne Stelle ${fehlt.join(', ')} — Schnitt und Abziehbilder wirken nicht`);
            };
            eingriff.kennung = () => DazschnittGLSL.FASSUNG;
            Shaderpatch.anhaengen(material, DazschnittGLSL.SCHLUESSEL, eingriff);
        }
        const schluessel = JSON.stringify([s.hals, s.saum, haut.laengen]);
        if (st.schluessel === schluessel) return false;
        st.schluessel = schluessel;
        const weg = Dazschnitt.wegflaechen(st.voll.index, st.koord, st.lage, s, haut.laengen);
        const neu = Hautmaske.indexOhne(st.voll.index, st.voll.gruppen, new Uint8Array(st.lage.length / 2), weg);
        Hautverdeckung.indexSetzen(geo, neu.index, neu.gruppen);
        geo.userData.indexVoll = { index: neu.index.slice(), gruppen: neu.gruppen.map(g => ({ ...g })) };
        const vorher = st.entfernt;
        st.entfernt = neu.entfernt;
        return vorher > 0 || neu.entfernt > 0;                         // der Index hat sich geändert: die Masken neu
    }

    /** Der Index wie geliefert (vor dem ersten Schnitt; liegt schon ein voller Index der Lagenverdeckung, dieser). */
    static _voll(geo) {
        const v = geo.userData.indexVoll;
        return v ? { index: v.index.slice(), gruppen: v.gruppen.map(g => ({ ...g })) }
            : { index: geo.index.array.slice(), gruppen: geo.groups.map(g => ({ start: g.start, count: g.count, materialIndex: g.materialIndex })) };
    }

    /** Je Dreieck 1, wenn alle drei Ecken jenseits der Kante liegen (`Dazschnittwerte.kante` < 0); `lage` 2N (x, Halsansatz). */
    static wegflaechen(index, koord, lage, s, laengen) {
        const n = lage.length / 2, f = new Float32Array(n), weg = new Uint8Array(index.length / 3);
        for (let p = 0; p < n; p++) {
            f[p] = Dazschnittwerte.kante(Math.round(koord[4 * p]), koord[4 * p + 1], koord[4 * p + 2], lage[2 * p], Math.cos(2 * Math.PI * koord[4 * p + 3]), s,
                                         laengen, lage[2 * p + 1]);
        }
        for (let t = 0; t < weg.length; t++) weg[t] = f[index[3 * t]] < 0 && f[index[3 * t + 1]] < 0 && f[index[3 * t + 2]] < 0 ? 1 : 0;
        return weg;
    }

    /** Alles zurück: Index wie geliefert, Eingriff und Attribute weg. → true, wenn Dreiecke zurückkamen. */
    static zurueck(netz) {
        const geo = netz.geometry, st = geo?.userData?.dazschnitt;
        if (!st) return false;
        Hautverdeckung.indexSetzen(geo, st.voll.index.slice(), st.voll.gruppen.map(g => ({ ...g })));
        geo.userData.indexVoll = { index: st.voll.index.slice(), gruppen: st.voll.gruppen.map(g => ({ ...g })) };
        for (const material of [netz.material].flat()) if (material) Shaderpatch.entfernen(material, DazschnittGLSL.SCHLUESSEL);
        geo.deleteAttribute('dkKoord');
        geo.deleteAttribute('dkLage');
        delete geo.userData.dazschnitt;
        return st.entfernt > 0;
    }

    /** Trägt das Stück Eigen-Werte (`schnitt:`)? */
    static traegt(inst, kennung) {
        return Object.keys(Dazschnittwerte.regler(inst, kennung)).some(k => k.startsWith(Dazschnittwerte.PRAEFIX));
    }

    static _fehler(fehler) {
        Protokoll.fehler('Daz-Schnitt', 'Schnitt nicht angewendet', fehler);
    }

    static einhaengen() {
        Stueckereignis.hoeren(({ inst, stueck, angezogen }) => {
            if (angezogen && inst?.quelle === 'genesis9' && Dazschnitt.traegt(inst, stueck)) Dazschnitt.anwenden(inst, stueck).catch(Dazschnitt._fehler);
        });
        Skelettereignis.hoeren(({ inst }) => {
            if (inst?.quelle !== 'genesis9') return;
            for (const kennung of Object.keys(inst.kleidung || {})) {
                if (Dazschnitt.traegt(inst, kennung)) Dazschnitt.anwenden(inst, kennung).catch(Dazschnitt._fehler);
            }
        });
    }
}

if (typeof document !== 'undefined') {
    Dazschnitt.einhaengen();
    window.__dazschnitt = Dazschnitt;
}
