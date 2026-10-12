/**
 * Meshfigurladezeit — wie lange es dauert, bis die Figur der Bühne zum ersten Mal GEZEICHNET ist (12.10.2026).
 *
 * Edgar: „40–50 s Wartezeit im Browser für das Modell ist viel zu lange, ich brauche 5–10 s“. Gemessen werden konnte nur ein Teil: im verdeckten Messtab zeichnet nichts, und die Serverzeiten
 * (`logs/client.log`, `server_call`) enden, bevor der Browser die Figur baut und zum ersten Mal zeichnet. Dieses Modul schreibt deshalb bei jedem Öffnen EINE Zeile ins Browserprotokoll
 * (`POST /api/log/`, Aktion `ladezeit`) mit den Marken seit Beginn der Seite:
 *   bühne    die Bühne ist angelegt (Module geladen)       zustand  der Auftrag ist gelesen, die Regler liegen vor
 *   bau      der Bau der Figur beginnt                     figur    `Genesis9Modell.bauen()` ist zurück (Käfig, noch ohne feine Stufe)
 *   bild     das erste Bild mit Figur ist FERTIG gezeichnet (GPU-Arbeit bis `finish()`), dahinter in Klammern die Dauer dieses einen Zeichnens
 * Das erste Zeichnen übersetzt die Shader und lädt Texturen und Netze auf die Karte; gemessen am Zauberer-Auftrag in einem verdeckten Tab (von Hand gerufen) 4,4–11,3 s bei 13–19 Programmen, das zweite Bild 9–14 ms.
 * Gesetzt wird nur die ERSTE Marke je Name; nach der Meldung ist das Modul still.
 */
export class Meshfigurladezeit {
    static ADRESSE = '/api/log/';
    static SEITE = 'buehne';

    /** `kennung`: Text oder Funktion, die ihn liefert (der Auftrag steht beim Anlegen der Bühne oft noch nicht fest). */
    constructor(kennung) {
        this.kennung = kennung;
        this.marken = {};
        this._fertig = false;
        this._verdeckt = document.hidden;
        this._sichtbar = null;
        if (this._verdeckt) {
            const beobachter = () => {
                if (document.hidden) return;
                this._sichtbar = Math.round(performance.now());
                document.removeEventListener('visibilitychange', beobachter);
            };
            document.addEventListener('visibilitychange', beobachter);
        }
    }

    /** Millisekunden seit Beginn der Seite (`performance.now()` zählt ab dem Navigationsbeginn). Nur die erste Marke je Name zählt. */
    marke(name) {
        if (!this._fertig && !(name in this.marken)) this.marken[name] = Math.round(performance.now());
    }

    /**
     * Zeichnen: `tat` zeichnet ein Bild. Das erste Bild MIT Figur wird bis zum Ende der Grafikarbeit gemessen und gemeldet, jedes andere läuft ohne Zutun durch.
     */
    zeichnen(tat, renderer, mitFigur) {
        if (this._fertig || !mitFigur) { tat(); return; }
        const von = performance.now();
        tat();
        renderer.getContext().finish();
        const dauer = Math.round(performance.now() - von);
        this.marke('bild');
        this._melden(renderer, dauer);
    }

    _melden(renderer, dauer) {
        this._fertig = true;
        const m = this.marken, f = (a, b) => (a in m && b in m ? `${m[b] - m[a]}ms` : '—');
        const info = renderer.info, leinwand = renderer.domElement;
        const kennung = (typeof this.kennung === 'function' ? this.kennung() : this.kennung) || '?';
        const text = `bereit nach ${m.bild}ms · Bühne ${m.buehne ?? '—'}ms · Zustand +${f('buehne', 'zustand')} · Bau +${f('zustand', 'bau')} · Figur +${f('bau', 'figur')} · erstes Bild +${f('figur', 'bild')} (Zeichnen ${dauer}ms)`
            + ` · ${info.programs ? info.programs.length : '?'} Programme · ${info.memory.textures} Texturen · Leinwand ${leinwand.width}x${leinwand.height} · DPR ${window.devicePixelRatio}`
            + (this._verdeckt ? ` · Tab beim Laden verdeckt, sichtbar ab ${this._sichtbar ?? 'nie'}ms` : '');
        try {
            fetch(Meshfigurladezeit.ADRESSE, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, keepalive: true,
                body: JSON.stringify({ page: Meshfigurladezeit.SEITE, action: 'ladezeit', detail: `[${kennung}] ${text}`, level: 'info' }),
            // stumm gewollt: Diese Zeile IST der Protokollweg — ein Fehler dabei darf die Bühne nicht aufhalten.
            }).catch(() => {});
        } catch { /* stumm gewollt: siehe oben */ }
    }
}
