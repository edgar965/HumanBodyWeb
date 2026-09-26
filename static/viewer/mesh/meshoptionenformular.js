/**
 * Meshoptionenformular — baut die Optionsfelder aus `Meshoptionen.katalog()` (JSON im
 * `#mesh-katalog`-Script-Tag oder per fetch) in einen Behälter.
 *
 * Jedes Feld nach `art`: `wahl` → `<select>`, `mehrfach` → Kästchen, `zahl` → `<input
 * type="number">`. Eine Option mit `fehlt` (Text) wird angezeigt, aber deaktiviert —
 * genau der Fall „Formmodell noch nicht heruntergeladen/verdrahtet".
 */
export class Meshoptionenformular {

    /**
     * @param {HTMLElement} behaelter
     * @param {object} katalog `{optionen: [...], rollen: [...]}`
     * @param {object} werte aktuelle Werte (Vorgabe, wenn leer)
     */
    static bauen(behaelter, katalog, werte = {}) {
        behaelter.innerHTML = '';
        for (const feld of katalog.optionen) {
            const zeile = document.createElement('div');
            zeile.className = 'mesh-optionsfeld';
            const label = document.createElement('label');
            label.textContent = feld.titel;
            if (feld.hinweis) label.title = feld.hinweis;
            zeile.appendChild(label);
            const wert = werte[feld.schluessel] ?? feld.vorgabe;
            if (feld.art === 'wahl') {
                zeile.appendChild(Meshoptionenformular._wahl(feld, wert));
            } else if (feld.art === 'mehrfach') {
                zeile.appendChild(Meshoptionenformular._mehrfach(feld, wert));
            } else if (feld.art === 'zahl') {
                zeile.appendChild(Meshoptionenformular._zahl(feld, wert));
            }
            behaelter.appendChild(zeile);
        }
    }

    static _wahl(feld, wert) {
        const auswahl = document.createElement('select');
        auswahl.name = feld.schluessel;
        auswahl.className = 'viewer-select';
        for (const eintrag of feld.werte) {
            const option = document.createElement('option');
            option.value = eintrag.wert;
            option.textContent = eintrag.fehlt ? `${eintrag.text} — ${eintrag.fehlt}` : eintrag.text;
            option.disabled = !!eintrag.fehlt;
            option.selected = eintrag.wert === wert;
            auswahl.appendChild(option);
        }
        return auswahl;
    }

    static _mehrfach(feld, werte) {
        const gruppe = document.createElement('div');
        gruppe.className = 'mesh-kaestchengruppe';
        gruppe.dataset.feld = feld.schluessel;
        for (const eintrag of feld.werte) {
            const kasten = document.createElement('label');
            kasten.className = 'mesh-kaestchen';
            const eingabe = document.createElement('input');
            eingabe.type = 'checkbox';
            eingabe.value = eintrag.wert;
            eingabe.checked = (werte || []).includes(eintrag.wert);
            kasten.append(eingabe, document.createTextNode(' ' + eintrag.text));
            gruppe.appendChild(kasten);
        }
        return gruppe;
    }

    static _zahl(feld, wert) {
        const eingabe = document.createElement('input');
        eingabe.type = 'number';
        eingabe.name = feld.schluessel;
        eingabe.className = 'viewer-eingabe';
        eingabe.min = String(feld.min ?? '');
        eingabe.max = String(feld.max ?? '');
        eingabe.value = String(wert);
        return eingabe;
    }

    /** Liest die aktuell im Behälter stehenden Werte als `{schluessel: wert}`. */
    static lesen(behaelter) {
        const aus = {};
        for (const auswahl of behaelter.querySelectorAll('select[name]')) aus[auswahl.name] = auswahl.value;
        for (const eingabe of behaelter.querySelectorAll('input[type="number"][name]')) {
            aus[eingabe.name] = Number(eingabe.value);
        }
        for (const gruppe of behaelter.querySelectorAll('.mesh-kaestchengruppe[data-feld]')) {
            aus[gruppe.dataset.feld] = [...gruppe.querySelectorAll('input:checked')].map(k => k.value);
        }
        return aus;
    }
}
