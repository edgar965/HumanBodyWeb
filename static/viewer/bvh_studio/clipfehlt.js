/**
 * Clipfehlt — Clips einer BVH aus allen Bewegungsspuren nehmen.
 *
 * Zwei Anlässe, ein Weg: Die Datei wurde über die Bibliothek gelöscht
 * (`Bibliothekablage`), oder sie ist beim Laden nicht mehr da — der Retarget
 * antwortet 404 (`Clipanimation`).
 *
 * WARUM (Edgar, 13.09.2026): „bei jedem Refresh soll der Ordner neu refresht
 * werden, so dass ich nicht auf eine Animation klicken kann die es nicht
 * gibt. Falls in der Timeline etwas ist was es nicht gibt, dann entfernen."
 * Bis dahin blieb ein Clip ohne Datei rot markiert stehen (`_loadError`),
 * und der Server suchte die Datei in anderen Ordnern — der falsche Ansatz:
 * Das Projekt zeigte Bewegung aus einer Datei, die niemand genannt hatte.
 *
 * WAS BEIM ENTFERNEN MITGEHT: Ein Clip, dessen Animation im Mixer bleibt,
 * kostet Speicher und spielt womöglich weiter — deshalb `uncacheClip`. Und
 * ist kein Clip mehr übrig, hält die Wiedergabe an.
 *
 * AUF ALLEN SPUREN (13.09.2026): Bewegungsclips lagen auch auf Kamera-, Ton-
 * und Modellspuren (`addClipToTrack` nahm jede Spur); dort fand die erste
 * Fassung sie nicht — „A_Results/002_Dance_gem gibt es nicht mehr — 0 Clips
 * entfernt", und der Clip blieb. Gesucht wird darum überall, gemeint sind
 * nur Bewegungsclips (`type === 'bvh'`) — dazu Standbilder (`type === 'freeze'`,
 * 21.09.2026): Die zeigen dieselbe Quelldatei und liefen sonst gegen ein 404,
 * das niemand mehr auf 'bvh' geprüft hätte.
 *
 * Ohne Import von `state.js` (das zieht Three.js nach): `state` und `fn`
 * kommen als Parameter, damit das Modul in Node prüfbar ist
 * (`test_js_clipfehlt.py`).
 */
export class Clipfehlt {

    /**
     * Alle Bewegungsclips der BVH `kategorie/name` aus allen Spuren nehmen.
     * @returns {number} Anzahl der entfernten Clips
     */
    static entfernen(kategorie, name, state, fn) {
        let entfernt = 0;
        for (const spur of state.project.tracks) {
            entfernt += Clipfehlt._spurRaeumen(spur, kategorie, name);
            if (spur.type !== 'bvh') continue;
            if (spur.clips.length === 0 && spur.group) spur.group.visible = false;
            spur._activeClip = null;
            spur._activeAction = null;
        }
        if (entfernt > 0) Clipfehlt._nachtragen(state, fn);
        return entfernt;
    }

    /**
     * Beim Laden nicht gefunden: entfernen und dem Nutzer sagen, was fehlt.
     * @param melden  nimmt den Meldungstext (Studioanzeige), optional
     * @returns {number} Anzahl der entfernten Clips
     */
    static verschwunden(clip, state, fn, melden) {
        const weg = Clipfehlt.entfernen(clip.category, clip.name, state, fn);
        const text = `${clip.category}/${clip.name} gibt es nicht mehr — `
            + `${weg} Clip${weg === 1 ? '' : 's'} aus der Zeitleiste entfernt`;
        if (melden) melden(text);
        fn.serverLog?.('clip_removed_missing', `${clip.category}/${clip.name} (${weg})`);
        return weg;
    }

    static _spurRaeumen(spur, kategorie, name) {
        let entfernt = 0;
        // Von hinten: Ein `splice` beim Vorwärtslaufen überspringt den Nachbarn.
        for (let i = spur.clips.length - 1; i >= 0; i--) {
            const clip = spur.clips[i];
            if ((clip.type !== 'bvh' && clip.type !== 'freeze')
                || clip.category !== kategorie || clip.name !== name) continue;
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

    static _nachtragen(state, fn) {
        state.selectedClipIdx = -1;
        const nochClips = state.project.tracks.some(spur => spur.clips.length > 0);
        if (!nochClips && state.playing) {
            state.playing = false;
            const zeichen = typeof document === 'undefined' ? null
                : document.getElementById('pb-play-icon');
            if (zeichen) zeichen.className = 'fas fa-play';
        }
        fn.updateDuration?.();
        fn.renderTimeline?.();
        fn.updateProperties?.();
    }
}
