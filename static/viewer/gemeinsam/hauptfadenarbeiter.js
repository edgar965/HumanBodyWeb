/**
 * Hauptfadenarbeiter — der Faden des Hauptfadenwächters (05.10.2026, `Hauptfadenwaechter`).
 *
 * Edgar: „warum sind keine Logs sichtbar, wenn ich auf den Tab Iterationen klicke?" — Jede Zeile des Seitenlogs geht vom HAUPTFADEN der Seite ab. Steht der
 * Hauptfaden (eine lange Aufgabe, ein Bild der 3D-Ansicht, das nicht fertig wird), kann er nichts melden, und der Beobachter für lange Aufgaben meldet erst, WENN sie vorbei
 * ist. Dieser Faden läuft getrennt: Er fragt den Hauptfaden alle `TAKT_MS` an (`ping`), der antwortet (`pong`). Bleibt die Antwort `STILL_MS` aus, schreibt er SELBST
 * ins Log — während der Hauptfaden noch steht — und wiederholt es alle `WIEDERHOLEN_MS`; kommt die Antwort wieder, meldet er die Dauer.
 *
 * Hängt an nichts (keine Importe), damit es auch läuft, wenn die Seitenklasse mit ihren Modulen nicht hochkommt. Ein verdeckter Tab wird nicht gemeldet (Chrome bremst ihn
 * absichtlich), und beim Sichtbarwerden beginnt die Zählung neu (ein eingefrorener Tab käme sonst mit einer Pause von Minuten zurück).
 *
 * Die Umwelt (`jetzt`, `takt`, `anfragen`, `anHaupt`) wird übergeben, damit die Klasse ohne Worker prüfbar ist (`test_js_hauptfadenarbeiter`); im Worker verdrahtet sie
 * der letzte Block dieser Datei.
 */
export class Hauptfadenarbeiter {

    static TAKT_MS = 500;
    static STILL_MS = 1500;
    static WIEDERHOLEN_MS = 5000;

    /** @param {{jetzt: () => number, takt: (rueckruf: () => void, ms: number) => unknown, anfragen: (adresse: string, optionen: object) => {catch: Function}, anHaupt: (nachricht: object) => void}} umwelt */
    constructor(umwelt) {
        this.umwelt = umwelt;
        this.adresse = '';
        this.seite = '';
        this.kennung = '';
        this.sichtbar = true;
        this.antwort = umwelt.jetzt();         // wann der Hauptfaden zuletzt geantwortet hat
        this.steht = false;                    // ein Stillstand ist gemeldet, das Ende noch nicht
        this.gemeldet = 0;
    }

    /** Eine Nachricht des Hauptfadens: `start` (Adresse, Seite, Kennung), `pong` (Antwort auf `ping`), `sicht` (Tab sichtbar oder verdeckt). */
    behandeln(daten) {
        if (daten.typ === 'start') this.start(daten);
        else if (daten.typ === 'pong') this.gehoert();
        else if (daten.typ === 'sicht') this.sichtbarWert(!!daten.wert);
    }

    start(daten) {
        this.adresse = daten.adresse;
        this.seite = daten.seite;
        this.kennung = daten.kennung;
        this.antwort = this.umwelt.jetzt();
        this.umwelt.takt(() => this.tick(), Hauptfadenarbeiter.TAKT_MS);
    }

    tick() {
        this.umwelt.anHaupt({ typ: 'ping' });
        const jetzt = this.umwelt.jetzt();
        const still = jetzt - this.antwort;
        if (!this.sichtbar || still < Hauptfadenarbeiter.STILL_MS) return;
        if (this.steht && jetzt - this.gemeldet < Hauptfadenarbeiter.WIEDERHOLEN_MS) return;
        this.steht = true;
        this.gemeldet = jetzt;
        this.melden('haenger_live', `Hauptfaden antwortet seit ${(still / 1000).toFixed(1)} s nicht — die Seite steht`, 'warning');
    }

    gehoert() {
        const jetzt = this.umwelt.jetzt();
        if (this.steht) this.melden('haenger_ende', `Hauptfaden wieder da nach ${((jetzt - this.antwort) / 1000).toFixed(1)} s`, 'warning');
        this.steht = false;
        this.antwort = jetzt;
    }

    sichtbarWert(sichtbar) {
        this.sichtbar = sichtbar;
        this.steht = false;
        this.antwort = this.umwelt.jetzt();
    }

    melden(aktion, detail, stufe) {
        // stumm gewollt: Das Log darf den Wächter nicht aufhalten und meldet sich nicht selbst.
        this.umwelt.anfragen(this.adresse, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page: this.seite, action: aktion, detail: `[${this.kennung}] ${detail}`, level: stufe }),
        }).catch(() => {});
    }
}

// Nur im Worker selbst: Die Klasse bekommt die echte Umwelt und hört auf den Hauptfaden. In Node (Test) oder als Import gibt es kein `WorkerGlobalScope`.
if (typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope) {
    const arbeiter = new Hauptfadenarbeiter({
        jetzt: () => performance.now(),
        takt: (rueckruf, ms) => setInterval(rueckruf, ms),
        anfragen: (adresse, optionen) => fetch(adresse, optionen),
        anHaupt: nachricht => self.postMessage(nachricht),
    });
    self.onmessage = ereignis => arbeiter.behandeln(ereignis.data || {});
}
