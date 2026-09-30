/**
 * Blendermodelliterationen — der zweite Reiter der Auftragsseite: die Runden des Iterationslaufs (29.09.2026).
 *
 * Edgar: „mach in dem Job Iterationen so dass man den Fortschritt sehen kann, in einem zweiten Tab des Jobs" und
 * „… einen Code der dann später per Knopfdruck durch alle Iterationen bis zum fertigen Ergebnis läuft. Ich kann
 * beliebig Iterationen weiter laufen lassen". Oben die Einstellungen der Iterationen (Runden, Kandidaten, Prüf-KI …,
 * das Formular baut `Blendermodellseite`), „Weiter iterieren" (startet NUR den Schritt „kostuem", ab dem besten
 * bisherigen Modell), die Kurve aller Runden (`Blendermodellverlauf`), der Vergleich Vorlage/Ergebnisvideo und die
 * Tabelle der Runden (`Blendermodellrundentabelle`, Stand 30.09.2026 statt der Karten).
 *
 * Den Zustand holt die Seite selbst im Takt (`Blendermodellseite.verfolgen`) und ruft `zeigen`; dieses Modul hat
 * keinen eigenen Takt mehr.
 */
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Blendermodellbildfenster } from './blendermodellbildfenster.js';
import { Blendermodellrundenbilder } from './blendermodellrundenbilder.js';
import { Blendermodellrundentabelle } from './blendermodellrundentabelle.js';
import { Blendermodellrundenzeilen } from './blendermodellrundenzeilen.js';
import { Blendermodellverlauf } from './blendermodellverlauf.js';

export class Blendermodelliterationen {

    /** Ohne gemessene Bildrate im Vergleich (`ergebnis.vergleich.video_fps`). */
    static FPS_VORGABE = 30;

    constructor(seite) {
        this.seite = seite;
        const $ = id => document.getElementById(id);
        this.vergleich = $('iterationen-vergleich');
        this.anzahl = $('iterationen-anzahl');
        this.verlauf = $('iterationen-verlauf');
        this.weiter = $('iterationen-weiter');
        this.halt = $('iterationen-anhalten');
        this.stand = $('iterationen-stand');
        this.ki = $('iterationen-ki');
        const datei = name => seite.dateiAdresse('iterationen', name);
        const bilder = new Blendermodellrundenbilder(datei, name => seite.fotoAdresse(name), new Blendermodellbildfenster());
        // Erst nach dem Bau der Seite da: Die Modelle der Bühne entstehen nach den Iterationen.
        bilder.dreid = (runde, art) => seite[art === 'sicht' ? 'sichtmodell' : 'buehnenmodell'].waehlen(runde);
        this.tabelle = new Blendermodellrundentabelle(seite, new Blendermodellrundenzeilen(datei, bilder));
        this._stand = '';
        this._fps = Blendermodelliterationen.FPS_VORGABE;
        for (const knopf of document.querySelectorAll('#auftrag-reiter [data-reiter]')) {
            knopf.addEventListener('click', () => this.umschalten(knopf.dataset.reiter));
        }
        this.weiter.addEventListener('click', () => this.weiterIterieren());
        this.halt.addEventListener('click', () => this.seite.anhalten());
        // In der Erfassungsphase: Chromes eigene Videosteuerung springt bei ←/→ sonst 5 s.
        document.addEventListener('keydown', ereignis => this._taste(ereignis), true);
    }

    /** Nur den Schritt „kostuem" rechnen — mit den Einstellungen, die oben im Reiter stehen (schon gespeichert). */
    async weiterIterieren() {
        const beschriftung = this.weiter.querySelector('span');
        const text = beschriftung.textContent;
        try {
            await Knopfsperre.waehrend(this.weiter, async () => {
                if (!await this.seite.einstellungen.jetzt()) throw new Error('Einstellungen nicht gespeichert');
                const antwort = await Serverabruf.senden(this.seite.adresse('starten/'), { ab: 'kostuem', bis: 'kostuem' });
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
        // Im Bildfenster blättern ←/→ die Blickwinkel (`Blendermodellbildfenster`), nicht das Video.
        if (document.querySelector('dialog[open]')) return;
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
        if (name === 'iterationen') this.seite.aktualisieren();
    }

    zeigen(z) {
        const e = z.ergebnis || {};
        const runden = e.iterationen || [];
        const vergleich = e.vergleich || null;
        const kostuem = e.kostuem || {};
        const o = (z.optionen || {}).kostuem || {};
        this.anzahl.textContent = runden.length ? `(${runden.length})` : '';
        this.weiter.disabled = !!z.laeuft;
        this.halt.disabled = !z.laeuft;
        this.stand.textContent = z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}`
            : kostuem.note ? `Bestes Modell: Runde ${kostuem.runde_bester}, Abweichung `
                + `${Blendermodellrundenzeilen.zahl(kostuem.note.abweichung, 4)}` : '';
        this.ki.textContent = o.pruefki && o.pruefki !== 'aus'
            ? `Prüf-KI: ${o.pruefki}, alle ${o.pruefki_alle} Runden` : 'Prüf-KI: aus';
        const verlauf = kostuem.verlauf || [];
        const stand = JSON.stringify([vergleich, verlauf.length, verlauf[verlauf.length - 1]]);
        if (stand !== this._stand) {
            this._stand = stand;
            Blendermodellverlauf.zeichnen(this.verlauf, kostuem.verlauf);
            this.vergleich.replaceChildren(...(vergleich ? [this._vergleich(vergleich)] : []));
        }
        this.tabelle.zeigen(z);
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
