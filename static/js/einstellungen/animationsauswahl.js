/**
 * Animationsauswahl — das aufklappbare Auswahlfeld der Einstellungsseiten.
 *
 * Umbau 16.08.2026, zwei Gruende:
 *
 * 1. Performance. Die Vorlage lieferte alle 7.067 Animationen mit, obwohl jede
 *    Kategorie zugeklappt startet. Jetzt kommen nur die Kategoriekoepfe; die
 *    Eintraege holt diese Klasse beim ERSTEN Aufklappen von
 *    /api/animationen/<kategorie>/ und behaelt sie danach im DOM.
 * 2. Doppelter Code (Anforderung 6). Die Aufklapp- und Auswahllogik stand
 *    Zeile fuer Zeile identisch in settings_model.html, settings_result.html,
 *    settings_scene.html und settings_theatre.html — vier Kopien, die bei
 *    jeder Aenderung einzeln nachgezogen werden mussten.
 *
 * Jedes Widget arbeitet nur in seinem eigenen Wurzelelement. Das frueher
 * noetige `data-selector` an jedem einzelnen Eintrag entfaellt damit: die
 * Zugehoerigkeit steht in der DOM-Struktur, nicht in 7.067 Attributen.
 */
import { Protokoll } from '../../viewer/gemeinsam/protokoll.js';
export class Animationsauswahl {

    static ENDPUNKT = '/api/animationen/';
    static LEER_TEXT = '(Keine Auto-Load)';

    /** Alle Widgets einer Seite in Betrieb nehmen. */
    static alleStarten(wurzel = document) {
        return Array.from(wurzel.querySelectorAll('.anim-auswahl'))
            .map(el => new Animationsauswahl(el));
    }

    constructor(element) {
        this.element = element;
        this.wertformat = element.dataset.wertformat || 'url';
        this.feld = element.querySelector('input[type="hidden"]');
        this.anzeige = document.getElementById(element.id + '-display');
        this.geladen = new Set();
        this._verdrahten();
    }

    _verdrahten() {
        this.element.querySelectorAll('.anim-kopf').forEach(kopf => {
            kopf.addEventListener('click', () => this.umschalten(kopf.parentElement));
        });
        // Ein Zuhoerer fuer alle Eintraege statt einer je Eintrag — die
        // nachgeladenen gibt es beim Verdrahten noch gar nicht.
        this.element.addEventListener('click', ereignis => {
            const eintrag = ereignis.target.closest('.anim-eintrag');
            if (eintrag && this.element.contains(eintrag)) this.waehlen(eintrag);
        });
    }

    async umschalten(kategorie) {
        const koerper = kategorie.querySelector('.anim-koerper');
        const pfeil = kategorie.querySelector('.anim-pfeil');
        const oeffnen = koerper.hidden;
        koerper.hidden = !oeffnen;
        pfeil.classList.toggle('offen', oeffnen);
        if (oeffnen) await this.nachladen(kategorie, koerper);
    }

    async nachladen(kategorie, koerper) {
        const name = kategorie.dataset.kategorie;
        if (this.geladen.has(name)) return;
        this.geladen.add(name);
        koerper.textContent = 'lädt …';
        try {
            const adresse = `${Animationsauswahl.ENDPUNKT}${encodeURIComponent(name)}/`
                + `?wertformat=${this.wertformat}&t=${Date.now()}`;
            const antwort = await fetch(adresse);
            if (!antwort.ok) throw new Error('HTTP ' + antwort.status);
            const daten = await antwort.json();
            this.eintragenIn(koerper, daten.animationen || []);
        } catch (fehler) {
            // Nochmal versuchen zu duerfen ist hier wichtiger als die Zeile im
            // Log: ohne das Zuruecknehmen bliebe die Kategorie fuer immer leer.
            this.geladen.delete(name);
            koerper.textContent = 'Fehler beim Laden';
            Protokoll.warnung('animationsauswahl', 'Animationen der Kategorie', name, 'nicht ladbar:', fehler);
        }
    }

    eintragenIn(koerper, animationen) {
        const aktuell = this.feld ? this.feld.value : '';
        koerper.textContent = '';
        const sammlung = document.createDocumentFragment();
        animationen.forEach(anim => {
            const zeile = document.createElement('div');
            zeile.className = 'anim-eintrag anim-tief';
            if (anim.value === aktuell) zeile.classList.add('gewaehlt');
            zeile.dataset.value = anim.value;
            zeile.textContent = anim.label;
            sammlung.appendChild(zeile);
        });
        koerper.appendChild(sammlung);
    }

    waehlen(eintrag) {
        const wert = eintrag.dataset.value || '';
        if (this.feld) this.feld.value = wert;
        if (this.anzeige) this.anzeige.textContent = wert || Animationsauswahl.LEER_TEXT;
        this.element.querySelectorAll('.anim-eintrag.gewaehlt')
            .forEach(e => e.classList.remove('gewaehlt'));
        eintrag.classList.add('gewaehlt');
    }
}
