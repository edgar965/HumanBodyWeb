/**
 * Animationsstopp — die Schritte, die beim Anhalten IMMER gleich sind.
 *
 * BEFUND `doppelcode` (30.08.2026): `stopAnimation` stand zweimal da —
 * `viewer/animation.js` (eine Figur) und `scene/animation.js` (mehrere
 * Figuren). Die beiden Fassungen unterscheiden sich in genau einem Punkt:
 * WELCHES Skelett in die Ruhelage zurückgeht und welches danach als
 * Hilfslinien-Gerüst gezeichnet wird. Alles andere — die laufende Aktion
 * anhalten, den Mischer wegwerfen, die alten Hilfslinien aus der Szene
 * nehmen — war Zeile für Zeile dasselbe.
 *
 * Das Skelett bleibt deshalb bei der Seite; hier stehen nur die Schritte,
 * die von ihm nichts wissen müssen.
 */
import { Skelettanzeige } from './skelettanzeige.js';

export class Animationsstopp {

    /**
     * Die laufende Aktion anhalten und auf den Anfang zurücksetzen.
     * @param {object} zustand Seitenzustand mit `currentAction`
     * @param {boolean} verwerfen true = die Aktion wird nicht mehr gebraucht
     */
    static aktion(zustand, verwerfen) {
        if (!zustand.currentAction) return;
        zustand.currentAction.stop();
        zustand.currentAction.reset();
        if (verwerfen) zustand.currentAction = null;
    }

    /**
     * Den Mischer wegwerfen — aber nur, wenn die Animation wirklich endet.
     * Beim blossen Pausieren bleibt er stehen, sonst wäre die Zeitleiste weg.
     */
    static mischer(zustand, verwerfen) {
        if (!zustand.mixer || !verwerfen) return;
        zustand.mixer.stopAllAction();
        zustand.mixer = null;
    }

    /**
     * Die Hilfslinien der letzten Animation aus der Szene nehmen.
     *
     * BEIDE, und in dieser Reihenfolge: `skelWrapper` hält das Gerüst einer
     * BVH-Vorschau, `skeletonHelper` die Knochenlinien der Figur. Bleibt eines
     * stehen, zeichnet die nächste Animation ihr Gerüst daneben — zwei
     * Skelette im Bild, ohne Fehlermeldung.
     */
    static hilfslinien(zustand) {
        for (const name of ['skelWrapper', 'skeletonHelper']) {
            if (!zustand[name]) continue;
            zustand.scene.remove(zustand[name]);
            zustand[name] = null;
        }
    }

    /**
     * Das Knochengerüst wieder zeichnen, wenn der Nutzer es eingeschaltet hat.
     * @param {object} zustand Seitenzustand mit `rigVisible` und `scene`
     * @param {object|null} skelett Das Skelett der Seite (Figur oder Instanz)
     */
    static rigZeigen(zustand, skelett) {
        if (!zustand.rigVisible || !skelett) return;
        zustand.skeletonHelper = Skelettanzeige.bauen(zustand.scene,
                                                      skelett.rootBone);
    }
}
