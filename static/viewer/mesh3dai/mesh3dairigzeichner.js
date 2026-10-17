/**
 * Mesh3dairigzeichner — das Genesis-9-Rig (138 Knochen: Becken bis Zehen, Finger, Gesicht) als Überlagerung auf der Seite „Mesh3D-AI" (14.10.2026).
 * Edgar: „ich möchte das volle Skelett mit allen Gesichts- und Handknochen" und „Rig soll ein Toggle-Button sein für alle Ansichten": der Knopf „Rig" jeder Zeile legt diese Zeichnung über JEDE Ansichtsart
 * (Oberfläche, Drahtnetz, Textur …). Gezeichnet werden Kugeln an den Knochenpunkten und Rohre vom Elternknochen zum Knochen — als zwei `InstancedMesh` (zwei Zeichenaufrufe statt Hunderter Netze: bei der Animation
 * wird jedes Bild neu gebaut), ohne Tiefentest, damit das Rig auch IM Körper zu sehen ist.
 * Soll: Farbe nach Gruppe (Rumpf, Arm, Hand, Finger, Bein, Fuß, Zehen, Gesicht); Ausgabe des Netzes: Kugeln nach dem Fehler je Knochen (grün 0 mm bis rot ab `fehler_rot_mm`), Rohre orange.
 * Die Punkte (`lagen`) liegen im Koordinatensystem der Zeile (Gesicht um die Kopfmitte, Hände und Füße in ihren Ausschnitten — `Mesh3dairig.zeilen` auf dem Server); `massstab` verkleinert Kugeln und Rohre für die Ausschnitte.
 */
import * as THREE from 'three';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3daikapseln } from './mesh3daikapseln.js';

export class Mesh3dairigzeichner {
    static GRUPPENFARBE = { rumpf: 0xffd166, kopf: 0xffd166, gesicht: 0xf78fb3, arm: 0x6ee7b7, hand: 0x7dd3fc, finger: 0x7dd3fc, bein: 0xa5b4fc, fuss: 0xfcd34d, zehen: 0xfcd34d };
    /** Kugelradius je Gruppe in m (am ganzen Körper gemessen; Ausschnitte verkleinert `massstab`). */
    static KUGELRADIUS = { rumpf: 0.010, kopf: 0.010, arm: 0.009, hand: 0.007, bein: 0.010, fuss: 0.008, finger: 0.0045, zehen: 0.0045, gesicht: 0.0040 };
    static ROHRRADIUS = 0.0025;

    /** Das Rig der Zeile über das Bild legen, wenn der Knopf „Rig" an ist — in allen drei Feldern. Im Start (dem Netz) liegt das Rig, das Mesh3D-AI für dieses Netz vorhersagt, gefärbt nach dem Abstand
     *  zum Ziel-Rig wie im Ergebnis (16.10.2026, Edgar: „im Mesh ist kein rig“; bis dahin das Rig aus „Mesh to 3D“, nur für neun Proben von Ursula1 — „ich brauche keine Meshto3d Aufträge, sondern Mesh3dAI“).
     *  `d`: `{rig, rigBeschreibung, rigIndizes, rigMassstab, teil}`. */
    static ueberlagern(inhalt, art, d) {
        const rig = d.teil?.rig;
        // Der Knopf „Rig“ schaltet das Rig in Soll UND Ausgabe, auch bei echten Daten (Edgar, 15.10.2026: „toggle button rig funktioniert nicht im Ergebnis fenster“ — dort war es fest an).
        if (!d.rig || !rig?.soll || !d.rigBeschreibung || !d.rigIndizes) return;
        // Zwischenbild „Rig → A-Pose“ (17.10.2026): das Skelett der Rig-Figur in Ruhe (alle 138, Reihenfolge des Rigs) in den Farben der Gruppen, darüber in Orange, wohin das Netz der Vorstufe die Gelenke
        // HIER in der A-Pose schiebt (`netz`) — das ist die ganze Arbeit des Netzes; Ziel und Ergebnis zeigen danach dieselben Gelenke zurück in der Haltung.
        if (art === 'apose') {
            const a = d.probe?.aposeDaten;
            if (a?.rig) inhalt.add(Mesh3dairigzeichner.zeichnen(d.rigBeschreibung, d.rigIndizes, d.rigIndizes.map(j => a.rig[j]), { massstab: d.rigMassstab ?? 1 }));
            if (a?.netz) inhalt.add(Mesh3dairigzeichner.zeichnen(d.rigBeschreibung, d.rigIndizes, d.rigIndizes.map(j => a.netz[j]), { massstab: 0.7 * (d.rigMassstab ?? 1), farbe: Mesh3daikapseln.AUSGABEFARBE }));
            return;
        }
        if (art === 'eingabe') {
            if (rig.ausgabe) inhalt.add(Mesh3dairigzeichner.zeichnen(d.rigBeschreibung, d.rigIndizes, rig.ausgabe, { je_mm: rig.je_mm, massstab: d.rigMassstab ?? 1 }));
            return;
        }
        inhalt.add(Mesh3dairigzeichner.zeichnen(d.rigBeschreibung, d.rigIndizes, art === 'soll' ? rig.soll : rig.ausgabe,
            { je_mm: art === 'soll' ? null : rig.je_mm, massstab: d.rigMassstab ?? 1 }));
    }

    /**
     * @param {{knochen: {name: string, eltern: number, gruppe: string}[], fehler_rot_mm: number}} beschreibung das Rig (`antwort.rig`)
     * @param {number[]} indizes die Knochen dieser Zeile (`antwort.rig.zeilen[schluessel]`)
     * @param {number[][]} lagen ihre Punkte, gleiche Reihenfolge wie `indizes`
     * @param {{je_mm?: number[]|null, massstab?: number, farbe?: number|null}} opt `je_mm`: Fehler je Knochen (Ausgabe des Netzes), sonst Gruppenfarben; `massstab`: Größe von Kugeln und Rohren;
     *        `farbe`: eine Farbe für alles (der Geist des Soll bei echten Daten, `Mesh3daiechtzeichner`)
     */
    static zeichnen(beschreibung, indizes, lagen, { je_mm: jeMm = null, massstab = 1, farbe: eineFarbe = null } = {}) {
        const z = Mesh3dairigzeichner;
        const knochen = beschreibung.knochen;
        const platz = new Map(indizes.map((j, k) => [j, k]));
        // Geometrie und Material sind für alle Bilder gleich (nur die Stellung je Instanz ändert sich) — geteilt, nicht je Bild neu (`Mesh3daigemeinsam`).
        const material = Mesh3daigemeinsam.material('rig', () => new THREE.MeshBasicMaterial({ depthTest: false, transparent: true, opacity: 0.95 }));
        const kugeln = new THREE.InstancedMesh(Mesh3daigemeinsam.geometrie('rigkugel', () => new THREE.SphereGeometry(1, 8, 6)), material, indizes.length);
        const paare = indizes.map((j, k) => [k, platz.get(knochen[j].eltern)]).filter(([, e]) => e !== undefined);
        const rohre = new THREE.InstancedMesh(Mesh3daigemeinsam.geometrie('rigrohr', () => new THREE.CylinderGeometry(1, 1, 1, 5)), material, Math.max(paare.length, 1));
        const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), a = new THREE.Vector3(), b = new THREE.Vector3(), farbe = new THREE.Color();
        const hoch = new THREE.Vector3(0, 1, 0);
        const orange = new THREE.Color(Mesh3daikapseln.AUSGABEFARBE);
        indizes.forEach((j, k) => {
            const g = knochen[j].gruppe;
            const r = (z.KUGELRADIUS[g] ?? 0.008) * massstab;
            kugeln.setMatrixAt(k, m.compose(a.fromArray(lagen[k]), q.identity(), s.set(r, r, r)));
            if (eineFarbe !== null) kugeln.setColorAt(k, farbe.set(eineFarbe));
            else kugeln.setColorAt(k, jeMm ? farbe.copy(Mesh3daikapseln.fehlerfarbe(jeMm[k], beschreibung.fehler_rot_mm)) : farbe.set(z.GRUPPENFARBE[g] ?? 0xffffff));
        });
        paare.forEach(([k, e], i) => {
            a.fromArray(lagen[k]);
            b.fromArray(lagen[e]);
            const richtung = new THREE.Vector3().subVectors(a, b);
            const laenge = Math.max(richtung.length(), 1e-4);
            const r = z.ROHRRADIUS * massstab;
            rohre.setMatrixAt(i, m.compose(b.clone().add(a).multiplyScalar(0.5), q.setFromUnitVectors(hoch, richtung.normalize()), s.set(r, laenge, r)));
            if (eineFarbe !== null) rohre.setColorAt(i, farbe.set(eineFarbe));
            else rohre.setColorAt(i, jeMm ? orange : farbe.set(z.GRUPPENFARBE[knochen[indizes[k]].gruppe] ?? 0xffffff));
        });
        rohre.count = paare.length;
        const gruppe = new THREE.Group();
        for (const teil of [rohre, kugeln]) {
            teil.instanceMatrix.needsUpdate = true;
            if (teil.instanceColor) teil.instanceColor.needsUpdate = true;
            teil.frustumCulled = false;
            teil.renderOrder = 20;
            gruppe.add(teil);
        }
        return gruppe;
    }
}
