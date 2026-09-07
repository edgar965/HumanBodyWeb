/**
 * Reglerbereich des GarmentCode-Reiters.
 *
 * GarmentCode führt 122 Einstellungen; welche gelten, hängt am
 * Kleidungsstück — eine Hose hat keinen Kragen. Der Server liefert deshalb
 * je Stück nur die passenden Gruppen (`/api/garmentcode/regler/`), und hier
 * werden sie gezeichnet: Schieber für Zahlen, Liste für Auswahlen,
 * Kästchen für Ja/Nein.
 *
 * VERSCHACHTELTE GRUPPEN (Edgar, 07.09.2026: „bei Ärmel fehlen mir die
 * Konfigurationen die es auf der webseite gibt")
 * ====================================================================
 * Gemessen erreichten 65 von 122 Reglern die Oberfläche nie — die Hälfte
 * davon, weil sie in einer UNTERGRUPPE stecken: `sleeve.cuff` (Manschette),
 * `collar.component` (Kragenaufbau), `pants.cuff`, `flare-skirt.cut`, dazu
 * die ganze Gruppe `left`. Der Server liefert sie jetzt als `untergruppen`,
 * und hier werden sie eingerückt darunter gezeichnet — so wie das
 * Online-Werkzeug es als aufklappbare Karte tut
 * (`upstream/gui/callbacks.py`, `def_flat_design_subtab`).
 *
 * DER SCHLÜSSEL IST DER PFAD DES SERVERS, NICHT SELBST ZUSAMMENGESETZT.
 * Früher stand hier `${gruppe}.${feld}`; bei `sleeve.cuff.cuff_len` ergäbe
 * das `sleeve.cuff_len` — ein Regler, den es nicht gibt, und der Server
 * hätte den Wert stumm verworfen.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

class GarmentcodeRegler {
    /** Was `null` in einer Auswahl anzeigt — „nichts davon". */
    static LEER = '—';

    constructor() {
        /** Für welches Kleidungsstück die Regler gerade stehen. */
        this.fuerVorlage = null;
        /** Vom Nutzer geänderte Werte: {"sleeve.cuff.cuff_len": 0.4}. */
        this.werte = {};
    }

    /** Die Regler eines Kleidungsstücks holen und zeichnen. */
    async laden(vorlage) {
        const ziel = document.getElementById('gc-regler');
        if (!ziel || !vorlage) return;
        if (this.fuerVorlage === vorlage) return;

        ziel.innerHTML = '<div class="hb-hinweis">Einstellungen werden geholt …</div>';
        try {
            const antwort = await Serverabruf.json(
                `/api/garmentcode/regler/?vorlage=${encodeURIComponent(vorlage)}`);
            // Ein Wechsel des Kleidungsstücks verwirft die alten Werte: Sie
            // gehören zu Gruppen, die es jetzt vielleicht nicht mehr gibt.
            this.werte = {};
            this.fuerVorlage = vorlage;
            this.zeichnen(ziel, antwort.gruppen || []);
        } catch (fehler) {
            ziel.innerHTML = '<div class="hb-hinweis">Einstellungen nicht '
                + `abrufbar: ${fehler.message || fehler}</div>`;
        }
    }

    zeichnen(ziel, gruppen) {
        ziel.innerHTML = '';
        if (!gruppen.length) {
            ziel.innerHTML = '<div class="hb-hinweis">Für dieses Stück gibt es '
                + 'keine Feineinstellungen.</div>';
            return;
        }
        for (const gruppe of gruppen) ziel.appendChild(this.block(gruppe, 0));
    }

    /**
     * Eine Gruppe samt ihrer Untergruppen.
     *
     * Untergruppen werden eingerückt, nicht ausgeklappt: Bei einem T-Shirt
     * sind es zwei Ebenen und zusammen 71 Regler — wer sie hinter Klicks
     * versteckt, hat sie für den Nutzer wieder verloren.
     */
    block(gruppe, tiefe) {
        const kasten = document.createElement('div');
        if (tiefe) kasten.className = 'gc-untergruppe';

        const titel = document.createElement('div');
        titel.className = tiefe ? 'gruppentitel-klein gedaempft'
                                : 'gruppentitel-klein';
        titel.textContent = gruppe.titel;
        titel.title = gruppe.pfad || gruppe.gruppe;
        kasten.appendChild(titel);

        for (const feld of (gruppe.felder || [])) {
            kasten.appendChild(this.zeile(feld));
        }
        for (const unter of (gruppe.untergruppen || [])) {
            kasten.appendChild(this.block(unter, tiefe + 1));
        }
        return kasten;
    }

    /** Eine Reglerzeile — je nach Typ Schieber, Liste oder Kästchen. */
    zeile(feld) {
        const schluessel = feld.pfad;
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';

        const beschriftung = document.createElement('label');
        beschriftung.textContent = feld.titel;
        beschriftung.title = schluessel;      // der echte Name im Tooltip
        zeile.appendChild(beschriftung);

        if (feld.typ === 'bool') {
            zeile.appendChild(this.kaestchen(schluessel, feld));
        } else if (feld.typ === 'select' || feld.typ === 'select_null') {
            zeile.appendChild(this.liste(schluessel, feld));
        } else {
            const [schieber, anzeige] = this.schieber(schluessel, feld);
            zeile.appendChild(schieber);
            zeile.appendChild(anzeige);
        }
        return zeile;
    }

    kaestchen(schluessel, feld) {
        const feldchen = document.createElement('input');
        feldchen.type = 'checkbox';
        feldchen.checked = !!feld.wert;
        feldchen.addEventListener('change',
            () => { this.werte[schluessel] = feldchen.checked; });
        return feldchen;
    }

    /**
     * Auswahlliste. `null` ist bei `select_null` ein gültiger Wert und
     * bedeutet „keine Manschette", „kein Kragenaufbau" — er bekommt einen
     * eigenen Eintrag, weil ein leerer Listeneintrag wie ein Fehler aussieht.
     */
    liste(schluessel, feld) {
        const auswahl = document.createElement('select');
        auswahl.className = 'viewer-select hb-dehnt-ohne-abstand';
        for (const wert of feld.bereich) {
            const eintrag = document.createElement('option');
            const leer = (wert === null || wert === undefined);
            eintrag.value = leer ? '' : wert;
            eintrag.textContent = leer ? GarmentcodeRegler.LEER : wert;
            eintrag.selected = (wert === feld.wert)
                || (leer && (feld.wert === null || feld.wert === undefined));
            auswahl.appendChild(eintrag);
        }
        auswahl.addEventListener('change', () => {
            // Leer heißt `null`, nicht die Zeichenkette "": Der Server
            // prüft gegen den Wertebereich, und "" steht dort nicht.
            this.werte[schluessel] = auswahl.value === '' ? null : auswahl.value;
        });
        return auswahl;
    }

    /**
     * Schieber für float/int. HTML-Schieber kennen nur ganze Schritte, die
     * Bereiche hier sind aber oft 0,1 bis 1,15 — deshalb wird intern in
     * Hundertsteln gerechnet und beim Lesen zurückgerechnet.
     */
    schieber(schluessel, feld) {
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

        schieber.addEventListener('input', () => {
            const wert = Number(schieber.value) / faktor;
            this.werte[schluessel] = ganz ? Math.round(wert) : wert;
            zeigen(wert);
        });
        return [schieber, anzeige];
    }

    /** Die geänderten Werte als JSON für den Server. */
    alsJson() {
        return JSON.stringify(this.werte);
    }

    /** Nach dem Bauen: Anzahl der abweichenden Werte, für die Meldung. */
    get anzahl() {
        return Object.keys(this.werte).length;
    }
}

export const garmentcodeRegler = new GarmentcodeRegler();
