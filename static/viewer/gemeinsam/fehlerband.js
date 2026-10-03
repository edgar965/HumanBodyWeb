/**
 * Fehlerband der Auftragsseiten (02.10.2026) — das Feld `#fehler`, jetzt dauerhaft sichtbar und mit OK wegklickbar.
 *
 * Edgar: „Starte gerade einen mesh workflow, die Fehlermeldung verschwindet nach ein paar s. Mach die dauerhaft sichtbar,
 * mit OK wegklickbar". Die Ursache: `zeigen()` der Seiten schrieb bei JEDEM Abfragetakt `fehler(…'')`, sobald der Auftrag
 * nicht „gescheitert" war — eine Meldung wie „Start fehlgeschlagen: …" war nach dem nächsten Takt weg. Dazu stand das Feld
 * oben in der Seite; wer weiter unten klickte (der Knopf „Mesh erzeugen"), sah es gar nicht. Das Band hängt deshalb am
 * Fenster (`position: fixed`, `bildmodell.css`).
 *
 * Drei Arten von Meldungen:
 *   `meldung(text)`     eine Aktion ist gescheitert (Start, Anhalten …): bleibt stehen, bis jemand OK klickt;
 *   `lesefehler(text)`  die Abfrage des Zustands ist gescheitert: ebenso, nach OK aber erst wieder, wenn eine Abfrage
 *                       zwischendurch gelungen ist (sonst käme sie alle paar Sekunden zurück);
 *   `auftrag(z)`        Zustand des Auftrags: ein gescheiterter Lauf zeigt seine Meldung, bis man OK klickt; ein neuer Lauf
 *                       oder eine andere Meldung zeigt sich wieder.
 */
export class Fehlerband {
    constructor(feld = document.getElementById('fehler')) {
        this.feld = feld;
        this._meldung = null;      // { text, lesen }
        this._auftrag = '';        // Meldung des gescheiterten Auftrags
        this._quittiert = '';      // vom Nutzer weggeklickt: die Auftragsmeldung …
        this._lesenQuittiert = ''; // … und der Lesefehler
        if (!feld) return;
        feld.classList.add('bildmodell-fehler-fest');
        feld.setAttribute('role', 'alert');
        const zeile = document.createElement('div');
        zeile.className = 'bildmodell-fehler-zeile';
        this.text = document.createElement('span');
        this.text.className = 'bildmodell-fehler-text';
        this.ok = document.createElement('button');
        this.ok.type = 'button';
        this.ok.className = 'btn bildmodell-fehler-ok';
        this.ok.textContent = 'OK';
        this.ok.addEventListener('click', () => this.quittieren());
        zeile.append(this.text, this.ok);
        feld.replaceChildren(zeile);
    }

    meldung(text) {
        this._meldung = text ? { text, lesen: false } : null;
        this.zeigen();
    }

    lesefehler(text) {
        if (text === this._lesenQuittiert) return;
        this._meldung = { text, lesen: true };
        this.zeigen();
    }

    /** Eine Abfrage ist gelungen: `z` ist der Zustand des Auftrags. */
    auftrag(z) {
        this._lesenQuittiert = '';
        if (this._meldung?.lesen) this._meldung = null; // die Verbindung ist wieder da
        const text = z.status === 'gescheitert' ? (z.error || 'Fehlgeschlagen — siehe auftrag.log') : '';
        if (!text) this._quittiert = ''; // neuer Lauf: der nächste Fehler zählt wieder
        this._auftrag = text && text !== this._quittiert ? text : '';
        this.zeigen();
    }

    quittieren() {
        if (this._meldung) {
            if (this._meldung.lesen) this._lesenQuittiert = this._meldung.text;
            this._meldung = null;
        } else {
            this._quittiert = this._auftrag;
            this._auftrag = '';
        }
        this.zeigen();
    }

    zeigen() {
        if (!this.feld) return;
        const text = this._meldung?.text || this._auftrag || '';
        this.text.textContent = text;
        this.feld.classList.toggle('hb-versteckt', !text);
    }
}
