import * as THREE from 'three';
import { Gezeichneterpunkt } from '../gemeinsam/gezeichneterpunkt.js';
import { Modellcheckbefunde } from './modellcheckbefunde.js';

/**
 * Modellcheckmarken — das Rot der 3D-Ansicht im Modell Check (`Modellcheck3d`; abgeteilt 02.11.2026 spätabends, als jede Zeile der Befundtabelle ihre eigene Marke
 * bekam). Je markiertem Netz ein Netz auf DENSELBEN Attributen und demselben Skelett mit den lageverändernden Eingriffen des Stoffs (`Gezeichneterpunkt.eingriffe`),
 * das nur die markierten Dreiecke zeichnet; beim Wechsel der Marke tauscht nur der Index (ein neues Netz je Wechsel gäbe beim Freigeben die geteilten Attribute im
 * Renderer frei, der Körper würde bei jedem Überfahren einer Zeile neu hochgeladen). Gelenke als Kugeln. Für EINEN Befund dazu Punkte fester Bildschirmgröße ohne
 * Tiefentest — drei Punkte eines Saums oder eine Stelle hinter dem Körper sind sonst nicht zu finden.
 */
export class Modellcheckmarken {

    static ROT = 0xff0000;
    static PUNKT_PX = 6;
    static PUNKTE_MAX = 4000;

    constructor() {
        const M = Modellcheckmarken;
        this.szene = new THREE.Scene();
        this.netze = new Map();                                             // Quelle → {netz, quelle, aktiv}
        this.kugeln = new Map();                                            // Knochen → Kugel
        this.kugelStoff = new THREE.MeshBasicMaterial({ color: M.ROT, toneMapped: false, depthTest: false });
        this.kugelNetz = new THREE.SphereGeometry(0.018, 16, 12);
        this.punkte = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: M.ROT, size: M.PUNKT_PX, sizeAttenuation: false,
            depthTest: false, toneMapped: false }));
        Object.assign(this.punkte, { frustumCulled: false, renderOrder: 10, visible: false });
        this.szene.add(this.punkte);
    }

    /** Rot, was `befunde` markieren; `mitPunkten`: dazu ihre Punkte über allem (ein einzelner Befund). */
    setzen(inst, befunde, mitPunkten = false) {
        const M = Modellcheckmarken, karte = new Map();
        for (const b of befunde) for (const [netz, liste] of b.punkte) {
            const a = karte.get(netz) || new Uint8Array(netz.geometry.attributes.position.count);
            if (liste) for (const i of liste) a[i] = 1; else a.fill(1);
            karte.set(netz, a);
        }
        for (const e of this.netze.values()) e.aktiv = false;
        for (const [quelle, marke] of karte) {
            const wahl = M.dreiecke(quelle.geometry, marke);
            if (!wahl.length) continue;
            const e = this.netze.get(quelle) || this._netz(quelle);
            e.netz.geometry.setIndex(wahl);
            e.aktiv = true;
        }
        const knochen = new Set(befunde.flatMap((b) => b.knochen || []));
        for (const k of knochen) {
            if (this.kugeln.has(k)) continue;
            const kugel = new THREE.Mesh(this.kugelNetz, this.kugelStoff);
            kugel.renderOrder = 10;
            this.szene.add(kugel);
            this.kugeln.set(k, kugel);
        }
        for (const [k, kugel] of this.kugeln) kugel.visible = knochen.has(k);
        this.punkte.geometry.dispose();
        this.punkte.geometry = new THREE.BufferGeometry();
        this.punkte.visible = false;
        if (!mitPunkten) return;
        const lagen = [];
        for (const b of befunde) for (const [netz, liste] of b.punkte) {
            if (!liste) continue;
            const schritt = Math.ceil(liste.length / M.PUNKTE_MAX);
            for (const x of Modellcheckbefunde.lagen(netz, liste.filter((_, j) => j % schritt === 0), inst)) lagen.push(x);
        }
        if (!lagen.length) return;
        this.punkte.geometry.setAttribute('position', new THREE.Float32BufferAttribute(lagen, 3));
        this.punkte.visible = true;
    }

    /** Index der Dreiecke mit mindestens einer markierten Ecke. */
    static dreiecke(g, marke) {
        const idx = g.index ? g.index.array : null, zahl = idx ? idx.length : g.attributes.position.count, wahl = [];
        for (let t = 0; t + 2 < zahl; t += 3) {
            const a = idx ? idx[t] : t, b = idx ? idx[t + 1] : t + 1, c = idx ? idx[t + 2] : t + 2;
            if (marke[a] || marke[b] || marke[c]) wahl.push(a, b, c);
        }
        return wahl;
    }

    /** Rotes Netz auf den Attributen von `quelle` (Einzug, Zuschlag, Bindung, Häutung wie das Netz). */
    _netz(quelle) {
        const g = quelle.geometry, geo = new THREE.BufferGeometry();
        for (const [name, a] of Object.entries(g.attributes)) geo.setAttribute(name, a);
        geo.morphAttributes = g.morphAttributes;
        geo.morphTargetsRelative = g.morphTargetsRelative;
        const stoff = Gezeichneterpunkt.eingriffe([quelle.material].flat()[0], new THREE.MeshBasicMaterial({ color: Modellcheckmarken.ROT, toneMapped: false,
            side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -8 }));
        const netz = quelle.isSkinnedMesh ? new THREE.SkinnedMesh(geo, stoff) : new THREE.Mesh(geo, stoff);
        if (quelle.isSkinnedMesh) { netz.bindMode = quelle.bindMode; netz.bind(quelle.skeleton, quelle.bindMatrix); }
        if (quelle.morphTargetInfluences) netz.morphTargetInfluences = quelle.morphTargetInfluences;
        Object.assign(netz, { matrixAutoUpdate: false, matrixWorldAutoUpdate: false, frustumCulled: false, renderOrder: 5 });
        this.szene.add(netz);
        const e = { netz, quelle, aktiv: false };
        this.netze.set(quelle, e);
        return e;
    }

    /** Vor jedem Bild: Lage von der Figur; Marken auf Kleidern aus, wenn der Schalter „Kleider“ aus ist. */
    vorBild(inst, kleider) {
        for (const e of this.netze.values()) {
            e.netz.matrixWorld.copy(Modellcheckbefunde.welt(e.quelle, inst));
            e.netz.visible = e.aktiv && (kleider || !Modellcheckbefunde.istKleid(e.quelle));
        }
        for (const [k, kugel] of this.kugeln) if (kugel.visible) k.getWorldPosition(kugel.position);
    }

    /** Freigeben — nur zusammen mit dem Renderer der Ansicht (die roten Netze teilen die Attribute der Figur). */
    weg() {
        for (const { netz } of this.netze.values()) { netz.geometry.dispose(); netz.material.dispose(); }
        this.kugelStoff.dispose(); this.kugelNetz.dispose();
        this.punkte.geometry.dispose(); this.punkte.material.dispose();
        this.netze.clear(); this.kugeln.clear();
    }
}
