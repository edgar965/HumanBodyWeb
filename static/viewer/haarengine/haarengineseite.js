import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';
import { Meshpfadliste } from '../mesh/meshpfadliste.js';
import { Meshfigurberichte } from '../meshfigur/meshfigurberichte.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Meshfigurexport } from '../meshfigur/meshfigurexport.js';
import { Meshfigurfrisur } from '../meshfigur/meshfigurfrisur.js';
import { Meshfigurhaar } from '../meshfigur/meshfigurhaar.js';
import { Meshfigurkleidung } from '../meshfigur/meshfigurkleidung.js';
import { Meshfigurspeicher } from '../meshfigur/meshfigurspeicher.js';
import { Haarengineanimation } from './haarengineanimation.js';
import { Haarenginefilmansicht } from './haarenginefilmansicht.js';
import { Haarenginebuehnenmodell } from './haarenginebuehnenmodell.js';
import { Haarenginebegutachtung } from './haarenginebegutachtung.js';
import { Haarengineeinstellungen } from './haarengineeinstellungen.js';
import { Haarenginefotos } from './haarenginefotos.js';
import { Haarengineiterationen } from './haarengineiterationen.js';
import { Haarengineformen } from './haarengineformen.js';
import { Haarenginemalen } from './haarenginemalen.js';

/**
 * Haarengineseite — die Auftragsseite von „2D3D Kleider" (Bereich haarengine): Lauf, Bildauswahl, 3D-Ausgabe, Optionen, Iterationen.
 *
 * DIE 3D-AUSGABE IST DIE VON „MESH TO 3D" (`static/viewer/meshfigur/`, unverändert); sie spricht nur mit `zustand`, `adresse()`,
 * `dateiAdresse()`, `buehne`. Dazu das Modell der letzten Iteration und der Film der Engine auf der Bühne. Der Zustand kommt beim
 * Laden als JSON in die Seite, danach alle `TAKT_MS` vom Server.
 */
export class Haarengineseite {

    static TAKT_MS = 2000;
    static TAKT_RUHE_MS = 6000;
    static NAMEN = {
        netz: 'Netz (TRELLIS)', koerper: 'Körper', grundfigur: 'Grundfigur', iterationen: 'Iterationen', export: 'GLB mit Rig',
        film: 'Film', speichern: 'Speichern',
    };
    static STATUS = {
        angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten',
        wartet: 'Wartet auf Begutachtung',
    };

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('haarengine-daten').textContent);
        // Handle zum Nachsehen im Browser (Bühne, Zustand) — wie `window.__characters` in der Szene.
        const seite = window.__haarengine = new Haarengineseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        Object.assign(this, { jobId, zustand, katalog, _timer: null });
    }

    adresse(pfad) { return `/api/haarengine/${this.jobId}/${pfad}`; }

    /** Eine Datei aus dem Auftrag (`ordner`: eingang, ergebnis, iterationen, vorlage). Die Fotos holt
     *  `fotoAdresse`. */
    dateiAdresse(ordner, name) {
        // Das Netz aus den Fotos (Schritt „netz") liegt unter `netz/`, die Bühne von „Mesh to 3D" fragt es als `eingang` an.
        if (ordner === 'eingang' && /\.glb$/i.test(name || '')) ordner = 'netz';
        return `/api/haarengine/${this.jobId}/datei/${ordner}/${encodeURIComponent(name)}`;
    }

    fotoAdresse(name) {
        return `/api/haarengine/${this.jobId}/datei/eingang/${encodeURIComponent(name)}`;
    }

    aufbauen() {
        const werte = this.zustand.optionen || {};
        for (const gruppe of ['figur', 'netz', 'koerper', 'iterationen', 'film']) {
            Meshoptionenformular.bauen(document.getElementById(`haarengine-optionen-${gruppe}`), this.katalog[gruppe],
                werte[gruppe]);
        }
        const wahl = document.getElementById('ab-schritt');
        for (const s of this.zustand.schritte || []) {
            const option = document.createElement('option');
            option.value = s;
            option.textContent = Haarengineseite.NAMEN[s] || s;
            wahl.appendChild(option);
        }
        document.getElementById('starten').addEventListener('click', () => this.starten());
        document.getElementById('anhalten').addEventListener('click', () => this.anhalten());
        document.getElementById('laufband-anhalten').addEventListener('click', () => this.anhalten());
        document.addEventListener('visibilitychange', () => { if (!document.hidden) this.aktualisieren(); });
        // Der Vorschlag für „Als Genesis-Figur speichern": `Meshfigurspeicher` schriebe „<Name> Mesh".
        const modellname = document.getElementById('modell-name');
        if (modellname && !modellname.value) modellname.value = this.zustand.modell || `${this.zustand.name} 2D3D Kleider`;
        this.einstellungen = new Haarengineeinstellungen(this);
        this.fotos = new Haarenginefotos(this);
        this._pfadstand = null;
        this.iterationen = new Haarengineiterationen(this);
        this.begutachtung = new Haarenginebegutachtung(this);
        this.buehne = new Meshfigurbuehne(this);
        this.buehnenmodell = new Haarenginebuehnenmodell(this, this.buehne);
        this.malen = new Haarenginemalen(this, this.buehne, this.buehnenmodell);
        this.formen = new Haarengineformen(this, this.buehne, this.buehnenmodell);
        this.film = new Haarenginefilmansicht(this);
        this.animation = new Haarengineanimation(this, this.buehne);
        this.berichte = new Meshfigurberichte(this);
        this.export = new Meshfigurexport(this);
        this.haar = new Meshfigurhaar(this);
        this.kleidung = new Meshfigurkleidung(this);
        this.frisur = new Meshfigurfrisur();
        this.speicher = new Meshfigurspeicher(this);
        this.zeigen();
        this.verfolgen();
    }

    // ---------------------------------------------------------------- Lauf

    /** „Neu berechnen" — gesperrt ab dem Klick, damit kein zweiter Lauf auf denselben Arbeitsdateien startet
     *  (Edgar, 27.09.2026). Die Optionen speichert die Seite selbst (`Haarengineeinstellungen`); der Start schickt
     *  sie nicht noch einmal mit. */
    async starten() {
        const ab = document.getElementById('ab-schritt').value;
        try {
            await Knopfsperre.waehrend(document.getElementById('starten'), async () => {
                if (!await this.einstellungen.jetzt()) throw new Error('Eingaben nicht gespeichert');
                const antwort = await Serverabruf.senden(this.adresse('starten/'), { ab });
                if (antwort.error) throw new Error(antwort.error);
            }, 'Startet …');
        } catch (fehler) {
            this.fehler(`Start fehlgeschlagen: ${fehler.daten?.error || fehler.message}`);
            return;
        }
        this.zustand.status = 'laeuft';
        this.zustand.laeuft = true;
        this.zeigen();
        this.verfolgen();
    }

    /** „Anhalten" — vom Knopf des Laufs, vom Band „Läuft im Hintergrund" und vom Reiter „Iterationen". Beendet den
     *  Arbeitsprozess sofort (`Haarenginearbeiter.anhalten`); eine Runde, die gerade rechnet, geht verloren, alles
     *  Abgelegte bleibt. */
    async anhalten() {
        const knopf = document.getElementById('laufband-anhalten');
        knopf.disabled = true;
        document.getElementById('laufband-text').textContent = 'Wird angehalten …';
        try {
            await Serverabruf.senden(this.adresse('anhalten/'), {});
            await this.aktualisieren();
        } catch (fehler) {
            this.fehler(`Anhalten fehlgeschlagen: ${fehler.message}`);
        } finally {
            knopf.disabled = false;
        }
    }

    /** Der Takt läuft IMMER weiter, auch wenn gerade nichts rechnet: Ein Lauf kann von außen gestartet werden
     *  (Skript, zweiter Tab) — bis 30.09.2026 hörte die Seite nach dem letzten Lauf auf zu fragen und zeigte ihn dann nie.
     *  Im Leerlauf seltener, und nicht in einem verdeckten Tab (`visibilitychange` holt es nach). */
    verfolgen() {
        if (this._timer) clearTimeout(this._timer);
        this._timer = setTimeout(async () => {
            if (!document.hidden) await this.aktualisieren();
            this.verfolgen();
        }, this.zustand.laeuft ? Haarengineseite.TAKT_MS : Haarengineseite.TAKT_RUHE_MS);
    }

    async aktualisieren() {
        try {
            // `error` im Zustand ist die Fehlermeldung des AUFTRAGS (`error_message`), kein Übertragungsfehler — ein
            // Fehler der Anfrage selbst wirft `Serverabruf.json`. BlenderModel wirft hier auf `z.error`: Ein Lauf, der
            // scheitert, bleibt dort auf „Läuft" stehen, und die Meldung trägt den Vorsatz „Zustand nicht lesbar".
            const z = await Serverabruf.json(this.adresse('zustand/'));
            this.zustand = z;
            this.zeigen();
        } catch (fehler) {
            this.fehler(`Zustand nicht lesbar: ${fehler.message}`);
        }
    }

    // -------------------------------------------------------------- Anzeige

    fehler(text) {
        const feld = document.getElementById('fehler');
        feld.textContent = text || '';
        feld.classList.toggle('hb-versteckt', !text);
    }

    zeigen() {
        const z = this.zustand;
        const status = document.getElementById('auftrag-status');
        status.textContent = Haarengineseite.STATUS[z.status] || z.status;
        status.className = `bildmodell-status hb-${z.status === 'fertig' ? 'gut' : z.status === 'gescheitert' ? 'schlecht' : 'laeuft'}`;
        document.getElementById('fortschritt').style.width = `${z.progress || 0}%`;
        document.getElementById('fortschritt-text').textContent =
            z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}` : (z.progress_detail || '');
        const start = document.getElementById('starten');
        start.disabled = !!z.laeuft;
        start.querySelector('span').textContent = z.laeuft ? 'Berechnet …' : 'Neu berechnen';
        document.getElementById('anhalten').disabled = !z.laeuft;
        // Das Band steht über beiden Reitern: „läuft im Hintergrund" muss man sehen, egal wo man gerade ist.
        document.getElementById('laufband').hidden = !z.laeuft;
        if (z.laeuft) {
            document.getElementById('laufband-text').textContent =
                `Läuft im Hintergrund — ${z.progress || 0} % · ${z.progress_detail || ''}`;
        }
        document.getElementById('optionen-gesperrt').hidden = !z.laeuft;
        this.einstellungen.sperren(!!z.laeuft);
        this.fehler(z.status === 'gescheitert' ? (z.error || 'Fehlgeschlagen — siehe auftrag.log') : '');
        this.schritte();
        this.fotos.zeigen(z);
        this.pfade(z);
        this.iterationen.zeigen(z);
        this.begutachtung.zeigen(z);
        this.berichte.zeigen(z);
        this.haar.zeigen(z);
        this.kleidung.zeigen(z);
        this.frisur.zeigen(z);
        this.buehne.zeigen(z);
        this.buehnenmodell.zeigen(z);
        this.film.zeigen(z);
        this.animation.zeigen(z);
        this.export.zeigen(z);
        this.speicher.zeigen(z);
    }

    /** „Gespeichert unter" — die Ablageorte zum Kopieren, neu gezeichnet nur bei Änderung. */
    pfade(z) {
        const stand = JSON.stringify(z.pfade);
        if (stand === this._pfadstand) return;
        this._pfadstand = stand;
        Meshpfadliste.zeichnen(document.getElementById('haarengine-pfade'), z.pfade);
    }

    schritte() {
        const z = this.zustand;
        const liste = document.getElementById('schritte');
        liste.innerHTML = '';
        const dauer = (z.ergebnis || {}).dauer || {};
        const jetzt = (z.schritte || []).indexOf(z.schritt);
        (z.schritte || []).forEach((s, i) => {
            const punkt = document.createElement('li');
            let art = 'offen';
            if (dauer[s] !== undefined && (!z.laeuft || i < jetzt)) art = 'fertig';
            if (z.laeuft && i === jetzt) art = 'laeuft';
            if (z.status === 'gescheitert' && i === jetzt) art = 'fehler';
            punkt.className = `meshfigur-schritt meshfigur-schritt-${art}`;
            punkt.textContent = Haarengineseite.NAMEN[s] || s;
            if (dauer[s] !== undefined) {
                const zeit = document.createElement('small');
                zeit.textContent = ` ${Math.round(dauer[s])} s`;
                punkt.appendChild(zeit);
            }
            liste.appendChild(punkt);
        });
    }
}
