import { Htmltext } from '/static/djangobase/js/htmltext.js';
import { Serverabruf } from '/static/djangobase/js/serverabruf.js';
import { Kategoriekasten } from '../../viewer/gemeinsam/kategoriekasten.js';

/**
 * Animationsbrowser — der Dialog „Animation wählen" der Seite „Effekte".
 *
 * Edgar, 12.09.2026: „mach mir einen Browser wo ich meine Animationen wählen
 * kann". Zwei Gruppen in EINEM Baum:
 *
 *   Process Videos   die fertigen Aufträge (BVH-Pfad, Pipeline, Format) —
 *                    stehen als JSON in der Seite (`#effektAuftraegeBvh`)
 *   Bibliothek       `3DObjects/animations/bvh/<Kategorie>/<Name>.bvh`,
 *                    Kategorie für Kategorie von /api/character/animations/
 *                    (7.000 Dateien; darum ein Suchfeld)
 *
 * Der Baum ist der der anderen Seiten (`Kategoriekasten`, `animationsbaum.css`),
 * der Rahmen der des Figurwahldialogs (`figurwahldialog.css`). Gewählt wird
 * mit Klick, übernommen mit Doppelklick oder dem Knopf; das Ergebnis geht als
 * `{wert, name, meta, format, passt}` an den Aufrufer — `wert` ist der Pfad
 * (Auftrag) oder die Bibliotheksadresse (`/api/character/bvh/<k>/<n>/`),
 * der Server macht daraus die Datei (`Effektpruefung.bvh_pfad`).
 */
export class Animationsbrowser {

    static ID = 'effekt-animationen-dialog';
    static BIBLIOTHEK = '/api/character/animations/';
    static AUFTRAEGE = 'Process Videos';

    /**
     * @param {Array} auftraege  Einträge aus `Effektquellen.bvh_dateien()`
     * @param {Function} beimWaehlen (auswahl) => …
     */
    constructor(auftraege, beimWaehlen) {
        this.auftraege = auftraege || [];
        this.beimWaehlen = beimWaehlen;
        this.bibliothek = null;
        this.element = null;
        this.gewaehlt = null;
        this.gesperrt = () => false;
    }

    /** Öffnen; `gesperrt(eintrag)` sagt, was in der Pipeline nicht geht. */
    async oeffnen(gesperrt = null) {
        this.gesperrt = gesperrt || (() => false);
        const dialog = this._element();
        dialog.classList.add('visible');
        this._waehlen(null);
        this._feld('suche').value = '';
        if (!this.bibliothek) await this._bibliothekLaden();
        this._zeichnen('');
        this._feld('suche').focus();
    }

    schliessen() {
        this.element?.classList.remove('visible');
    }

    // ------------------------------------------------------------ Aufbau

    _element() {
        if (this.element) return this.element;
        const overlay = document.createElement('div');
        overlay.className = 'scene-modal-overlay figurwahl-dialog effekt-animationen';
        overlay.id = Animationsbrowser.ID;
        overlay.innerHTML = this._html();
        document.body.appendChild(overlay);
        this.element = overlay;
        this._verdrahten();
        return overlay;
    }

    _html() {
        const k = Animationsbrowser.ID;
        return `
    <div class="scene-modal effekt-animationen-modal">
        <div class="scene-modal-header">
            <h4><i class="fas fa-running"></i> Animation wählen</h4>
            <button class="scene-modal-close" data-close>&times;</button>
        </div>
        <div class="scene-modal-body">
            <input type="search" id="${k}-suche" class="effekt-suche"
                   placeholder="Suchen (Name, Kategorie, Pipeline) …" autocomplete="off">
            <div class="effekt-baum" id="${k}-baum"></div>
        </div>
        <div class="scene-modal-footer">
            <span class="dialoghinweis" id="${k}-hinweis">Erst einen Eintrag wählen</span>
            <button data-close>Abbrechen</button>
            <button class="primary" id="${k}-bestaetigen" disabled>Übernehmen</button>
        </div>
    </div>`;
    }

    _feld(name) {
        return this.element?.querySelector(`#${Animationsbrowser.ID}-${name}`) || null;
    }

    _verdrahten() {
        for (const knopf of this.element.querySelectorAll('[data-close]')) {
            knopf.addEventListener('click', () => this.schliessen());
        }
        this.element.addEventListener('click', (e) => {
            if (e.target === this.element) this.schliessen();
        });
        this._feld('suche').addEventListener('input',
            (e) => this._zeichnen(e.target.value));
        this._feld('bestaetigen').addEventListener('click', () => this._uebernehmen());
    }

    // ------------------------------------------------------------- Daten

    async _bibliothekLaden() {
        const baum = this._feld('baum');
        baum.innerHTML = '<p class="gedaempft"><i class="fas fa-spinner fa-spin"></i> Lade Bibliothek …</p>';
        try {
            const daten = await Serverabruf.json(Animationsbrowser.BIBLIOTHEK);
            this.bibliothek = daten.categories || {};
        } catch (fehler) {
            this.bibliothek = {};
            baum.innerHTML = `<p class="fehlertext">Bibliothek nicht ladbar: ${Htmltext.t(fehler.message)}</p>`;
        }
    }

    /** Alle Gruppen als [{titel, eintraege: [{wert, name, meta, format, passt, suchtext}]}]. */
    gruppen() {
        const gruppen = [];
        if (this.auftraege.length) {
            gruppen.push({ titel: Animationsbrowser.AUFTRAEGE, eintraege: this.auftraege.map(a => ({
                wert: a.pfad, name: a.name, format: a.format || '', passt: Boolean(a.passt),
                meta: `${a.pipeline} · ${a.bilder} Bilder @ ${a.bildrate} fps`
                    + (a.format ? ` · ${a.format}` : ' · Format unbekannt'),
                suchtext: `${a.name} ${a.auftrag} ${a.pipeline} ${a.format}`.toLowerCase(),
            })) });
        }
        for (const [kategorie, liste] of Object.entries(this.bibliothek || {})) {
            gruppen.push({ titel: kategorie, eintraege: liste.map(e => ({
                wert: e.url, name: `${e.name}.bvh`, format: '', passt: null,
                meta: `${kategorie} · ${e.frames} Bilder`,
                suchtext: `${e.name} ${kategorie}`.toLowerCase(),
            })) });
        }
        return gruppen;
    }

    // ------------------------------------------------------------ Zeichnen

    _zeichnen(suche) {
        const baum = this._feld('baum');
        const wort = suche.trim().toLowerCase();
        baum.replaceChildren();
        let treffer = 0;
        for (const gruppe of this.gruppen()) {
            const eintraege = wort
                ? gruppe.eintraege.filter(e => e.suchtext.includes(wort)) : gruppe.eintraege;
            if (!eintraege.length) continue;
            treffer += eintraege.length;
            // Zugeklappt ist die Vorgabe (Edgar, 12.09.2026); nur eine Suche
            // klappt auf, sonst sähe man die Treffer nicht.
            const { kasten, koerper } = Kategoriekasten.bauen(
                gruppe.titel, eintraege.length, { offen: Boolean(wort) });
            for (const eintrag of eintraege) koerper.appendChild(this._zeile(eintrag));
            baum.appendChild(kasten);
        }
        if (!treffer) {
            baum.innerHTML = '<p class="gedaempft">Nichts gefunden.</p>';
        }
    }

    _zeile(eintrag) {
        const zeile = document.createElement('div');
        const gesperrt = this.gesperrt(eintrag);
        zeile.className = 'anim-item' + (gesperrt ? ' effekt-gesperrt' : '');
        zeile.dataset.wert = eintrag.wert;
        const name = document.createElement('span');
        name.textContent = eintrag.name;
        const meta = document.createElement('span');
        meta.className = 'frames';
        meta.textContent = gesperrt ? `${eintrag.meta} · ${gesperrt}` : eintrag.meta;
        zeile.append(name, meta);
        if (gesperrt) {
            zeile.title = gesperrt;
            return zeile;
        }
        zeile.addEventListener('click', () => this._waehlen(eintrag));
        zeile.addEventListener('dblclick', () => { this._waehlen(eintrag); this._uebernehmen(); });
        return zeile;
    }

    _waehlen(eintrag) {
        this.gewaehlt = eintrag;
        this._feld('bestaetigen').disabled = !eintrag;
        this._feld('hinweis')?.classList.toggle('hb-versteckt', Boolean(eintrag));
        for (const zeile of this.element.querySelectorAll('.anim-item')) {
            zeile.classList.toggle('active', Boolean(eintrag) && zeile.dataset.wert === eintrag.wert);
        }
    }

    _uebernehmen() {
        if (!this.gewaehlt) return;
        this.schliessen();
        this.beimWaehlen(this.gewaehlt);
    }
}
