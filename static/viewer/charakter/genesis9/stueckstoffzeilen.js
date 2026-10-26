/**
 * Stueckstoffzeilen — die Bedienzeilen des Blocks „Stoff“ (`Stueckstoff`): Schieber, Auswahl, Farbe. Aus `stueckstoff.js` herausgelöst
 * (25.10.2026), als der Block von drei auf zehn Felder wuchs; jede Zeile ist ein `slider-row` wie in der übrigen Reglerliste.
 * Jede Zeile trägt `data-feld` — daran findet die Prüfung im Browser den Schieber (`[data-feld="glanz"] input`).
 */
export class Stueckstoffzeilen {

    /** Ein Schieber mit Zahl; `bei(wert)` bei jedem Zug. `zeile.stellen(w)` setzt ihn ohne Meldung, `zeile.wert()` liest ihn. */
    static regler(feld, titel, min, max, schritt, wert, bei, hilfe = '') {
        const zeile = Stueckstoffzeilen._zeile(feld, titel, hilfe);
        const regler = document.createElement('input');
        Object.assign(regler, { type: 'range', min: String(min), max: String(max), step: String(schritt) });
        const zahl = document.createElement('span');
        zahl.className = 'slider-value';
        zeile.stellen = (w) => { regler.value = String(w); zahl.textContent = Number(w).toFixed(2); };
        zeile.wert = () => Number(regler.value);
        zeile.regler = regler;
        zeile.stellen(wert);
        regler.addEventListener('input', () => {
            zahl.textContent = Number(regler.value).toFixed(2);
            if (bei) bei(Number(regler.value));
        });
        zeile.append(regler, zahl);
        return zeile;
    }

    /** Eine Auswahl aus `[[wert, titel]]`; `bei(wert)` bei jeder Änderung. */
    static wahl(feld, titel, eintraege, wert, bei, hilfe = '') {
        const zeile = Stueckstoffzeilen._zeile(feld, titel, hilfe);
        const wahl = document.createElement('select');
        for (const [w, t] of eintraege) wahl.add(new Option(t, w));
        wahl.value = wert ?? '';
        if (bei) wahl.addEventListener('change', () => bei(wahl.value));
        zeile.wahl = wahl;
        zeile.appendChild(wahl);
        return zeile;
    }

    /** Eine Farbe, die auch „keine eigene“ sein kann (Haken aus = ''); `bei('#rrggbb' | '')`. */
    static farbe(feld, titel, hex, bei, hilfe = '', ohne = 'wie der Stoff') {
        const zeile = Stueckstoffzeilen._zeile(feld, titel, hilfe);
        const eigen = document.createElement('input');
        eigen.type = 'checkbox';
        eigen.checked = Boolean(hex);
        eigen.title = `Eigene Farbe — ohne Haken ${ohne}`;
        const wahl = document.createElement('input');
        wahl.type = 'color';
        wahl.value = hex || '#ffffff';
        wahl.disabled = !hex;
        const melden = () => { wahl.disabled = !eigen.checked; bei(eigen.checked ? wahl.value : ''); };
        eigen.addEventListener('change', melden);
        wahl.addEventListener('input', melden);
        zeile.append(eigen, wahl);
        return zeile;
    }

    static _zeile(feld, titel, hilfe) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.dataset.feld = feld;
        if (hilfe) zeile.title = hilfe;
        const name = document.createElement('label');
        name.textContent = titel;
        zeile.appendChild(name);
        return zeile;
    }
}
