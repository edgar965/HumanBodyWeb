/**
 * Die zwei Feineinstellungen unter „Bauen" — Hautabstand und Netzfeinheit.
 *
 * AUFTRAG (Edgar, 09.09.2026): „die 3 mm Mindestabstand oder mehr sollen
 * einstellbar sein, unter «Bauen» mach einen Regler dafür" und „was war
 * resolution_scale nochmal?? mehr Rechenzeit dafür bessere Ergebnisse? dann
 * mach den Slider auch gleich unter dem «Bauen» Bereich".
 *
 * WARUM SIE ÜBERHAUPT REGLER SIND
 * ===============================
 * Beide standen als Konstante im Code. Der Hautabstand
 * (`Stoffkorrektur.ABSTAND_MM`) wurde am 08.09.2026 von 3,0 auf 6,0 mm
 * gesetzt, weil die Haut durch die Hose schien. Edgars Einordnung dazu: „Bei
 * der Hose war das ein Bug, weil der Abstand negativ war." Eine Konstante,
 * die einen Bug zudeckt, gehört an einen Regler.
 *
 * Nachgemessen steht er seit dem 09.09.2026 auf 1,0 mm: Die 6,0 räumten bei
 * der Hose — dem Stück, für das sie eingeführt wurden — 5 von 92
 * durchstehenden Punkten mehr weg als 1,0 und kosteten dafür überall 2,5 mm
 * Abstand.
 *
 * SIE WIRKEN BEIM NÄCHSTEN BAU MIT 3D, nicht auf ein fertiges Stück: Der
 * Hautabstand greift nach der Simulation, die Netzfeinheit davor. Ein
 * fertiges Netz nachträglich zu verschieben hiesse, die Falten mitzuziehen.
 */
import { garmentcodePreset } from './garmentcode_preset.js';
import { GarmentcodeBaugedaechtnis } from './garmentcode_baugedaechtnis.js';
import { BAUREGLER_HINWEISE } from './garmentcode_bauregler_hinweise.js';

export class GarmentcodeBauregler {

    static HAUTABSTAND = 'gc-hautabstand';
    static AUFLOESUNG = 'gc-aufloesung';
    static ANLIEGEN = 'gc-anliegen';

    /** Vorgaben — dieselben Zahlen wie in `Baufeineinstellung`. */
    static HAUTABSTAND_VORGABE = 1.0;
    static AUFLOESUNG_VORGABE = 1.0;
    /** 0 = aus; unter 0,5 mm gilt als aus (`Baufeineinstellung.ANLIEGEN_MIN`). */
    static ANLIEGEN_VORGABE = 0.0;
    static ANLIEGEN_MIN = 0.5;

    /**
     * Pseudo-Pfade der Voreinstellungen (`passform.py`, `BAU_PFADE`) →
     * Regler. Ein Preset wie „Leggings" setzt neben Schnittwerten auch
     * diesen Bauwert; `garmentcode_regler.js` leitet `bau.*` hierher.
     */
    static PFADE = { 'bau.anliegen_mm': 'gc-anliegen' };

    /** Die drei Werte, wie sie `Baufeineinstellung` heißen → Feld. */
    static FELDER = { hautabstand_mm: 'gc-hautabstand',
                      aufloesung: 'gc-aufloesung',
                      anliegen_mm: 'gc-anliegen' };

    /** Anzeigeformat je Feld — steht nach `verdrahten`. */
    static _formate = {};

    /** Die Hover-Texte, je Kennung (`garmentcode_bauregler_hinweise.js`). */
    static HINWEISE = BAUREGLER_HINWEISE;

    /** Beide Anzeigen nachziehen; ohne Regler im DOM passiert nichts. */
    static verdrahten() {
        const a = GarmentcodeBauregler._binden(
            GarmentcodeBauregler.HAUTABSTAND,
            (wert) => `${wert.toFixed(1).replace('.', ',')} mm`);
        const b = GarmentcodeBauregler._binden(
            GarmentcodeBauregler.AUFLOESUNG,
            (wert) => `${wert.toFixed(1).replace('.', ',')}×`);
        const c = GarmentcodeBauregler._binden(
            GarmentcodeBauregler.ANLIEGEN, GarmentcodeBauregler._anliegenText);
        // Von Hand bewegt: Ein Preset, das diesen Wert setzt („Leggings"),
        // gilt dann nicht mehr — sein Häkchen geht weg wie bei jedem Regler.
        document.getElementById(GarmentcodeBauregler.ANLIEGEN)
            ?.addEventListener('input', () => garmentcodePreset.pruefen(
                'bau.anliegen_mm', (p) => GarmentcodeBauregler.wert(p)));
        // Jeder Zug merkt die drei Werte für DIESE Vorlage
        // (`garmentcode_baugedaechtnis.js`, 11.09.2026).
        for (const kennung of Object.values(GarmentcodeBauregler.FELDER)) {
            document.getElementById(kennung)
                ?.addEventListener('input', () => GarmentcodeBauregler.merken());
        }
        GarmentcodeBauregler._beschriften();
        return a && b && c;
    }

    /** Die drei Werte für die gewählte Vorlage merken. */
    static merken() {
        return GarmentcodeBaugedaechtnis.merken(GarmentcodeBauregler.werte());
    }

    /**
     * Die Bauwerte DIESER Vorlage in die Felder — gemerkt oder Vorgabe.
     *
     * Beim Vorlagenwechsel, VOR den Presets: Ein Preset legt seine Werte
     * dann darüber. Ohne diesen Schritt blieben die Werte der vorigen
     * Vorlage stehen (das angelegte T-Shirt, 11.09.2026). Ohne `input`,
     * ohne Merken — es ist der gemerkte Stand, der gerade gelesen wird.
     */
    static herstellen(vorlage) {
        const gemerkt = GarmentcodeBaugedaechtnis.holen(vorlage);
        const vorgaben = GarmentcodeBauregler.vorgaben();
        let gesetzt = 0;
        for (const [name, kennung] of Object.entries(GarmentcodeBauregler.FELDER)) {
            const wert = Number.isFinite(Number(gemerkt[name]))
                ? Number(gemerkt[name]) : vorgaben[name];
            if (GarmentcodeBauregler._stellen(kennung, wert)) gesetzt += 1;
        }
        return gesetzt;
    }

    static vorgaben() {
        return { hautabstand_mm: GarmentcodeBauregler.HAUTABSTAND_VORGABE,
                 aufloesung: GarmentcodeBauregler.AUFLOESUNG_VORGABE,
                 anliegen_mm: GarmentcodeBauregler.ANLIEGEN_VORGABE };
    }

    /** Feld und Anzeige stellen, ohne Ereignis. */
    static _stellen(kennung, wert) {
        const feld = document.getElementById(kennung);
        if (!feld) return false;
        feld.value = String(wert);
        const anzeige = document.getElementById(`${kennung}-val`);
        const format = GarmentcodeBauregler._formate[kennung];
        if (anzeige && format) anzeige.textContent = format(Number(wert));
        return true;
    }

    static _anliegenText(wert) {
        return wert < GarmentcodeBauregler.ANLIEGEN_MIN
            ? 'aus' : `${wert.toFixed(1).replace('.', ',')} mm`;
    }

    /** Der Wert eines Pseudo-Pfades (`bau.anliegen_mm`), für die Presets. */
    static wert(pfad) {
        const kennung = GarmentcodeBauregler.PFADE[pfad];
        if (!kennung) return undefined;
        return GarmentcodeBauregler._zahl(kennung, GarmentcodeBauregler.ANLIEGEN_VORGABE);
    }

    /**
     * Pseudo-Pfade setzen — Schieber und Anzeige nachziehen, OHNE
     * `input`-Ereignis: Das würde `pruefen` rufen und das Häkchen, das
     * gerade gesetzt wird, gleich wieder wegnehmen. Gemerkt wird der Wert
     * trotzdem, DIREKT — je Vorlage (`GarmentcodeBauregler.merken`): Das
     * Gedächtnis hört nur auf Ereignisse, und ohne diesen Aufruf stand
     * „An die Haut ziehen" nach jedem Neuladen wieder auf 0, während die
     * Schnittwerte der Leggings zurückkamen — die Hose baute weit (Edgar,
     * 11.09.2026: „das ist eine regression!").
     * `merken = false` für ein Vorbild der Kleiderbibliothek — das ist eine
     * Ableitung, keine Einstellung, und merkt auch seine Schnittwerte nicht.
     */
    static setzen(werte, merken = true) {
        let gesetzt = 0;
        for (const [pfad, wert] of Object.entries(werte || {})) {
            const kennung = GarmentcodeBauregler.PFADE[pfad];
            if (kennung && GarmentcodeBauregler._stellen(kennung, wert)) gesetzt += 1;
        }
        if (merken && gesetzt) GarmentcodeBauregler.merken();
        return gesetzt;
    }

    /**
     * Den Hinweis an die ganze Zeile hängen, nicht nur an den Schieber.
     *
     * Die Vorlage `{% regler %}` kennt kein `title` — und ein Hinweis, der
     * nur über dem 2 mm schmalen Schieber erscheint, findet niemand.
     */
    static _beschriften() {
        for (const [kennung, text]
             of Object.entries(GarmentcodeBauregler.HINWEISE)) {
            const feld = document.getElementById(kennung);
            const zeile = feld && feld.closest('.slider-row');
            if (zeile) zeile.title = text;
        }
    }

    /**
     * Die beiden Werte an die Drapieranfrage hängen.
     *
     * Immer beide, auch wenn sie auf der Vorgabe stehen: Der Server klemmt
     * und meldet zurück, womit gebaut wurde. Ein weggelassenes Feld liesse
     * offen, ob der Regler fehlte oder zufällig auf der Vorgabe stand.
     */
    static anhaengen(daten) {
        if (!daten || typeof daten.append !== 'function') return false;
        for (const [name, wert] of Object.entries(GarmentcodeBauregler.werte())) {
            daten.append(name, String(wert));
        }
        return true;
    }

    /** Die drei Werte als Objekt — für die Kombiliste, die sie je Stück kopiert. */
    static werte() {
        return {
            hautabstand_mm: GarmentcodeBauregler.hautabstand(),
            aufloesung: GarmentcodeBauregler.aufloesung(),
            anliegen_mm: GarmentcodeBauregler.anliegen(),
        };
    }

    static anliegen() {
        return GarmentcodeBauregler._zahl(GarmentcodeBauregler.ANLIEGEN,
                                          GarmentcodeBauregler.ANLIEGEN_VORGABE);
    }

    static hautabstand() {
        return GarmentcodeBauregler._zahl(GarmentcodeBauregler.HAUTABSTAND,
                                          GarmentcodeBauregler.HAUTABSTAND_VORGABE);
    }

    static aufloesung() {
        return GarmentcodeBauregler._zahl(GarmentcodeBauregler.AUFLOESUNG,
                                          GarmentcodeBauregler.AUFLOESUNG_VORGABE);
    }

    /**
     * Was der Bau tatsächlich benutzt hat, in die Meldung.
     *
     * Nur wenn etwas von der Vorgabe abweicht — eine Zeile, die bei jedem
     * Bau dasselbe sagt, liest niemand mehr.
     */
    static zusatz(feineinstellung) {
        if (!feineinstellung) return '';
        const abstand = Number(feineinstellung.hautabstand_mm);
        const feinheit = Number(feineinstellung.aufloesung);
        const teile = [];
        if (Number.isFinite(abstand)
            && abstand !== GarmentcodeBauregler.HAUTABSTAND_VORGABE) {
            teile.push(`Hautabstand ${abstand.toFixed(1).replace('.', ',')} mm`);
        }
        if (Number.isFinite(feinheit)
            && feinheit !== GarmentcodeBauregler.AUFLOESUNG_VORGABE) {
            teile.push(`Netzfeinheit ${feinheit.toFixed(1).replace('.', ',')}×`);
        }
        const anliegen = Number(feineinstellung.anliegen_mm);
        if (feineinstellung.anliegen_mm != null && Number.isFinite(anliegen)) {
            teile.push(`an die Haut gezogen (${anliegen.toFixed(1).replace('.', ',')} mm)`);
        }
        return teile.length ? `, ${teile.join(', ')}` : '';
    }

    static _zahl(kennung, vorgabe) {
        const feld = document.getElementById(kennung);
        if (!feld) return vorgabe;
        const wert = parseFloat(feld.value);
        return Number.isFinite(wert) ? wert : vorgabe;
    }

    /** Anzeige an den Regler hängen und einmal sofort stellen. */
    static _binden(kennung, format) {
        const feld = document.getElementById(kennung);
        if (!feld) return false;
        GarmentcodeBauregler._formate[kennung] = format;
        const anzeige = document.getElementById(`${kennung}-val`);
        const nachziehen = () => {
            const wert = parseFloat(feld.value);
            if (anzeige && Number.isFinite(wert)) {
                anzeige.textContent = format(wert);
            }
        };
        feld.addEventListener('input', nachziehen);
        nachziehen();
        return true;
    }
}

// Selbststartend wie die übrigen Reitermodule: `boot.js` lädt sie, das
// Panel steht dann schon im DOM. Beim Laden vor dem DOM greift die Weiche.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded',
                              () => GarmentcodeBauregler.verdrahten());
} else {
    GarmentcodeBauregler.verdrahten();
}
