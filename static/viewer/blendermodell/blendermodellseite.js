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
import { Blendermodelleinstellungen } from './blendermodelleinstellungen.js';
import { Blendermodellfotos } from './blendermodellfotos.js';
import { Blendermodelliterationen } from './blendermodelliterationen.js';

/**
 * Blendermodellseite — die Auftragsseite des Bereichs „BlenderModel" (Edgar, 29.09.2026): Lauf verfolgen (Schritte
 * mit Dauer, Balken, neu ab einem Schritt, Anhalten), die Bildauswahl (`Blendermodellfotos`), die 3D-Ausgabe und ihre
 * Berichte, die Optionen (`Blendermodelleinstellungen`, sofort gespeichert).
 *
 * DIE 3D-AUSGABE IST DIE VON „MESH TO 3D": Bühne, Berichte, Export, Speichern und die Karten Haar, Kleidung und
 * Frisur sind die Module aus `static/viewer/meshfigur/`, unverändert. Sie sprechen nur mit dem, was diese Seite
 * anbietet — `zustand`, `adresse()`, `dateiAdresse()`, `buehne` — und lesen dieselben Felder aus `zustand.ergebnis`.
 * Der Zustand kommt beim Laden als JSON in die Seite, danach alle `TAKT_MS` vom Server.
 */
export class Blendermodellseite {

    static TAKT_MS = 2000;
    static NAMEN = {
        grundfigur: 'Grundfigur', kostuem: 'Kostüm', export: 'GLB mit Rig', blender: 'Blender', speichern: 'Speichern',
    };
    static STATUS = {
        angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen', angehalten: 'Angehalten',
    };

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('blendermodell-daten').textContent);
        const seite = new Blendermodellseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        // Handle zum Nachsehen im Browser (Bühne, Zustand) — wie `window.__characters` in der Szene.
        window.__blendermodell = seite;
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        this.jobId = jobId;
        this.zustand = zustand;
        this.katalog = katalog;
        this._timer = null;
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
        // Der Vorschlag für „Als Genesis-Figur speichern": `Meshfigurspeicher` schriebe „<Name> Mesh".
        const modellname = document.getElementById('modell-name');
        if (modellname && !modellname.value) modellname.value = this.zustand.modell || `${this.zustand.name} BlenderModel`;
        this.einstellungen = new Blendermodelleinstellungen(this);
        this.fotos = new Blendermodellfotos(this);
        this._pfadstand = null;
        this.iterationen = new Blendermodelliterationen(this);
        this.buehne = new Meshfigurbuehne(this);
        this.animation = new Blendermodellanimation(this, this.buehne);
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

    async anhalten() {
        try {
            await Serverabruf.senden(this.adresse('anhalten/'), {});
        } catch (fehler) {
            this.fehler(`Anhalten fehlgeschlagen: ${fehler.message}`);
        }
    }

    verfolgen() {
        if (this._timer) clearTimeout(this._timer);
        this._timer = setTimeout(async () => {
            try {
                this.zustand = await Serverabruf.json(this.adresse('zustand/'));
                this.zeigen();
            } catch (fehler) {
                this.fehler(`Zustand nicht lesbar: ${fehler.message}`);
            }
            if (this.zustand.laeuft) this.verfolgen();
        }, Blendermodellseite.TAKT_MS);
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
        status.textContent = Blendermodellseite.STATUS[z.status] || z.status;
        status.className = `bildmodell-status hb-${z.status === 'fertig' ? 'gut' : z.status === 'gescheitert' ? 'schlecht' : 'laeuft'}`;
        document.getElementById('fortschritt').style.width = `${z.progress || 0}%`;
        document.getElementById('fortschritt-text').textContent =
            z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}` : (z.progress_detail || '');
        const start = document.getElementById('starten');
        start.disabled = !!z.laeuft;
        start.querySelector('span').textContent = z.laeuft ? 'Berechnet …' : 'Neu berechnen';
        document.getElementById('anhalten').disabled = !z.laeuft;
        this.einstellungen.sperren(!!z.laeuft);
        this.fehler(z.status === 'gescheitert' ? (z.error || 'Fehlgeschlagen — siehe auftrag.log') : '');
        this.schritte();
        this.fotos.zeigen(z);
        this.pfade(z);
        this.iterationen.zeigen(z);
        this.berichte.zeigen(z);
        this.haar.zeigen(z);
        this.kleidung.zeigen(z);
        this.frisur.zeigen(z);
        this.buehne.zeigen(z);
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
