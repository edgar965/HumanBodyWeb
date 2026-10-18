import { Kontextmenue } from './kontextmenue.js';
import { Ordnerwahl } from './ordnerwahl.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Figurwahlordnermenue — Rechtsklick auf einen Ordner der gespeicherten Modelle im Dialog „Charakter hinzufügen": Umbenennen, Löschen;
 * auf ein Modell: „Verschieben nach …" (neben Umbenennen und Löschen aus `Figurwahlzeile`).
 *
 * AUFTRAG (Edgar, 18.10.2026): „Kontextmenü für die Ordner fehlt noch, die sollen löschen, umbenennen enthalten" — und „bei den Modellen war noch
 * das Kontextmenü Verschieben (in Unterordner)". Verschoben wurde bis dahin über Haken + Auswahl „Verschieben nach …" in der Leiste (client.log 16.10.2026,
 * `select feld=ziel`); die bleibt für mehrere Modelle. Das Fenster ist dasselbe wie bei Animationen und Posen (`Ordnerwahl`), mit „Neuer Ordner …".
 *
 * Ein Ordner ist eine Zuordnung auf dem Server (`Modellordner`), kein Verzeichnis. LÖSCHEN nimmt deshalb nur den Ordner weg: seine Modelle bleiben
 * auf der Platte und stehen danach ohne Ordner — Modelle löschen geht weiter über Haken und „Löschen" in der Leiste. Rückfragen über
 * `window.prompt`/`confirm` wie beim Umbenennen und Löschen eines Modells (`Katalogpflege`). Nur in Reitern mit Pflege (`Figurwahlordner.darfPflegen`).
 * Eigenes Modul, weil `figurwahlordner.js` sonst über 300 Zeilen wüchse.
 */
export class Figurwahlordnermenue {

    /** Wert für „— ohne Ordner —" im Fenster (`Ordnerwahl` liefert für einen leeren Wert `null` = Abbruch). */
    static OHNE = '__ohne__';

    /**
     * @param ordner   der `Figurwahlordner` (Senden mit Meldung und Neuaufbau: `_tun`; offener Ordner: `offenUmbenennen`)
     * @param adresse  Basis der Ordner-Endpunkte (`Figurwahlordner.ADRESSE`)
     */
    constructor(ordner, adresse) {
        this.ordner = ordner;
        this.adresse = adresse;
    }

    /** Rechtsklick auf den Kopf (`summary`) des Ordners `name` öffnet das Menü. */
    binden(kopf, quelle, name, anzahl) {
        Kontextmenue.binden(kopf, () => [
            { symbol: 'fa-pen', text: 'Umbenennen', tun: () => this._umbenennen(kopf, quelle, name) },
            { symbol: 'fa-trash', text: 'Löschen', tun: () => this._loeschen(kopf, quelle, name, anzahl) },
        ]);
    }

    async _umbenennen(kopf, quelle, name) {
        const eingabe = window.prompt(`Neuer Name für den Ordner „${name}“:`, name);
        const neu = (eingabe ?? '').trim();
        if (!neu || neu === name) return;
        await this.ordner._tun(quelle, this._leiste(kopf), () => Serverabruf.senden(`${this.adresse}umbenennen/`, { quelle, ordner: name, name: neu }),
                               (a) => {
                                   this.ordner.offenUmbenennen(quelle, name, a.name);
                                   return `Ordner „${name}“ heißt jetzt „${a.name}“.`;
                               });
    }

    async _loeschen(kopf, quelle, name, anzahl) {
        const inhalt = !anzahl ? 'Der Ordner ist leer.'
            : anzahl === 1 ? 'Das Modell darin bleibt erhalten und steht danach ohne Ordner.'
                : `Die ${anzahl} Modelle darin bleiben erhalten und stehen danach ohne Ordner.`;
        if (!window.confirm(`Ordner „${name}“ löschen?\n\n${inhalt}`)) return;
        await this.ordner._tun(quelle, this._leiste(kopf), () => Serverabruf.senden(`${this.adresse}loeschen/`, { quelle, ordner: name }),
                               a => `Ordner „${name}“ gelöscht` + (a.anzahl ? ` — ${a.anzahl} ${a.anzahl === 1 ? 'Modell steht' : 'Modelle stehen'} jetzt ohne Ordner.` : '.'));
    }

    /** Einträge für den Rechtsklick auf ein Modell (`Figurwahlzeile`, `zusatz`). Leer ohne Pflege und für einen abgebrochenen Import. */
    modellEintraege(quelle, eintrag, zeile) {
        if (eintrag.verwaist || !this.ordner.darfPflegen(quelle)) return [];
        return [{ symbol: 'fa-arrows-alt', text: 'Verschieben nach …', tun: () => this._modellVerschieben(quelle, eintrag.name, zeile) }];
    }

    async _modellVerschieben(quelle, name, zeile) {
        const q = this.ordner.daten[quelle] || {};
        const ordner = [...(q.ordner || [])].sort((a, b) => a.localeCompare(b, 'de', { sensitivity: 'base', numeric: true }));
        const jetzt = q.modelle?.[name] || '';
        const wahl = await Ordnerwahl.waehlen(jetzt ? `„${name}“ liegt in „${jetzt}“.` : `„${name}“ liegt in keinem Ordner.`,
                                              [{ wert: Figurwahlordnermenue.OHNE, text: '— ohne Ordner —', aktuell: !jetzt },
                                               ...ordner.map(o => ({ wert: o, text: o, aktuell: o === jetzt }))]);
        if (!wahl) return;
        // Ein neuer Name, der sich nur in der Schreibweise von einem Ordner unterscheidet, ist dieser Ordner (der Server legte ihn nicht an).
        const ziel = wahl === Figurwahlordnermenue.OHNE ? '' : (ordner.find(o => o.toLowerCase() === wahl.toLowerCase()) ?? wahl);
        await this.ordner._tun(quelle, this._leiste(zeile), async () => {
            const nach = ziel && !ordner.includes(ziel) ? (await Serverabruf.senden(`${this.adresse}anlegen/`, { quelle, name: ziel })).name : ziel;
            return { ...(await Serverabruf.senden(`${this.adresse}verschieben/`, { quelle, namen: [name], ordner: nach })), nach };
        }, a => `„${name}“ ${a.nach ? `nach „${a.nach}“` : 'aus dem Ordner'} verschoben.`);
    }

    /** Die Leiste des Bereichs „Gespeicherte Modelle" — dort steht die Meldung. */
    _leiste(kopf) {
        return kopf.closest('details.dialogbereich')?.querySelector(':scope > .figurwahl-ordnerleiste');
    }
}
