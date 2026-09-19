/**
 * Standardmodell — das Vorgabemodell einer Seite über den Figurwahl-Dialog wählen.
 *
 * WARUM (Edgar, 19.09.2026, Einstellungen → Szene): „fehlt die Möglichkeit,
 * auch ein Genesis, UMA usw. als Standard-Modell auszuwählen. Mach die
 * Modellauswahl in einem Dialog. Nimm den Modell-Hinzufügen-Dialog von Szene
 * und BVH-Studio." Bis dahin war das Feld ein `<select>` mit den HumanBody-
 * Vorgaben (`Modellfeld`) — die anderen fünf Figurarten kamen nicht vor.
 *
 * Es ist DERSELBE Dialog wie „Charakter hinzufügen" in der Szene und
 * „Modell hinzufügen" im Studio (`viewer/gemeinsam/figurwahldialog.js`),
 * alle Reiter, ohne Lage-Felder, ohne Umbenennen und Löschen — die
 * Einstellungsseite pflegt keine Modelle. Die Wahl landet in drei
 * versteckten Formularfeldern (Name, Figurart, Bereich); gespeichert wird
 * mit dem Formular wie bisher. Die Szene liest sie beim Start
 * (`scene/startfigur.js`).
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

    /**
     * @param {HTMLElement} kasten  Behälter mit `[data-feld=name|quelle|bereich]`
     *        (versteckte Eingaben), `[data-anzeige=name]`, `[data-anzeige=meta]`
     *        und dem Knopf `[data-tun=waehlen]`
     * @param {Object} wahl         { name, quelle, bereich } — der gespeicherte Stand
     * @param {string} kennung      Präfix der Dialog-IDs (je Feld ein eigener)
     */
    constructor(kasten, wahl, kennung = 'standardmodell-dialog') {
        this.kasten = kasten;
        this.wahl = { ...Standardmodell.VORGABE, ...Standardmodell.bereinigt(wahl) };
        const lader = {};
        for (const quelle of Figurkataloge.REIHENFOLGE) {
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

    /** Leere und unbekannte Angaben fallen auf die Vorgabe zurück. */
    static bereinigt(wahl) {
        const sauber = {};
        if (wahl?.name) sauber.name = String(wahl.name);
        if (wahl?.quelle && Figurkataloge.QUELLEN[wahl.quelle]) sauber.quelle = wahl.quelle;
        if (wahl?.bereich === 'standard' || wahl?.bereich === 'gespeichert') sauber.bereich = wahl.bereich;
        return sauber;
    }

    /** Knopf anbinden, Felder und Anzeige auf den gespeicherten Stand setzen. */
    anbinden() {
        this.kasten.querySelector('[data-tun="waehlen"]')
            ?.addEventListener('click', () => this.dialog.oeffnen());
        this.zeigen(null);
        this.nachschlagen();
    }

    /** Die gewählte Zeile in die Felder und die Anzeige schreiben. */
    uebernehmen(quelle, name, eintrag = null) {
        this.wahl = { name, quelle, bereich: eintrag?.bereich || 'standard' };
        this.zeigen(eintrag);
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
        if (name) name.textContent = eintrag?.anzeige || this.wahl.name;
        if (meta) meta.textContent = Standardmodell.beschreibung(this.wahl, eintrag);
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
