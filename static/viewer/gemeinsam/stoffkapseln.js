import * as THREE from 'three';
import { Kapselmass } from './kapselmass.js';
import { Kleidungsmass } from './kleidungsmass.js';
import { Stoffkoerper } from './stoffkoerper.js';
import { Koerperzuordnung } from './koerperzuordnung.js';

/**
 * Stoffkapseln — der Körper für den Stoffschwung, als Kapseln um die Knochen,
 * und die Häutung auf der CPU (`Stoffhaut`), die dieselbe Rechnung macht wie
 * Threes Vertex-Shader (`bindMatrix`, `boneMatrices`, `bindMatrixInverse`).
 *
 * WARUM KAPSELN: Der Stoff muss je Bild gegen den Körper prüfen — 75.977
 * Punkte des Dancing-Queen-Kleids gegen 104.480 Hautpunkte wäre je Bild ein
 * Nächste-Nachbar-Lauf. Eine Kapsel je Knochen (Achse Kopf→Mittel seiner
 * Knochenkinder, Radius aus der Haut der Hautpunkte, die dieser Knochen am
 * stärksten hält) ist 20–30 Prüfungen je Punkt, mit Hülle davor.
 * Knochen mit weniger als `MINDESTPUNKTE` Hautpunkten (Finger, Gesicht) oder
 * Radius unter `MINDESTRADIUS` bleiben weg; höchstens `HOECHSTENS` Kapseln.
 *
 * KONISCH, MEDIAN, KINDERMITTEL (19.09.2026, Edgar: „Hose (genesis) animiert
 * nicht"): In Daz' Idle blähte die Angie-Jeans an Ursula 12–19 cm auf. Ohne
 * Kapseln folgte sie der gehäuteten Lage auf 5,6 mm (max 33 mm), mit den
 * alten Kapseln (EIN Radius, 85. Perzentil, Achse zum ERSTEN Kind) lag sie
 * 36 mm daneben (max 120): `l_thightwist1` bekam 12 cm über die ganze Länge —
 * am Knie ist der Schenkel halb so dick —, und `pelvis → l_thigh` läuft
 * schief nach links, sodass der rechte Hüftpunkt 15 cm „Radius" ergab.
 * Jetzt: Achse zum Mittel der Knochenkinder, je Ende zwei Halbachsen quer
 * zum Knochen (Hauptachsen der Hautpunkte, `Kapselmass.ellipse`), dazwischen
 * linear; die erste Hauptachse `u` liegt im Knochenraum und dreht mit
 * (`bild`). Rund mit Median gemessen: 8,7 mm / max 65 mm, aber 2,4 % der
 * Jeanspunkte bis 19 mm in der Haut — die Ellipse trifft beide Seiten.
 */
export class Stoffkapseln {

    static MINDESTPUNKTE = 200;
    static MINDESTRADIUS = 0.02;
    static HOECHSTENS = 32;
    /**
     * Nur GLIEDMASSEN bekommen eine Kapsel (Daz: l_thigh, l_thightwist1, l_shin, l_foot,
     * l_toes, l_upperarm, l_forearm, l_hand, Finger; Rigify: DEF-thigh_L, DEF-shin_L,
     * DEF-foot_L, DEF-upper_arm_L, DEF-forearm_L, DEF-hand_L, DEF-f_…). Rumpf, Becken
     * und Kopf hält seit dem 20.09.2026 die Haut selbst (`Stoffoberflaeche`): Ein Rumpf
     * ist keine Ellipse, und die Kugelkappen der Wirbelsegmente (Rigify: DEF-spine_001…003,
     * Radien 11–14 cm) standen aus dem Rücken heraus und schoben die Punkte des Oberteils
     * je Bild in verschiedene Richtungen. Gemessen (HumanBody, Idle, Browser): mit
     * Rumpfkapseln Kantendehnung p99 3,22, ohne 1,79; Haut −0,7 mm in beiden Fällen.
     * Gliedmaßen brauchen die Kapsel weiter: ein Bein zieht beim Sprung 10 cm je Bild
     * durch den Rock, die Haut (Reichweite 5 cm) sähe die Punkte erst dahinter.
     * UMA (25.09.2026): `LeftUpLeg`, `LeftLeg`, `LeftArm` — `UpLeg|Leg$|Arm$`; die
     * `*Adjust`-Hilfsknochen enden anders und bleiben draußen.
     */
    static GLIEDER = /thigh|shin|foot|toe|upperarm|upper_arm|forearm|hand|shldr|shoulder|f_|thumb|index|mid|ring|pinky|carpal|UpLeg|Leg$|Arm$/i;
    /** Die Achse spannt die Hautpunkte auf — ohne die äußersten 2 % je Ende. */
    static RAND = 0.02;

    /** Einmal je Skelett: Maße aus dem Körpernetz. `[{bone, kinder, u (Knochenraum), ta, tb, rua, rwa, rub, rwb}]`. */
    static anlegen(inst) {
        const netz = inst.bodyMesh;
        if (!netz?.isSkinnedMesh || !netz.skeleton) return [];
        const bones = netz.skeleton.bones;
        const welt = Stoffhaut.welt(netz);
        const n = netz.geometry.attributes.position.count;
        // Der stärkste Knochen je Hautpunkt — dieselbe Zuordnung, die
        // `Oberflaechenbindung` für die Gruppen der Kleidungspunkte nutzt.
        const zuordnung = Koerperzuordnung.staerksterKnochen(netz);
        const a = new THREE.Vector3(), b = new THREE.Vector3(), q = new THREE.Vector3();
        const d = new THREE.Vector3(), e1 = new THREE.Vector3(), e2 = new THREE.Vector3(), o = new THREE.Vector3();
        const aus = [];
        bones.forEach((bone, nummer) => {
            if (!Stoffkapseln.GLIEDER.test(bone.name)) return;
            const kinder = Stoffkapseln.achsenkinder(bone);
            if (!kinder.length) return;
            bone.getWorldPosition(a); Stoffkapseln.mittel(kinder, b, q);
            Stoffkapseln.basis(a, b, d, e1, e2);
            // Projektion auf die Achse (Meter ab a) — die Kapsel reicht zum Kopf
            // hin so weit wie die Haut des Knochens (`spine1` hält den Bauch
            // nicht, `pelvis` schon), zum Kind hin höchstens bis zum Kind: Über
            // die Schenkelköpfe hinaus verlängert stand die Pelvis-Kapsel im
            // Schritt und drückte die Jeans dort 19 cm heraus (19.09.2026).
            const lauf = [], x1 = [], x2 = [];
            for (let i = 0; i < n; i++) {
                if (zuordnung[i] !== nummer) continue;
                o.set(welt[3 * i], welt[3 * i + 1], welt[3 * i + 2]).sub(a);
                lauf.push(o.dot(d)); x1.push(o.dot(e1)); x2.push(o.dot(e2));
            }
            if (lauf.length < Stoffkapseln.MINDESTPUNKTE) return;
            const ta = Math.min(0, Kapselmass.perzentil(lauf, Stoffkapseln.RAND));
            const tb = Math.min(a.distanceTo(b), Kapselmass.perzentil(lauf, 1 - Stoffkapseln.RAND));
            if (tb - ta < 1e-3) return;
            const anteile = lauf.map((l) => (l - ta) / (tb - ta));
            const m = Kapselmass.ellipse(x1, x2, anteile);
            if (Math.max(m.rua, m.rwa, m.rub, m.rwb) < Stoffkapseln.MINDESTRADIUS) return;
            // u in den Knochenraum — dreht dann mit dem Knochen (`bild`).
            const u = e1.clone().multiplyScalar(Math.cos(m.theta)).addScaledVector(e2, Math.sin(m.theta));
            u.applyQuaternion(bone.getWorldQuaternion(new THREE.Quaternion()).invert());
            aus.push({ bone, kinder, u, ta, tb, rua: m.rua, rwa: m.rwa, rub: m.rub, rwb: m.rwb,
                       punkte: lauf.length, gruppe: Koerperzuordnung.gruppenindex(bone.name) });
        });
        aus.sort((x, y) => y.punkte - x.punkte);
        return aus.slice(0, Stoffkapseln.HOECHSTENS);
    }

    /**
     * Die Knochenkinder, zu deren Mittel die Achse zeigt. Setzt ein Kind die Kette
     * fort (Rigify: `DEF-spine` → `DEF-spine_001`), zählt nur dieses: `DEF-spine`
     * hat fünf Kinder (Becken links/rechts, beide Schenkel, die Wirbelsäule), ihr
     * Mittel liegt 7 cm vom Kopf, und die Kapsel war ein Kegel von 1,6 cm Radius
     * am Kopf - das Becken hatte keinen Körper, der Rock fiel hinein (HumanBody,
     * Idle: Haut −38 mm, gemessen 20.09.2026). Daz' Namen kennen keine
     * Fortsetzung, dort bleibt es beim Mittel aller Kinder.
     */
    static achsenkinder(bone) {
        const kinder = bone.children.filter(k => k.isBone);
        const kette = kinder.find(k => k.name === bone.name + '_001' || k.name === bone.name + '.001');
        return kette ? [kette] : kinder;
    }

    /** Achse `d` = b − a (Einheit) und eine Basis `e1`, `e2` senkrecht dazu. */
    static basis(a, b, d, e1, e2) {
        d.subVectors(b, a).normalize();
        e1.set(0, 1, 0);
        if (Math.abs(d.dot(e1)) > 0.9) e1.set(1, 0, 0);
        e1.crossVectors(d, e1).normalize();
        e2.crossVectors(d, e1);
    }

    /** Das Mittel der Weltlagen der Knochenkinder in `ziel`. */
    static mittel(kinder, ziel, q) {
        ziel.set(0, 0, 0);
        for (const k of kinder) ziel.add(k.getWorldPosition(q));
        return ziel.divideScalar(kinder.length);
    }

    /** Die Kapseln dieses Bildes in Weltkoordinaten, flach (13 je Kapsel, `Stoffkoerper.lesen`). */
    static bild(kapseln) {
        const v = new THREE.Vector3(), q = new THREE.Vector3(), dreh = new THREE.Quaternion();
        const je = Stoffkoerper.JE_KAPSEL, aus = new Float32Array(kapseln.length * je);
        const a = new THREE.Vector3(), d = new THREE.Vector3();
        kapseln.forEach((k, i) => {
            const o = je * i;
            k.bone.getWorldPosition(a); Stoffkapseln.mittel(k.kinder, v, q); d.subVectors(v, a).normalize();
            v.copy(a).addScaledVector(d, k.ta); aus[o] = v.x; aus[o + 1] = v.y; aus[o + 2] = v.z;
            v.copy(a).addScaledVector(d, k.tb); aus[o + 3] = v.x; aus[o + 4] = v.y; aus[o + 5] = v.z;
            v.copy(k.u).applyQuaternion(k.bone.getWorldQuaternion(dreh)); aus[o + 6] = v.x; aus[o + 7] = v.y; aus[o + 8] = v.z;
            aus[o + 9] = k.rua; aus[o + 10] = k.rwa; aus[o + 11] = k.rub; aus[o + 12] = k.rwb;
        });
        return aus;
    }

    /**
     * Gruppen-ID je Kapsel (`Koerperzuordnung.GRUPPEN`, 0 = keine) — parallel
     * zu `bild()`, für den Gruppenfilter der Oberflächenbindung
     * (`oberflaecheglsl.js`): eine Kapsel bewegt nur Punkte FREMDER Gruppen.
     */
    static gruppen(kapseln) {
        return Float32Array.from(kapseln, (k) => k.gruppe || 0);
    }
}

/** Häutung auf der CPU, Ergebnis in WELTkoordinaten (Float32Array n·3). */
export class Stoffhaut {

    static _m = new THREE.Matrix4();
    static _bind = new THREE.Matrix4();
    /** Rasterweite (m) der Stichprobe für `Stoffoberflaeche`: ein Hautpunkt je Zelle der Ruhelage.
     *  2,5 cm: auf einem Schenkel (Radius 10 cm) weicht die Sehne zwischen zwei Proben 0,8 mm von
     *  der Haut ab - genau genug, und der Worker prüft je Stoffpunkt ein Drittel der Hautpunkte
     *  gegenüber 1,5 cm (Node: `oberflaeche.hinaus` 22 ms → siehe pendel_zeit2). */
    static STICHPROBE_ZELLE = 0.025;

    /**
     * Eine Stichprobe des Körpernetzes für den Worker (`Stoffoberflaeche`): je Rasterzelle
     * der Ruhelage der erste Punkt, mit Normale und Hautgewichten - 8–12k statt 70–104k.
     * null ohne Normalen oder Haut. `{n, pos, nrm, index, gewicht}` (Float32Arrays).
     */
    static stichprobe(netz, zelle = Stoffhaut.STICHPROBE_ZELLE) {
        const a = netz?.geometry?.attributes;
        if (!netz?.isSkinnedMesh || !a?.normal || !a.skinIndex || !a.skinWeight) return null;
        const pos = a.position.array, nrm = a.normal.array, si = a.skinIndex.array, sw = a.skinWeight.array;
        const gesehen = new Set(), wahl = [];
        for (let i = 0; i < a.position.count; i++) {
            const k = Math.floor(pos[3 * i] / zelle) + ',' + Math.floor(pos[3 * i + 1] / zelle) + ',' + Math.floor(pos[3 * i + 2] / zelle);
            if (gesehen.has(k)) continue;
            gesehen.add(k); wahl.push(i);
        }
        const n = wahl.length, aus = { n, pos: new Float32Array(n * 3), nrm: new Float32Array(n * 3),
                                       index: new Float32Array(n * 4), gewicht: new Float32Array(n * 4) };
        wahl.forEach((i, j) => {
            for (let k = 0; k < 3; k++) { aus.pos[3 * j + k] = pos[3 * i + k]; aus.nrm[3 * j + k] = nrm[3 * i + k]; }
            for (let k = 0; k < 4; k++) { aus.index[4 * j + k] = si[4 * i + k]; aus.gewicht[4 * j + k] = sw[4 * i + k]; }
        });
        // HumanBodys feines Netz trägt Normalen nach INNEN (gegen die eigenen Flächen gewickelt,
        // beidseitiges Material - siehe `Kleidungsmass.auswaerts`); als Körper zog es den Rock
        // in den Bauch. Deshalb nach außen drehen, bevor die Stichprobe zum Worker geht.
        aus.auswaerts = Kleidungsmass.auswaerts(aus.pos, aus.nrm, n);
        return aus;
    }

    /** Je Knochen die Matrix `bindMatrixInverse · matrixWorld · boneInverse · bindMatrix`, als 16er-Block. */
    static matrizen(netz) {
        const { bones, boneInverses } = netz.skeleton;
        const aus = new Float32Array(bones.length * 16);
        const m = Stoffhaut._m, bind = Stoffhaut._bind;
        for (let i = 0; i < bones.length; i++) {
            m.multiplyMatrices(bones[i].matrixWorld, boneInverses[i]);
            bind.multiplyMatrices(m, netz.bindMatrix);
            m.multiplyMatrices(netz.bindMatrixInverse, bind);
            aus.set(m.elements, 16 * i);
        }
        return aus;
    }

    /** Gehäutete Punkte in der Welt (`netz.matrixWorld` obendrauf). */
    static welt(netz, ziel = null) {
        const pos = netz.geometry.attributes.position.array;
        const index = netz.geometry.attributes.skinIndex.array;
        const gewicht = netz.geometry.attributes.skinWeight.array;
        const n = netz.geometry.attributes.position.count;
        const M = Stoffhaut.matrizen(netz);
        const W = netz.matrixWorld.elements;
        const aus = ziel || new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            let sx = 0, sy = 0, sz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
            }
            aus[3 * i] = W[0] * sx + W[4] * sy + W[8] * sz + W[12];
            aus[3 * i + 1] = W[1] * sx + W[5] * sy + W[9] * sz + W[13];
            aus[3 * i + 2] = W[2] * sx + W[6] * sy + W[10] * sz + W[14];
        }
        return aus;
    }
}
