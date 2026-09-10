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
export class GarmentcodeBauregler {

    static HAUTABSTAND = 'gc-hautabstand';
    static AUFLOESUNG = 'gc-aufloesung';

    /** Vorgaben — dieselben Zahlen wie in `Baufeineinstellung`. */
    static HAUTABSTAND_VORGABE = 1.0;
    static AUFLOESUNG_VORGABE = 1.0;

    /**
     * Was die Regler tun — im Klartext, nicht als Parametername.
     *
     * Edgar, 09.09.2026: „die Hover texte verständlich, z.B. bei Netzfeinheit
     * die Info was das ist, und Auswirkung auf Rechenzeit usw." Jeder Text
     * sagt dasselbe in derselben Reihenfolge: WAS es ist, was HOCH bewirkt,
     * was RUNTER bewirkt, was es KOSTET.
     */
    static HINWEISE = {
        'gc-hautabstand':
            'Wie weit der Stoff nach der Simulation mindestens vor der Haut '
            + 'liegen soll. Höher: kein Durchscheinen der Haut, aber das '
            + 'Stück steht sichtbar ab. Niedriger: liegt enger an, dafür '
            + 'können Brustwarze, Nabel oder Knie durch den Stoff stoßen. '
            + 'Kostet keine Rechenzeit — die Korrektur läuft nach der '
            + 'Simulation. 1,0 mm ist die Vorgabe: Gemessen an drei Stücken '
            + 'räumt sie genauso viele durchstehende Stellen weg wie die '
            + '6,0 mm von vorher, ohne deren 2,5 mm Aufschlag. Achtung: Wie '
            + 'eng es überhaupt werden KANN, entscheidet nicht dieser '
            + 'Regler, sondern der Kollisionsabstand der Simulation (im '
            + 'Bereich „Simulation" darunter, Vorgabe 0,05 cm).',
        'gc-aufloesung':
            'Wie fein das Stoffnetz für die Simulation vernäht wird — die '
            + 'Zahl der Stoffpunkte, nicht die Bildauflösung. Höher: feinere '
            + 'Falten und weniger Durchstich, weil eine Wölbung von 2,5 mm '
            + 'nicht mehr zwischen zwei Stoffpunkten verschwindet (bei 1,0 '
            + 'ist das Netz am Oberschenkel rund 1 cm grob). Niedriger: '
            + 'gröber und schneller. Kostet Rechenzeit: Ein T-Shirt braucht '
            + 'bei 1,0 gemessen rund 17 bis 23 s, und die Zeit wächst mit '
            + 'der Zahl der Punkte. Bei hohen Werten muss „Netzbau '
            + 'höchstens (s)" darunter mitwachsen, sonst bricht der Bau ab.',
    };

    /** Beide Anzeigen nachziehen; ohne Regler im DOM passiert nichts. */
    static verdrahten() {
        const a = GarmentcodeBauregler._binden(
            GarmentcodeBauregler.HAUTABSTAND,
            (wert) => `${wert.toFixed(1).replace('.', ',')} mm`);
        const b = GarmentcodeBauregler._binden(
            GarmentcodeBauregler.AUFLOESUNG,
            (wert) => `${wert.toFixed(1).replace('.', ',')}×`);
        GarmentcodeBauregler._beschriften();
        return a && b;
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
        daten.append('hautabstand_mm', String(GarmentcodeBauregler.hautabstand()));
        daten.append('aufloesung', String(GarmentcodeBauregler.aufloesung()));
        return true;
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
