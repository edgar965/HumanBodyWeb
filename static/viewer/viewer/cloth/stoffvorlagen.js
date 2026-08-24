/**
 * Stoffvorlagen — der Vorlagen-Bereich der Kleidungs-Erzeugung.
 *
 * Aus viewer/cloth.js herausgeloest (Umbau 16.08.2026). `loadClothUI()` hatte
 * 245 Zeilen und baute vier Bereiche hintereinander auf — Vorlagen,
 * gespeicherte Vorgaben, Bauer und Grundformen — mit verschachtelten Funktionen
 * dazwischen. Zwei Dinge fielen dabei auf:
 *
 *  * Beim Laden einer Vorgabe standen VIER gleich gebaute Bloecke
 *      const feld = document.getElementById('cloth-tpl-…');
 *      const anzeige = document.getElementById('cloth-tpl-…-val');
 *      if (feld && d.x !== undefined) { feld.value = …; if (anzeige) anzeige.textContent = …; }
 *    mit jeweils anderer Umrechnung. Jetzt eine Methode mit Tabelle.
 *  * Die Parameterliste der Vorlage stand zweimal: einmal zum Erzeugen
 *    (`_tplParams`), einmal zum Speichern (`_saveClothPreset`).
 */
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
export class Stoffvorlagen {

    /** Welche Vorlage zu welcher Vorgaben-Kategorie gehört. */
    static KATEGORIE = {
        TPL_TSHIRT: 'Top', TPL_DRESS: 'Top',
        TPL_PANTS: 'Pants', TPL_SKIRT: 'Pants',
    };
    static VORGABE_VORLAGE = 'TPL_TSHIRT';
    static VORGABE_FARBE = '#404870';

    /**
     * Die vier Regler: Feld-Kennung, Schlüssel in der Vorgabe, Faktor,
     * Anzeigeform. Diese Tabelle ersetzt vier ausgeschriebene Bloecke.
     */
    static REGLER = [
        ['cloth-tpl-segments', 'segments', 1, wert => String(wert)],
        ['cloth-tpl-tightness', 'tightness', 100, wert => wert.toFixed(2)],
        ['cloth-tpl-top-ext', 'top_extend', 100, wert => wert.toFixed(2) + ' m'],
        ['cloth-tpl-bot-ext', 'bottom_extend', 100, wert => wert.toFixed(2) + ' m'],
    ];

    /**
     * @param {Object} daten    Antwort von /api/character/cloth/regions/
     * @param {Object} dienste  { reglerBinden, reglerWert, stoffLaden,
     *                            bereichEntfernen, stoffNetze }
     */
    constructor(daten, dienste) {
        this.daten = daten;
        this.dienste = dienste;
        this.vorlagenfeld = document.getElementById('cloth-tpl-type');
        this.vorgabenfeld = document.getElementById('cloth-tpl-preset');
    }

    verdrahten() {
        this._vorlagenfuellen();
        this._reglerBinden();
        this._vorgabenknoepfe();
        this._erzeugenknoepfe();
        if (this.vorlagenfeld) {
            this.vorlagenfeld.addEventListener('change', () => this.vorgabenListe());
            this.vorgabenListe();
        }
        return this;
    }

    /** Aktuell gewählte Vorlage. */
    vorlage() {
        return this.vorlagenfeld ? this.vorlagenfeld.value
                                 : Stoffvorlagen.VORGABE_VORLAGE;
    }

    kategorie() {
        return Stoffvorlagen.KATEGORIE[this.vorlage()] || 'Top';
    }

    /**
     * Die Werte der vier Regler. Eine Stelle fuer beides — Erzeugen und
     * Speichern brauchten dieselbe Liste und hatten sie doppelt.
     */
    werte() {
        const werte = {};
        for (const [feldId, schluessel, faktor] of Stoffvorlagen.REGLER) {
            werte[schluessel] = this.dienste.reglerWert(feldId) / faktor;
        }
        return werte;
    }

    /** Kennung und Parameter fuer das Erzeugen. */
    auftrag() {
        const vorlage = this.vorlage();
        return {
            key: `tpl_${vorlage}`,
            params: { method: 'template', template: vorlage, ...this.werte() },
        };
    }

    // ------------------------------------------------------------------ Aufbau

    _vorlagenfuellen() {
        if (!this.vorlagenfeld) return;
        for (const vorlage of (this.daten.templates || [])) {
            this.vorlagenfeld.appendChild(new Option(vorlage.label, vorlage.key));
        }
    }

    _reglerBinden() {
        for (const [feldId, , faktor, form] of Stoffvorlagen.REGLER) {
            this.dienste.reglerBinden(feldId, feldId + '-val',
                                      wert => form(wert / faktor));
        }
    }

    // ---------------------------------------------------------------- Vorgaben

    /** Vorgabenliste des aktuellen Bereichs neu holen. */
    async vorgabenListe() {
        if (!this.vorgabenfeld || !this.vorlagenfeld) return;
        try {
            const daten = await Serverabruf.json(
                `/api/character/cloth/presets/?category=${this.kategorie()}`);
            // Den ersten Eintrag („bitte wählen") stehen lassen.
            while (this.vorgabenfeld.options.length > 1) this.vorgabenfeld.remove(1);
            for (const vorgabe of (daten.presets || [])) {
                this.vorgabenfeld.appendChild(new Option(vorgabe.name, vorgabe.name));
            }
        } catch (fehler) {
            Protokoll.warnung('stoffvorlagen', 'Stoff-Vorgaben nicht ladbar:', fehler);
        }
    }

    async vorgabeSpeichern(name) {
        const farbfeld = document.getElementById('cloth-color');
        const daten = {
            template: this.vorlage(),
            ...this.werte(),
            color: farbfeld ? farbfeld.value : Stoffvorlagen.VORGABE_FARBE,
        };
        try {
            const antwort = await fetch('/api/character/cloth/presets/save/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, data: daten }),
            });
            const ergebnis = await antwort.json();
            if (!ergebnis.ok) {
                alert('Fehler: ' + (ergebnis.error || 'Unbekannt'));
                return false;
            }
            await this.vorgabenListe();
            if (this.vorgabenfeld) {
                this.vorgabenfeld.value = ergebnis.filename.replace('.json', '');
            }
            Protokoll.info('Kleidung', 'Stoff-Vorgabe gespeichert:', ergebnis.filename);
            return true;
        } catch (fehler) {
            alert('Fehler: ' + fehler.message);
            return false;
        }
    }

    async vorgabeLaden() {
        if (!this.vorgabenfeld?.value) return;
        try {
            const daten = await Serverabruf.json(`/api/character/cloth/presets/`
                + `${this.kategorie()}/${encodeURIComponent(this.vorgabenfeld.value)}/`);
            if (daten.error) {
                alert(daten.error);
                return;
            }
            if (daten.template && this.vorlagenfeld) {
                this.vorlagenfeld.value = daten.template;
            }
            for (const [feldId, schluessel, faktor, form] of Stoffvorlagen.REGLER) {
                this._reglerSetzen(feldId, daten[schluessel], faktor, form);
            }
            const farbfeld = document.getElementById('cloth-color');
            if (farbfeld && daten.color) farbfeld.value = daten.color;
            Protokoll.debug('Kleidung', 'Stoff-Vorgabe geladen:', this.vorgabenfeld.value);
        } catch (fehler) {
            alert('Fehler beim Laden: ' + fehler.message);
        }
    }

    /** Einen Regler und seine Anzeige setzen — vorher viermal ausgeschrieben. */
    _reglerSetzen(feldId, wert, faktor, form) {
        if (wert === undefined || wert === null) return;
        const feld = document.getElementById(feldId);
        if (!feld) { Protokoll.debug('stoffvorlagen', `kein Regler ${feldId}`); return; }
        feld.value = Math.round(wert * faktor);
        const anzeige = document.getElementById(feldId + '-val');
        if (anzeige) anzeige.textContent = form(wert);
    }

    // ------------------------------------------------------------------ Knöpfe

    _vorgabenknoepfe() {
        document.getElementById('cloth-tpl-preset-save')
            ?.addEventListener('click', async () => {
                let name = this.vorgabenfeld ? this.vorgabenfeld.value : '';
                if (!name) {
                    name = (prompt('Vorgabe-Name:') || '').trim();
                    if (!name) return;
                }
                await this.vorgabeSpeichern(name);
            });
        document.getElementById('cloth-tpl-preset-saveas')
            ?.addEventListener('click', async () => {
                const name = (prompt('Vorgabe-Name:',
                    this.vorgabenfeld ? this.vorgabenfeld.value : '') || '').trim();
                if (name) await this.vorgabeSpeichern(name);
            });
        document.getElementById('cloth-tpl-preset-load')
            ?.addEventListener('click', () => this.vorgabeLaden());
    }

    _erzeugenknoepfe() {
        document.getElementById('cloth-tpl-create')?.addEventListener('click', () => {
            const { key, params } = this.auftrag();
            this.dienste.stoffLaden(key, params);
        });
        document.getElementById('cloth-tpl-update')?.addEventListener('click', () => {
            const { key, params } = this.auftrag();
            if (!this.dienste.stoffNetze()[key]) {
                Protokoll.warnung('stoffvorlagen', `Kein Stoff "${key}" zum Ändern — erst Erzeugen`);
                return;
            }
            this.dienste.stoffLaden(key, params);
        });
        document.getElementById('cloth-tpl-delete')?.addEventListener('click', () => {
            const key = `tpl_${this.vorlage()}`;
            if (!this.dienste.stoffNetze()[key]) return;
            this.dienste.bereichEntfernen(key);
            Protokoll.debug('Kleidung', `Stoff "${key}" entfernt`);
        });
    }
}
