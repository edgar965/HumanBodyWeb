import * as THREE from 'three';
import { Eigenkleidwerte } from './eigenkleidwerte.js';

/**
 * Eigenkleidtreffer — eigene Stücke im View anklickbar machen (Edgar, 26.10.2026: „wenn ich auf das Eigen T-Shirt klicke, soll das Tab aufgehen, wo das selektiert ist
 * (so wie bei den anderen Assets)“ — „es wird immer nur das Genesis-Modell ausgewählt“).
 *
 * Die SCHALE (Oberteil, Hose, Socken, Oberteil des Kleids) hat die Geometrie der Haut, ihre Form entsteht erst im Shader — ein Raycast gegen sie träfe genau die Haut.
 * Darum fragt ihr Raycast den KÖRPER und behält nur Treffer, die das Stück deckt: Körperkoordinaten des getroffenen Punkts (`kkKoord`, dieselbe Punktnummer wie die
 * Haut) gegen die Säume des Stücks (`Eigenkleidwerte.shaderwerte`). Der Treffer zählt `VOR_M` vor der Haut — so wählt `Trefferwahl` das Stück, wie bei Stoff über Haut.
 * Ausschnitt und Kragen sind nicht nachgebildet (grob genug für die Wahl, nicht für eine Messung). Der ROCK (`Eigenrock`) ist echte Geometrie: gewöhnlicher Raycast mit
 * Häutung, ohne Suchbaum — `Raycastbeschleunigung` überginge das Drapieren (die Punkte ändern sich, der Baum nicht).
 *
 * Beide Netze tragen `userData.eigenerRaycast`; `Raycastbeschleunigung.sicherstellen` lässt sie dann in Ruhe.
 */
export class Eigenkleidtreffer {

    static VOR_M = 0.002;
    static SCHLUESSEL = 'eigen_';

    /** Den Raycast an das Netz einer Schale hängen. `stueck`: das `Eigenkleid` (koerper, art, werte). */
    static schale(netz, stueck) {
        netz.userData.eigenerRaycast = true;
        netz.raycast = function (raycaster, treffer) {
            const koerper = stueck.koerper, kk = this.geometry?.attributes?.kkKoord;
            if (!koerper?.parent || !kk) return;
            const roh = [];
            koerper.raycast(raycaster, roh);
            for (const t of roh) {
                if (t.face && Eigenkleidtreffer.deckt(stueck.art, stueck.werte, kk, t.face.a)) {
                    treffer.push({ ...t, object: this, distance: t.distance - Eigenkleidtreffer.VOR_M });
                }
            }
        };
    }

    /** Den Raycast des Rocks: gehäutet, ohne Suchbaum. */
    static rock(netz) {
        netz.userData.eigenerRaycast = true;
        netz.raycast = THREE.SkinnedMesh.prototype.raycast;
    }

    /** Deckt das Stück den Hautpunkt `i`? Kette 1 Rumpf (Höhe 0 Halsansatz … 1 Schritt), 2/3 Arm, 4/5 Bein (Anteil 0 Hüfte … 1 Knöchel), 10/11 Fuß. */
    static deckt(art, werte, kk, i) {
        const saum = Eigenkleidwerte.shaderwerte(art, werte).saum;
        const kette = Math.round(kk.getX(i)), anteil = kk.getY(i), hoehe = kk.getZ(i);
        const bein = kette === 4 || kette === 5;
        if (art === 'hose') return (kette === 1 && hoehe >= saum[0]) || (bein && anteil <= saum[1]);
        if (art === 'socke') return (bein && anteil >= saum[0]) || kette === 10 || kette === 11;
        return (kette === 1 && hoehe >= 0 && hoehe <= saum[0]) || ((kette === 2 || kette === 3) && anteil <= saum[1]);
    }

    /**
     * Die eigenen Stücke einer Figur als Teilnetz-Ziele (`getSelectableSubMeshes`): je Netz ein Ziel, beim Kleid Schale UND Rock mit demselben Schlüssel
     * (`eigen_<art>`, `Reiterzuordnung` → Reiter „Assets“). `stueck(inst, art)`: `Eigenkleider.stueck`.
     */
    static ziele(inst, charId, stueck) {
        const aus = [];
        for (const art of Eigenkleidwerte.getragen(inst)) {
            const s = stueck(inst, art);
            for (const netz of [s?.netz, s?.rock?.netz]) {
                if (netz?.parent) aus.push({ type: 'eigen', key: Eigenkleidtreffer.SCHLUESSEL + art, label: Eigenkleidwerte.ARTEN[art].titel, meshObj: netz, charId });
            }
        }
        return aus;
    }
}
