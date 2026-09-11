import * as THREE from 'three';
import { Hautmaske } from '../gemeinsam/hautmaske.js';
import { Lagenmaske } from '../gemeinsam/lagenmaske.js';
import { Hautmaskegeometrie } from '../gemeinsam/hautmaskegeometrie.js';
import { Hauteinzug } from '../gemeinsam/hauteinzug.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Spurhaut — die Haut unter der Kleidung einer Studio-Figur wird nicht
 * gezeichnet, und Stoff unter Stoff auch nicht.
 *
 * ANLASS (Edgar, 11.09.2026): „die haut ist immer noch sichtbar im BVH
 * Studio, spiele die Animation ab." Die Maske vom selben Tag lief nur in
 * der Szene (`scene/hautverdeckung.js`, `scene/lagenverdeckung.js`, am
 * `Stueckereignis`); das Studio baut seine Figur selbst (`Spurfigur`,
 * `Spurzubehoer`) und zeichnete den ganzen Körper — in Bewegung kam die
 * Haut an Bund, Schritt und Knie durch die Leggings wie vorher in der Szene.
 *
 * Dieselbe Rechnung (`gemeinsam/hautmaske.js`, `lagenmaske.js`, Einzug der
 * Randdreiecke über `gemeinsam/hauteinzug.js`), nur die Figur ist anders
 * gebaut: Körper ist `spur.mesh`, die Stücke hängen direkt in `spur.group`
 * und tragen `userData.isGarment` (GarmentCode aus `Garmentcodestueck`,
 * MakeHuman-Stücke aus `Spurzubehoer._anhaengen`); Haare nicht — sie sind
 * kein Stoff und liegen ohnehin über der Haut.
 *
 * WANN: einmal nach dem Bau der Figur (`Spurfigur.laden`, auch im Vorlade-
 * Weg). Die Geometrien liegen dann in Ruhelage im selben Raum; das Skinning
 * kommt erst beim Abspielen, und der Einzug läuft im Shader VOR dem Skinning
 * mit. Der volle Index bleibt in `geometry.userData.indexVoll`, wie in der
 * Szene.
 */
export class Spurhaut {

    static anwenden(spur) {
        const koerper = spur?.mesh;
        const geo = koerper?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Spurhaut.merken(geo);
        const stoffe = Spurhaut.stoffe(spur);
        if (!stoffe.length) return null;
        const t0 = performance.now();
        const voll = geo.userData.indexVoll;
        const maske = Hautmaske.verdeckt(geo.attributes.position.array, voll.index, stoffe);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
        Spurhaut.indexSetzen(geo, neu.index, neu.gruppen);
        geo.userData.hautVerdeckt = maske;
        Hauteinzug.setzen(koerper, maske, voll.index);
        const stand = { verdeckt: Spurhaut._anzahl(maske), dreiecke: neu.entfernt,
                        stuecke: stoffe.length, lagen: [] };
        if (stoffe.length > 1) stand.lagen = Spurhaut._lagen(geo, stoffe);
        stand.ms = Math.round(performance.now() - t0);
        Protokoll.debug('BVH Studio', `Hautmaske ${spur.name}: ${stand.verdeckt} Punkte unter `
            + `${stoffe.length} Stücken, ${stand.dreiecke} Dreiecke weg, ${stand.ms} ms`);
        return stand;
    }

    /** Stoff unter Stoff: je Stück der gekürzte Index und der Einzug. */
    static _lagen(geo, stoffe) {
        const koerper = { punkte: geo.attributes.position.array, dreiecke: geo.userData.indexVoll.index };
        const ergebnis = Lagenmaske.verdeckt(koerper, stoffe);
        const N = Hautmaskegeometrie.normalen(koerper.punkte, koerper.dreiecke);
        const gitter = Hautmaskegeometrie.punktgitter(koerper.punkte, Hautmaskegeometrie.ZELLE_M);
        const lagen = [];
        for (const s of stoffe) {
            const { maske, ueber } = ergebnis.get(s.schluessel);
            if (!ueber.length) continue;
            const voll = s.netz.geometry.userData.indexVoll;
            const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
            Spurhaut.indexSetzen(s.netz.geometry, neu.index, neu.gruppen);
            s.netz.geometry.userData.lagenVerdeckt = maske;
            Spurhaut._einzug(s.netz, maske, koerper, N, gitter);
            lagen.push({ stueck: s.schluessel, unter: ueber, verdeckt: Spurhaut._anzahl(maske),
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
    static stoffe(spur) {
        const aus = [];
        for (const netz of spur.group?.children || []) {
            const g = netz?.geometry;
            if (!netz.isMesh || !netz.userData?.isGarment || !g?.attributes?.position || !g.index) continue;
            Spurhaut.merken(g);
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

// Für Messungen aus der Konsole.
window.__spurhaut = Spurhaut;
