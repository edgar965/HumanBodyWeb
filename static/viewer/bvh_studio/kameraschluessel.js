import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Kameraschluessel — eine Kameraposition auf der Zeitleiste festhalten.
 *
 * Herausgelöst aus `tracks.js` (324 Zeilen). Was gespeichert wird, ist mehr als
 * Position und Drehung, und dafür gibt es Gründe:
 *
 * * **Quaternion NEBEN den Eulerwinkeln.** Zwei Eulerwinkel können dieselbe
 *   Blickrichtung beschreiben und trotzdem verschieden sein. Wer beim Abspielen
 *   aus ihnen ein Quaternion baut, erwischt die falsche Halbkugel — die Kamera
 *   fährt dann quer durch die Szene statt auf kurzem Weg.
 * * **Der Blickpunkt** (`lookAt`, das Ziel der Umlaufsteuerung). Mit ihm kann
 *   das Abspielen Position UND Ziel getrennt überblenden und `camera.lookAt`
 *   rufen; das Motiv bleibt mittig, auch wenn Anfang und Ende weit auseinander
 *   liegen.
 * * **`fade`** entscheidet, ob zum nächsten Schlüssel überblendet wird oder ob
 *   die Kamera springt — ein harter Schnitt ist ein Gestaltungsmittel.
 */
export class Kameraschluessel {

    static VORGABE_UEBERGANG = 'smooth';    // 'linear' | 'smooth' | 'step'

    static setzen(spurIndex, bild) {
        const spur = state.project.tracks[spurIndex];
        if (!spur || spur.type !== 'camera') return;
        pushUndo('Kamera Keyframe');
        const stelle = (bild != null) ? bild : state.playheadFrame;
        const schluessel = new Clip(null,
                                    `Kameraposition ${spur.clips.length + 1}`,
                                    0, state.project.fps);
        schluessel.type = 'camera_kf';
        schluessel.startFrame = stelle;
        schluessel.data = Kameraschluessel._stand();
        spur.clips.push(schluessel);
        spur.clips.sort((a, b) => a.startFrame - b.startFrame);
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        Protokoll.info('BVH Studio',
                       `Kameraposition gespeichert bei Frame ${stelle}`);
    }

    static _stand() {
        const kamera = state.camera;
        return {
            position: Kameraschluessel._punkt(kamera.position),
            rotation: Kameraschluessel._punkt(kamera.rotation),
            quaternion: { x: kamera.quaternion.x, y: kamera.quaternion.y,
                          z: kamera.quaternion.z, w: kamera.quaternion.w },
            lookAt: state.controls?.target
                ? Kameraschluessel._punkt(state.controls.target) : null,
            fov: kamera.fov,
            interpolation: Kameraschluessel.VORGABE_UEBERGANG,
            fade: true,
        };
    }

    static _punkt(quelle) {
        return { x: quelle.x, y: quelle.y, z: quelle.z };
    }
}
