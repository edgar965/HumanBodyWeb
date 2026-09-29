/**
 * Blendermodelliterationen — der zweite Reiter der Auftragsseite: die Runden des Kostüm-Kreislaufs (29.09.2026).
 *
 * Edgar: „mach in dem Job Iterationen so dass man den Fortschritt sehen kann, in einem zweiten Tab des Jobs" und
 * „… einen Code der dann später per Knopfdruck durch alle Iterationen bis zum fertigen Ergebnis läuft. Ich kann
 * beliebig Iterationen weiter laufen lassen". Oben „Weiter iterieren" (startet NUR den Schritt „kostuem", ab dem
 * besten bisherigen Kostüm), die Kurve aller Runden (`Blendermodellverlauf`), der Vergleich Vorlage/Ergebnisvideo,
 * darunter je Runde eine Karte (`Blendermodellrunde`). Solange der Reiter offen ist, holt das Modul den Zustand alle
 * `TAKT_MS` selbst.
 */
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Blendermodellrunde } from './blendermodellrunde.js';
import { Blendermodellverlauf } from './blendermodellverlauf.js';

export class Blendermodelliterationen {

    static TAKT_MS = 5000;
    /** Ohne gemessene Bildrate im Vergleich (`ergebnis.vergleich.video_fps`). */
    static FPS_VORGABE = 30;

    constructor(seite) {
        this.seite = seite;
        this.liste = document.getElementById('iterationen');
        this.vergleich = document.getElementById('iterationen-vergleich');
        this.anzahl = document.getElementById('iterationen-anzahl');
        this.verlauf = document.getElementById('iterationen-verlauf');
        this.runden = document.getElementById('iterationen-runden');
        this.weiter = document.getElementById('iterationen-weiter');
        this.halt = document.getElementById('iterationen-anhalten');
        this.stand = document.getElementById('iterationen-stand');
        this.karten = new Blendermodellrunde(name => this.seite.dateiAdresse('iterationen', name));
        this._timer = null;
        this._stand = '';
        this._fps = Blendermodelliterationen.FPS_VORGABE;
        const vorgabe = (seite.zustand.optionen || {}).kostuem || {};
        if (vorgabe.runden) this.runden.value = vorgabe.runden;
        for (const knopf of document.querySelectorAll('#auftrag-reiter [data-reiter]')) {
            knopf.addEventListener('click', () => this.umschalten(knopf.dataset.reiter));
        }
        this.weiter.addEventListener('click', () => this.weiterIterieren());
        this.halt.addEventListener('click', () => this.seite.anhalten());
        // In der Erfassungsphase: Chromes eigene Videosteuerung springt bei ←/→ sonst 5 s.
        document.addEventListener('keydown', ereignis => this._taste(ereignis), true);
    }

    /** Nur den Schritt „kostuem" rechnen, mit der hier gewählten Zahl Runden (wird als Option gespeichert). */
    async weiterIterieren() {
        const runden = Math.max(1, Math.min(1000, Math.round(Number(this.runden.value) || 1)));
        const beschriftung = this.weiter.querySelector('span');
        const text = beschriftung.textContent;
        try {
            await Knopfsperre.waehrend(this.weiter, async () => {
                const antwort = await Serverabruf.senden(this.seite.adresse('starten/'),
                    { ab: 'kostuem', bis: 'kostuem', optionen: { kostuem: { runden } } });
                if (antwort.error) throw new Error(antwort.error);
            }, 'Startet …');
        } catch (fehler) {
            this.stand.textContent = `Start fehlgeschlagen: ${fehler.daten?.error || fehler.message}`;
            this.weiter.disabled = false;
            return;
        } finally {
            // `Knopfsperre` lässt nach Erfolg den Ersatztext stehen; gesperrt bleibt der Knopf über `zeigen` (läuft).
            beschriftung.textContent = text;
        }
        this.seite.zustand.laeuft = true;
        this.seite.zustand.status = 'laeuft';
        this.seite.zeigen();
        this.seite.verfolgen();
    }

    /** ←/→ gehen im Video des Vergleichs ein Bild zurück/vor (Edgar, 29.09.2026) — angehalten, auf die Mitte des
     *  Bildes gesetzt, damit Rundung an der Bildgrenze nicht das Nachbarbild zeigt. */
    _taste(ereignis) {
        if (ereignis.key !== 'ArrowLeft' && ereignis.key !== 'ArrowRight') return;
        if (document.getElementById('reiter-iterationen').hidden) return;
        if (ereignis.target.closest?.('input, select, textarea')) return;
        const video = this.vergleich.querySelector('video');
        if (!video || !Number.isFinite(video.duration)) return;
        ereignis.preventDefault();
        ereignis.stopPropagation();
        video.pause();
        const letztes = Math.max(0, Math.floor(video.duration * this._fps) - 1);
        const jetzt = Math.floor(video.currentTime * this._fps + 1e-6);
        const ziel = Math.min(letztes, Math.max(0, jetzt + (ereignis.key === 'ArrowRight' ? 1 : -1)));
        video.currentTime = (ziel + 0.5) / this._fps;
    }

    umschalten(name) {
        for (const knopf of document.querySelectorAll('#auftrag-reiter [data-reiter]')) {
            knopf.setAttribute('aria-selected', String(knopf.dataset.reiter === name));
        }
        document.getElementById('reiter-auftrag').hidden = name !== 'auftrag';
        document.getElementById('reiter-iterationen').hidden = name !== 'iterationen';
        clearTimeout(this._timer);
        if (name === 'iterationen') this.nachladen();
    }

    async nachladen() {
        try {
            const z = await Serverabruf.json(this.seite.adresse('zustand/'));
            if (!z.error) {
                this.seite.zustand = z;
                this.zeigen(z);
            }
        } catch (fehler) {
            this.liste.textContent = `Zustand nicht geladen: ${fehler.message}`;
        }
        this._timer = setTimeout(() => this.nachladen(), Blendermodelliterationen.TAKT_MS);
    }

    zeigen(z) {
        const runden = (z.ergebnis || {}).iterationen || [];
        const vergleich = (z.ergebnis || {}).vergleich || null;
        const kostuem = (z.ergebnis || {}).kostuem || {};
        this.anzahl.textContent = runden.length ? `(${runden.length})` : '';
        this.weiter.disabled = !!z.laeuft;
        this.halt.disabled = !z.laeuft;
        this.stand.textContent = z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}`
            : kostuem.note ? `Bestes Kostüm: Runde ${kostuem.runde_bester}, Abweichung `
                + `${Blendermodellrunde.zahl(kostuem.note.abweichung, 4)}` : '';
        const stand = JSON.stringify([runden, vergleich, kostuem.verlauf]);
        if (stand === this._stand) return;
        this._stand = stand;
        Blendermodellverlauf.zeichnen(this.verlauf, kostuem.verlauf);
        this.vergleich.replaceChildren(...(vergleich ? [this._vergleich(vergleich)] : []));
        this.liste.replaceChildren(...[...runden].reverse().map(r => this.karten.karte(r)));
        if (!runden.length) this.liste.textContent = 'Noch keine Runde abgelegt.';
    }

    _vergleich(v) {
        const datei = name => this.seite.dateiAdresse('iterationen', name);
        const karte = document.createElement('div');
        karte.className = 'blendermodell-vergleich';
        const titel = document.createElement('h3');
        titel.textContent = 'Vergleich: Vorlage und Ergebnisvideo (ChatGPT)';
        karte.appendChild(titel);
        const zeile = document.createElement('div');
        zeile.className = 'blendermodell-vergleichzeile';
        if (v.vorlage) {
            const bild = document.createElement('img');
            bild.src = datei(v.vorlage);
            bild.alt = 'Vorlage';
            zeile.appendChild(bild);
        }
        if (v.video) {
            this._fps = Number(v.video_fps) || Blendermodelliterationen.FPS_VORGABE;
            const video = document.createElement('video');
            video.title = '← / → : ein Bild zurück / vor';
            video.src = datei(v.video);
            video.controls = true;
            video.muted = true;
            video.loop = true;
            zeile.appendChild(video);
        }
        karte.appendChild(zeile);
        return karte;
    }
}
