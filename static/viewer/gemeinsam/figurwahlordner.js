import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Figurkataloge } from './figurkataloge.js';
import { Figurwahlordnermenue } from './figurwahlordnermenue.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Figurwahlordner — Ordner, Mehrfachauswahl, Verschieben und Löschen im Bereich „Gespeicherte Modelle“ des Figurwahl-Dialogs (15.10.2026).
 *
 * ANLASS (Edgar, 15.10.2026): „bei Modell hinzufügen (im Fenster Charakter), mach mir ein UI so dass ich Ordner Anlegen kann mit Namen bei den gespeicherten
 * Modellen. ich möchte Modelle zu den Ordnern verschieben können, auch batch verschieben. ich möchte Modelle batch löschen können (Mehrfachauswahl und löschen)“.
 *
 * Ein Ordner ist eine Zuordnung auf dem Server (`Modellordner`, `3DObjects/models/modellordner.json`), kein Verzeichnis — die Modelle bleiben, wo sie sind, und jeder
 * Lader findet sie unter ihrem Namen. Die Ordner stehen zugeklappt über den Modellen ohne Ordner — bei jedem Öffnen des Dialogs (18.10.2026, „immer eingeklappt“);
 * offen bleibt einer nur, solange der Dialog steht. Rechtsklick auf einen Ordner: Umbenennen, Löschen (`Figurwahlordnermenue`). Ordner sieht jeder Dialog;
 * anlegen, verschieben und löschen nur ein Dialog mit Pflege (die Szene „/Charakter/“, `Katalogpflege`) und nur in Reitern mit Pflege (`Figurkataloge.QUELLEN`).
 * Haken je Zeile wählen aus (Umschalt-Klick: alle sichtbaren dazwischen); ein Klick auf die Zeile selbst wählt weiter das EINE Modell zum Hinzufügen.
 */
export class Figurwahlordner {

    static ADRESSE = '/api/character/modellordner/';
    static LOESCHEN = '/api/character/katalog/loeschen-mehrere/';
    /** Reiter → `art` des Löschens mehrerer (`Katalogverwaltung.ABLAGEN`). */
    static ARTEN = { genesis9: 'genesis9', modell: 'modell', uma: 'uma' };

    /** @param dialog  der `Figurwahldialog` (Pflege, Kennung, Neuaufbau eines Reiters) */
    constructor(dialog) {
        this.dialog = dialog;
        this.daten = {};
        this.gewaehlt = {};
        this._letzter = {};
        this._laeuft = null;
        this._offen = new Set();
        this.menue = new Figurwahlordnermenue(this, Figurwahlordner.ADRESSE);
    }

    /** Die Zuordnung vom Server (eine Anfrage, auch wenn alle Reiter zugleich füllen). Ohne Antwort bleibt die Liste flach. */
    laden() {
        this._laeuft ??= Serverabruf.json(Figurwahlordner.ADRESSE)
            .then(daten => { this.daten = daten || {}; })
            .catch(() => { this.daten = {}; })
            .finally(() => { this._laeuft = null; });
        return this._laeuft;
    }

    darfPflegen(quelle) {
        return Boolean(this.dialog.pflege) && Boolean(Figurkataloge.QUELLEN[quelle]?.pflege) && Boolean(Figurwahlordner.ARTEN[quelle]);
    }

    _auswahl(quelle) {
        return (this.gewaehlt[quelle] ??= new Set());
    }

    /**
     * Den Bereich „Gespeicherte Modelle“ eines Reiters füllen: Leiste (nur mit Pflege), Ordner mit ihren Modellen, dann die Modelle ohne Ordner.
     * `eintraege` sind schon sortiert (`Figurwahlbereiche.sortiert`); `zeile(eintrag)` baut das `li` wie bisher.
     */
    fuellen(quelle, liste, eintraege, zeile, leerText) {
        const q = this.daten[quelle] || {};
        const ordner = [...(q.ordner || [])].sort((a, b) => a.localeCompare(b, 'de', { sensitivity: 'base', numeric: true }));
        const zuordnung = q.modelle || {};
        const pflege = this.darfPflegen(quelle);
        const auswahl = this._auswahl(quelle);
        const namen = new Set(eintraege.filter(e => !e.verwaist).map(e => e.name));
        for (const n of [...auswahl]) if (!namen.has(n)) auswahl.delete(n);
        this._leiste(quelle, liste, pflege, ordner);
        liste.innerHTML = '';
        const inhalt = new Map(ordner.map(o => [o, []]));
        const ohne = [];
        for (const e of eintraege) {
            const o = !e.verwaist && zuordnung[e.name];
            (o && inhalt.has(o) ? inhalt.get(o) : ohne).push(e);
        }
        for (const o of ordner) liste.appendChild(this._ordner(quelle, o, inhalt.get(o), zeile, pflege));
        for (const e of ohne) liste.appendChild(this._modell(quelle, e, zeile, pflege));
        if (!eintraege.length && !ordner.length) liste.innerHTML = `<li class="gedaempft">${Htmltext.t(leerText)}</li>`;
        this._leisteStand(quelle, liste);
    }

    _ordner(quelle, name, eintraege, zeile, pflege) {
        const li = document.createElement('li');
        li.className = 'figurwahl-ordner';
        li.dataset.ordner = name;
        const details = document.createElement('details');
        details.open = this._istOffen(quelle, name);
        details.addEventListener('toggle', () => this._merken(quelle, name, details.open));
        const kopf = document.createElement('summary');
        kopf.innerHTML = `<i class="fas fa-folder${details.open ? '-open' : ''}"></i> ${Htmltext.t(name)} <span class="gedaempft">(${eintraege.length})</span>`;
        details.addEventListener('toggle', () => kopf.querySelector('i')?.classList.replace(details.open ? 'fa-folder' : 'fa-folder-open', details.open ? 'fa-folder-open' : 'fa-folder'));
        const ul = document.createElement('ul');
        ul.className = 'preset-list';
        ul.dataset.quelle = quelle;
        ul.dataset.bereich = 'gespeichert';
        for (const e of eintraege) ul.appendChild(this._modell(quelle, e, zeile, pflege));
        if (!eintraege.length) ul.innerHTML = '<li class="gedaempft">Leer — Modelle mit Haken wählen und „Verschieben nach …“.</li>';
        details.append(kopf, ul);
        li.appendChild(details);
        if (pflege) this.menue.binden(kopf, quelle, name, eintraege.length);
        return li;
    }

    _modell(quelle, eintrag, zeile, pflege) {
        const li = zeile(eintrag);
        if (!pflege || eintrag.verwaist) return li;
        const haken = document.createElement('input');
        haken.type = 'checkbox';
        haken.className = 'figurwahl-haken';
        haken.dataset.tun = 'haken';          // `Figurwahlzeile`: ein Klick auf `[data-tun]` wählt die Zeile nicht
        haken.dataset.modell = eintrag.name;
        haken.checked = this._auswahl(quelle).has(eintrag.name);
        haken.title = 'Für Verschieben und Löschen auswählen (Umschalt-Klick: alle dazwischen)';
        haken.addEventListener('click', (e) => this._haken(quelle, haken, e.shiftKey));
        li.prepend(haken);
        return li;
    }

    /** Ein Haken: setzen/lösen, mit Umschalt alle sichtbaren Haken zwischen dem letzten und diesem auf denselben Stand. */
    _haken(quelle, haken, bereich) {
        const auswahl = this._auswahl(quelle);
        const liste = haken.closest('.figurwahl-bereiche');
        const sichtbar = [...(liste?.querySelectorAll('input.figurwahl-haken') || [])].filter(h => h.offsetParent !== null);
        const von = sichtbar.indexOf(this._letzter[quelle]);
        const bis = sichtbar.indexOf(haken);
        const betroffen = bereich && von >= 0 && bis >= 0 ? sichtbar.slice(Math.min(von, bis), Math.max(von, bis) + 1) : [haken];
        for (const h of betroffen) {
            h.checked = haken.checked;
            if (haken.checked) auswahl.add(h.dataset.modell);
            else auswahl.delete(h.dataset.modell);
        }
        this._letzter[quelle] = haken;
        this._leisteStand(quelle, haken.closest('ul[data-bereich="gespeichert"]'));
    }

    // -- Leiste ----------------------------------------------------------------

    _leiste(quelle, liste, pflege, ordner) {
        let leiste = liste.parentElement.querySelector(':scope > .figurwahl-ordnerleiste');
        if (!pflege) {
            leiste?.remove();
            return;
        }
        if (!leiste) {
            leiste = document.createElement('div');
            leiste.className = 'figurwahl-ordnerleiste';
            leiste.innerHTML = `
                <button type="button" data-tat="neu" title="Einen Ordner für gespeicherte Modelle anlegen"><i class="fas fa-folder-plus"></i> Neuer Ordner</button>
                <span class="figurwahl-neuerordner hb-versteckt">
                    <input type="text" maxlength="60" placeholder="Name des Ordners" data-feld="name">
                    <button type="button" data-tat="anlegen">Anlegen</button>
                    <button type="button" data-tat="abbrechen">Abbrechen</button>
                </span>
                <span class="figurwahl-auswahl hb-versteckt">
                    <span data-feld="zahl"></span>
                    <select data-feld="ziel" title="Die gewählten Modelle in einen Ordner legen"></select>
                    <button type="button" data-tat="loeschen" title="Die gewählten Modelle von der Platte löschen"><i class="fas fa-trash"></i> Löschen</button>
                    <button type="button" data-tat="aufheben">Auswahl aufheben</button>
                </span>
                <span class="figurwahl-meldung" data-feld="meldung"></span>`;
            liste.before(leiste);
            this._verdrahten(quelle, leiste);
        }
        const ziel = leiste.querySelector('[data-feld="ziel"]');
        ziel.replaceChildren(...[['__', 'Verschieben nach …'], ['', '— ohne Ordner —'], ...ordner.map(o => [o, o])].map(([wert, text]) => {
            const opt = document.createElement('option');
            opt.value = wert;
            opt.textContent = text;
            return opt;
        }));
    }

    _leisteStand(quelle, liste) {
        // `liste` kann die Liste eines Ordners sein — die Leiste hängt am Bereich, nicht am Ordner.
        const leiste = liste?.closest('details.dialogbereich')?.querySelector(':scope > .figurwahl-ordnerleiste');
        if (!leiste) return;
        const n = this._auswahl(quelle).size;
        leiste.querySelector('.figurwahl-auswahl').classList.toggle('hb-versteckt', n === 0);
        leiste.querySelector('[data-feld="zahl"]').textContent = `${n} gewählt`;
    }

    _verdrahten(quelle, leiste) {
        const feld = name => leiste.querySelector(`[data-feld="${name}"]`);
        const neu = leiste.querySelector('.figurwahl-neuerordner');
        const zeigeNeu = an => {
            neu.classList.toggle('hb-versteckt', !an);
            leiste.querySelector('[data-tat="neu"]').classList.toggle('hb-versteckt', an);
            if (an) feld('name').focus();
            else feld('name').value = '';
        };
        leiste.querySelector('[data-tat="neu"]').addEventListener('click', () => zeigeNeu(true));
        leiste.querySelector('[data-tat="abbrechen"]').addEventListener('click', () => zeigeNeu(false));
        const anlegen = async () => {
            const name = feld('name').value.trim();
            if (!name) return;
            if (await this._tun(quelle, leiste, () => Serverabruf.senden(`${Figurwahlordner.ADRESSE}anlegen/`, { quelle, name }),
                                a => `Ordner „${a.name}“ angelegt.`)) zeigeNeu(false);
        };
        leiste.querySelector('[data-tat="anlegen"]').addEventListener('click', anlegen);
        feld('name').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); anlegen(); }
            if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); zeigeNeu(false); }
        });
        feld('ziel').addEventListener('change', async () => {
            const ordner = feld('ziel').value;
            if (ordner === '__') return;
            const namen = [...this._auswahl(quelle)];
            feld('ziel').value = '__';
            if (!namen.length) return;
            // Die Auswahl leert sich VOR dem Neuaufbau (im Rückruf) — danach stünden die Haken noch gesetzt da.
            await this._tun(quelle, leiste, () => Serverabruf.senden(`${Figurwahlordner.ADRESSE}verschieben/`, { quelle, namen, ordner }), (a) => {
                this._auswahl(quelle).clear();
                return `${a.anzahl} ${a.anzahl === 1 ? 'Modell' : 'Modelle'} ${ordner ? `nach „${ordner}“` : 'aus dem Ordner'} verschoben.`;
            });
        });
        leiste.querySelector('[data-tat="loeschen"]').addEventListener('click', () => this._loeschen(quelle, leiste));
        leiste.querySelector('[data-tat="aufheben"]').addEventListener('click', () => {
            this._auswahl(quelle).clear();
            const bereich = leiste.closest('details.dialogbereich');
            for (const h of bereich.querySelectorAll('input.figurwahl-haken')) h.checked = false;
            this._leisteStand(quelle, bereich.querySelector('ul[data-bereich]'));
        });
    }

    async _loeschen(quelle, leiste) {
        const namen = [...this._auswahl(quelle)];
        if (!namen.length) return;
        const liste = namen.slice(0, 15).map(n => `• ${n}`).join('\n') + (namen.length > 15 ? `\n… und ${namen.length - 15} weitere` : '');
        if (!window.confirm(`${namen.length} ${namen.length === 1 ? 'Modell' : 'Modelle'} endgültig von der Platte löschen?\n\n${liste}`)) return;
        await this._tun(quelle, leiste, () => Serverabruf.senden(Figurwahlordner.LOESCHEN, { art: Figurwahlordner.ARTEN[quelle], namen }), (a) => {
            for (const n of a.geloescht || []) this._auswahl(quelle).delete(n);
            if (namen.includes(this.dialog.gewaehlt?.name)) this.dialog._waehlen(null);
            const fehler = Object.entries(a.fehler || {});
            return `${(a.geloescht || []).length} gelöscht.` + (fehler.length ? ` Nicht gelöscht: ${fehler.map(([n, g]) => `${n} (${g})`).join('; ')}` : '');
        });
    }

    /** Eine Änderung senden, die Meldung neben die Leiste schreiben und den Reiter neu füllen. → `true` bei Erfolg. */
    async _tun(quelle, leiste, senden, meldung) {
        const feld = leiste.querySelector('[data-feld="meldung"]');
        feld.classList.remove('fehlertext');
        feld.textContent = '…';
        try {
            const antwort = await senden();
            // Die Meldung sofort: der Neuaufbau wartet am Ende noch auf die Liste der abgebrochenen Importe (`Figurwahlfuellung`, bis zu Sekunden); die Leiste bleibt dabei stehen.
            feld.textContent = meldung(antwort);
            this._leisteStand(quelle, leiste.closest('details.dialogbereich')?.querySelector('ul[data-bereich]'));
            await this.dialog._fuellen(quelle);
            return true;
        } catch (fehler) {
            feld.classList.add('fehlertext');
            feld.textContent = fehler.daten?.error || fehler.message || String(fehler);
            return false;
        }
    }

    // -- Welcher Ordner offen ist: nur solange der Dialog steht (ein Neuaufbau nach Verschieben klappt ihn nicht zu) --

    /** Beim Öffnen des Dialogs: alle Ordner zu. */
    zuklappen() {
        this._offen.clear();
    }

    /** Ein umbenannter Ordner bleibt offen, wenn er es war. */
    offenUmbenennen(quelle, alt, neu) {
        if (this._offen.delete(`${quelle}:${alt}`)) this._offen.add(`${quelle}:${neu}`);
    }

    _istOffen(quelle, name) {
        return this._offen.has(`${quelle}:${name}`);
    }

    _merken(quelle, name, offen) {
        if (offen) this._offen.add(`${quelle}:${name}`);
        else this._offen.delete(`${quelle}:${name}`);
    }
}
