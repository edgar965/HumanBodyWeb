import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Modelldialog — „Modell laden" und „Modell speichern unter".
 *
 * Herausgelöst aus `presets.js` (352 Zeilen). Ein Dialog für beide Fälle: Der
 * Aufbau ist derselbe (Liste vorhandener Modelle, Namensfeld, zwei Knöpfe), nur
 * Überschrift und Knopfbeschriftung wechseln.
 *
 * `zeigen()` liefert ein Versprechen auf den Namen oder `null` bei Abbruch —
 * so liest sich der Aufrufer wie ein `prompt()`, ohne einen zu benutzen.
 *
 * **Alle Zuhörer werden beim Schließen wieder abgemeldet.** Der Dialog bleibt im
 * Dokument stehen und wird wiederverwendet; ohne das Abmelden würde nach dem
 * dritten Öffnen ein Klick auf „Speichern" drei Versprechen auflösen.
 */
export class Modelldialog {

    static KENNUNG = 'save-dialog-overlay';

    static BESCHRIFTUNG = {
        load: { titel: '<i class="fas fa-folder-open"></i> Modell laden',
                knopf: '<i class="fas fa-folder-open"></i> Laden',
                platzhalter: 'Modellname...' },
        save: { titel: '<i class="fas fa-file-export"></i> Modell speichern unter',
                knopf: '<i class="fas fa-save"></i> Speichern',
                platzhalter: 'Neuer Name...' },
    };

    static laden() { return new Modelldialog('load').zeigen(); }
    static speichern() { return new Modelldialog('save').zeigen(); }

    constructor(art) {
        this.art = art;
        Modelldialog.aufbauen();
        this.rahmen = document.getElementById(Modelldialog.KENNUNG);
        this.liste = document.getElementById('save-dialog-list');
        this.feld = document.getElementById('save-dialog-name');
        this.bestaetigen = document.getElementById('save-dialog-confirm');
        this.abbrechen = document.getElementById('save-dialog-cancel');
        this.schliessen = this.rahmen.querySelector('.save-dialog-close');
    }

    /** Das Gerüst einmal ins Dokument hängen. */
    static aufbauen() {
        if (document.getElementById(Modelldialog.KENNUNG)) return;
        const rahmen = document.createElement('div');
        rahmen.id = Modelldialog.KENNUNG;
        rahmen.innerHTML = `<div class="save-dialog">
            <div class="save-dialog-header">
                <h3></h3>
                <button class="save-dialog-close" title="Schließen">&times;</button>
            </div>
            <div class="save-dialog-body">
                <label>Vorhandene Modelle:</label>
                <div class="save-dialog-list" id="save-dialog-list"></div>
                <label class="abstand-12">Name:</label>
                <input type="text" id="save-dialog-name" autocomplete="off">
            </div>
            <div class="save-dialog-footer">
                <button class="save-dialog-btn cancel" id="save-dialog-cancel">Abbrechen</button>
                <button class="save-dialog-btn confirm" id="save-dialog-confirm"></button>
            </div>
        </div>`;
        document.body.appendChild(rahmen);
    }

    zeigen() {
        return new Promise(fertig => {
            this._beschriften();
            this.rahmen.classList.add('open');
            if (this.art === 'save') this.feld.focus();
            this._modelleLaden();
            this._binden(fertig);
        });
    }

    _beschriften() {
        const text = Modelldialog.BESCHRIFTUNG[this.art];
        this.rahmen.querySelector('.save-dialog-header h3').innerHTML = text.titel;
        this.bestaetigen.innerHTML = text.knopf;
        this.feld.placeholder = text.platzhalter;
        this.feld.value = this.art === 'save' ? (state.currentPresetName || '') : '';
    }

    _hinweis(text, fehler = false) {
        this.liste.innerHTML = '';
        const zeile = document.createElement('div');
        zeile.className = 'save-dialog-hinweis'
            + (fehler ? ' save-dialog-fehler' : '');
        zeile.textContent = text;
        this.liste.appendChild(zeile);
    }

    async _modelleLaden() {
        this._hinweis('Lade...');
        let daten;
        try {
            daten = await Serverabruf.json('/api/character/models/');
        } catch (fehler) {
            Protokoll.fehler('presets', 'Modelliste nicht ladbar', fehler);
            this._hinweis('Fehler beim Laden', true);
            return;
        }
        const modelle = daten.presets || [];
        if (modelle.length === 0) {
            this._hinweis('Keine Modelle vorhanden');
            return;
        }
        this.liste.innerHTML = '';
        for (const modell of modelle) this.liste.appendChild(this._zeile(modell));
    }

    _zeile(modell) {
        const zeile = document.createElement('div');
        zeile.className = 'save-dialog-item';
        zeile.textContent = modell.label || modell.name;
        zeile.dataset.name = modell.name;
        zeile.addEventListener('click', () => {
            this.liste.querySelectorAll('.save-dialog-item')
                .forEach(el => el.classList.remove('selected'));
            zeile.classList.add('selected');
            this.feld.value = modell.name;
            if (this.art === 'save') this.feld.focus();
        });
        if (this.art === 'load') {
            zeile.addEventListener('dblclick', () => {
                this.feld.value = modell.name;
                this._schliessen(modell.name);
            });
        }
        return zeile;
    }

    _binden(fertig) {
        this._fertig = fertig;
        this._zuhoerer = [
            [this.bestaetigen, 'click', () => this._bestaetigen()],
            [this.abbrechen, 'click', () => this._schliessen(null)],
            [this.schliessen, 'click', () => this._schliessen(null)],
            [this.rahmen, 'click',
             ereignis => { if (ereignis.target === this.rahmen) this._schliessen(null); }],
            [this.feld, 'keydown', ereignis => this._taste(ereignis)],
        ];
        for (const [ziel, art, tun] of this._zuhoerer) {
            ziel.addEventListener(art, tun);
        }
    }

    _taste(ereignis) {
        if (ereignis.key === 'Enter') this._bestaetigen();
        if (ereignis.key === 'Escape') this._schliessen(null);
    }

    _bestaetigen() {
        const name = this.feld.value.trim();
        if (name) this._schliessen(name);
        else this.feld.focus();
    }

    _schliessen(ergebnis) {
        this.rahmen.classList.remove('open');
        for (const [ziel, art, tun] of this._zuhoerer) {
            ziel.removeEventListener(art, tun);
        }
        this._zuhoerer = [];
        this._fertig(ergebnis);
    }
}
