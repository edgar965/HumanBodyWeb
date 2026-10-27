/**
 * Mesh3dailinienzeichner — die Messlinien der Regler-KI (27.10.2026, Edgar: „Zeig mir den Input, den Output und die ganzen Linien, die du errechnet hast“), gezeichnet wie die Messpunkte der
 * 2d-3d-AI (`Ai2d3dmesspunkte.FARBE`; Edgar: „blau ist die Vorlage, schwarz das Ergebnis und rote Linien zwischen den zusammengehörenden schwarzen und blauen Punkten, damit man die Abweichung
 * sieht“): blau = wo die Linie die Wolke trifft (Vorlage), schwarz = der Figurpunkt (Ergebnis), rot = Verbindung, grau = Figurpunkt, an dem nichts gefunden wurde.
 * Paket `…/linien/<nr>/` (Server `Mesh3dailinien`). Geometrie und Material tragen `userData.gemeinsam`: die Felder geben ihren Inhalt bei jedem Zeichnen frei, Geometrie und Material bleiben;
 * jedes Feld bekommt ein eigenes Objekt darauf (ein three.js-Objekt hängt nur in EINER Szene).
 */
import * as THREE from 'three';

/** Wie `Ai2d3dmesspunkte.FARBE` (vorlage, ergebnis_linie, offen, verbindung). */
export const FARBE = { vorlage: 0x1c7ed6, ergebnis: 0x000000, offen: 0x868e96, verbindung: 0xe03131, wolke: 0xdfe3ea };

const gemeinsam = m => {
    m.userData.gemeinsam = true;
    return m;
};
const punkt = (farbe, extra = {}) => gemeinsam(new THREE.PointsMaterial({ color: farbe, size: 0.006, sizeAttenuation: true, ...extra }));
const MATERIAL = {
    wolke: punkt(FARBE.wolke, { size: 0.005, transparent: true, opacity: 0.35, depthWrite: false }),
    vorlage: punkt(FARBE.vorlage),
    ergebnis: punkt(FARBE.ergebnis),
    offen: punkt(FARBE.offen),
    verbindung: gemeinsam(new THREE.LineBasicMaterial({ color: FARBE.verbindung })),
};

export class Mesh3dailinienzeichner {
    /** Paket → {kopf, daten: {Name: Float32Array | Uint8Array}} (Sichten auf den Puffer, jeder Block beginnt auf einem Vielfachen von 4). */
    static paket(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        const daten = {};
        let ab = 4 + laenge;
        for (const [name, typ, n] of kopf.bloecke) {
            daten[name] = typ === 'f4' ? new Float32Array(puffer, ab, n) : new Uint8Array(puffer, ab, n);
            ab += typ === 'f4' ? n * 4 : Math.ceil(n / 4) * 4;
        }
        return { kopf, daten };
    }

    static _geometrie(lage) {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        g.userData.gemeinsam = true;
        return g;
    }

    /** Punkte (Float32Array, je 3) der Linien, deren Klasse `wahl(klasse)` erfüllt → geteilte Geometrie. */
    static punkte(lage, klasse, wahl) {
        const aus = [];
        for (let i = 0; i < klasse.length; i++) if (wahl(klasse[i])) aus.push(lage[3 * i], lage[3 * i + 1], lage[3 * i + 2]);
        return Mesh3dailinienzeichner._geometrie(new Float32Array(aus));
    }

    /** Je gewählter Linie ein Strich vom Figurpunkt (ort) zum Treffer auf der Wolke (ende). */
    static verbindung(ort, ende, klasse, wahl) {
        const aus = [];
        for (let i = 0; i < klasse.length; i++) {
            if (!wahl(klasse[i])) continue;
            aus.push(ort[3 * i], ort[3 * i + 1], ort[3 * i + 2], ende[3 * i], ende[3 * i + 1], ende[3 * i + 2]);
        }
        return Mesh3dailinienzeichner._geometrie(new Float32Array(aus));
    }

    static wolke(lage) {
        return Mesh3dailinienzeichner._geometrie(lage);
    }

    /** art: 'wolke' | 'vorlage' | 'ergebnis' | 'offen' → Punkte auf der geteilten Geometrie; 'verbindung' → Striche. */
    static objekt(art, geometrie) {
        return art === 'verbindung' ? new THREE.LineSegments(geometrie, MATERIAL.verbindung) : new THREE.Points(geometrie, MATERIAL[art]);
    }
}
