import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _swapToPreloaded } from './vorladen.js';

/**
 * Modellspur — welche Figur (welches Preset) am Abspielkopf gilt.
 *
 * Herausgelöst aus `spur_anwenden.js` (288 Zeilen). Eine Modellspur steuert die
 * Figur einer VERKNÜPFTEN Bewegungsspur: Der Nutzer legt auf der Zeitleiste fest,
 * ab wann welche Figur zu sehen ist.
 *
 * WARUM DAS LADEN SO UMSICHTIG IST
 * ================================
 * Ein Preset zu laden dauert (Netz, Gewichte, Kleidung). In der Zwischenzeit kann
 * der Abspielkopf weiterlaufen und ein anderes Preset gelten. Deshalb:
 *
 * * `_loadingPreset` merkt, WORAUF gewartet wird. Kommt ein Ergebnis für ein
 *   anderes Preset zurück, wird es verworfen (`preset_load_superseded`) — sonst
 *   erscheint eine Figur, die längst nicht mehr gilt.
 * * Während des Ladens ist die Gruppe unsichtbar. Ohne das blitzt die ALTE Figur
 *   auf, sobald die Sichtbarkeit sonst berechnet wird.
 * * Vorgeladene Presets (`_preloadCache`) kommen über `_swapToPreloaded` — der
 *   Tausch geschieht dann ohne Ladezeit.
 */
export class Modellspur {

    static anwenden(spur, zeit) {
        const bewegung = state.project.getLinkedAnimation(spur);
        if (!bewegung) return;
        const preset = Modellspur._aktives(spur, zeit);
        if (bewegung._loadingPreset) {
            // Warten: Die alte Figur darf nicht auftauchen.
            if (bewegung.group) bewegung.group.visible = false;
            return;
        }
        if (preset === bewegung.meshActive) {
            if (bewegung.group) bewegung.group.visible = !!preset;
            return;
        }
        if (bewegung.group) bewegung.group.visible = false;
        if (!preset) {
            bewegung.meshActive = null;
            return;
        }
        Modellspur._laden(bewegung, preset);
    }

    /** Das Preset des Clips, der `zeit` enthält — oder `null`. */
    static _aktives(spur, zeit) {
        for (const clip of spur.clips) {
            if (clip.type !== 'model') continue;
            const beginn = clip.startFrame / state.project.fps;
            if (zeit >= beginn && zeit < beginn + clip.duration) {
                return clip.data?.preset || null;
            }
        }
        return null;
    }

    static _laden(bewegung, preset) {
        const vorgeladen = bewegung._preloadCache?.[preset];
        if (vorgeladen) {
            Modellspur._ausCache(bewegung, preset, vorgeladen);
            return;
        }
        bewegung._loadingPreset = preset;
        bewegung.preset = preset;
        if (bewegung.group) bewegung.group.visible = false;
        fn.serverLog('preset_load_start',
                     `track=${bewegung.name} preset=${preset}`);
        fn.loadTrackCharacter(bewegung)
            .then(() => Modellspur._fertig(bewegung, preset))
            .catch(fehler => Modellspur._gescheitert(bewegung, preset, fehler));
    }

    static _ausCache(bewegung, preset, vorgeladen) {
        bewegung._loadingPreset = preset;
        Promise.resolve(vorgeladen).then(teile => {
            if (bewegung._loadingPreset !== preset) return;   // überholt
            _swapToPreloaded(bewegung, teile, preset);
        }).catch(fehler => Modellspur._gescheitert(bewegung, preset, fehler));
    }

    static _fertig(bewegung, preset) {
        if (bewegung._loadingPreset !== preset) {
            fn.serverLog('preset_load_superseded',
                         `track=${bewegung.name} preset=${preset} `
                         + `now=${bewegung._loadingPreset}`);
            return;
        }
        bewegung._loadingPreset = null;
        if (!bewegung.mesh) {
            fn.serverLog('preset_load_no_mesh',
                         `track=${bewegung.name} preset=${preset}`);
            return;
        }
        if (bewegung.group) bewegung.group.visible = true;
        // Der laufende Clip gilt nicht mehr: Das Skelett ist ein neues.
        bewegung._activeClip = null;
        bewegung._activeAction = null;
        bewegung.meshActive = preset;
        fn.serverLog('preset_load_done',
            `track=${bewegung.name} preset=${preset} mesh=${!!bewegung.mesh} `
            + `skel=${!!bewegung.skeleton} mix=${!!bewegung.mixer} `
            + `meshSkel=${!!bewegung.mesh?.skeleton} `
            + `bones=${bewegung.skeleton?.skeleton?.bones?.length || '?'}`);
    }

    static _gescheitert(bewegung, preset, fehler) {
        bewegung._loadingPreset = null;
        fn.serverLog('preset_load_failed',
                     `track=${bewegung.name} preset=${preset} err=${fehler.message}`);
    }
}
