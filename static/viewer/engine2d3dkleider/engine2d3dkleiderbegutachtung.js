import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderbegutachtung — das Formular im Reiter „Iterationen", mit dem eine Runde begutachtet wird (30.09.2026).
 *
 * Im Modus „Begutachtung" wartet der Auftrag nach jeder Runde („Wartet auf Begutachtung"). Wer die Bilder angesehen hat —
 * Fable oder der Nutzer — schreibt ein Rezept: Aufrufe an `ModellMitKleidern` (`m.kleid_nur('g9_base_shirt')`, eine je Zeile)
 * und einen Kommentar, und „Runde rechnen" schickt beides an `POST …/begutachtung/`. Die Funktionsliste kommt vom Server
 * (`GET /api/engine2d3dkleider/funktionen/`) und steht aufklappbar unter dem Formular; „Rezept" öffnet die wirksamen Aufrufe aller
 * übernommenen Runden als Text.
 */
export class Engine2d3dKleiderbegutachtung {

    static FUNKTIONEN = '/api/engine2d3dkleider/funktionen/';

    constructor(seite) {
        this.seite = seite;
        const $ = id => document.getElementById(id);
        this.karte = $('begutachtung');
        this.aufrufe = $('begutachtung-aufrufe');
        this.kommentar = $('begutachtung-kommentar');
        this.knopf = $('begutachtung-runde');
        this.automatisch = $('begutachtung-automatisch');
        this.runden = $('begutachtung-runden');
        this.meldung = $('begutachtung-meldung');
        this.stand = $('begutachtung-stand');
        this.liste = $('begutachtung-funktionen');
        this.rezept = $('begutachtung-rezept');
        if (!this.karte) return;
        this.knopf.addEventListener('click', () => this.senden(false));
        this.automatisch.addEventListener('click', () => this.senden(true));
        this.rezept.href = seite.adresse('rezept/');
        this._funktionen();
    }

    async _funktionen() {
        try {
            const daten = await Serverabruf.json(Engine2d3dKleiderbegutachtung.FUNKTIONEN);
            this.liste.replaceChildren();
            for (const f of daten.funktionen || []) {
                const zeile = document.createElement('div');
                zeile.className = 'begutachtung-funktion';
                const code = document.createElement('code');
                code.textContent = `${daten.objekt}.${f.name}${f.signatur}`;
                const text = document.createElement('span');
                text.className = 'hb-hinweis';
                text.textContent = ` — ${f.text}`;
                zeile.append(code, text);
                this.liste.appendChild(zeile);
            }
        } catch (fehler) {
            this.liste.textContent = `Funktionen nicht lesbar: ${fehler.message}`;
        }
    }

    /**
     * `automatisch`: statt des Rezepts im Feld schreibt `IterationModell` (Ordner 2d3DIterationen) die Rezepte selbst —
     * `runden` Runden nacheinander, jede mit Befund; der Kommentar geht mit.
     */
    async senden(automatisch) {
        const rumpf = { aufrufe: automatisch ? '' : this.aufrufe.value, kommentar: this.kommentar.value,
            automatisch: !!automatisch, runden: automatisch ? Number(this.runden.value) || 1 : 1 };
        const knopf = automatisch ? this.automatisch : this.knopf;
        this.meldung.textContent = '';
        try {
            await Knopfsperre.waehrend(knopf, async () => {
                const antwort = await Serverabruf.senden(this.seite.adresse('begutachtung/'), rumpf);
                if (antwort.error) throw new Error(antwort.error);
            }, 'Startet …');
        } catch (fehler) {
            this.meldung.textContent = `Runde nicht gestartet: ${fehler.daten?.error || fehler.message}`;
            knopf.disabled = false;
            return;
        }
        this.aufrufe.value = '';
        this.kommentar.value = '';
        this.seite.zustand.laeuft = true;
        this.seite.zustand.status = 'laeuft';
        this.seite.zeigen();
        this.seite.verfolgen();
    }

    zeigen(z) {
        if (!this.karte) return;
        const o = (z.optionen || {}).iterationen || {};
        const b = (z.ergebnis || {}).begutachtung || {};
        this.karte.hidden = o.modus !== 'begutachtung';
        this.knopf.disabled = !!z.laeuft;
        this.automatisch.disabled = !!z.laeuft;
        const zustand = z.laeuft ? 'Eine Runde rechnet …'
            : z.status === 'wartet' ? `Runde ${b.runde || '–'} gerechnet — wartet auf Begutachtung`
            : b.runde ? `Letzte Runde ${b.runde}` : 'Noch keine Runde — „Neu berechnen" rechnet die Ausgangslage';
        this.stand.textContent = b.fehler ? `${zustand} · Rezept der letzten Runde fehlerhaft: ${b.fehler}` : zustand;
    }
}
