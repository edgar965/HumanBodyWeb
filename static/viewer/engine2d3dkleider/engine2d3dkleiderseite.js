import { Fehlerband } from '../gemeinsam/fehlerband.js';
import { Knopfsperre } from '../gemeinsam/knopfsperre.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';
import { Meshpfadliste } from '../mesh/meshpfadliste.js';
import { Meshfigurberichte } from '../meshfigur/meshfigurberichte.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Meshfigurfrisur } from '../meshfigur/meshfigurfrisur.js';
import { Meshfigurhaar } from '../meshfigur/meshfigurhaar.js';
import { Meshfigurkleidung } from '../meshfigur/meshfigurkleidung.js';
import { Meshfigurspeicher } from '../meshfigur/meshfigurspeicher.js';
import { Engine2d3dKleideranimation } from './engine2d3dkleideranimation.js';
import { Engine2d3dKleideranimexport } from './engine2d3dkleideranimexport.js';
import { Engine2d3dKleiderfilmansicht } from './engine2d3dkleiderfilmansicht.js';
import { Engine2d3dKleiderbuehnenmodell } from './engine2d3dkleiderbuehnenmodell.js';
import { Engine2d3dKleiderbegutachtung } from './engine2d3dkleiderbegutachtung.js';
import { Engine2d3dKleidereinstellungen } from './engine2d3dkleidereinstellungen.js';
import { Engine2d3dKleiderfotos } from './engine2d3dkleiderfotos.js';
import { Engine2d3dKleideriterationen } from './engine2d3dkleideriterationen.js';
import { Engine2d3dKleiderformen } from './engine2d3dkleiderformen.js';
import { Engine2d3dKleidermalen } from './engine2d3dkleidermalen.js';
import { Engine2d3dKleidermeshkarte } from './engine2d3dkleidermeshkarte.js';
import { Engine2d3dKleidernetzansicht } from './engine2d3dkleidernetzansicht.js';
import { Engine2d3dKleiderrender } from './engine2d3dkleiderrender.js';
import { Engine2d3dKleidersegmentierung } from './engine2d3dkleidersegmentierung.js';
import { Engine2d3dKleiderstuecke } from './engine2d3dkleiderstuecke.js';
import { Engine2d3dKleidervorbereitung } from './engine2d3dkleidervorbereitung.js';
import { Engine2d3dKleiderveraltet } from './engine2d3dkleiderveraltet.js';

/**
 * Engine2d3dKleiderseite — die Auftragsseite von „2D3D Kleider" (Bereich engine2d3dkleider): Lauf, Bildauswahl, 3D-Ausgabe, Optionen, Iterationen.
 *
 * DIE 3D-AUSGABE IST DIE VON „MESH TO 3D" (`static/viewer/meshfigur/`, unverändert); sie spricht nur mit `zustand`, `adresse()`,
 * `dateiAdresse()`, `buehne`. Dazu das Modell der letzten Iteration und der Film der Engine auf der Bühne. Der Zustand kommt beim
 * Laden als JSON in die Seite, danach alle `TAKT_MS` vom Server.
 */
export class Engine2d3dKleiderseite {

    static TAKT_MS = 2000;
    static TAKT_RUHE_MS = 6000;
    static NAMEN = {
        vorbereitung: 'Vorbereitung', netz: 'Netz', segmentierung: 'Segmentierung (optional)', koerper: 'Körper', grundfigur: 'Grundfigur', kleiderstuecke: 'Kleiderstücke', iterationen: 'Iterationen',
        export: 'GLB mit Rig', film: 'Film', speichern: 'Speichern',
    };
    static STATUS = {
        angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten',
        wartet: 'Wartet auf Begutachtung',
    };

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('engine2d3dkleider-daten').textContent);
        // Handle zum Nachsehen im Browser (Bühne, Zustand) — wie `window.__characters` in der Szene.
        const seite = window.__engine2d3dkleider = new Engine2d3dKleiderseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        Object.assign(this, { jobId, zustand, katalog, _timer: null });
        this.fehlerband = new Fehlerband(); // dauerhaft, mit OK wegklickbar (02.10.2026)
        this.veraltet = new Engine2d3dKleiderveraltet(); // offener Tab älter als der Code auf dem Server → Band „Neu laden"
    }

    adresse(pfad) { return `/api/engine2d3dkleider/${this.jobId}/${pfad}`; }

    /** Eine Datei aus dem Auftrag (`ordner`: eingang, ergebnis, iterationen, vorlage). Die Fotos holt
     *  `fotoAdresse`. */
    dateiAdresse(ordner, name) {
        // Das Netz aus den Fotos (Schritt „netz") liegt unter `netz/`, die Bühne von „Mesh to 3D" fragt es als `eingang` an.
        if (ordner === 'eingang' && /\.glb$/i.test(name || '')) ordner = 'netz';
        return `/api/engine2d3dkleider/${this.jobId}/datei/${ordner}/${encodeURIComponent(name)}`;
    }

    fotoAdresse(name) {
        return `/api/engine2d3dkleider/${this.jobId}/datei/eingang/${encodeURIComponent(name)}`;
    }

    aufbauen() {
        const werte = this.zustand.optionen || {};
        for (const gruppe of Object.keys(this.katalog).filter(g => document.getElementById('engine2d3dkleider-optionen-' + g))) {      // alle Gruppen des Katalogs mit Behälter (04.10.2026: dazu die Renderregler)
            Meshoptionenformular.bauen(document.getElementById(`engine2d3dkleider-optionen-${gruppe}`), this.katalog[gruppe],
                werte[gruppe]);
        }
        const wahl = document.getElementById('ab-schritt');
        const ende = document.getElementById('bis-schritt');
        const bisende = document.createElement('option');
        bisende.value = '';
        bisende.textContent = 'Ende';
        ende.appendChild(bisende);
        for (const s of this.zustand.schritte || []) {
            for (const auswahl of [wahl, ende]) {
                const option = document.createElement('option');
                option.value = s;
                option.textContent = Engine2d3dKleidermeshkarte.schrittname(s, this.zustand, Engine2d3dKleiderseite.NAMEN[s] || s);
                auswahl.appendChild(option);
            }
        }
        // Die Reiter bindet `Seitenreiter` im Template, in einem kleinen Modul ohne three.js (03.10.2026, Edgar: „Iterationen“ nicht
        // anklickbar): Hing der Klick an dieser Klasse, waren die Reiter tot, bis dreißig Module geladen und alle Bausteine gebaut waren
        // — und für immer, wenn einer davon beim Aufbau warf. Die Seite hört nur noch auf den Wechsel.
        document.getElementById('auftrag-reiter').addEventListener('reiterwechsel', e => this.reiterGewechselt(e.detail.name));
        document.getElementById('starten').addEventListener('click', () => this.starten());
        document.getElementById('anhalten').addEventListener('click', () => this.anhalten());
        document.getElementById('laufband-anhalten').addEventListener('click', () => this.anhalten());
        document.addEventListener('visibilitychange', () => { if (!document.hidden) this.aktualisieren(); });
        // Der Vorschlag für „Als Genesis-Figur speichern": `Meshfigurspeicher` schriebe „<Name> Mesh".
        const modellname = document.getElementById('modell-name');
        if (modellname && !modellname.value) modellname.value = this.zustand.modell || `${this.zustand.name} 2D3D Kleider`;
        this.einstellungen = new Engine2d3dKleidereinstellungen(this);
        this.meshkarte = new Engine2d3dKleidermeshkarte(this);
        this.fotos = new Engine2d3dKleiderfotos(this);
        this.vorbereitung = new Engine2d3dKleidervorbereitung(this);
        this.segmentierung = new Engine2d3dKleidersegmentierung(this);
        this.kleiderstuecke = new Engine2d3dKleiderstuecke(this);
        this._pfadstand = null;
        this.iterationen = new Engine2d3dKleideriterationen(this);
        this.begutachtung = new Engine2d3dKleiderbegutachtung(this);
        this.buehne = new Meshfigurbuehne(this);
        this.buehnenmodell = new Engine2d3dKleiderbuehnenmodell(this, this.buehne);
        this.netzansicht = new Engine2d3dKleidernetzansicht(this, this.buehne);
        this.malen = new Engine2d3dKleidermalen(this, this.buehne, this.buehnenmodell);
        this.formen = new Engine2d3dKleiderformen(this, this.buehne, this.buehnenmodell);
        this.film = new Engine2d3dKleiderfilmansicht(this);
        this.animation = new Engine2d3dKleideranimation(this, this.buehne);
        this.animexport = new Engine2d3dKleideranimexport(this);
        this.render = new Engine2d3dKleiderrender(this);
        this.berichte = new Meshfigurberichte(this);
        this.haar = new Meshfigurhaar(this);
        this.kleidung = new Meshfigurkleidung(this);
        this.frisur = new Meshfigurfrisur();
        this.speicher = new Meshfigurspeicher(this);
        this.zeigen();
        this.verfolgen();
        this.reiterFertig(); // ein Klick auf einen Reiter, der kam, bevor die Seite fertig war, wartet nicht länger
    }

    // ---------------------------------------------------------------- Lauf

    /** „Neu berechnen" — gesperrt ab dem Klick, damit kein zweiter Lauf auf denselben Arbeitsdateien startet
     *  (Edgar, 27.09.2026). Die Optionen speichert die Seite selbst (`Engine2d3dKleidereinstellungen`); der Start schickt
     *  sie nicht noch einmal mit. */
    async starten(ab = null, bis = null, knopf = null) {
        // Ohne Angabe gelten „ab" und „bis" der Laufleiste; „bis" leer = bis zum Ende. „Mesh erzeugen" ruft mit
        // `ab = bis = netz` auf (02.10.2026: der Schritt „Netz" getrennt von den nächsten).
        ab = ab || document.getElementById('ab-schritt').value;
        bis = bis || document.getElementById('bis-schritt').value || null;
        const schritte = this.zustand.schritte || [];
        if (bis && schritte.indexOf(bis) < schritte.indexOf(ab)) {
            this.fehler(`„bis ${Engine2d3dKleiderseite.NAMEN[bis] || bis}" liegt vor „ab ${Engine2d3dKleiderseite.NAMEN[ab] || ab}".`);
            return;
        }
        try {
            await Knopfsperre.waehrend(knopf || document.getElementById('starten'), async () => {
                if (!await this.einstellungen.jetzt()) throw new Error('Eingaben nicht gespeichert');
                const antwort = await Serverabruf.senden(this.adresse('starten/'), bis ? { ab, bis } : { ab });
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
     *  Arbeitsprozess sofort (`Engine2d3dKleiderarbeiter.anhalten`); eine Runde, die gerade rechnet, geht verloren, alles
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
        }, this.zustand.laeuft ? Engine2d3dKleiderseite.TAKT_MS : Engine2d3dKleiderseite.TAKT_RUHE_MS);
    }

    async aktualisieren() {
        try {
            // `error` im Zustand ist die Fehlermeldung des AUFTRAGS (`error_message`), kein Übertragungsfehler — ein
            // Fehler der Anfrage selbst wirft `Serverabruf.json`. BlenderModel wirft hier auf `z.error`: Ein Lauf, der
            // scheitert, bleibt dort auf „Läuft" stehen, und die Meldung trägt den Vorsatz „Zustand nicht lesbar".
            const z = await Serverabruf.json(this.adresse('zustand/'));
            this.zustand = z;
            this.veraltet.pruefen(z);
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
        status.textContent = Engine2d3dKleiderseite.STATUS[z.status] || z.status;
        status.className = `bildmodell-status hb-${z.status === 'fertig' ? 'gut' : z.status === 'gescheitert' ? 'schlecht' : 'laeuft'}`;
        document.getElementById('fortschritt').style.width = `${z.progress || 0}%`;
        document.getElementById('fortschritt-text').textContent =
            z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}` : (z.progress_detail || '');
        const start = document.getElementById('starten');
        start.disabled = !!z.laeuft;
        start.querySelector('span').textContent = z.laeuft ? 'Berechnet …' : 'Neu berechnen';
        document.getElementById('anhalten').disabled = !z.laeuft;
        this.meshkarte.zeigen(z);
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
        this.vorbereitung.zeigen(z);
        this.segmentierung.zeigen(z);
        this.kleiderstuecke.zeigen(z);
        this.pfade(z);
        this.iterationen.zeigen(z);
        this.begutachtung.zeigen(z);
        this.berichte.zeigen(z);
        this.haar.zeigen(z);
        this.kleidung.zeigen(z);
        this.frisur.zeigen(z);
        this.buehne.zeigen(z);
        this.buehnenmodell.zeigen(z);
        this.netzansicht.zeigen(z);
        this.film.zeigen(z);
        this.animation.zeigen(z);
        this.animexport.zeigen(z);
        this.render.zeigen(z);
        this.speicher.zeigen(z);
    }

    /** Reiter „Auftrag" / „Iterationen" gewechselt (die Felder hat `Seitenreiter` schon umgeschaltet): bei „Iterationen" den Zustand
     *  frisch holen, danach die Sanduhr beenden (`Seitenreiterwartet`) — auch wenn das Holen scheitert. */
    async reiterGewechselt(name) {
        try {
            if (name === 'iterationen') await this.aktualisieren();
        } finally {
            this.reiterFertig();
        }
    }

    reiterFertig() {
        document.getElementById('auftrag-reiter').dispatchEvent(new Event('reiterfertig'));
    }

    /** „Gespeichert unter" — die Ablageorte zum Kopieren, neu gezeichnet nur bei Änderung. */
    pfade(z) {
        const stand = JSON.stringify(z.pfade);
        if (stand === this._pfadstand) return;
        this._pfadstand = stand;
        Meshpfadliste.zeichnen(document.getElementById('engine2d3dkleider-pfade'), z.pfade);
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
            punkt.textContent = Engine2d3dKleidermeshkarte.schrittname(s, z, Engine2d3dKleiderseite.NAMEN[s] || s);
            if (dauer[s] !== undefined) {
                const zeit = document.createElement('small');
                zeit.textContent = ` ${Math.round(dauer[s])} s`;
                punkt.appendChild(zeit);
            }
            liste.appendChild(punkt);
        });
    }
}
