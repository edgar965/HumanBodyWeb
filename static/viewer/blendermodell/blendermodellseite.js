import { Fehlerband } from '../gemeinsam/fehlerband.js';
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
import { Blendermodellanimation } from './blendermodellanimation.js';
import { Blendermodellblenderfilm } from './blendermodellblenderfilm.js';
import { Blendermodellleertaste } from './blendermodellleertaste.js';
import { Blendermodellbuehnenmodell } from './blendermodellbuehnenmodell.js';
import { Blendermodelleinstellungen } from './blendermodelleinstellungen.js';
import { Blendermodellfotos } from './blendermodellfotos.js';
import { Blendermodelliterationen } from './blendermodelliterationen.js';

/**
 * Blendermodellseite — die Auftragsseite von „BlenderModel" (29.09.2026): Lauf, Bildauswahl, 3D-Ausgabe, Optionen.
 * DIE 3D-AUSGABE IST DIE VON „MESH TO 3D" (`static/viewer/meshfigur/`, unverändert); sie spricht nur mit `zustand`,
 * `adresse()`, `dateiAdresse()`, `buehne`. Dazu Iterationsmodell und Blender-Film auf der Bühne.
 * Der Zustand kommt beim Laden als JSON in die Seite, danach alle `TAKT_MS` vom Server.
 */
export class Blendermodellseite {

    static TAKT_MS = 2000;
    static TAKT_RUHE_MS = 6000;
    static NAMEN = {
        grundfigur: 'Grundfigur', kostuem: 'Iterationen', export: 'GLB mit Rig', blender: 'Blender', speichern: 'Speichern',
    };
    static STATUS = {
        angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten',
    };

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('blendermodell-daten').textContent);
        // Handle zum Nachsehen im Browser (Bühne, Zustand) — wie `window.__characters` in der Szene.
        const seite = window.__blendermodell = new Blendermodellseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        Object.assign(this, { jobId, zustand, katalog, _timer: null });
        this.fehlerband = new Fehlerband(); // dauerhaft, mit OK wegklickbar (02.10.2026)
    }

    adresse(pfad) { return `/api/blendermodell/${this.jobId}/${pfad}`; }

    /** Eine Datei aus dem Auftrag. Die Module der Figur kennen nur „eingang" (ihr Netz) und „ergebnis"; das Netz liegt
     *  hier in `netz/` (`Blendermodellablage`), also wird „eingang" dorthin umgeleitet. Die Fotos holt `fotoAdresse`. */
    dateiAdresse(ordner, name) {
        const echt = ordner === 'eingang' ? 'netz' : ordner;
        return `/api/blendermodell/${this.jobId}/datei/${echt}/${encodeURIComponent(name)}`;
    }

    fotoAdresse(name) {
        return `/api/blendermodell/${this.jobId}/datei/eingang/${encodeURIComponent(name)}`;
    }

    aufbauen() {
        const werte = this.zustand.optionen || {};
        for (const gruppe of ['figur', 'kostuem', 'blender']) {
            Meshoptionenformular.bauen(document.getElementById(`blendermodell-optionen-${gruppe}`), this.katalog[gruppe],
                werte[gruppe]);
        }
        const wahl = document.getElementById('ab-schritt');
        for (const s of this.zustand.schritte || []) {
            const option = document.createElement('option');
            option.value = s;
            option.textContent = Blendermodellseite.NAMEN[s] || s;
            wahl.appendChild(option);
        }
        document.getElementById('starten').addEventListener('click', () => this.starten());
        document.getElementById('anhalten').addEventListener('click', () => this.anhalten());
        document.getElementById('laufband-anhalten').addEventListener('click', () => this.anhalten());
        document.addEventListener('visibilitychange', () => { if (!document.hidden) this.aktualisieren(); });
        // Der Vorschlag für „Als Genesis-Figur speichern": `Meshfigurspeicher` schriebe „<Name> Mesh".
        const modellname = document.getElementById('modell-name');
        if (modellname && !modellname.value) modellname.value = this.zustand.modell || `${this.zustand.name} BlenderModel`;
        this.einstellungen = new Blendermodelleinstellungen(this);
        this.fotos = new Blendermodellfotos(this);
        this._pfadstand = null;
        this.iterationen = new Blendermodelliterationen(this);
        this.buehne = new Meshfigurbuehne(this);
        this.buehnenmodell = new Blendermodellbuehnenmodell(this, this.buehne, 'modell');
        this.sichtmodell = new Blendermodellbuehnenmodell(this, this.buehne, 'sicht');
        this.buehnenmodell.geschwister = this.sichtmodell;
        this.sichtmodell.geschwister = this.buehnenmodell;
        this.blenderfilm = new Blendermodellblenderfilm(this);
        this.animation = new Blendermodellanimation(this, this.buehne);
        this.leertaste = new Blendermodellleertaste(this);
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
     *  (Edgar, 27.09.2026). Die Optionen speichert die Seite selbst (`Blendermodelleinstellungen`); der Start schickt
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
     *  Arbeitsprozess sofort (`Blendermodellarbeiter.anhalten`); eine Runde, die gerade rechnet, geht verloren, alles
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
        }, this.zustand.laeuft ? Blendermodellseite.TAKT_MS : Blendermodellseite.TAKT_RUHE_MS);
    }

    async aktualisieren() {
        try {
            const z = await Serverabruf.json(this.adresse('zustand/'));
            if (z.error) throw new Error(z.error);
            this.zustand = z;
            this.zeigen();
        } catch (fehler) {
            this.fehlerband.lesefehler(`Zustand nicht lesbar: ${fehler.message}`);
        }
    }

    // -------------------------------------------------------------- Anzeige

    /** Meldung einer gescheiterten Aktion — bleibt stehen, bis jemand OK klickt (`Fehlerband`). */
    fehler(text) {
        this.fehlerband.meldung(text);
    }

    zeigen() {
        const z = this.zustand;
        const status = document.getElementById('auftrag-status');
        status.textContent = Blendermodellseite.STATUS[z.status] || z.status;
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
        this.fehlerband.auftrag(z); // der Takt löscht eine stehende Meldung NICHT mehr
        this.schritte();
        this.fotos.zeigen(z);
        this.pfade(z);
        this.iterationen.zeigen(z);
        this.berichte.zeigen(z);
        this.haar.zeigen(z);
        this.kleidung.zeigen(z);
        this.frisur.zeigen(z);
        this.buehne.zeigen(z);
        this.buehnenmodell.zeigen(z);
        this.sichtmodell.zeigen(z);
        this.blenderfilm.zeigen(z);
        this.animation.zeigen(z);
        this.export.zeigen(z);
        this.speicher.zeigen(z);
    }

    /** „Gespeichert unter" — die Ablageorte zum Kopieren, neu gezeichnet nur bei Änderung. */
    pfade(z) {
        const stand = JSON.stringify(z.pfade);
        if (stand === this._pfadstand) return;
        this._pfadstand = stand;
        Meshpfadliste.zeichnen(document.getElementById('blendermodell-pfade'), z.pfade);
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
            punkt.textContent = Blendermodellseite.NAMEN[s] || s;
            if (dauer[s] !== undefined) {
                const zeit = document.createElement('small');
                zeit.textContent = ` ${Math.round(dauer[s])} s`;
                punkt.appendChild(zeit);
            }
            liste.appendChild(punkt);
        });
    }
}
