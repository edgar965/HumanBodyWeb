/**
 * Standardmodell — das Vorgabemodell einer Seite über den Figurwahl-Dialog wählen.
 *
 * WARUM (Edgar, 19.09.2026, Einstellungen → Szene): „fehlt die Möglichkeit,
 * auch ein Genesis, UMA usw. als Standard-Modell auszuwählen. Mach die
 * Modellauswahl in einem Dialog. Nimm den Modell-Hinzufügen-Dialog von Szene
 * und BVH-Studio." Bis dahin war das Feld ein `<select>` mit den HumanBody-
 * Vorgaben (`Modellfeld`) — die anderen fünf Figurarten kamen nicht vor.
 * Seit dem 21.09.2026 auf allen Einstellungsseiten (Edgar: „Korrigiere das
 * auch bei den anderen"): `{% modell %}` baut den Kasten, `alleStarten()`
 * findet ihn über `data-modellkasten`. Nur die Szene lädt jede Figurart
 * (`data-quellen="alle"`); Theatre, Ergebnis, Konfiguration, Animationen,
 * Effekte und SMPL laden über `/api/character/model/<name>/` — also nur den
 * Reiter HumanBody, dort aber beide Bereiche (Körpertypen und Gespeichertes).
 *
 * Es ist DERSELBE Dialog wie „Charakter hinzufügen" in der Szene und
 * „Modell hinzufügen" im Studio (`viewer/gemeinsam/figurwahldialog.js`),
 * ohne Lage-Felder, ohne Umbenennen und Löschen — die Einstellungsseite
 * pflegt keine Modelle. Die Wahl landet in versteckten Formularfeldern
 * (Name; bei der Szene auch Figurart und Bereich); gespeichert wird mit dem
 * Formular wie bisher. Die Szene liest sie beim Start (`scene/startfigur.js`).
 *
 * Node-testbar bis auf `oeffnen` (`test_js_standardmodell.py`): Der Dialog
 * baut sein HTML erst beim Öffnen.
 */
import { Figurwahldialog } from '../../viewer/gemeinsam/figurwahldialog.js';
import { Figurkataloge } from '../../viewer/gemeinsam/figurkataloge.js';
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';

export class Standardmodell {

    /** Was ohne Wahl gilt — die alte Vorgabe der Szene-Seite. */
    static VORGABE = { name: 'femaleWithClothes', quelle: 'modell', bereich: 'gespeichert' };

    /** Jeden Kasten der Seite (`_einstellungen_modell.html`) anbinden. */
    static alleStarten(wurzel = document) {
        return Array.from(wurzel.querySelectorAll('[data-modellkasten]'))
            .map(kasten => Standardmodell.ausKasten(kasten).anbinden());
    }

    /** Wahl und Einstellungen aus den Feldern und `data-*` des Kastens. */
    static ausKasten(kasten) {
        const wert = (feld) => kasten.querySelector(`[data-feld="${feld}"]`)?.value || '';
        return new Standardmodell(kasten,
            { name: wert('name'), quelle: wert('quelle'), bereich: wert('bereich') },
            { kennung: `${kasten.id || 'standardmodell'}-dialog`,
              quellen: kasten.dataset.quellen === 'alle' ? null : ['modell'],
              leer: kasten.dataset.leer || '' });
    }

    /**
     * @param {HTMLElement} kasten  Behälter mit `[data-feld=name|quelle|bereich]`
     *        (versteckte Eingaben), `[data-anzeige=name]`, `[data-anzeige=meta]`
     *        und den Knöpfen `[data-tun=waehlen]` und wahlweise `[data-tun=leeren]`
     * @param {Object} wahl         { name, quelle, bereich } — der gespeicherte Stand
     * @param {Object} einstellungen
     *   kennung  Präfix der Dialog-IDs (je Feld ein eigener)
     *   quellen  Reiter des Dialogs; null = alle (nur die Szene lädt alle)
     *   leer     Anzeigetext ohne Modell; gesetzt = das Feld darf leer sein
     */
    constructor(kasten, wahl, { kennung = 'standardmodell-dialog', quellen = null, leer = '' } = {}) {
        this.kasten = kasten;
        this.leer = leer;
        this.wahl = { ...this.vorgabe(), ...Standardmodell.bereinigt(wahl) };
        const lader = {};
        for (const quelle of (quellen || Figurkataloge.REIHENFOLGE)) {
            lader[quelle] = (name, lage, eintrag) => this.uebernehmen(quelle, name, eintrag);
        }
        this.dialog = new Figurwahldialog({
            lader,
            titel: 'Standard-Modell wählen',
            knopf: 'Übernehmen',
            symbol: 'fa-user',
            lage: false,
            kennung,
        });
    }

    /** Darf das Feld leer sein, ist „kein Modell" die Vorgabe. */
    vorgabe() {
        return this.leer ? { ...Standardmodell.VORGABE, name: '' } : Standardmodell.VORGABE;
    }

    /** Leere und unbekannte Angaben fallen auf die Vorgabe zurück. */
    static bereinigt(wahl) {
        const sauber = {};
        if (wahl?.name) sauber.name = String(wahl.name);
        if (wahl?.quelle && Figurkataloge.QUELLEN[wahl.quelle]) sauber.quelle = wahl.quelle;
        if (wahl?.bereich === 'standard' || wahl?.bereich === 'gespeichert') sauber.bereich = wahl.bereich;
        return sauber;
    }

    /** Knöpfe anbinden, Felder und Anzeige auf den gespeicherten Stand setzen. */
    anbinden() {
        this.kasten.querySelector('[data-tun="waehlen"]')
            ?.addEventListener('click', () => this.dialog.oeffnen());
        this.kasten.querySelector('[data-tun="leeren"]')
            ?.addEventListener('click', () => this.leeren());
        this.zeigen(null);
        this.nachschlagen();
        return this;
    }

    /** Die gewählte Zeile in die Felder und die Anzeige schreiben. */
    uebernehmen(quelle, name, eintrag = null) {
        this.wahl = { name, quelle, bereich: eintrag?.bereich || 'standard' };
        this.zeigen(eintrag);
        return this.wahl;
    }

    /** „Keins": kein Modell vorwählen — nur, wo das Feld leer sein darf. */
    leeren() {
        this.wahl = { ...this.wahl, name: '' };
        this.zeigen(null);
        return this.wahl;
    }

    /** Felder und Anzeige aus `this.wahl`; `eintrag` liefert Anzeigetext und Unterzeile. */
    zeigen(eintrag) {
        for (const feld of ['name', 'quelle', 'bereich']) {
            const eingabe = this.kasten.querySelector(`[data-feld="${feld}"]`);
            if (eingabe) eingabe.value = this.wahl[feld];
        }
        const name = this.kasten.querySelector('[data-anzeige="name"]');
        const meta = this.kasten.querySelector('[data-anzeige="meta"]');
        if (name) name.textContent = this.wahl.name ? (eintrag?.anzeige || this.wahl.name) : this.leer;
        if (meta) meta.textContent = this.wahl.name ? Standardmodell.beschreibung(this.wahl, eintrag) : '';
    }

    /** „Genesis 9 · Standard-Modell · weiblich · 25.000 Punkte · 3 Regler gesetzt". */
    static beschreibung(wahl, eintrag = null) {
        const teile = [Figurkataloge.QUELLEN[wahl.quelle]?.titel || wahl.quelle];
        teile.push(wahl.bereich === 'gespeichert' ? 'gespeichertes Modell' : 'Standard-Modell');
        if (eintrag?.unterzeile) teile.push(eintrag.unterzeile);
        return teile.join(' · ');
    }

    /**
     * Den Anzeigetext des gespeicherten Stands aus dem Katalog holen — ohne
     * Treffer bleibt der Name stehen, mit Hinweis: Das Modell gibt es nicht mehr.
     */
    async nachschlagen() {
        if (!this.wahl.name) return null;
        let eintraege;
        try {
            eintraege = await Figurkataloge.liste(this.wahl.quelle);
        } catch (fehler) {
            Protokoll.warnung('standardmodell', 'Katalog nicht ladbar:', fehler);
            return null;
        }
        const eintrag = eintraege.find(e => e.name === this.wahl.name) || null;
        if (eintrag) {
            this.wahl.bereich = eintrag.bereich || this.wahl.bereich;
            this.zeigen(eintrag);
        } else {
            const meta = this.kasten.querySelector('[data-anzeige="meta"]');
            if (meta) meta.textContent = Standardmodell.beschreibung(this.wahl)
                + ' · nicht mehr im Katalog — bitte neu wählen';
        }
        return eintrag;
    }
}
