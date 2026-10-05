import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Engine2d3dKleiderNachbesserungKi } from './engine2d3dkleidernachbesserungski.js';

/**
 * Engine2d3dKleiderNachbesserung — der Block „Nachbesserungen" unten auf der Auftragsseite, mit dem die Nachbesserung gestartet wird (05.10.2026).
 *
 * Edgar: „mache mir unten im Job das UI, mit dem ich die Iterationen starten kann für die Nachbesserungen. Die Anzahl der Iterationen
 * möchte ich setzen können, Vorgabe 1." Jede Iteration lässt die gewählte KI (`Engine2d3dKleiderNachbesserungKi`: Lokal oder Remote) Vorlage und letzte Runde
 * ansehen, ein Rezept schreiben und die Runde rechnen (Paket `Edgar` in `2d3DIterationen`, Anbindung `core/api/engine2d3dkleidernachbesserung.py`).
 *
 * Der Block steht AUSSERHALB der Reiter und hängt nicht an der Seitenklasse (`Engine2d3dKleiderseite`): Er lädt als eigenes Modulskript, damit er
 * auch dann arbeitet, wenn die Seite wegen eines fehlenden Moduls nicht fertig wird. Ein Lauf ist ein eigener Prozess auf dem Server; hier wird nur
 * gestartet, angehalten und der Zustand gelesen (alle `TAKT_LAUF_MS` während eines Laufs, sonst alle `TAKT_RUHE_MS`).
 */
export class Engine2d3dKleiderNachbesserung {

    static TAKT_LAUF_MS = 4000;
    static TAKT_RUHE_MS = 20000;

    static starten(jobId) {
        const block = new Engine2d3dKleiderNachbesserung(jobId);
        block.laden();
        return block;
    }

    constructor(jobId) {
        this.jobId = jobId;
        const $ = id => document.getElementById(id);
        this.karte = $('nachbesserung');
        this.runden = $('nachbesserung-runden');
        this.start = $('nachbesserung-start');
        this.stopp = $('nachbesserung-anhalten');
        this.meldung = $('nachbesserung-meldung');
        this.status = $('nachbesserung-status');
        this.verlauf = $('nachbesserung-verlauf');
        this.ki = new Engine2d3dKleiderNachbesserungKi();
        this.timer = null;
        if (!this.karte) {
            console.warn('[2D3D Kleider] Nachbesserung: Block fehlt in der Vorlage');
            return;
        }
        this.start.addEventListener('click', () => this.losgehen());
        this.stopp.addEventListener('click', () => this.anhalten());
    }

    adresse(rest = '') {
        return `/api/engine2d3dkleider/${this.jobId}/nachbesserung/${rest}`;
    }

    // ------------------------------------------------------------------ Server

    async laden() {
        if (!this.karte) return;
        clearTimeout(this.timer);
        let lauf = false;
        try {
            const antwort = await Serverabruf.json(this.adresse());
            this.zeigen(antwort);
            lauf = antwort.lauf?.status === 'laeuft';
        } catch (fehler) {
            this.status.textContent = `Stand nicht lesbar: ${fehler.daten?.error || fehler.message}`;
        }
        this.timer = setTimeout(() => this.laden(),
            lauf ? Engine2d3dKleiderNachbesserung.TAKT_LAUF_MS : Engine2d3dKleiderNachbesserung.TAKT_RUHE_MS);
    }

    /** Die Zahl der Iterationen: ganze Zahl von 1 bis `max`; ein leeres oder ungültiges Feld gilt als 1 (die Vorgabe). */
    zahl(max) {
        const wert = Math.floor(Number(this.runden.value));
        return Number.isFinite(wert) && wert >= 1 ? Math.min(wert, max) : 1;
    }

    async losgehen() {
        this.meldung.textContent = '';
        const max = Number(this.runden.max) || 50;
        const runden = this.zahl(max);
        this.runden.value = String(runden);
        try {
            await Knopfsperre.waehrend(this.start, async () => {
                const antwort = await Serverabruf.senden(this.adresse('starten/'), { runden, ki: this.ki.wahl() });
                if (antwort.error) throw new Error(antwort.error);
                this.zeigen(antwort);
            }, 'Startet …');
        } catch (fehler) {
            this.meldung.textContent = `Nicht gestartet: ${fehler.daten?.error || fehler.message}`;
            this.start.disabled = false;
            return;
        }
        this.laden();
    }

    async anhalten() {
        this.meldung.textContent = '';
        try {
            await Knopfsperre.waehrend(this.stopp, async () => {
                const antwort = await Serverabruf.senden(this.adresse('anhalten/'), {});
                if (antwort.error) throw new Error(antwort.error);
                this.zeigen(antwort);
            }, 'Hält an …');
        } catch (fehler) {
            this.meldung.textContent = `Nicht angehalten: ${fehler.daten?.error || fehler.message}`;
            this.stopp.disabled = false;
        }
    }

    // ------------------------------------------------------------------ Anzeige

    /** Zustand des Blocks: Knöpfe, Statuszeile, Verlauf. `antwort`: `{lauf, kann, grund, standard, hoechstens, ki}`. */
    zeigen(antwort) {
        const lauf = antwort.lauf || {};
        const laeuft = lauf.status === 'laeuft';
        this.ki.laden(antwort.ki);
        this.ki.sperren(laeuft);
        this.runden.max = String(antwort.hoechstens || 50);
        if (!this.runden.dataset.gesetzt) {                 // die Vorgabe nur einmal einsetzen — was der Nutzer eingibt, bleibt
            this.runden.value = String(antwort.standard || 1);
            this.runden.dataset.gesetzt = '1';
        }
        this.runden.disabled = laeuft;
        this.start.disabled = !antwort.kann;
        this.start.title = antwort.kann ? 'Startet die Iterationen: je Iteration sieht die gewählte KI Vorlage und letzte Runde an, schreibt ein Rezept und die Runde rechnet'
            : antwort.grund;
        this.stopp.disabled = !laeuft || !!antwort.anhalten;
        this.status.textContent = this.statuszeile(antwort, lauf);
        this.eintraege(lauf.eintraege || []);
    }

    statuszeile(antwort, lauf) {
        const ki = lauf.ki?.text ? ` [${lauf.ki.text}]` : '';
        if (lauf.status === 'laeuft') {
            const halt = antwort.anhalten ? ' (Anhalten verlangt: die laufende Runde rechnet zu Ende)' : '';
            return `Iteration ${lauf.nr || 0} von ${lauf.runden}${ki}: ${lauf.meldung || 'startet …'}${halt}`;
        }
        if (lauf.status === 'bereit' || !lauf.status) return antwort.kann ? 'Bereit.' : antwort.grund;
        const kosten = lauf.kosten_usd != null ? ` · Kosten ${Number(lauf.kosten_usd).toFixed(2)} USD` : '';
        const ende = { fertig: 'Fertig', angehalten: 'Angehalten', fehler: 'Fehler', abgebrochen: 'Abgebrochen' }[lauf.status] || lauf.status;
        return `${ende}${ki}: ${lauf.meldung || ''}${kosten}${antwort.kann ? '' : ` — ${antwort.grund}`}`;
    }

    eintraege(liste) {
        this.verlauf.replaceChildren();
        for (const e of [...liste].reverse()) this.verlauf.appendChild(this.eintrag(e));
    }

    /** Eine Iteration: Kopfzeile (Runde, Note, übernommen, Kosten, Dauer) und aufklappbar Urteil, Abweichungen, Rezept. */
    eintrag(e) {
        const zeile = document.createElement('details');
        zeile.className = 'nachbesserung-eintrag';
        const kopf = document.createElement('summary');
        const teile = [`Iteration ${e.i}`, `Runde ${e.runde}`];
        if (e.note != null) teile.push(`Gesamtnote ${Number(e.note).toFixed(4)}`);
        if (e.uebernommen != null) teile.push(e.uebernommen ? 'übernommen' : 'verworfen');
        if (e.offen != null) teile.push(`${e.offen} Abweichung(en) Schwere 1–2 gemeldet`);
        if (e.kosten_usd != null) teile.push(`${Number(e.kosten_usd).toFixed(2)} USD`);
        if (e.dauer_agent_s != null) teile.push(`KI ${Math.round(e.dauer_agent_s)} s`);
        if (e.dauer_runde_s != null) teile.push(`Runde ${Math.round(e.dauer_runde_s)} s`);
        kopf.textContent = `${teile.join(' · ')} — ${e.ergebnis || ''}`;
        zeile.appendChild(kopf);
        const text = (klasse, wert) => {
            const p = document.createElement('p');
            p.className = klasse;
            p.textContent = wert;
            return p;
        };
        zeile.appendChild(text('nachbesserung-urteil', e.urteil || '(kein Urteil)'));
        if (e.kommentar && e.kommentar !== e.urteil) zeile.appendChild(text('hb-hinweis', `Kommentar der Runde: ${e.kommentar}`));
        if (e.fehler) zeile.appendChild(text('nachbesserung-fehler', `Fehler in der Runde: ${e.fehler}`));
        for (const a of e.abweichungen || []) {
            zeile.appendChild(text('nachbesserung-abweichung',
                `[${a.schwere}] ${a.teil}: Vorlage — ${a.vorlage}; Render — ${a.render}; Maßnahme — ${a.massnahme}`));
        }
        if ((e.aufrufe || []).length) {
            const rezept = document.createElement('pre');
            rezept.className = 'nachbesserung-rezept';
            rezept.textContent = e.aufrufe.join('\n');
            zeile.appendChild(rezept);
        }
        return zeile;
    }
}
