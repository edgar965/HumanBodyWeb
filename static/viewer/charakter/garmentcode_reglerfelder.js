/**
 * Die drei Feldarten des Reglerbereichs — Kästchen, Auswahlliste, Schieber.
 *
 * Herausgelöst aus `garmentcode_regler.js` (11.09.2026), das mit der
 * `bau.*`-Weiche für die Leggings-Voreinstellung über seine 300 Zeilen
 * wuchs. Jede Feldart bekommt den Reglerbestand (`regler`) herein und
 * schreibt in dessen `werte`, `nachziehen` und ruft `vonHand` — der Bestand
 * bleibt an einer Stelle, hier steht nur der DOM-Bau.
 */
export class GarmentcodeReglerfelder {

    /** Anzeige eines `null`-Eintrags in einer `select_null`-Liste. */
    static LEER = '—';

    static kaestchen(regler, schluessel, feld) {
        const feldchen = document.createElement('input');
        feldchen.type = 'checkbox';
        feldchen.checked = !!feld.wert;
        regler.nachziehen[schluessel] = (wert) => { feldchen.checked = !!wert; };
        feldchen.addEventListener('change', () => {
            regler.werte[schluessel] = feldchen.checked;
            regler.vonHand(schluessel);
        });
        return feldchen;
    }

    /**
     * Auswahlliste. `null` ist bei `select_null` ein gültiger Wert und
     * bedeutet „keine Manschette", „kein Kragenaufbau" — er bekommt einen
     * eigenen Eintrag, weil ein leerer Listeneintrag wie ein Fehler aussieht.
     */
    static liste(regler, schluessel, feld) {
        const auswahl = document.createElement('select');
        auswahl.className = 'viewer-select hb-dehnt-ohne-abstand';
        // Die deutschen Namen kommen NACH STELLE gepaart, nicht nach Wert
        // (`wertetitel[i]` gehört zu `bereich[i]`): `null` taugt nicht als
        // Schlüssel eines Wörterbuchs, ist hier aber ein gültiger Wert.
        const namen = feld.wertetitel || [];
        feld.bereich.forEach((wert, i) => {
            const eintrag = document.createElement('option');
            const leer = (wert === null || wert === undefined);
            eintrag.value = leer ? '' : wert;
            eintrag.textContent = leer ? GarmentcodeReglerfelder.LEER
                                       : (namen[i] || wert);
            // Der Originalname bleibt erreichbar — er ist es, was im
            // Online-Werkzeug und im Upstream-Code steht.
            if (!leer && namen[i] && namen[i] !== String(wert)) {
                eintrag.title = String(wert);
            }
            eintrag.selected = (wert === feld.wert)
                || (leer && (feld.wert === null || feld.wert === undefined));
            auswahl.appendChild(eintrag);
        });
        regler.nachziehen[schluessel] = (wert) => {
            auswahl.value = (wert === null || wert === undefined) ? '' : wert;
        };
        auswahl.addEventListener('change', () => {
            // Leer heißt `null`, nicht die Zeichenkette "": Der Server
            // prüft gegen den Wertebereich, und "" steht dort nicht.
            regler.werte[schluessel] = auswahl.value === '' ? null : auswahl.value;
            regler.vonHand(schluessel);
        });
        return auswahl;
    }

    /**
     * Schieber für float/int. HTML-Schieber kennen nur ganze Schritte, die
     * Bereiche hier sind aber oft 0,1 bis 1,15 — deshalb wird intern in
     * Hundertsteln gerechnet und beim Lesen zurückgerechnet.
     */
    static schieber(regler, schluessel, feld) {
        const [unten, oben] = feld.bereich.length === 2
            ? feld.bereich.map(Number) : [0, 1];
        const ganz = (feld.typ === 'int');
        const faktor = ganz ? 1 : 100;

        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.min = String(Math.round(unten * faktor));
        schieber.max = String(Math.round(oben * faktor));
        schieber.step = '1';
        schieber.value = String(Math.round(Number(feld.wert) * faktor));

        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        const zeigen = (wert) => {
            anzeige.textContent = ganz ? String(wert) : wert.toFixed(2);
        };
        zeigen(Number(feld.wert));

        // Nachziehen OHNE `input`-Ereignis: Ein Preset setzt die Werte
        // selbst und stösst den Bau EINMAL an — feuerte jeder Schieber
        // dabei sein Ereignis, liefe der Schnitt vier Mal.
        regler.nachziehen[schluessel] = (wert) => {
            const zahl = Number(wert);
            if (!Number.isFinite(zahl)) return;
            schieber.value = String(Math.round(zahl * faktor));
            zeigen(zahl);
        };

        schieber.addEventListener('input', () => {
            const wert = Number(schieber.value) / faktor;
            regler.werte[schluessel] = ganz ? Math.round(wert) : wert;
            zeigen(wert);
            // Der Schnitt folgt, sobald der Regler kurz ruht (Edgar,
            // 08.09.2026). `GarmentcodeLive` entprellt selbst — hier darf
            // kein Zeitgeber stehen, sonst hat jede Reglerart einen eigenen.
            regler.vonHand(schluessel);
        });
        return [schieber, anzeige];
    }
}
