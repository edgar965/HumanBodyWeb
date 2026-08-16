import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Fallanzeige } from './fallanzeige.js';

/**
 * Testlauf — die Testseite bedienen: Tests starten, Ergebnisse eintragen,
 * Ansicht filtern.
 *
 * Herausgeloest aus templates/testcases.html (Umbau 16.08.2026). Dort standen
 * `runAll`, `runCategory` und `runSingle` als drei fast gleiche Funktionen
 * (12, 14 und 12 Zeilen) — sie unterscheiden sich nur darin, WAS auf "läuft"
 * gestellt wird und welche Frage an den Server geht. Das ist jetzt eine
 * Methode mit zwei Angaben.
 *
 * Dazu behoben: `runTest` las die Antwort ohne `.ok`-Pruefung. Bei einem Fehler
 * im Testlaeufer kam die Django-Fehlerseite in `json()` und die Meldung lautete
 * "Unexpected token '<'" statt der eigentlichen Ursache.
 */
export class Testlauf {

    static ENDPUNKT = '/api/tests/run/';

    /** Knoepfe und Klappen der Seite anmelden. */
    static aufbauen() {
        const lauf = new Testlauf();
        lauf._knoepfe();
        lauf._klappen();
        return lauf;
    }

    /**
     * Tests laufen lassen.
     * @param {Object} frage   {} = alle, {category} oder {category, case}
     * @param {Iterable} faelle  die Faelle, die auf "läuft" gehen
     */
    async laufen(frage = {}, faelle = document.querySelectorAll('.tc-case')) {
        const start = performance.now();
        Fallanzeige.laufend(faelle);
        try {
            const daten = await this._holen(frage);
            Fallanzeige.ergebnisse(daten.results);
            if (frage.category) Fallanzeige.kategoriezaehler(frage.category);
            else Fallanzeige.alleZaehler();
            Fallanzeige.zusammenfassung();
            if (!frage.category) Fallanzeige.zeit(performance.now() - start);
            return daten;
        } catch (fehler) {
            alert('Testlauf fehlgeschlagen: ' + fehler.message);
            return null;
        }
    }

    async _holen(frage) {
        const anhang = new URLSearchParams(frage).toString();
        return Serverabruf.json(Testlauf.ENDPUNKT + (anhang ? '?' + anhang : ''));
    }

    _knoepfe() {
        this._klick('run-all-btn', () => this.laufen());
        this._klick('expand-all-btn', () => this._alleKategorien(true));
        this._klick('collapse-all-btn', () => this._alleKategorien(false));
        this._klick('show-only-failed-btn', () => this._nurFehler());
        this._klick('reset-view-btn', () => this._alleZeigen());
    }

    _klick(kennung, tun) {
        document.getElementById(kennung)?.addEventListener('click', tun);
    }

    _klappen() {
        document.querySelectorAll('[data-toggle-cat]').forEach(kopf => {
            kopf.addEventListener('click', ereignis => {
                // Klicks auf die Knoepfe im Kopf klappen nicht mit.
                if (ereignis.target.closest('button')) return;
                kopf.closest('.tc-cat').classList.toggle('open');
            });
        });
        document.querySelectorAll('.tc-run-cat').forEach(knopf => {
            knopf.addEventListener('click', ereignis => {
                ereignis.stopPropagation();
                this._kategorie(knopf.dataset.category);
            });
        });
        document.querySelectorAll('[data-run-case]').forEach(knopf => {
            knopf.addEventListener('click', ereignis => {
                ereignis.stopPropagation();
                this._einzeln(knopf.dataset.category, knopf.dataset.case);
            });
        });
    }

    _kategorie(kategorieId) {
        const kategorie = document.querySelector(
            `.tc-cat[data-category="${kategorieId}"]`);
        if (!kategorie) return;
        kategorie.classList.add('open');
        this.laufen({ category: kategorieId },
                    kategorie.querySelectorAll('.tc-case'));
    }

    _einzeln(kategorieId, fallId) {
        const fall = document.querySelector(
            `.tc-case[data-category="${kategorieId}"][data-case="${fallId}"]`);
        if (!fall) return;
        this.laufen({ category: kategorieId, case: fallId }, [fall]);
    }

    _alleKategorien(offen) {
        document.querySelectorAll('.tc-cat').forEach(
            kategorie => kategorie.classList.toggle('open', offen));
    }

    /** Nur fehlgeschlagene Faelle zeigen, Kategorien aufklappen. */
    _nurFehler() {
        document.querySelectorAll('.tc-case').forEach(fall => {
            const zustand = fall.querySelector('[data-status]').className;
            fall.classList.toggle('tc-versteckt', !zustand.includes('fail'));
        });
        this._alleKategorien(true);
    }

    _alleZeigen() {
        document.querySelectorAll('.tc-case').forEach(
            fall => fall.classList.remove('tc-versteckt'));
    }
}
