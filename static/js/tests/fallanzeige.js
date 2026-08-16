/**
 * Fallanzeige — der DOM-Teil der Testseite: Status eines Falls, Zaehler je
 * Kategorie, Zusammenfassung oben.
 *
 * Herausgeloest aus templates/testcases.html (Umbau 16.08.2026). Der Block dort
 * hatte 137 Zeilen inline, darin dreimal dasselbe Muster (alles auf "läuft",
 * Server rufen, Ergebnisse eintragen, Zaehler, Zusammenfassung) — einmal fuer
 * alle Tests, einmal je Kategorie, einmal je Fall. Die Serverseite steht jetzt
 * in `testlauf.js`, die Anzeige hier.
 */
export class Fallanzeige {

    /** Symbol je Zustand. */
    static SYMBOLE = {
        ok: 'fa-check-circle',
        fail: 'fa-times-circle',
        running: 'fa-spinner fa-spin',
        pending: 'fa-circle',
    };

    /** Einen Fall auf einen Zustand setzen. */
    static setzen(element, zustand, einzelheit, dauerMs, fehler) {
        const symbol = element.querySelector('[data-status]');
        symbol.className = 'tc-status ' + zustand;
        symbol.innerHTML = `<i class="fas ${Fallanzeige.SYMBOLE[zustand]
            || 'fa-question-circle'}"></i>`;
        element.querySelector('[data-detail]').textContent = einzelheit || '';
        element.querySelector('[data-duration]').textContent =
            dauerMs != null ? `${dauerMs}ms` : '';
        element.querySelector('[data-error]').textContent = fehler || '';
        element.classList.toggle('has-error', !!fehler);
    }

    /** Die uebergebenen Faelle auf "läuft" stellen. */
    static laufend(faelle) {
        for (const fall of faelle) {
            Fallanzeige.setzen(fall, 'running', '', null, null);
        }
    }

    /** Ergebnisliste des Servers in die Seite eintragen. */
    static ergebnisse(liste) {
        for (const ergebnis of liste || []) {
            const fall = document.querySelector(
                `.tc-case[data-category="${ergebnis.categoryId}"]`
                + `[data-case="${ergebnis.caseId}"]`);
            if (fall) {
                Fallanzeige.setzen(fall, ergebnis.ok ? 'ok' : 'fail',
                                   ergebnis.detail, ergebnis.durationMs,
                                   ergebnis.error);
            }
        }
    }

    /** Zaehler am Kategoriekopf. */
    static kategoriezaehler(kategorieId) {
        const kategorie = document.querySelector(
            `.tc-cat[data-category="${kategorieId}"]`);
        if (!kategorie) return;
        const faelle = kategorie.querySelectorAll('.tc-case');
        const { gut, schlecht, offen } = Fallanzeige._zaehlen(faelle);
        const abzeichen = kategorie.querySelector('.tc-cat-badge');
        abzeichen.innerHTML = offen === faelle.length ? ''
            : `<span class="tc-pass">✓ ${gut}</span> · `
              + `<span class="tc-fail">✗ ${schlecht}</span>`;
    }

    /** Zaehler aller Kategorien. */
    static alleZaehler() {
        document.querySelectorAll('.tc-cat').forEach(
            kategorie => Fallanzeige.kategoriezaehler(kategorie.dataset.category));
    }

    /** Zusammenfassung oben. */
    static zusammenfassung() {
        const faelle = document.querySelectorAll('.tc-case');
        const { gut, schlecht } = Fallanzeige._zaehlen(faelle);
        document.getElementById('sum-total').textContent =
            `${faelle.length} Tests`;
        document.getElementById('sum-pass').textContent = gut;
        document.getElementById('sum-fail').textContent = schlecht;
    }

    static zeit(millisekunden) {
        document.getElementById('sum-time').textContent =
            `${Math.round(millisekunden)}ms gesamt`;
    }

    static _zaehlen(faelle) {
        let gut = 0, schlecht = 0, offen = 0;
        for (const fall of faelle) {
            const zustand = fall.querySelector('[data-status]').className;
            if (zustand.includes('ok')) gut++;
            else if (zustand.includes('fail')) schlecht++;
            else offen++;
        }
        return { gut, schlecht, offen };
    }
}
