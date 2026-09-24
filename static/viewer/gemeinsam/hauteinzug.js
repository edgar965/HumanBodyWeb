/**
 * Hauteinzug — die verdeckten Ecken der Randdreiecke wandern im Shader
 * unter den Stoff.
 *
 * BEFUND (11.09.2026, Female1 in Dance1, Bild 32, nach der Hautmaske mit
 * anliegenden Kanten): Kein gezeichneter Körperpunkt lag mehr vor dem
 * Stoff — und am Bund standen trotzdem zwei feine weiße Splitter. Das sind
 * die Dreiecke, die die Maskengrenze ÜBERSPANNEN: eine Ecke verdeckt (unter
 * dem Stoff, bis 5 mm hinter der Bundkante), zwei davor. Sie bleiben
 * gezeichnet, weil nur Dreiecke mit drei verdeckten Ecken aus dem Index
 * fallen; ihr innerer Teil liegt unter dem Stoff und kommt in Bewegung
 * genauso heraus wie vorher die ganze Fläche.
 *
 * Alle drei Ecken zu verlangen ist richtig — sonst entstünde jenseits der
 * Stoffkante ein Loch von einer Dreieckslänge, sichtbar als dunkler Saum um
 * jeden Bund. Stattdessen bekommen die VERDECKTEN Ecken einen Einzug:
 * `EINZUG_M` entlang der Ruhenormale nach innen, als Attribut `einzug` und
 * im Vertex-Shader VOR dem Skinning addiert (`begin_vertex`), damit er
 * mit dem Knochen mitdreht. Ein Randdreieck kippt damit unter den Stoff —
 * am Bund sieht das aus wie ein Bund, der die Haut leicht eindrückt. Die
 * Geometrie bleibt unverändert: Messungen, Stoffgrenze, Export und
 * Speichern sehen davon nichts.
 *
 * Das Weichgewebe klont dasselbe Material später (`Shaderpatch.klonen`
 * nimmt den Einzug mit); ohne den gemeinsamen `Shaderpatch` löschte der
 * zweite Eingriff den ersten.
 *
 * AN DER STOFFKANTE NICHT NACH INNEN, SONDERN UNTER DIE KANTE (13.09.2026,
 * Edgar: „der Innensaum der Kleider ist eckig"): Der Einzug nach innen
 * kippt jedes Randdreieck in den Körper — von oben gesehen zeigt es seine
 * Rückseite, und am Bund stand ein Zahn je Dreieck. Verdeckte Ecken eines
 * gezeichneten Randdreiecks nahe einer Stoffkante wandern deshalb entlang
 * der Haut unter die Kante (`Saumschnitt`); der Einzug nach innen bleibt
 * für alles, was keine Kante in Reichweite hat (lockere Säume, Maskengrenzen
 * im Stoffinneren).
 *
 * HINTER DER KANTE BLEIBT EIN BAND HAUT (13.09.2026, Edgar mit Bild vom
 * Ärmel: „Offenbar wird kein Skin erzeugt unter dem T-Shirt, dann kommt
 * der Ärmel von der anderen Körperseite durch"): Verdeckte Haut bis
 * `Saumband.BAND_M` neben der gezeichneten bleibt gezeichnet, versenkt mit
 * dem Abstand — erst dahinter fallen Dreiecke aus dem Index. `setzen` gibt
 * dafür die Maske `weg` zurück, mit der der Index gekürzt wird.
 *
 * Liegt in `gemeinsam/`, weil das BVH Studio dieselbe Maske braucht
 * (`studio/spurhaut.js`, 11.09.2026).
 */
import * as THREE from 'three';
import { Shaderpatch } from './shaderpatch.js';
import { Hautmaskegeometrie } from './hautmaskegeometrie.js';
import { Saumschnitt } from './saumschnitt.js';
import { Saumband } from './saumband.js';
import { Hautdicke } from './hautdicke.js';

export class Hauteinzug {

    /** Einzug der verdeckten Ecken nach innen (Meter) — die Tiefe des Saumbands. */
    static EINZUG_M = Saumband.TIEFE_M;

    /**
     * Das `einzug`-Attribut aus der Maske setzen und die Materialien des
     * Netzes patchen. Verdeckte Punkte: −Tiefe · Normale, die Tiefe nach
     * `Saumband.tiefe` mit dem Abstand zur gezeichneten Haut — außer Ecken
     * gezeichneter Randdreiecke nahe einer Stoffkante (`optionen.kanten`,
     * Strecken): die wandern unter die Kante. `optionen.normalen` ersetzt
     * die eigenen Ruhenormalen (ein Stoff unter Stoff nimmt die der Haut).
     * `maske` null oder leer: kein Einzug, Attribut auf null.
     *
     * @returns {{gesetzt, geschnappt, band, weg}} — `weg`: je Punkt 1, wenn
     *   er verdeckt und jenseits des Saumbands liegt (für `indexOhne`);
     *   null ohne Maske.
     */
    static setzen(netz, maske, dreiecke, optionen = {}) {
        const geo = netz.geometry;
        const pos = geo.attributes.position.array;
        const n = pos.length / 3;
        const werte = new Float32Array(n * 3);
        const stand = { gesetzt: 0, geschnappt: 0, band: 0, weg: null };
        if (maske && dreiecke) {
            // Ruhenormalen nach außen (signiertes Volumen) — das
            // `normal`-Attribut des Körpers zeigt im Browser nach innen.
            const N = optionen.normalen || Hautmaskegeometrie.normalen(pos, dreiecke);
            const kanten = optionen.kanten?.length ? optionen.kanten : null;
            const gitter = kanten
                ? Hautmaskegeometrie.punktgitter(Saumschnitt.mitten(kanten), Saumschnitt.ZELLE_M) : null;
            const ecken = kanten ? Saumschnitt.randecken(maske, dreiecke) : null;
            const abstaende = Saumband.abstaende(pos, maske, dreiecke);
            // Nie tiefer als ein Teil der Körperdicke — sonst tritt ein Punkt
            // an einer dünnen Stelle drüben wieder aus (`hautdicke.js`). Nur für
            // die Haut; Stoff unter Stoff bringt die Hautnormalen mit.
            const dicken = optionen.normalen ? null : Hautdicke.dicken(pos, N, maske);
            for (let i = 0; i < n; i++) {
                if (!maske[i]) continue;
                const nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
                const schnapp = (ecken && ecken[i])
                    ? Saumschnitt.verschiebung(pos[3 * i], pos[3 * i + 1], pos[3 * i + 2],
                                               nx, ny, nz, kanten, gitter)
                    : null;
                if (schnapp) {
                    werte[3 * i] = schnapp[0]; werte[3 * i + 1] = schnapp[1]; werte[3 * i + 2] = schnapp[2];
                    stand.geschnappt += 1;
                } else {
                    const tiefe = dicken
                        ? Math.min(Saumband.tiefe(abstaende[i]), Hautdicke.grenze(dicken[i]))
                        : Saumband.tiefe(abstaende[i]);
                    werte[3 * i] = -tiefe * nx;
                    werte[3 * i + 1] = -tiefe * ny;
                    werte[3 * i + 2] = -tiefe * nz;
                }
                if (abstaende[i] <= Saumband.BAND_M) stand.band += 1;
                stand.gesetzt += 1;
            }
            stand.weg = Saumband.weg(maske, abstaende);
        }
        geo.userData.saumschnitt = stand.geschnappt;
        geo.userData.saumband = stand.band;
        const bisher = geo.getAttribute('einzug');
        if (bisher && bisher.array.length === werte.length) {
            bisher.array.set(werte);
            bisher.needsUpdate = true;
        } else {
            geo.setAttribute('einzug', new THREE.BufferAttribute(werte, 3));
        }
        Hauteinzug.patchen(netz);
        return stand;
    }

    /** Die Materialien des Netzes (eines oder ein Feld) um den Einzug ergänzen. */
    static patchen(netz) {
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) {
            if (!mat || Shaderpatch.hat(mat, 'hauteinzug')) continue;
            Shaderpatch.anhaengen(mat, 'hauteinzug', (shader) => {
                Shaderpatch.hinterInclude(shader, 'common', 'attribute vec3 einzug;');
                Shaderpatch.hinterInclude(shader, 'begin_vertex', 'transformed += einzug;');
            });
        }
    }
}
