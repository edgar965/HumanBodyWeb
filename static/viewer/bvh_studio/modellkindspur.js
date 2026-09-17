import { state, TRACK_COLORS } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Track } from './models.js';
import { pushUndo } from './undo.js';
import { Mimikbasis } from './mimikbasis.js';
import { Spurerzeugung } from './spurerzeugung.js';

/**
 * Modellkindspur — eine Spur, die an einer Modellspur hängt (`_modellIdx`)
 * und eingerückt darunter steht: Mimik und Script.
 *
 * Anlegen und Suchen standen in `mimikspur.js` und `scriptspur.js` gleich
 * (Befund `doppelcode`, 17.09.2026); die Spurarten unterscheiden sich nur
 * in `type`, Farbe und Namensvorsatz. Was DANACH geschieht (Script zur
 * ersten Mimikspur), bleibt bei der jeweiligen Klasse.
 */
export class Modellkindspur {

    /**
     * Die Spur der Art `art` zur Modellspur `modellIdx` — oder null.
     * @param {number} modellIdx
     * @param {'mimik'|'script'} art
     */
    static zuModell(modellIdx, art) {
        return state.project.tracks.find(s => s.type === art && s._modellIdx === modellIdx) || null;
    }

    /**
     * Eine neue Spur der Art `art` unter der Modellspur anlegen und wählen.
     * @param {number} modellIdx
     * @param {'mimik'|'script'} art
     * @param {string} vorsatz  Namensvorsatz („Mimik", „Script")
     * @param {string} undoText Beschriftung des Undo-Schritts
     * @param {string|null} name  eigener Name, sonst `<vorsatz> <Modellname>`
     */
    static anlegen(modellIdx, art, vorsatz, undoText, name = null) {
        pushUndo(undoText);
        const modell = state.project.tracks[modellIdx];
        const spur = new Track(name || `${vorsatz} ${modell?.name || ''}`.trim());
        spur.type = art;
        spur.color = TRACK_COLORS[art];
        spur._modellIdx = modellIdx;
        Mimikbasis.laden().then(() => fn.applyPlayhead());
        return Spurerzeugung.einhaengen(spur);
    }
}
