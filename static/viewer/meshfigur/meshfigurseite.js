import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Meshoptionenformular } from '../mesh/meshoptionenformular.js';
import { Meshfigurbuehne } from './meshfigurbuehne.js';
import { Meshfigurberichte } from './meshfigurberichte.js';
import { Meshfigurexport } from './meshfigurexport.js';

/**
 * Meshfigurseite — die Auftragsseite des Reiters „Mesh to 3D" (27.09.2026): Lauf verfolgen
 * (Schritte mit Dauer, Balken, neu ab einem Schritt, Anhalten), die Figur in 3D
 * (`Meshfigurbuehne`), die Berichte (`Meshfigurberichte`) und der Export (`Meshfigurexport`).
 * Der Zustand kommt beim Laden als JSON in die Seite, danach alle `TAKT_MS` vom Server.
 */
export class Meshfigurseite {

    static TAKT_MS = 2000;
    static NAMEN = {
        erkennung: 'Erkennung', kalibrierung: 'Kalibrierung', koerper: 'Körperkette', gesicht: 'Gesichtskette',
        rest: 'Eigenmorph', textur: 'Textur', vorschau: 'Vorschau', speichern: 'Speichern',
    };

    static starten(jobId) {
        const daten = JSON.parse(document.getElementById('meshfigur-daten').textContent);
        const seite = new Meshfigurseite(jobId, daten.zustand, daten.katalog);
        seite.aufbauen();
        return seite;
    }

    constructor(jobId, zustand, katalog) {
        this.jobId = jobId;
        this.zustand = zustand;
        this.katalog = katalog;
        this._timer = null;
    }

    adresse(pfad) { return `/api/meshfigur/${this.jobId}/${pfad}`; }

    dateiAdresse(ordner, name) {
        return `/api/meshfigur/${this.jobId}/datei/${ordner}/${encodeURIComponent(name)}`;
    }

    aufbauen() {
        Meshoptionenformular.bauen(document.getElementById('meshfigur-optionen'), this.katalog, this.zustand.optionen);
        const wahl = document.getElementById('ab-schritt');
        for (const s of this.zustand.schritte || []) {
            const option = document.createElement('option');
            option.value = s;
            option.textContent = Meshfigurseite.NAMEN[s] || s;
            wahl.appendChild(option);
        }
        document.getElementById('starten').addEventListener('click', () => this.starten());
        document.getElementById('anhalten').addEventListener('click', () => this.anhalten());
        this.buehne = new Meshfigurbuehne(this);
        this.berichte = new Meshfigurberichte(this);
        this.export = new Meshfigurexport(this);
        this.zeigen();
        this.verfolgen();
    }

    // ---------------------------------------------------------------- Lauf

    async starten() {
        const optionen = Meshoptionenformular.lesen(document.getElementById('meshfigur-optionen'));
        const ab = document.getElementById('ab-schritt').value;
        try {
            const antwort = await Serverabruf.senden(this.adresse('starten/'), { optionen, ab });
            if (antwort.error) throw new Error(antwort.error);
        } catch (fehler) {
            this.fehler(`Start fehlgeschlagen: ${fehler.message}`);
            return;
        }
        this.zustand.status = 'laeuft';
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
        }, Meshfigurseite.TAKT_MS);
    }

    // -------------------------------------------------------------- Anzeige

    fehler(text) {
        const feld = document.getElementById('fehler');
        feld.textContent = text || '';
        feld.classList.toggle('hb-versteckt', !text);
    }

    zeigen() {
        const z = this.zustand;
        document.getElementById('auftrag-status').textContent =
            { angelegt: 'Angelegt', laeuft: 'Läuft', fertig: 'Fertig', gescheitert: 'Fehlgeschlagen',
              angehalten: 'Angehalten' }[z.status] || z.status;
        document.getElementById('fortschritt').style.width = `${z.progress || 0}%`;
        document.getElementById('fortschritt-text').textContent =
            z.laeuft ? `${z.progress || 0} % · ${z.progress_detail || ''}` : (z.progress_detail || '');
        document.getElementById('starten').disabled = !!z.laeuft;
        document.getElementById('anhalten').disabled = !z.laeuft;
        this.fehler(z.status === 'gescheitert' ? (z.error || 'Fehlgeschlagen — siehe auftrag.log') : '');
        this.schritte();
        this.berichte.zeigen(z);
        this.buehne.zeigen(z);
        this.export.zeigen(z);
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
            punkt.textContent = Meshfigurseite.NAMEN[s] || s;
            if (dauer[s] !== undefined) {
                const zeit = document.createElement('small');
                zeit.textContent = ` ${Math.round(dauer[s])} s`;
                punkt.appendChild(zeit);
            }
            liste.appendChild(punkt);
        });
    }
}
