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

    /** Ansichtsarten mit geschlossener Fläche: dort zeigt die Rückseite durchscheinend, wo die Außenfläche ein Loch hat. */
    static FLAECHENARTEN = new Set(['oberflaeche', 'oberflaeche_draht', 'textur', 'matcap', 'normalen']);
    /** Die Rückseite: Farbe der Fläche (in „Textur“ die Farbe je Punkt), sonst ein mittlerer Ton — halb durchsichtig (`DECKKRAFT`). */
    static INNEN_EINHEIT = 0x8a8a8a;
    static DECKKRAFT = 0.3;

    /**
     * Das Feld „Rig → A-Pose“ einer Probe zeichnen (`Mesh3daiechtzeichner`, Art `apose`). Edgar (17.10.2026): „es fehlen Punkte im Mesh“ — die Außenfläche trägt nur, was in der Haltung von außen zu sehen
     * war; in der A-Pose liegen diese Stellen offen. Die Rückseite der Fläche ist darum sichtbar, aber halb durchsichtig in ihrer eigenen Farbe: durch ein Loch sieht man die Innenseite gegenüber UND den Grund
     * dahinter — ein Fenster, kein Farbfleck. Erste Fassung rot (färbte die einseitigen Haarsträhnen rot, UrsulaSpagat), zweite dunkel in der eigenen Farbe: an MannLaufen standen die Löcher der Oberarme
     * (27 % der Armfläche in der Laufpose verdeckt) als braune Flecken auf der Haut, Edgar: „Mesh texturfehler“ — die Farben selbst stimmen, Dreieck für Dreieck aus der Eingabe
     * (`ProjektTemp/_wegwerf/mesh3dai_apose_ecken.py`, `mesh3dai_apose_loecher.py`).
     */
    static zeichnen(inhalt, d) {
        const a = d.probe?.aposeDaten;
        if (!a) return;
        const objekt = Mesh3daiechtmaterial.netz(a.geo, d.modus);
        objekt.traverse(o => { o.frustumCulled = false; });
        inhalt.add(objekt);
        if (Mesh3daiapose.FLAECHENARTEN.has(d.modus)) {
            const farbig = d.modus === 'textur';
            const durch = { side: THREE.BackSide, transparent: true, opacity: Mesh3daiapose.DECKKRAFT, depthWrite: false };
            const material = Mesh3daigemeinsam.material(farbig ? 'apose:durch_farbe' : 'apose:durch', () => new THREE.MeshBasicMaterial(
                farbig ? { ...durch, vertexColors: true } : { ...durch, color: Mesh3daiapose.INNEN_EINHEIT }));
            const rueck = new THREE.Mesh(a.geo, material);
            rueck.frustumCulled = false;
            rueck.renderOrder = 1;
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
        // Seit 17.10.2026 abends füllt der Schritt „apose“ die Löcher mit der Fläche der Rig-Figur (`Vorstufenluecken`); ältere Ablagen zeigen sie noch durchscheinend.
        // MeshToRigToPose_MIA schließt Löcher mit MeshLab „Close Holes“ (`Miafuellung`), nicht aus einer Figur.
        const loecher = k.methode === 'mia'
            ? ' Löcher: mit MeshLab „Close Holes“ auf der größten Insel geschlossen; kleine Stücke (Haarsträhnen) behalten nur Gewichte naher Knochen (Inselregel). '
            : k.gefuellt
            ? ` Löcher gefüllt (${de(k.gefuellt)} Dreiecke): was in der Haltung verdeckt war (die Außenfläche hat dort nichts) oder beim Zurückrechnen riss, kommt aus der Fläche der Rig-Figur — `
              + 'in der Höhe der Fläche ringsum (Kleidung, Haar), mit der Farbe der nächsten echten Stelle. Hände bleiben ungefüllt. Was noch durchscheint, ist ein Loch unter 1 cm. '
            : ' Durchscheinend: ein Loch — Fläche, die in der Haltung verdeckt war (die Außenfläche hat dort nichts) oder beim Zurückrechnen riss. ';
        // Methode (18.10.2026 abends, `Mesh3daiapose.paket` → `methode`): der Text beschreibt, was DIESER Lauf tat — vorher stand hier auch bei MIA „Figur aus Mesh to 3D“.
        const rueckfall = k.methode === 'rig' && k.weg_grund && !k.weg_grund.startsWith('Weg MIA aus') ? ` (${k.weg_grund})` : '';
        const wie = k.methode === 'mia'
            ? `${k.methode_name}: Make-It-Animatable v2 hat das Netz geriggt (Hautgewichte je Punkt, 52 Mixamo-Knochen), es damit in die T-Pose gerechnet und die Oberarme auf die Genesis-A-Pose gesenkt; `
              + `ausgerichtet und auf ${k.figur} skaliert`
            : `${k.methode_name}${rueckfall}: ein Mesh-3D-Auftrag „Nur Rig“ (${k.mesh3d}) hat eine Genesis-Figur an das Netz angepasst (SAM 3D Body + „Mesh to 3D“), jeder Punkt des Netzes folgt `
              + `ihrem Käfig in deren A-Pose; ausgerichtet und auf ${k.figur} skaliert`;
        const finger = k.methode === 'mia' ? '' : 'Die Finger dreht das Rig nicht zurück (seine Finger stehen in Ruhe): eine Faust bleibt eine Faust. ';
        return `${wie} — so bekommt das Netz der Vorstufe (${k.netz_vorstufe}) die Figur (${de(k.punkte)} Punkte, ${de(k.dreiecke)} Dreiecke).${eingabe}${loecher}`
            + `${finger}Stücke, die neben ihrem Platz liegen (etwa ein Hemdsaum), zeigen, wo das Rig nicht genau `
            + `in der Haltung des Netzes steht — diesen Fehler gleicht das Netz der Vorstufe aus. `
            + `Rig: das Skelett des Riggers in Ruhe (Farben der Gruppen); orange: wohin das Netz der Vorstufe die Gelenke hier schiebt, im Mittel ${de(k.abstand_mm, 1)} mm. Nur hier, in der A-Pose, rechnet das Netz; `
            + `Ziel und Ergebnis stehen wieder in der Haltung des Netzes, weil das Skelett DIESES Netzes gesucht ist — das Rig dreht die Korrektur Knochen für Knochen zurück.`;
    }
}
