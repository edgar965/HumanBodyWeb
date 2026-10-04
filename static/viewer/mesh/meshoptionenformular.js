/**
 * Meshoptionenformular — baut die Optionsfelder aus `Meshoptionen.katalog()` (JSON im
 * `#mesh-katalog`-Script-Tag oder per fetch) in einen Behälter.
 *
 * Jedes Feld nach `art`: `wahl` → `<select>`, `mehrfach` → Kästchen, `haken` → ein Häkchen
 * (Werte `an`/`aus` des Katalogs), `zahl` → `<input type="number">`. Eine Option mit `fehlt` (Text) wird angezeigt, aber deaktiviert —
 * genau der Fall „Formmodell noch nicht heruntergeladen/verdrahtet".
 *
 * Felder mit `fein` (die Stellschrauben der Pipelines selbst, seit 27.09.2026) stehen in
 * einem zugeklappten `<details>` darunter: Sie gehören ins Formular, sollen aber die acht
 * Felder, die man täglich braucht, nicht zuschütten.
 */
export class Meshoptionenformular {

    /**
     * @param {HTMLElement} behaelter
     * @param {object} katalog `{optionen: [...], rollen: [...]}`
     * @param {object} werte aktuelle Werte (Vorgabe, wenn leer)
     */
    static bauen(behaelter, katalog, werte = {}) {
        behaelter.innerHTML = '';
        const fein = katalog.optionen.filter(f => f.fein);
        for (const feld of katalog.optionen.filter(f => !f.fein)) {
            behaelter.appendChild(Meshoptionenformular._zeile(feld, werte));
        }
        if (!fein.length) return;
        const klappe = document.createElement('details');
        klappe.className = 'mesh-feineinstellungen';
        const titel = document.createElement('summary');
        // `fein_titel` (02.10.2026): die Gruppe „Mesh" der 2D3D Kleider nennt ihren Bereich wie der TRELLIS.2-Space.
        titel.textContent = katalog.fein_titel || 'Feineinstellungen der Modelle';
        klappe.appendChild(titel);
        // Die Felder in EINEM Behälter: Ein Raster auf dem `<details>` selbst greift in Chrome nicht (der Inhalt liegt in
        // `::details-content`) — so kann eine Seite sie mit `.mesh-fein-felder` anordnen; ohne Regel bleibt es wie vorher.
        const felder = document.createElement('div');
        felder.className = 'mesh-fein-felder';
        for (const feld of fein) felder.appendChild(Meshoptionenformular._zeile(feld, werte));
        klappe.appendChild(felder);
        behaelter.appendChild(klappe);
        Meshoptionenformular._gilt(behaelter, katalog.gilt_nach);
    }

    /**
     * Felder mit `gilt` (Liste von Werten) zeigt das Formular nur, wenn das Feld `gilt_nach` (02.10.2026: das Modell der Gruppe
     * „Mesh" von „2D3D Kleider") einen dieser Werte trägt — TRELLIS.2 und Pixal3D haben verschiedene Regler. Ausgeblendet
     * heißt nicht verworfen: `lesen` liest alle Felder, die Werte bleiben beim Wechsel erhalten.
     */
    static _gilt(behaelter, gilt_nach) {
        const wahl = gilt_nach && behaelter.querySelector(`select[name="${gilt_nach}"]`);
        if (!wahl) return;
        const anwenden = () => {
            for (const zeile of behaelter.querySelectorAll('.mesh-optionsfeld[data-gilt]')) {
                zeile.classList.toggle('hb-versteckt', !zeile.dataset.gilt.split(' ').includes(wahl.value));
            }
        };
        wahl.addEventListener('change', anwenden);
        anwenden();
    }

    static _zeile(feld, werte) {
        const zeile = document.createElement('div');
        zeile.className = 'mesh-optionsfeld';
        if (feld.gilt) zeile.dataset.gilt = feld.gilt.join(' ');
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
        } else if (feld.art === 'text') {
            zeile.appendChild(Meshoptionenformular._text(feld, wert));
        } else if (feld.art === 'haken') {
            zeile.appendChild(Meshoptionenformular._haken(feld, wert));
        } else if (feld.art === 'farbe') {
            zeile.appendChild(Meshoptionenformular._farbe(feld, wert));
        }
        // Nur bei den Feineinstellungen steht der Hinweis auch als Text da — sie sind neu
        // und erklärungsbedürftig; bei den Hauptfeldern bliebe es beim Tooltip, sonst wird
        // aus acht Feldern eine Textwand.
        if (feld.hinweis && feld.fein) {
            const hinweis = document.createElement('span');
            hinweis.className = 'hb-hinweis mesh-optionshinweis';
            hinweis.textContent = feld.hinweis;
            zeile.appendChild(hinweis);
        }
        return zeile;
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
        if (feld.schritt) eingabe.step = String(feld.schritt);
        eingabe.value = String(wert);
        return eingabe;
    }

    /**
     * Ein einzelnes Häkchen — Art `haken` (03.10.2026, „Körper senkrecht stellen" von „2D3D Kleider"): angehakt liefert `lesen` den Wert `feld.an`, sonst `feld.aus`
     * (zwei Werte des Katalogs, kein Wahrheitswert — der Server speichert, was im Katalog steht).
     */
    static _haken(feld, wert) {
        const eingabe = document.createElement('input');
        eingabe.type = 'checkbox';
        eingabe.name = feld.schluessel;
        eingabe.dataset.an = feld.an;
        eingabe.dataset.aus = feld.aus;
        eingabe.checked = wert === feld.an;
        return eingabe;
    }

    /** Farbwähler — Art `farbe` (04.10.2026, Renderregler): Wert `#rrggbb`. */
    static _farbe(feld, wert) {
        const eingabe = document.createElement('input');
        eingabe.type = 'color';
        eingabe.name = feld.schluessel;
        eingabe.className = 'viewer-eingabe';
        eingabe.value = String(wert ?? '#808080');
        return eingabe;
    }

    /** Textfeld (Pfad, Name) — Art `text`, seit dem 29.09.2026 für die BVH-Datei von „BlenderModel". */
    static _text(feld, wert) {
        const eingabe = document.createElement('input');
        eingabe.type = 'text';
        eingabe.name = feld.schluessel;
        eingabe.className = 'viewer-eingabe';
        eingabe.autocomplete = 'off';
        eingabe.spellcheck = false;
        eingabe.value = String(wert ?? '');
        return eingabe;
    }

    /** Liest die aktuell im Behälter stehenden Werte als `{schluessel: wert}`. */
    static lesen(behaelter) {
        const aus = {};
        for (const auswahl of behaelter.querySelectorAll('select[name]')) aus[auswahl.name] = auswahl.value;
        for (const eingabe of behaelter.querySelectorAll('input[type="number"][name]')) {
            aus[eingabe.name] = Number(eingabe.value);
        }
        for (const eingabe of behaelter.querySelectorAll('input[type="text"][name]')) aus[eingabe.name] = eingabe.value;
        for (const eingabe of behaelter.querySelectorAll('input[type="color"][name]')) aus[eingabe.name] = eingabe.value;
        for (const eingabe of behaelter.querySelectorAll('input[type="checkbox"][name]')) aus[eingabe.name] = eingabe.checked ? eingabe.dataset.an : eingabe.dataset.aus;
        for (const gruppe of behaelter.querySelectorAll('.mesh-kaestchengruppe[data-feld]')) {
            aus[gruppe.dataset.feld] = [...gruppe.querySelectorAll('input:checked')].map(k => k.value);
        }
        return aus;
    }
}
