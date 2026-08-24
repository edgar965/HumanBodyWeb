import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bibliothekablage — Dateioperationen auf der BVH-Bibliothek.
 *
 * Herausgelöst aus `library.js` (329 Zeilen): Umbenennen, Kopieren,
 * Verschieben, Löschen, Ordner anlegen — alles über EINEN Endpunkt
 * (`/api/character/bvh-manage/`) mit einem `action`-Feld.
 *
 * WARUM `Serverabruf.senden` UND NICHT `fetch`
 * ===========================================
 * Frühere Reihenfolge war `resp.json()` vor `resp.ok`. Bei einer Fehlerseite
 * scheiterte schon das Auslesen — der Hinweis mit der Servermeldung kam nie an,
 * stattdessen stand „Unexpected token '<'" im Fenster.
 *
 * WAS BEIM LÖSCHEN MITGEHT
 * ========================
 * `clipsEntfernen` räumt die Zeitleiste auf. Eine gelöschte BVH, deren Clip
 * stehen bleibt, ist der übelste Fall: Der Clip zeigt weiter Bewegung an, beim
 * nächsten Laden ist er leer — und der Mixer hält die Animation im Speicher.
 * Deshalb auch `uncacheClip`.
 */
export class Bibliothekablage {

    static ENDPUNKT = '/api/character/bvh-manage/';

    /**
     * Eine Aktion ausführen. Liefert die Antwort oder `null` (mit Meldung).
     */
    static async senden(aktion, daten) {
        try {
            return await Serverabruf.senden(Bibliothekablage.ENDPUNKT,
                                            { action: aktion, ...daten });
        } catch (fehler) {
            alert('Fehler: ' + fehler.message);
            return null;
        }
    }

    /**
     * Alle Clips einer BVH aus allen Spuren entfernen.
     *
     * Rückgabe: Anzahl der entfernten Clips.
     */
    static clipsEntfernen(kategorie, name) {
        let entfernt = 0;
        for (const spur of state.project.tracks) {
            if (spur.type !== 'bvh') continue;
            entfernt += Bibliothekablage._spurRaeumen(spur, kategorie, name);
            if (spur.clips.length === 0 && spur.group) spur.group.visible = false;
            spur._activeClip = null;
            spur._activeAction = null;
        }
        if (entfernt > 0) Bibliothekablage._nachtragen(kategorie, name, entfernt);
        return entfernt;
    }

    static _spurRaeumen(spur, kategorie, name) {
        let entfernt = 0;
        // Von hinten: Ein `splice` beim Vorwaertslaufen ueberspringt den Nachbarn.
        for (let i = spur.clips.length - 1; i >= 0; i--) {
            const clip = spur.clips[i];
            if (clip.category !== kategorie || clip.name !== name) continue;
            if (spur.mixer) {
                spur.mixer.stopAllAction();
                // Ohne `uncacheClip` bleibt die Animation im Speicher des Mixers.
                if (clip.animClip) spur.mixer.uncacheClip(clip.animClip);
            }
            spur.clips.splice(i, 1);
            entfernt++;
        }
        return entfernt;
    }

    static _nachtragen(kategorie, name, entfernt) {
        state.selectedClipIdx = -1;
        const nochClips = state.project.tracks.some(spur => spur.clips.length > 0);
        if (!nochClips && state.playing) {
            state.playing = false;
            const zeichen = document.getElementById('pb-play-icon');
            if (zeichen) zeichen.className = 'fas fa-play';
        }
        fn.updateDuration();
        fn.renderTimeline();
        fn.updateProperties();
        Protokoll.debug('BVH Studio',
                        `Removed ${entfernt} clip(s) of ${kategorie}/${name} from tracks`);
    }
}
