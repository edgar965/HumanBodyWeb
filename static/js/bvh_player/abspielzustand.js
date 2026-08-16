/**
 * Abspielzustand — wo die Wiedergabe steht und ob das Skelett gezeigt wird.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026). Dort lagen sechs lose
 * Variablen in der Closure (`isPlaying`, `manualTime`, `lastTimestamp`,
 * `currentSpeed`, `overlayActive`, `overlayForced`), auf die neun Funktionen
 * zugriffen — die Datei liess sich deshalb nicht aufteilen.
 *
 * Die Ersatzuhr ist der Grund fuer die Haelfte davon: Fehlt das Video oder ist
 * es kaputt (Dauer NaN oder unendlich), laeuft die Wiedergabe ueber die
 * BVH-Dauer weiter. Beide Faelle mussten in jeder Funktion unterschieden
 * werden; hier steht die Unterscheidung einmal.
 */

export class Abspielzustand {
    constructor(video) {
        this.video = video;
        this.laeuft = false;
        /** Stand der Ersatzuhr in Sekunden. */
        this.eigenzeit = 0;
        /** Zeitstempel des letzten Bildes, fuer die Zeitdifferenz. */
        this.letzterStempel = 0;
        this.tempo = 1;
        /** Erst nach dem ersten Abspielen oder Springen zeigen. */
        this.zeigen = false;
        /** Von aussen erzwungen (Knopf "Rig" der Ergebnisseite). */
        this.erzwungen = false;
        this.klipdauer = 0;
    }

    /** Liefert das Video eine brauchbare Dauer? */
    get videoBrauchbar() {
        const d = this.video.duration;
        return d > 0 && isFinite(d) && !isNaN(d);
    }

    get dauer() {
        return this.videoBrauchbar ? this.video.duration : this.klipdauer;
    }

    get zeit() {
        return this.videoBrauchbar ? this.video.currentTime : this.eigenzeit;
    }

    get fortschritt() {
        return this.dauer > 0 ? this.zeit / this.dauer : 0;
    }

    get sichtbar() {
        return this.zeigen || this.erzwungen;
    }

    /** Ersatzuhr weiterstellen. Nur noetig, wenn kein Video da ist. */
    takt(stempel) {
        if (!this.videoBrauchbar && this.laeuft && this.klipdauer > 0) {
            const dt = this.letzterStempel ? (stempel - this.letzterStempel) / 1000 : 0;
            this.eigenzeit += dt * this.tempo;
            if (this.eigenzeit >= this.klipdauer) this.eigenzeit = 0;   // von vorn
        }
        this.letzterStempel = stempel;
    }

    /** Zeit setzen — je nach Quelle am Video oder an der Ersatzuhr. */
    springen(sekunden) {
        const ziel = Math.max(0, Math.min(this.dauer || 0, sekunden));
        if (this.videoBrauchbar) {
            this.video.currentTime = ziel;
        } else {
            this.eigenzeit = ziel;
        }
        this.zeigen = true;
    }

    zuruecksetzen() {
        this.laeuft = false;
        this.eigenzeit = 0;
        this.zeigen = false;
    }
}
