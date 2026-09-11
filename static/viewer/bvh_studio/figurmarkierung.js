import * as THREE from 'three';
import { state } from './state.js';

/**
 * Figurmarkierung — die gewählte Figur im Bild als gewählt zeigen.
 *
 * ANLASS (Edgar, 11.09.2026): „wenn ich auf ein Modell in der Szene klicke,
 * soll es in der Timeline ausgewählt werden, umgekehrt auch, wenn ich das in
 * der Timeline auswähle, soll es im View als ausgewählt erscheinen."
 *
 * Gewählt ist eine SPUR (`state.selectedTrackIdx`). Eine Figur gehört zur
 * Animationsspur (`spur.group`, `spur.mesh`); die Modellspur stellt sie über
 * die Verknüpfung. Beide Spuren zeigen darum dieselbe Figur als gewählt.
 *
 * DER RAHMEN FOLGT DER BEWEGUNG: ein Kasten um die Knochen des Skeletts
 * (Weltlage je Bild, plus `RAND_M` fürs Fleisch). Der Kasten der Geometrie
 * (`Box3.setFromObject`) stünde bei Wurzelbewegung am Ladeort, während die
 * Figur davonläuft; die genaue Fassung (`precise`) rechnete je Bild über
 * jeden Punkt des Netzes.
 *
 * Kein Zustand außer dem Helfer: Je Bild wird aus der Auswahl neu
 * entschieden. So überstehen Spurlöschung, Projektwechsel und Vorlagentausch
 * ohne Nachziehen an anderer Stelle.
 */
export class Figurmarkierung {

    static FARBE = 0xffb347;
    static RAND_M = 0.12;
    static _helfer = null;
    static _box = new THREE.Box3();
    static _punkt = new THREE.Vector3();

    /** Die Figur (Animationsspur mit Netz), die zur Spur gehört — sonst null. */
    static figur(spur) {
        if (!spur) return null;
        const bewegung = spur.type === 'model' ? state.project.getLinkedAnimation(spur)
                       : (spur.type === 'bvh' ? spur : null);
        if (!bewegung?.group || !bewegung.mesh || bewegung.group.visible === false) return null;
        return bewegung;
    }

    /** Je Bild: Rahmen an die gewählte Figur legen oder verbergen. */
    static nachziehen() {
        const spur = state.project?.tracks?.[state.selectedTrackIdx] || null;
        const figur = Figurmarkierung.figur(spur);
        if (!figur) {
            if (Figurmarkierung._helfer) Figurmarkierung._helfer.visible = false;
            return;
        }
        Figurmarkierung.umfassen(figur, Figurmarkierung._box);
        Figurmarkierung._anzeigen().visible = true;
    }

    /** Kasten um die Knochen (folgt der Bewegung); ohne Skelett um die Gruppe. */
    static umfassen(figur, box) {
        const knochen = figur.mesh?.skeleton?.bones;
        box.makeEmpty();
        if (knochen?.length) {
            for (const k of knochen) {
                box.expandByPoint(k.getWorldPosition(Figurmarkierung._punkt));
            }
            box.expandByScalar(Figurmarkierung.RAND_M);
        } else {
            box.setFromObject(figur.group);
        }
        return box;
    }

    static _anzeigen() {
        let helfer = Figurmarkierung._helfer;
        if (!helfer) {
            helfer = new THREE.Box3Helper(Figurmarkierung._box, Figurmarkierung.FARBE);
            helfer.name = 'figurmarkierung';
            helfer.userData.isSelectionFrame = true;
            helfer.raycast = () => {};   // nie selbst getroffen (Alt+Klick, Auswahl)
            Figurmarkierung._helfer = helfer;
        }
        // Die Szene kann neu aufgebaut worden sein (Projekt laden).
        if (helfer.parent !== state.scene) state.scene.add(helfer);
        return helfer;
    }
}
