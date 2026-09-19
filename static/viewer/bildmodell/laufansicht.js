/**
 * Laufansicht — Schritte, Fortschritt, Fehler, Start ab Schritt, Anhalten.
 *
 * Die sieben Schritte stehen als Kette (`#schritte`): erledigt, laufend,
 * offen — aus `zustand.schritt` und `zustand.status`. Der Balken zeigt
 * `progress`, die Zeile darunter `progress_detail`. „Start ab" nimmt die
 * Optionen aus dem Formular und die festgehaltenen Regler der Ergebnisliste.
 */
export class Laufansicht {

    static NAMEN = { sichtung: 'Zuschnitt und Sichtung', schaetzung: 'Schätzung', ziel: 'Zielnetz',
                     anpassung: 'Anpassung', rest: 'Restmorph', vorschau: 'Vorschau',
                     speichern: 'Speichern' };
    static STATUS = { angelegt: ['Angelegt', 'hb-laeuft'], laeuft: ['Läuft', 'hb-laeuft'],
                      fertig: ['Fertig', 'hb-gut'], gescheitert: ['Fehlgeschlagen', 'hb-schlecht'],
                      angehalten: ['Angehalten', 'hb-laeuft'] };

    constructor(auftrag, formular, festgehalten) {
        this.auftrag = auftrag;
        this.formular = formular;
        this.festgehalten = festgehalten || (() => ({}));
        this._kette();
        document.getElementById('starten')?.addEventListener('click', () => this.starten());
        document.getElementById('anhalten')?.addEventListener('click', () => this.anhalten());
        auftrag.zuhoeren(z => this.zeigen(z));
    }

    _kette() {
        const feld = document.getElementById('schritte');
        const wahl = document.getElementById('ab-schritt');
        if (!feld) return;
        feld.innerHTML = '';
        for (const s of this.auftrag.constructor.SCHRITTE) {
            const e = document.createElement('div');
            e.className = 'bildmodell-schritt';
            e.dataset.schritt = s;
            e.innerHTML = `<span class="bildmodell-schrittpunkt"></span><span>${Laufansicht.NAMEN[s]}</span>`;
            feld.appendChild(e);
            if (wahl) {
                const o = document.createElement('option');
                o.value = s; o.textContent = Laufansicht.NAMEN[s];
                wahl.appendChild(o);
            }
        }
    }

    zeigen(z) {
        const reihe = this.auftrag.constructor.SCHRITTE;
        const aktuell = reihe.indexOf(z.schritt);
        for (const e of document.querySelectorAll('.bildmodell-schritt')) {
            const i = reihe.indexOf(e.dataset.schritt);
            e.classList.toggle('erledigt', z.status === 'fertig' || (aktuell > i));
            e.classList.toggle('laeuft', z.status === 'laeuft' && i === aktuell);
            e.classList.toggle('gescheitert', z.status === 'gescheitert' && i === aktuell);
        }
        const balken = document.getElementById('fortschritt');
        if (balken) balken.style.width = `${z.progress || 0}%`;
        const text = document.getElementById('fortschritt-text');
        if (text) {
            text.textContent = z.status === 'laeuft'
                ? `${z.progress || 0} % · ${Laufansicht.NAMEN[z.schritt] || ''}${z.progress_detail ? ' · ' + z.progress_detail : ''}`
                : (z.status === 'fertig' ? 'Alle Schritte erledigt' : '');
        }
        const status = document.getElementById('auftrag-status');
        if (status) {
            const [name, klasse] = Laufansicht.STATUS[z.status] || [z.status, ''];
            status.textContent = name;
            status.className = `bildmodell-status ${klasse}`;
        }
        const fehler = document.getElementById('fehler');
        if (fehler) {
            fehler.classList.toggle('hb-versteckt', !z.error);
            fehler.textContent = z.error || '';
        }
        const laeuft = z.status === 'laeuft';
        const starten = document.getElementById('starten');
        const anhalten = document.getElementById('anhalten');
        if (starten) starten.disabled = laeuft;
        if (anhalten) anhalten.disabled = !laeuft;
        const wahl = document.getElementById('ab-schritt');
        if (wahl && !laeuft && !wahl.dataset.gestellt) {
            // Vorschlag: nach einem Fehler beim gescheiterten Schritt, sonst am Anfang
            wahl.value = z.status === 'gescheitert' && z.schritt ? z.schritt : 'sichtung';
        }
        wahl?.addEventListener('change', () => { wahl.dataset.gestellt = '1'; }, { once: true });
    }

    async starten() {
        const ab = document.getElementById('ab-schritt')?.value || 'sichtung';
        try {
            const person = window.__bildmodell?.person?.werte?.() || {};
            await this.auftrag.starten({ ...this.formular.werte(), person }, ab, this.festgehalten());
        } catch (fehler) {
            window.alert(`Start fehlgeschlagen: ${fehler.message}`);
        }
    }

    async anhalten() {
        try { await this.auftrag.anhalten(); }
        catch (fehler) { window.alert(fehler.message); }
    }
}
