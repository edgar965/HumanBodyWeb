/**
 * Mesh3dairechnen — Knopf „Rechnen“ und Fortschritt auf der Testseite von Mesh3D-AI (23.10.2026, Server `Mesh3dairechenlauf`).
 * Fragt `GET /api/mesh3dai/test/<k>/rechnen/stand/` alle `TAKT_MS`, solange der Lauf wartet oder rechnet (und einmal beim Öffnen); „Rechnen“ = `POST …/rechnen/`.
 * Ist der Lauf fertig, lädt die Seite einmal neu — erst dann zeigt sie die neuen Ergebnisse.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3dairechnen {
    static TAKT_MS = 5000;
    static ZEICHEN = { offen: '○', laeuft: '⏳', fertig: '✓', fehler: '✗' };

    constructor(feld) {
        if (!feld) return;
        this.feld = feld;
        this.kennung = feld.dataset.kennung;
        this.knopf = feld.querySelector('[data-aktion="rechnen"]');
        this.status = feld.querySelector('[data-status]');
        this.balken = feld.querySelector('[data-balken]');
        this.liste = feld.querySelector('[data-schritte]');
        this.vorher = null;
        this.knopf.addEventListener('click', () => this.rechnen());
        this.holen();
    }

    async rechnen() {
        if (!window.confirm('Den Test jetzt neu rechnen? Die Ergebnisse auf dieser Seite werden durch den neuen Lauf ersetzt.')) return;
        this.knopf.disabled = true;
        try {
            await Serverabruf.senden(`/api/mesh3dai/test/${this.kennung}/rechnen/`, {});
        } catch (fehler) {
            this.status.textContent = `Start fehlgeschlagen: ${fehler.message}`;
            this.knopf.disabled = false;
            return;
        }
        this.holen();
    }

    async holen() {
        clearTimeout(this._zeit);
        let d;
        try {
            const antwort = await fetch(`/api/mesh3dai/test/${this.kennung}/rechnen/stand/`, { cache: 'no-store' });
            d = await antwort.json();
        } catch (fehler) {
            this.status.textContent = `Stand nicht lesbar: ${fehler.message}`;
            this._zeit = setTimeout(() => this.holen(), Mesh3dairechnen.TAKT_MS);
            return;
        }
        this.zeigen(d);
        const s = d.stand?.status;
        if (s === 'wartet' || s === 'laeuft') this._zeit = setTimeout(() => this.holen(), Mesh3dairechnen.TAKT_MS);
        else if (this.vorher && (this.vorher === 'wartet' || this.vorher === 'laeuft') && s === 'fertig') window.location.reload();
        this.vorher = s;
    }

    zeigen(d) {
        const st = d.stand;
        const s = st?.status;
        this.knopf.disabled = s === 'wartet' || s === 'laeuft';
        if (!st) {
            this.status.textContent = 'Noch nie über den Knopf gerechnet.';
            this.liste.replaceChildren();
            this.balken.style.width = '0%';
            return;
        }
        const schritte = st.schritte || [];
        const fertig = schritte.filter(x => x.status === 'fertig').length;
        this.balken.style.width = `${Math.round(100 * fertig / Math.max(schritte.length, 1))}%`;
        const dauer = st.dauer_s ? ` in ${Mesh3dairechnen.zeit(st.dauer_s)}` : '';
        this.status.textContent = {
            wartet: d.platz > 1 ? `Wartet (Platz ${d.platz} der Warteschlange).` : 'Wartet auf den Start …',
            laeuft: `Rechnet: Schritt ${st.schritt || 1} von ${schritte.length}.`,
            fertig: `Fertig${dauer} (${(st.ende || '').replace('T', ' ')}).`,
            fehler: `Abgebrochen: ${st.fehler || ''}`,
        }[s] || s;
        this.liste.replaceChildren(...schritte.map(x => {
            const li = document.createElement('li');
            li.className = `mesh3dai-rechnen-${x.status}`;
            li.textContent = `${Mesh3dairechnen.ZEICHEN[x.status] || ''} ${x.text}${x.dauer_s != null ? ` — ${Mesh3dairechnen.zeit(x.dauer_s)}` : ''}${x.uebernommen ? ' (vom letzten Lauf übernommen)' : ''}`;
            return li;
        }), Object.assign(document.createElement('li'), { className: 'mesh3dai-rechnen-hinweis', textContent: st.haut || '' }));
        this.liste.title = `KI-Fassungen: ${JSON.stringify(st.fassungen || {})}`;
    }

    static zeit(s) {
        const m = Math.floor(s / 60);
        return m ? `${m} min ${Math.round(s % 60)} s` : `${Math.round(s)} s`;
    }
}
