/**
 * Stoffwache — wann der Stoffschwung eines Stücks zurück auf die GPU-Häutung geht.
 *
 * WARUM (19.09.2026 spät, Edgar: „Ursula1 mit Animation ist jetzt besser, aber
 * hose animiert noch nicht"): Beim Abspielen zeigt der Stoffschwung statt der
 * `SkinnedMesh` ein zweites Netz mit den Punkten des Workers
 * (`scene/genesis9/genesis9stoffschwung.js`). Sobald der Worker einmal
 * geantwortet hat, ist die `SkinnedMesh` unsichtbar — und wenn er DANACH
 * stirbt (Fehler in einer späteren Nachricht) oder nie mehr antwortet, bleibt
 * das Anzeigenetz mit seinen letzten Punkten stehen, während der Körper
 * weitertanzt. Ein Stück, das „nicht animiert", ohne Fehlermeldung. In zwei
 * Sitzungen ließ sich das im eigenen Tab nicht auslösen (Worker bereit,
 * Bilder kommen); Edgars Bild zeigte es trotzdem.
 *
 * Deshalb eine Wache ohne Three.js, in Node prüfbar: Ein Worker gilt als
 * ausgefallen, wenn er einen Fehler gemeldet hat oder seit WARTEZEIT_MS auf
 * eine Nachricht nicht geantwortet hat. Dann kommt die `SkinnedMesh` zurück
 * — die GPU häutet weiter, nur ohne Schwung — und der Worker wird beendet.
 */
export class Stoffwache {

    /** So lange darf eine Antwort des Workers ausbleiben (ms). */
    static WARTEZEIT_MS = 2000;

    /**
     * @param e     Eintrag des Stoffschwungs `{fehler, beschaeftigt, gesendet, …}`
     * @param jetzt `performance.now()`
     */
    static ausgefallen(e, jetzt) {
        if (e.fehler) return true;
        return !!(e.beschaeftigt && e.gesendet && jetzt - e.gesendet > Stoffwache.WARTEZEIT_MS);
    }

    /** Zurück auf die GPU-Häutung: Anzeigenetz weg, Stück sichtbar, Worker aus. */
    static zurueck(e) {
        e.bereit = false;
        e.beschaeftigt = false;
        e.ausgefallen = true;
        if (e.anzeige) e.anzeige.visible = false;
        if (e.netz) e.netz.visible = true;
        if (e.worker && typeof e.worker.terminate === 'function') e.worker.terminate();
        e.worker = null;
    }
}
