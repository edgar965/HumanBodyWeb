import { THREE } from './state.js';
import { state } from './state.js';

/**
 * Greifgeometrie — die Three.js-Seite des Greifens: Bezugsebene, Schnittpunkt
 * des Zeigerstrahls, Bildmitte der Figur und das Umlegen einer Bewegung auf
 * den Boden.
 *
 * Aus `greifen.js` herausgelöst (06.09.2026), als die Datei über 300 Zeilen
 * ging. `Greifen` steuert den Ablauf, hier steht das Rechnen mit der Szene;
 * die Entscheidungen ohne Three.js liegen daneben in
 * `gemeinsam/greifrechnung.js`.
 */
export class Greifgeometrie {

    /** Darunter zeigt die Kamera senkrecht nach unten: dann gibt es kein „weg". */
    static MIN_WAAGRECHT = 1e-6;

    /**
     * Die Ebene, auf der gemessen wird: quer zur Kamera, durch den Punkt, an
     * dem die Figur beim Start stand. Sie ist immer gut zu treffen — anders
     * als der Boden, den eine fast waagrechte Kamera erst in 34 m Entfernung
     * schneidet (gemessen am 06.09.2026: Kamera auf 1 m, Blick-y −0,03).
     */
    static ebene(weltStart, achse) {
        const normale = state.camera.getWorldDirection(new THREE.Vector3()).negate();
        return new THREE.Plane().setFromNormalAndCoplanarPoint(normale, weltStart);
    }

    /**
     * Eine Bewegung in der Bildebene auf den Boden legen: seitwärts bleibt
     * seitwärts, hoch heißt weiter weg. Die Höhe bleibt, wie sie war.
     *
     * WARUM: Figuren stehen. Wer eine zur Seite schiebt, will sie nicht
     * nebenbei ein paar Zentimeter anheben — beim ersten Versuch kamen
     * −0,31 m heraus, weil die Kamera fast waagrecht schaut und „Maus hoch"
     * dort geradewegs nach oben zeigt. Wer die Höhe meint, drückt Y.
     */
    static aufDenBoden(roh) {
        const rechts = new THREE.Vector3().setFromMatrixColumn(state.camera.matrixWorld, 0);
        const oben = new THREE.Vector3().setFromMatrixColumn(state.camera.matrixWorld, 1);
        const seitlich = roh.dot(rechts), hoch = roh.dot(oben);
        const rechtsFlach = rechts.clone().setY(0);
        const vornFlach = state.camera.getWorldDirection(new THREE.Vector3()).setY(0);
        if (rechtsFlach.lengthSq() < Greifgeometrie.MIN_WAAGRECHT
            || vornFlach.lengthSq() < Greifgeometrie.MIN_WAAGRECHT) {
            // Senkrecht von oben: die Bildebene IST schon der Boden.
            return { x: roh.x, y: 0, z: roh.z };
        }
        const v = rechtsFlach.normalize().multiplyScalar(seitlich)
            .add(vornFlach.normalize().multiplyScalar(hoch));
        return { x: v.x, y: 0, z: v.z };
    }

    /** Wo der Zeigerstrahl die Ebene trifft; null, wenn er sie verfehlt. */
    static aufDerEbene(ebene, punkt) {
        const r = state.canvas.getBoundingClientRect();
        const zeiger = new THREE.Vector2(((punkt.x - r.left) / r.width) * 2 - 1,
                                         -((punkt.y - r.top) / r.height) * 2 + 1);
        const strahl = new THREE.Raycaster();
        strahl.setFromCamera(zeiger, state.camera);
        const treffer = new THREE.Vector3();
        return strahl.ray.intersectPlane(ebene, treffer) ? treffer : null;
    }

    /**
     * Die Figurmitte in Bildschirmkoordinaten — Bezug für Drehen und Größe.
     *
     * Gemeint ist die Mitte des KÖRPERS, nicht der Ursprung der Gruppe: der
     * liegt zwischen den Füßen, und damit war die Größenänderung nicht zu
     * bedienen. Gemessen am 06.09.2026 stand er bei y = 1111 von 1218 Bildpunkten,
     * also ganz unten; die Maus nach rechts zu ziehen machte die Figur KLEINER,
     * weil sie sich dabei dem Fußpunkt näherte.
     */
    static mitteImBild(objekt) {
        const r = state.canvas.getBoundingClientRect();
        const mitte = new THREE.Box3().setFromObject(objekt)
            .getCenter(new THREE.Vector3());
        const punkt = isFinite(mitte.y) ? mitte
            : objekt.getWorldPosition(new THREE.Vector3());
        const p = punkt.project(state.camera);
        return { x: r.left + (p.x * 0.5 + 0.5) * r.width,
                 y: r.top + (-p.y * 0.5 + 0.5) * r.height };
    }
}
