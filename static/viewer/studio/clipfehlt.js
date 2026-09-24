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
 * GEÄNDERT (Edgar, 24.09.2026): „Fehlermeldung, mit Abfrage ob die gelöscht
 * werden sollen" — `verschwunden` entfernt nicht mehr stillschweigend,
 * sondern fragt (einmal je Datei und Sitzung, `_entschieden`); bei „Nein"
 * bleibt der Clip stehen, wie ein anderer Ladefehler. Das automatische
 * Entfernen (`entfernen`) bleibt, WIE ES WAR, für die bewusste Löschung über
 * die Bibliothek (`Bibliothekablage`, dort mit eigenem „wirklich löschen?").
 *
 * NACHGEBESSERT, NOCH AM 24.09.2026 (Edgar: „Popup kommt, aber die
 * Animationen sind immer noch drin ... 'keine Bewegung hier' - was soll
 * das??"): Ein Projekt mit MEHREREN verschiedenen fehlenden Dateien (TechnoDance:
 * Dance1, Dance2, 0001_Dance, …) löste beim Laden ebenso viele `confirm()`
 * NACHEINANDER aus — Chrome unterdrückt mehrere Dialoge kurz hintereinander
 * automatisch als „Abbrechen" (die Checkbox „Diese Seite bittet, keine
 * weiteren Dialogfelder mehr anzuzeigen"), und der Rest blieb unbemerkt bei
 * „Nein" hängen: sichtbar, aber ohne geladene Bewegung — genau das zeigt
 * `zeitleiste_spuren.js` als „⚠ keine Bewegung hier" an (ein Clip ohne
 * `animClip`). Jetzt wird EINMAL gesammelt (`_sammlung`, 300 ms Pause nach
 * dem letzten Fund) und EIN Dialog für alle zusammen gestellt.
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
     * Merkt sich je `Kategorie/Name`, was der Nutzer diese Sitzung schon
     * geantwortet hat — dieselbe Datei fragt kein zweites Mal.
     */
    static _entschieden = new Map();

    /** Noch nicht abgefragte Funde dieser Sammelrunde: `Kategorie/Name` -> {kategorie, name}. */
    static _sammlung = new Map();
    static _timer = null;
    /** Sammelfenster: Clips derselben Ladephase treffen selten im selben Tick ein. */
    static WARTE_MS = 300;

    /**
     * Beim Laden nicht gefunden (404): dem Nutzer sagen, was fehlt, und
     * fragen, statt stillschweigend zu entfernen (Edgar, 24.09.2026: „dann
     * Fehlermeldung, mit Abfrage ob die gelöscht werden sollen" — vorher,
     * 13.09.2026, galt noch „dann entfernen" ohne Rückfrage).
     *
     * Fragt NICHT sofort je Aufruf — das ergäbe bei mehreren verschiedenen
     * fehlenden Dateien ebenso viele `confirm()` nacheinander, und Chrome
     * unterdrückt mehrere Dialoge kurz hintereinander automatisch als
     * „Nein". Stattdessen wird `WARTE_MS` gesammelt und EIN Dialog für alle
     * gestellt (`_abfragen`).
     *
     * Bis zur Antwort — und bei „Nein" danach — bleibt der Clip stehen, rot
     * markiert (`_loadError`) wie ein anderer Ladefehler: nicht totes
     * Gewicht, sondern sichtbar als das, was er ist — eine Referenz, die
     * (noch) nicht aufgelöst werden konnte.
     *
     * @param melden  nimmt den Meldungstext (Studioanzeige), optional
     */
    static verschwunden(clip, state, fn, melden) {
        const schluessel = `${clip.category}/${clip.name}`;
        clip._loadError = true;
        fn.renderTimeline?.();
        const bekannt = Clipfehlt._entschieden.get(schluessel);
        if (bekannt !== undefined) {
            if (bekannt) Clipfehlt.entfernen(clip.category, clip.name, state, fn);
            return;
        }
        if (!Clipfehlt._sammlung.has(schluessel)) {
            Clipfehlt._sammlung.set(schluessel, { kategorie: clip.category, name: clip.name });
        }
        clearTimeout(Clipfehlt._timer);
        Clipfehlt._timer = setTimeout(
            () => Clipfehlt._abfragen(state, fn, melden), Clipfehlt.WARTE_MS);
    }

    /** Die gesammelten Funde EINMAL abfragen und je nach Antwort entfernen. */
    static _abfragen(state, fn, melden) {
        const eintraege = [...Clipfehlt._sammlung.values()];
        Clipfehlt._sammlung.clear();
        if (!eintraege.length) return;
        const namen = eintraege.map(e => `${e.kategorie}/${e.name}`);
        const gesamt = eintraege.reduce(
            (summe, e) => summe + Clipfehlt._zaehlen(e.kategorie, e.name, state), 0);
        const kopf = namen.length === 1
            ? `„${namen[0]}" gibt es nicht mehr auf der Platte.`
            : `${namen.length} Animationen gibt es nicht mehr auf der Platte:\n\n`
              + namen.map(n => `„${n}"`).join('\n');
        const loeschen = confirm(
            `${kopf}\n\n${gesamt} Clip${gesamt === 1 ? '' : 's'} in der Zeitleiste betroffen. `
            + 'Aus der Zeitleiste entfernen?');
        let entfernt = 0;
        for (const { kategorie, name } of eintraege) {
            Clipfehlt._entschieden.set(`${kategorie}/${name}`, loeschen);
            if (loeschen) entfernt += Clipfehlt.entfernen(kategorie, name, state, fn);
        }
        if (melden) {
            melden(loeschen
                ? `${entfernt} Clip${entfernt === 1 ? '' : 's'} ohne Datei aus der Zeitleiste entfernt`
                : `${namen.length} fehlende Animation${namen.length === 1 ? '' : 'en'} `
                  + `${namen.length === 1 ? 'bleibt' : 'bleiben'} markiert`);
        }
        if (loeschen) fn.serverLog?.('clip_removed_missing', namen.join(', '));
    }

    /** Bewegungsclips der Datei über ALLE Spuren zählen, ohne sie anzufassen. */
    static _zaehlen(kategorie, name, state) {
        let anzahl = 0;
        for (const spur of state.project.tracks) {
            for (const clip of spur.clips) {
                if ((clip.type === 'bvh' || clip.type === 'freeze')
                        && clip.category === kategorie && clip.name === name) anzahl++;
            }
        }
        return anzahl;
    }

    /**
     * Eine BVH-Bibliotheksdatei wurde umbenannt: alle Clips, die noch den
     * ALTEN Namen tragen, auf den neuen umstellen — statt sie beim nächsten
     * Laden als 404 zu verlieren (Edgar, 24.09.2026: „die Umbenennung soll
     * sofort im UI sichtbar sein"). `clip.animClip` bleibt unangetastet: Eine
     * schon geladene Animation ist weiterhin gültig, nur ihr Name/Ordner im
     * Projekt muss zum neuen Dateinamen passen, damit ein SPÄTERES Laden
     * (Reload, `_neuHolen`) die Datei wiederfindet.
     * @returns {number} Anzahl der umgestellten Clips
     */
    static umbenannt(kategorie, alterName, neuerName, state, fn) {
        let geaendert = 0;
        for (const spur of state.project.tracks) {
            for (const clip of spur.clips) {
                if ((clip.type !== 'bvh' && clip.type !== 'freeze')
                    || clip.category !== kategorie || clip.name !== alterName) continue;
                clip.name = neuerName;
                geaendert++;
            }
        }
        if (geaendert > 0) Clipfehlt._nachtragen(state, fn);
        return geaendert;
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
