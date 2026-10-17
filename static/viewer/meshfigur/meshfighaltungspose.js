import * as THREE from 'three';
import { Dazachsen } from '../gemeinsam/dazachsen.js';
import { Genesis9drehknochen } from '../gemeinsam/genesis9drehknochen.js';
import { Genesis9felder } from '../gemeinsam/genesis9felder.js';
import { Genesis9gelenke } from '../gemeinsam/genesis9gelenke.js';

/**
 * Meshfighaltungspose — die Knochen der Figur in der HALTUNG des Netzes, gerechnet im Browser (14.10.2026).
 *
 * WARUM: Die Objekte aus dem Netz (Robe, Hut, Stab …) liegen in der Haltung des Netzes unverändert vor (`teil_*_haltung.glb`, Netzpunkte im Raum der gebackenen Figur). In die Ruhelage (A-Pose) zurückgerechnet
 * werden sie verzerrt — bei weiten Gewändern fächerförmig (`mesh-3d-bestandteile.md`), und ein gehaltener Stab sitzt dort nicht mehr in der Faust (die Hand hat sich gegen die Haltung gedreht). Wer die Objekte
 * stattdessen an die Haltung BINDET — Hautmatrix = Knochen in der Bewegung × Umkehrung der Knochen in der Haltung —, spart das Zurückrechnen: der Stoff steht im Bild 0 des Netzes genau so, wie er im Netz steht,
 * und jede Bewegung verformt ihn von dort aus; der Stab behält die Lage zur Hand, in der die Faust ihn greift.
 *
 * WIE: Aus der Ruhe und den Daz-Winkeln der Haltung (`ergebnis.haltung.drehung`, dieselben, mit denen der Server die Figur backt) wird das Skelett vorwärts gerechnet: Winkel → lokale Drehung
 * (`Dazachsen.quaternion`, wie bei der Gelenkkorrektur und den Visemes), danach die Twist-Knochen (`Genesis9drehknochen`). Gemessen am Zauberer (14.10.2026): alle 16 geprüften Gelenke liegen gegen die vom Server
 * gebackene Haltungsfigur auf 0 mm in x und z und konstant 16 mm in y — der Boden: der Server hebt die Figur, bis ihr tiefster Punkt auf 0 steht (`G9formung.boden`). `boden` ist hier das Maß, um das die gebackene
 * Figur (und damit die Objekte der Haltung) tiefer liegen als die Vorwärtsrechnung; es wird am Körper in der Haltung gemessen.
 */
export class Meshfighaltungspose {

    static _achsen = new WeakMap();         // skelett.skeleton -> Promise<{knochen, drehknochen} | null>
    static _posen = new WeakMap();          // skelett.skeleton -> {schluessel, inverse, boden}

    /** Schrittweite beim Messen des tiefsten Punkts am Körper (jeder n-te Punkt; die Füße sind groß genug). */
    static BODEN_SCHRITT = 3;

    /** Die Daz-Achsen aller Knochen des Skeletts (sie kommen mit den Feldern der Gelenkkorrekturen, die die Gelenke ohnehin laden) und die Twist-Knochen — einmal je Skelett. */
    static achsen(inst) {
        const skeleton = inst.skelett.skeleton;
        let versprechen = Meshfighaltungspose._achsen.get(skeleton);
        if (!versprechen) {
            versprechen = Genesis9felder.holen(Genesis9gelenke.GRUPPE, inst.stufen).then(felder => {
                if (!felder) return null;
                const knochen = Dazachsen.vorbereiten(inst.skelett, felder.achsen);
                return { knochen, drehknochen: Genesis9drehknochen.vorbereiten(knochen, felder.achsen) };
            });
            Meshfighaltungspose._achsen.set(skeleton, versprechen);
        }
        return versprechen;
    }

    /**
     * `{inverse: Matrix4[], boden}` für `inst` in der Haltung `drehung` (`{knochen: {'rotation/x': Grad, …}}`) — `inverse[i]` zu `skeleton.bones[i]`; null, solange die Achsen nicht da sind.
     * Das Ergebnis wird je Skelett und Haltung gemerkt. Die Bewegung der Knochen bleibt unberührt (Lage, Drehung und Maßstab werden zurückgesetzt).
     */
    static fuer(inst, drehung) {
        const skeleton = inst.skelett.skeleton;
        const schluessel = JSON.stringify(drehung);
        const alt = Meshfighaltungspose._posen.get(skeleton);
        if (alt && alt.schluessel === schluessel) return alt;
        return Meshfighaltungspose.achsen(inst).then(achsen => {
            if (!achsen) return null;
            const neu = { schluessel, ...Meshfighaltungspose.berechnen(inst, achsen, drehung) };
            Meshfighaltungspose._posen.set(skeleton, neu);
            return neu;
        });
    }

    /** Wie `fuer`, aber nur, wenn die Haltung schon gerechnet ist (sonst null) — für den Takt. */
    static gemerkt(inst, drehung) {
        const p = Meshfighaltungspose._posen.get(inst.skelett.skeleton);
        return p && p.schluessel === JSON.stringify(drehung) ? p : null;
    }

    static berechnen(inst, achsen, drehung) {
        const skeleton = inst.skelett.skeleton;
        const gemerkt = skeleton.bones.map(b => ({ p: b.position.clone(), q: b.quaternion.clone(), s: b.scale.clone() }));
        skeleton.pose();
        const euler = new THREE.Euler(), q = new THREE.Quaternion(), r = Math.PI / 180;
        for (const [name, kanaele] of Object.entries(drehung)) {
            const k = achsen.knochen[name];
            if (!k) continue;
            euler.set((kanaele['rotation/x'] || 0) * r, (kanaele['rotation/y'] || 0) * r, (kanaele['rotation/z'] || 0) * r, k.order);
            q.setFromEuler(euler);
            k.bone.quaternion.copy(k.Ainv).multiply(q).multiply(k.Binv);
        }
        Genesis9drehknochen.takt(achsen.drehknochen);
        inst.group.updateMatrixWorld(true);
        // Die Umkehrmatrizen eines Skeletts liegen in der Lage der FIGURGRUPPE (`Knochenbau`), nicht in der Welt: erst die Gruppe herausrechnen.
        const gruppeInv = new THREE.Matrix4().copy(inst.group.matrixWorld).invert();
        const inverse = skeleton.bones.map(b => b.matrixWorld.clone().premultiply(gruppeInv).invert());
        const boden = Meshfighaltungspose._boden(inst);
        skeleton.bones.forEach((b, i) => { b.position.copy(gemerkt[i].p); b.quaternion.copy(gemerkt[i].q); b.scale.copy(gemerkt[i].s); });
        inst.group.updateMatrixWorld(true);
        return { inverse, boden };
    }

    /** Der tiefste Punkt des Körpers in der gerade gestellten Haltung (m) — um so viel steht die Vorwärtsrechnung höher als die gebackene Figur (Füße auf 0). */
    static _boden(inst) {
        const koerper = inst.bodyMesh;
        if (!koerper?.isSkinnedMesh) return 0;
        koerper.skeleton.update();
        const p = new THREE.Vector3();
        const n = koerper.geometry.attributes.position.count;
        let tiefster = Infinity;
        for (let i = 0; i < n; i += Meshfighaltungspose.BODEN_SCHRITT) {
            koerper.getVertexPosition(i, p);
            if (p.y < tiefster) tiefster = p.y;
        }
        return Number.isFinite(tiefster) ? tiefster : 0;
    }
}
