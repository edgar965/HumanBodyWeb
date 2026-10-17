/**
 * Mesh3daiapose — das Zwischenbild „Rig → A-Pose“ auf der Jobseite von Mesh3D-AI (17.10.2026, Server `Mesh3daiapose`, `/api/mesh3dai/<job>/apose/<nr>/`).
 * Edgar: „Gegebenenfalls müsste man auf der Trainingsseite ein Zwischenbild machen. Also nicht drei Bilder, sondern vier Bilder, mit dem Rig und Bringen in die A-Position?“
 * Das Feld zwischen Start und Ziel zeigt, was das Netz der Vorstufe bekommt: die Außenfläche, mit der Figur aus „Mesh to 3D“ („Nur Rig“) in deren Ruhelage zurückgerechnet, ausgerichtet und auf die
 * trainierte Figur skaliert — in der gewählten Ansichtsart (Farbe je Punkt in „Textur“ und „Punkte“). Der Knopf „Rig“ legt das Skelett der Rig-Figur in Ruhe darüber (`Mesh3dairigzeichner.ueberlagern`).
 * Nur die Probe, auf der die Kette lief (`probe.apose`), hat das Feld; sonst bleibt es verborgen.
 */
import * as THREE from 'three';
import { Mesh3daiechtmaterial } from './mesh3daiechtmaterial.js';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';

const de = (n, s = 0) => n.toLocaleString('de-DE', { minimumFractionDigits: s, maximumFractionDigits: s });

export class Mesh3daiapose {
    /** Das Paket der Probe holen und lesen → `{kopf, geo, rig, netz}`; wirft bei 404. */
    static async holen(jobId, nr) {
        const antwort = await fetch(`/api/mesh3dai/${encodeURIComponent(jobId)}/apose/${nr}/`);
        if (!antwort.ok) throw new Error(antwort.status === 404 ? 'Zwischenbild nicht gerechnet' : `HTTP ${antwort.status}`);
        return Mesh3daiapose.lesen(await antwort.arrayBuffer());
    }

    static lesen(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        const v = kopf.punkte, f = kopf.dreiecke;
        let ab = 4 + laenge;
        const lage = new Float32Array(puffer, ab, v * 3);
        ab += v * 12;
        const dreiecke = new Uint32Array(puffer, ab, f * 3);
        ab += f * 12;
        const roh = new Uint8Array(puffer, ab, v * 3);
        // Farbe je Punkt ist sRGB (wie die Punktwolke der Eingabe) — three.js rechnet linear.
        const farbe = new Float32Array(v * 3);
        const c = new THREE.Color();
        for (let i = 0; i < v; i++) {
            c.setRGB(roh[i * 3] / 255, roh[i * 3 + 1] / 255, roh[i * 3 + 2] / 255, THREE.SRGBColorSpace);
            farbe[i * 3] = c.r;
            farbe[i * 3 + 1] = c.g;
            farbe[i * 3 + 2] = c.b;
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(farbe, 3));
        geo.setIndex(new THREE.BufferAttribute(dreiecke, 1));
        geo.computeVertexNormals();
        geo.computeBoundingSphere();
        // Die Felder entsorgen geteilte Geometrien nicht (`Mesh3daigemeinsam.freigeben`) — die Probe behält sie, solange sie geladen ist.
        geo.userData.gemeinsam = true;
        return { kopf, geo, rig: kopf.rig, netz: kopf.netz };
    }

    /** Ansichtsarten mit geschlossener Fläche: dort zeigt die Rückseite dunkel, wo die Außenfläche ein Loch hat. */
    static FLAECHENARTEN = new Set(['oberflaeche', 'oberflaeche_draht', 'textur', 'matcap', 'normalen']);
    /** Die Rückseite: Farbe der Fläche × `DUNKEL` (in „Textur“ die Farbe je Punkt), sonst ein dunkler Ton. */
    static DUNKEL = 0x4a4a4a;
    static DUNKEL_EINHEIT = 0x5b534c;

    /**
     * Das Feld „Rig → A-Pose“ einer Probe zeichnen (`Mesh3daiechtzeichner`, Art `apose`). Edgar (17.10.2026): „es fehlen Punkte im Mesh“ — die Außenfläche trägt nur, was in der Haltung von außen zu sehen
     * war; in der A-Pose liegen diese Stellen offen. Damit man durch ein Loch nicht einfach auf den Grund schaut, bekommt die Fläche eine DUNKLE Rückseite: ein Loch sieht aus wie der Blick ins Innere einer
     * hohlen Schale. Die erste Fassung (rot) färbte auch die Haarsträhnen rot — sie sind einseitige Flächen, ihre Rückseite ist kein Loch (im Chrome gesehen, UrsulaSpagat).
     */
    static zeichnen(inhalt, d) {
        const a = d.probe?.aposeDaten;
        if (!a) return;
        const objekt = Mesh3daiechtmaterial.netz(a.geo, d.modus);
        objekt.traverse(o => { o.frustumCulled = false; });
        inhalt.add(objekt);
        if (Mesh3daiapose.FLAECHENARTEN.has(d.modus)) {
            const farbig = d.modus === 'textur';
            const material = Mesh3daigemeinsam.material(farbig ? 'apose:innen_farbe' : 'apose:innen', () => new THREE.MeshBasicMaterial(
                farbig ? { vertexColors: true, color: Mesh3daiapose.DUNKEL, side: THREE.BackSide } : { color: Mesh3daiapose.DUNKEL_EINHEIT, side: THREE.BackSide }));
            const rueck = new THREE.Mesh(a.geo, material);
            rueck.frustumCulled = false;
            inhalt.add(rueck);
        }
    }

    /** Der Text unter dem Feld. */
    static text(probe) {
        if (!probe?.apose) return '';
        if (probe.aposeFehlt) return `Zwischenbild nicht geladen: ${probe.aposeFehlt}`;
        const a = probe.aposeDaten;
        if (!a) return 'Zwischenbild wird geladen …';
        const k = a.kopf;
        const eingabe = k.eingabe ? ` Eingabe: ${k.eingabe}.` : '';
        return `Die Außenfläche, mit der Figur aus „Mesh to 3D“ (Auftrag ${k.mesh3d}, „Nur Rig“) in deren A-Pose zurückgerechnet, ausgerichtet und auf ${k.figur} skaliert — so bekommt das Netz der `
            + `Vorstufe (${k.netz_vorstufe}) die Figur (${de(k.punkte)} Punkte, ${de(k.dreiecke)} Dreiecke).${eingabe} Dunkel (Blick ins Innere): ein Loch — Fläche, die in der Haltung verdeckt war (die Außenfläche hat dort nichts) oder beim Zurückrechnen riss. `
            + `Rig: das Skelett der Rig-Figur in Ruhe (Farben der Gruppen); orange: wohin das Netz der Vorstufe die Gelenke hier schiebt, im Mittel ${de(k.abstand_mm, 1)} mm. Nur hier, in der A-Pose, rechnet das Netz; `
            + `Ziel und Ergebnis stehen wieder in der Haltung des Netzes, weil das Skelett DIESES Netzes gesucht ist — das Rig dreht die Korrektur Knochen für Knochen zurück.`;
    }
}
