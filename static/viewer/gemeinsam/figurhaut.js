import * as THREE from 'three';
import { Hautmaske } from './hautmaske.js';
import { Lagenmaske } from './lagenmaske.js';
import { Hautmaskegeometrie } from './hautmaskegeometrie.js';
import { Hauteinzug } from './hauteinzug.js';
import { Protokoll } from './protokoll.js';

/**
 * Figurhaut — die Haut unter der Kleidung einer selbst gebauten Figur wird
 * nicht gezeichnet, und Stoff unter Stoff auch nicht.
 *
 * HERKUNFT: `bvh_studio/spurhaut.js` (Edgar, 11.09.2026: „die haut ist immer
 * noch sichtbar im BVH Studio, spiele die Animation ab"). Am 12.09.2026
 * dasselbe auf der Ergebnisseite („bei einer animation mit Female2 scheint
 * die Haut durch das Kleid"): `result_character/garmentcode_stuecke.js`
 * bindet die GarmentCode-Stücke wie das Studio (`Garmentcodebindung`), und
 * auch dort zeichnete niemand die Haut weg. Die Klasse ist nicht ans Studio
 * gebunden — sie braucht nur einen Körper und eine Gruppe mit Stücken —
 * deshalb liegt sie jetzt hier; `Spurhaut` im Studio erbt sie.
 *
 * Dieselbe Rechnung wie die Szene-Seite (`gemeinsam/hautmaske.js`,
 * `lagenmaske.js`, Einzug der Randdreiecke über `hauteinzug.js`), nur die
 * Figur ist anders gebaut: Körper ist `figur.mesh`, die Stücke hängen
 * direkt in `figur.group` und tragen `userData.isGarment` (GarmentCode aus
 * `Garmentcodestueck`, MakeHuman-Stücke aus `Spurzubehoer._anhaengen`);
 * Haare nicht — sie sind kein Stoff und liegen ohnehin über der Haut.
 *
 * WANN: einmal nach dem Bau der Figur, wenn die Geometrien in Ruhelage im
 * selben Raum liegen; das Skinning kommt erst beim Abspielen, und der
 * Einzug läuft im Shader VOR dem Skinning mit. Der volle Index bleibt in
 * `geometry.userData.indexVoll`; `aufheben` stellt ihn her, wenn die Stücke
 * gehen (Ergebnisseite: Vorgabe gewechselt).
 */
export class Figurhaut {

    /** @param {{mesh: THREE.Mesh, group: THREE.Group, name?: string}} figur */
    static anwenden(figur) {
        const koerper = figur?.mesh;
        const geo = koerper?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Figurhaut.merken(geo);
        const stoffe = Figurhaut.stoffe(figur);
        if (!stoffe.length) return Figurhaut.aufheben(figur);
        const t0 = performance.now();
        const voll = geo.userData.indexVoll;
        const maske = Hautmaske.verdeckt(geo.attributes.position.array, voll.index, stoffe);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
        Figurhaut.indexSetzen(geo, neu.index, neu.gruppen);
        geo.userData.hautVerdeckt = maske;
        Hauteinzug.setzen(koerper, maske, voll.index);
        const stand = { verdeckt: Figurhaut._anzahl(maske), dreiecke: neu.entfernt,
                        stuecke: stoffe.length, lagen: [] };
        if (stoffe.length > 1) stand.lagen = Figurhaut._lagen(geo, stoffe);
        stand.ms = Math.round(performance.now() - t0);
        Protokoll.debug('Figurhaut', `Hautmaske ${figur.name || ''}: ${stand.verdeckt} Punkte `
            + `unter ${stoffe.length} Stücken, ${stand.dreiecke} Dreiecke weg, ${stand.ms} ms`);
        return stand;
    }

    /** Den vollen Index wiederherstellen — kein Stück mehr an der Figur. */
    static aufheben(figur) {
        const koerper = figur?.mesh;
        const geo = koerper?.geometry;
        const voll = geo?.userData?.indexVoll;
        if (!voll) return null;
        Figurhaut.indexSetzen(geo, voll.index, voll.gruppen);
        delete geo.userData.hautVerdeckt;
        Hauteinzug.setzen(koerper, null, null);
        return { verdeckt: 0, dreiecke: 0, stuecke: 0, lagen: [], ms: 0 };
    }

    /** Stoff unter Stoff: je Stück der gekürzte Index und der Einzug. */
    static _lagen(geo, stoffe) {
        const koerper = { punkte: geo.attributes.position.array,
                          dreiecke: geo.userData.indexVoll.index };
        const ergebnis = Lagenmaske.verdeckt(koerper, stoffe);
        const N = Hautmaskegeometrie.normalen(koerper.punkte, koerper.dreiecke);
        const gitter = Hautmaskegeometrie.punktgitter(koerper.punkte, Hautmaskegeometrie.ZELLE_M);
        const lagen = [];
        for (const s of stoffe) {
            const { maske, ueber } = ergebnis.get(s.schluessel);
            if (!ueber.length) continue;
            const voll = s.netz.geometry.userData.indexVoll;
            const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
            Figurhaut.indexSetzen(s.netz.geometry, neu.index, neu.gruppen);
            s.netz.geometry.userData.lagenVerdeckt = maske;
            Figurhaut._einzug(s.netz, maske, koerper, N, gitter);
            lagen.push({ stueck: s.schluessel, unter: ueber, verdeckt: Figurhaut._anzahl(maske),
                         dreiecke: neu.entfernt });
        }
        return lagen;
    }

    /** Einzug entlang der HAUTnormale — wie `Lagenverdeckung._einzug`. */
    static _einzug(netz, maske, koerper, N, gitter) {
        const P = netz.geometry.attributes.position.array;
        const NS = Lagenmaske.normalenVonHaut(P, koerper.punkte, N, gitter);
        const werte = new Float32Array(P.length);
        for (let i = 0; i < maske.length; i++) {
            if (!maske[i]) continue;
            for (let k = 0; k < 3; k++) werte[3 * i + k] = -Hauteinzug.EINZUG_M * NS[3 * i + k];
        }
        netz.geometry.setAttribute('einzug', new THREE.BufferAttribute(werte, 3));
        Hauteinzug.patchen(netz);
    }

    /** Die Stücke der Figur — Netze mit `isGarment`, direkt in der Gruppe. */
    static stoffe(figur) {
        const aus = [];
        for (const netz of figur?.group?.children || []) {
            const g = netz?.geometry;
            if (!netz.isMesh || !netz.userData?.isGarment
                || !g?.attributes?.position || !g.index) continue;
            Figurhaut.merken(g);
            aus.push({ schluessel: netz.name || `stueck_${aus.length}`, netz,
                       punkte: g.attributes.position.array, dreiecke: g.userData.indexVoll.index });
        }
        return aus;
    }

    /** Der volle Index — einmal gemerkt, bevor je gekürzt wurde. */
    static merken(geo) {
        if (geo.userData.indexVoll) return geo.userData.indexVoll;
        geo.userData.indexVoll = {
            index: geo.index.array.slice(),
            gruppen: geo.groups.map((g) => ({ start: g.start, count: g.count,
                                              materialIndex: g.materialIndex })),
        };
        return geo.userData.indexVoll;
    }

    static indexSetzen(geo, index, gruppen) {
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        geo.clearGroups();
        for (const g of gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
    }

    static _anzahl(maske) {
        let n = 0;
        for (let i = 0; i < maske.length; i++) n += maske[i];
        return n;
    }
}
