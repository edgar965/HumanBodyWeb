import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { pushUndo } from './undo.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Spurabbau — eine Spur samt allem, was an ihr hängt, entfernen.
 *
 * Herausgelöst aus `tracks.js` (324 Zeilen). Löschen ist hier kein Einzeiler:
 * An einer Spur hängen Mischer, Netz, Werkstoffe, Lichtquelle, Helferlinien,
 * Tonkanal und ein Szenenobjekt — jedes davon belegt Grafikspeicher, den erst
 * `dispose()` freigibt. `remove()` allein nimmt es nur aus dem Bild.
 *
 * **Szenen-Elemente sind geschützt** (`_sceneItem`, z. B. der Boden): Sie kommen
 * beim nächsten Aufbau ohnehin wieder — nur ohne ihre Einstellungen.
 * Szenen-LICHTER dürfen weg; dann muss aber die Referenz in `state` fallen,
 * sonst legt der Szenenaufbau sie sofort neu an.
 */
export class Spurabbau {

    /** Szenenlicht-Felder in `state`, die auf eine Lichtquelle zeigen. */
    static LICHTFELDER = ['sceneKeyLight', 'sceneFillLight', 'sceneBackLight',
                          'sceneAmbient'];

    static entfernen(index) {
        if (index < 0 || index >= state.project.tracks.length) return;
        pushUndo('Track löschen');
        const spur = state.project.tracks[index];
        if (spur._sceneItem) {
            Protokoll.warnung('BVH Studio',
                              `Szenen-Element "${spur.name}" kann nicht `
                              + 'gelöscht werden.');
            return;
        }
        Spurabbau._modellspur(spur);
        Spurabbau._mischer(spur);
        Spurabbau._netz(spur);
        state.scene.remove(spur.group);
        spur.group = null;
        Spurabbau._licht(spur);
        if (spur.type === 'audio') fn.stopAudioTrack(spur);
        Spurabbau._objekt(spur);
        Spurabbau._nachziehen(index);
    }

    /** Eine Modellspur nimmt die Figur ihrer Animationsspur mit aus dem Bild. */
    static _modellspur(spur) {
        if (spur.type !== 'model') return;
        const animation = state.project.getLinkedAnimation(spur);
        if (animation?.group) animation.group.visible = false;
    }

    static _mischer(spur) {
        if (spur.mixer) {
            spur.mixer.stopAllAction();
            spur.mixer = null;
        }
        spur._activeClip = null;
        spur._activeAction = null;
    }

    static _netz(spur) {
        if (!spur.mesh) return;
        spur.group.remove(spur.mesh);
        spur.mesh.geometry?.dispose();
        Spurabbau._werkstoffeWeg(spur.mesh.material);
        spur.mesh = null;
    }

    static _werkstoffeWeg(werkstoff) {
        if (!werkstoff) return;
        if (Array.isArray(werkstoff)) werkstoff.forEach(einer => einer.dispose?.());
        else werkstoff.dispose?.();
    }

    static _licht(spur) {
        if (spur.light) {
            if (spur.light.target) state.scene.remove(spur.light.target);
            state.scene.remove(spur.light);
            spur.light.dispose();
            if (spur._sceneLight) {
                for (const feld of Spurabbau.LICHTFELDER) {
                    if (state[feld] === spur.light) state[feld] = null;
                }
            }
        }
        if (!spur.lightHelper) return;
        state.scene.remove(spur.lightHelper);
        spur.lightHelper.traverse?.(teil => {
            teil.geometry?.dispose?.();
            Spurabbau._werkstoffeWeg(teil.material);
        });
    }

    static _objekt(spur) {
        if (spur.type !== 'scene_object' || !spur.mesh) return;
        state.scene.remove(spur.mesh);
        spur.mesh.traverse?.(teil => {
            teil.geometry?.dispose?.();
            Spurabbau._werkstoffeWeg(teil.material);
        });
    }

    static _nachziehen(index) {
        state.project.removeTrackAt(index);   // zieht `_linkedAnimIdx` nach
        if (state.selectedTrackIdx >= state.project.tracks.length) {
            state.selectedTrackIdx = state.project.tracks.length - 1;
        }
        state.selectedClipIdx = -1;
        fn.updateTrackHeaders();
        fn.updateProperties();
        fn.renderTimeline();
    }
}
