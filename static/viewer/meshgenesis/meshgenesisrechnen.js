/**
 * Meshgenesisrechnen — Knopf „Rechnen“ und Fortschritt auf der Testseite von Mesh-Genesis (23.10.2026, Server `Meshgenesisrechenlauf`).
 * Fragt `GET /api/meshgenesis/test/<k>/rechnen/stand/` alle `TAKT_MS`, solange der Lauf wartet oder rechnet (und einmal beim Öffnen); „Rechnen“ = `POST …/rechnen/`.
 * „Ab Einpassung rechnen“ (06.11.2026) schickt `{ab}` aus `data-ab`: Die Kette beginnt beim ersten Schritt, der das Geschlecht kennt (`Meshgenesisrechenlauf.AB_GESCHLECHT`).
 * Ist der Lauf fertig, lädt die Seite einmal neu — erst dann zeigt sie die neuen Ergebnisse.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Meshgenesisrechnen {
    static TAKT_MS = 5000;
    static ZEICHEN = { offen: '○', laeuft: '⏳', fertig: '✓', fehler: '✗' };

    constructor(feld) {
        if (!feld) return;
        this.feld = feld;
        this.kennung = feld.dataset.kennung;
        this.knopf = feld.querySelector('[data-aktion="rechnen"]');
        this.knopfAb = feld.querySelector('[data-aktion="rechnen-ab"]');
        this.status = feld.querySelector('[data-status]');
        this.balken = feld.querySelector('[data-balken]');
        this.liste = feld.querySelector('[data-schritte]');
        this.vorher = null;
        this.knopf.addEventListener('click', () => this.rechnen());
        this.knopfAb.addEventListener('click', () => this.rechnen(this.knopfAb.dataset.ab));
        this.holen();
    }

    _sperren(an) {
        this.knopf.disabled = an;
        this.knopfAb.disabled = an;
    }

    async rechnen(ab = null) {
        const frage = ab ? 'Ab der Einpassung für das eingestellte Geschlecht neu rechnen? Rig, Erkennung und Zerlegung bleiben, Einpassung, Figur, Haut und Kleider werden ersetzt.'
            : 'Den Test jetzt neu rechnen? Die Ergebnisse auf dieser Seite werden durch den neuen Lauf ersetzt.';
        if (!window.confirm(frage)) return;
        this._sperren(true);
        try {
            await Serverabruf.senden(`/api/meshgenesis/test/${this.kennung}/rechnen/`, ab ? { ab } : {});
        } catch (fehler) {
            this.status.textContent = `Start fehlgeschlagen: ${fehler.daten?.error || fehler.message}`;
            this._sperren(false);
            return;
        }
        this.holen();
    }

    async holen() {
        clearTimeout(this._zeit);
        let d;
        try {
            const antwort = await fetch(`/api/meshgenesis/test/${this.kennung}/rechnen/stand/`, { cache: 'no-store' });
            d = await antwort.json();
        } catch (fehler) {
            this.status.textContent = `Stand nicht lesbar: ${fehler.message}`;
            this._zeit = setTimeout(() => this.holen(), Meshgenesisrechnen.TAKT_MS);
            return;
        }
        this.zeigen(d);
        const s = d.stand?.status;
        if (s === 'wartet' || s === 'laeuft') this._zeit = setTimeout(() => this.holen(), Meshgenesisrechnen.TAKT_MS);
        else if (this.vorher && (this.vorher === 'wartet' || this.vorher === 'laeuft') && s === 'fertig') window.location.reload();
        this.vorher = s;
    }

    zeigen(d) {
        const st = d.stand;
        const s = st?.status;
        this._sperren(s === 'wartet' || s === 'laeuft');
        if (!st) {
            this.status.textContent = 'Noch nie über den Knopf gerechnet.';
            this.liste.replaceChildren();
            this.balken.style.width = '0%';
            return;
        }
        const schritte = st.schritte || [];
        const fertig = schritte.filter(x => x.status === 'fertig').length;
        this.balken.style.width = `${Math.round(100 * fertig / Math.max(schritte.length, 1))}%`;
        const dauer = st.dauer_s ? ` in ${Meshgenesisrechnen.zeit(st.dauer_s)}` : '';
        this.status.textContent = {
            wartet: d.platz > 1 ? `Wartet (Platz ${d.platz} der Warteschlange).` : 'Wartet auf den Start …',
            laeuft: `Rechnet: Schritt ${st.schritt || 1} von ${schritte.length}.`,
            fertig: `Fertig${dauer} (${(st.ende || '').replace('T', ' ')}).`,
            fehler: `Abgebrochen: ${st.fehler || ''}`,
        }[s] || s;
        this.liste.replaceChildren(...schritte.map(x => {
            const li = document.createElement('li');
            li.className = `meshgenesis-rechnen-${x.status}`;
            li.textContent = `${Meshgenesisrechnen.ZEICHEN[x.status] || ''} ${x.text}${x.dauer_s != null ? ` — ${Meshgenesisrechnen.zeit(x.dauer_s)}` : ''}${x.uebernommen ? ' (vom letzten Lauf übernommen)' : ''}`;
            return li;
        }), Object.assign(document.createElement('li'), { className: 'meshgenesis-rechnen-hinweis', textContent: st.haut || '' }));
        this.liste.title = `KI-Fassungen: ${JSON.stringify(st.fassungen || {})}`;
    }

    static zeit(s) {
        const m = Math.floor(s / 60);
        return m ? `${m} min ${Math.round(s % 60)} s` : `${Math.round(s)} s`;
    }
}
