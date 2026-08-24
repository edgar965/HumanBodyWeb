import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Audiospur — eine Tondatei in eine Audiospur legen.
 *
 * Herausgelöst aus `tracks.js` (324 Zeilen). Dieselbe Arbeit stand ein zweites
 * Mal in `zeitleiste_spurmenue.js` (Menü „Clip hinzufügen") — dekodieren,
 * Clip bauen, hochladen, Zeitleiste neu zeichnen. Beide Wege laufen jetzt hier
 * zusammen; sie unterscheiden sich nur in drei Werten:
 *
 *                        Knopf „Audio laden"     Menü „Clip hinzufügen"
 *     Clip-Länge         ganze Datei             10 Sekunden
 *     `audioDuration`    ganze Datei             höchstens 10 Sekunden
 *     Rückgängig         nein (wie bisher)       „Audio-Clip hinzufügen"
 *
 * Die Datei wird ZWEIMAL gebraucht: im Browser dekodiert (nur so kennt das
 * Studio die Länge und kann den Ton mitlaufen lassen) und auf dem Server
 * abgelegt (der dekodierte Puffer lebt nur im Speicher — ohne die Adresse wäre
 * der Ton nach dem nächsten Seitenaufruf weg und fehlte im Videoexport).
 *
 * Scheitert der Upload, bleibt der Clip trotzdem: Hören geht, Speichern nicht.
 * Das ist besser als eine Spur, die wegen eines Netzfehlers gar nicht entsteht.
 */
export class Audiospur {

    static HOCHLADEN = '/api/studio/audio-upload/';

    /** Dateiauswahl öffnen und die gewählte Datei einlegen. */
    static dateiWaehlen(spurIndex, wahl = {}) {
        const spur = state.project.tracks[spurIndex];
        if (!spur || spur.type !== 'audio') return;
        const feld = document.createElement('input');
        feld.type = 'file';
        feld.accept = 'audio/*';
        feld.addEventListener('change',
                              () => Audiospur.einlegen(spur, feld.files[0], wahl));
        feld.click();
    }

    /**
     * @param {Object} spur   die Audiospur
     * @param {File} datei    die gewählte Datei
     * @param {Object} wahl   {startbild, bilder, hoechstdauer, undoText}
     */
    static async einlegen(spur, datei, wahl = {}) {
        if (!datei) return;
        let puffer;
        try {
            puffer = await spur.audioCtx.decodeAudioData(await datei.arrayBuffer());
        } catch (fehler) {
            Protokoll.fehler('BVH Studio', 'Audio nicht lesbar', fehler);
            alert('Audio laden fehlgeschlagen: ' + fehler.message);
            return;
        }
        if (wahl.undoText) pushUndo(wahl.undoText);
        spur.clips.push(await Audiospur._clip(datei, puffer, wahl));
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        Protokoll.debug('BVH Studio',
                        `Audio loaded: ${datei.name} `
                        + `(${puffer.duration.toFixed(1)}s)`);
    }

    static async _clip(datei, puffer, wahl) {
        const bilder = wahl.bilder
            ?? Math.round(puffer.duration * state.project.fps);
        const clip = new Clip(null, datei.name, bilder, state.project.fps);
        clip.type = 'audio';
        clip.startFrame = wahl.startbild ?? state.playheadFrame;
        clip.data = {
            fileName: datei.name,
            audioBuffer: puffer,
            audioDuration: wahl.hoechstdauer
                ? Math.min(wahl.hoechstdauer, puffer.duration) : puffer.duration,
            volume: 1.0, fadeIn: 0, fadeOut: 0, offset: 0,
        };
        clip.data.audioUrl = await Audiospur._hochladen(datei);
        return clip;
    }

    /** Die Datei auf den Server legen; `undefined`, wenn das misslingt. */
    static async _hochladen(datei) {
        const formular = new FormData();
        formular.append('audio', datei);
        try {
            const antwort = await Serverabruf.formular(Audiospur.HOCHLADEN,
                                                       formular);
            if (antwort.ok) {
                Protokoll.debug('BVH Studio', `Audio uploaded: ${antwort.url}`);
                return antwort.url;
            }
            Protokoll.warnung('BVH Studio', 'Audio upload failed:', antwort.error);
        } catch (fehler) {
            Protokoll.warnung('BVH Studio', 'Audio upload error:', fehler);
        }
        return undefined;
    }
}
