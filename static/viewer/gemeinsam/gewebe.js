/**
 * Gewebe — die Mikrostruktur eines Stoffs als Normalkarte, gerechnet.
 *
 * WARUM (Edgar, 10.09.2026: „Meine Kleider sehen mir noch zu schlecht aus"):
 * Ein GarmentCode-Stück war im Browser eine einfarbige Fläche mit einem
 * Rauheitswert — kein Bild, keine Struktur. Was einen Stoff als Stoff
 * lesbar macht, ist nicht der Faltenwurf allein, sondern die Bindung: Kette
 * und Schuss, die einander abwechselnd über- und unterlaufen und das Licht
 * in feinen Reihen brechen.
 *
 * GERECHNET, NICHT GELADEN. Eine Bilddatei wäre eine weitere Datei im
 * Statikbaum, mit Fassung, Ladezeit und einer festen Fadenzahl. Die Kachel
 * hier ist 128×128 (64 KB), entsteht in Millisekunden und ist über
 * `faeden` und `staerke` einstellbar. Vor allem aber ist sie damit PRÜFBAR:
 * Dieses Modul kennt weder DOM noch Three.js, es liefert nur Zahlenfelder
 * (`core/tests/unit/test_js_gewebe.py`).
 *
 * DIE KACHEL MUSS KACHELN. Das Höhenfeld wird über den Rand hinweg
 * fortgesetzt (`_wickeln`), sonst steht in jeder Kachelfuge eine Naht, die
 * es im Stoff nicht gibt — bei fünfzig Wiederholungen über ein T-Shirt ein
 * sichtbares Gitter.
 */
export class Gewebe {

    // Weitere Bindungen (Köper, Jersey, Satin) stehen in `gewebearten.js`
    // und geben `hoehenfeld`/`normalfeld` ihr eigenes `hoehe` mit.

    /** Kantenlänge der Kachel in Bildpunkten. Zweierpotenz wegen Mipmaps. */
    static GROESSE = 128;

    /**
     * Fäden je Kachel und Richtung.
     *
     * 8 bei 128 Bildpunkten sind 16 Punkte je Faden — genug für einen
     * runden Querschnitt. Mehr Fäden je Kachel heißt feineres Gewebe bei
     * gleicher Kachelgröße, aber unter etwa 6 Punkten je Faden verschluckt
     * die Mipmap-Stufe die Struktur, und übrig bleibt eine graue Fläche.
     */
    static FAEDEN = 8;

    /**
     * Wie steil die Normalen kippen. 1 heißt: eine Fadenwölbung von einer
     * halben Fadenbreite Höhe. Der Wert wirkt mit `normalScale` zusammen —
     * hier bleibt er neutral, die Feinabstimmung steht am Material.
     */
    static STAERKE = 1.0;

    /**
     * Wie tief sich die beiden Fadenscharen ineinander verschränken, und
     * wie dick ein Faden aufträgt.
     *
     * Beide zusammen ergeben den Wertebereich; das Feld wird am Ende auf
     * 0..1 gelegt. Ohne die Verschränkung (`AMPLITUDE = 0`) wäre die
     * Leinwandbindung ein Gitter aus lauter gleich hohen Hügeln — das sieht
     * aus wie Waffelmuster, nicht wie Gewebe.
     */
    static AMPLITUDE = 0.35;
    static DICKE = 0.65;

    /**
     * Das Höhenfeld einer Leinwandbindung, Zeile für Zeile.
     *
     * Leinwandbindung ist die einfachste und häufigste Webart: Jeder
     * Schussfaden läuft abwechselnd über und unter je einem Kettfaden, und
     * in der nächsten Reihe versetzt. Welcher Faden an einer Kreuzung oben
     * liegt, sagt deshalb die Parität der beiden Fadennummern.
     *
     * @param {number} groesse Kantenlänge in Bildpunkten
     * @param {number} faeden Fäden je Kante
     * @returns {Float32Array} groesse*groesse Werte in 0..1
     */
    static hoehenfeld(groesse = Gewebe.GROESSE, faeden = Gewebe.FAEDEN,
                      hoehe = Gewebe.hoehe) {
        const feld = new Float32Array(groesse * groesse);
        const breite = groesse / faeden;         // Bildpunkte je Faden
        for (let y = 0; y < groesse; y++) {
            for (let x = 0; x < groesse; x++) {
                feld[y * groesse + x] = hoehe(x, y, breite);
            }
        }
        return feld;
    }

    /**
     * Die Höhe an einer Stelle — die eigentliche Rechnung.
     *
     * Zwei Fadenscharen, jede mit einem runden Querschnitt und einer
     * Wellenlinie über ihre Länge: Der Kettfaden steigt über jeden zweiten
     * Schussfaden und taucht unter den dazwischen. Sichtbar ist, wer an der
     * Stelle höher liegt — deshalb das Maximum der beiden und nicht ihre
     * Summe. Eine Summe verwischt die Verschränkung, und übrig bleibt ein
     * gleichmäßiges Karo.
     *
     * Die Welle läuft über ZWEI Fadenbreiten und ist stetig; der
     * Querschnitt ist an den Fadenrändern genau null, weil dort der
     * Nachbarfaden anstößt. Beides zusammen macht die Kachel wiederholbar.
     *
     * `breite` ist die Fadenbreite in denselben Einheiten wie x und y.
     */
    static hoehe(x, y, breite) {
        const langK = x / breite;                // Lage quer zur Kette
        const langS = y / breite;                // Lage quer zum Schuss
        const kette = Math.floor(langK);         // senkrechter Faden
        const schuss = Math.floor(langS);        // waagrechter Faden
        // Querschnitt: ein halber Sinusbogen über die Fadenbreite.
        const rundK = Math.sin(Math.PI * (langK - kette));
        const rundS = Math.sin(Math.PI * (langS - schuss));
        // Über/unter: Kettfaden `kette` liegt über Schussfaden `schuss`,
        // wenn deren Summe gerade ist. Als stetige Welle geschrieben, damit
        // der Übergang zwischen zwei Kreuzungen weich bleibt.
        const welleK = Gewebe._vorzeichen(kette) * Math.cos(Math.PI * (langS - 0.5));
        const welleS = -Gewebe._vorzeichen(schuss) * Math.cos(Math.PI * (langK - 0.5));
        const hoeheK = Gewebe.AMPLITUDE * welleK + Gewebe.DICKE * rundK;
        const hoeheS = Gewebe.AMPLITUDE * welleS + Gewebe.DICKE * rundS;
        const roh = Math.max(hoeheK, hoeheS);
        // Auf 0..1 legen: der tiefste mögliche Wert ist -AMPLITUDE, der
        // höchste AMPLITUDE + DICKE.
        return (roh + Gewebe.AMPLITUDE)
            / (2 * Gewebe.AMPLITUDE + Gewebe.DICKE);
    }

    static _vorzeichen(nummer) {
        return ((nummer % 2) + 2) % 2 === 0 ? 1 : -1;
    }

    /**
     * Die Kachel als Normalkarte in RGBA-Bytes.
     *
     * Tangentenraum wie Three.js ihn erwartet: R = x, G = y, B = z, jeweils
     * von -1..1 auf 0..255 gelegt. Die Steigung entsteht aus der zentralen
     * Differenz der Nachbarpunkte, über den Rand hinweg gewickelt.
     *
     * @returns {Uint8Array} groesse*groesse*4 Bytes
     */
    static normalfeld(groesse = Gewebe.GROESSE, faeden = Gewebe.FAEDEN,
                      staerke = Gewebe.STAERKE, hoehe = Gewebe.hoehe) {
        const hoehen = Gewebe.hoehenfeld(groesse, faeden, hoehe);
        const bytes = new Uint8Array(groesse * groesse * 4);
        // Die Steigung wird auf die Fadenbreite bezogen, nicht auf einen
        // Bildpunkt: Sonst hinge die Wirkung an der Auflösung der Kachel,
        // und 256 Punkte ergäben ein flacheres Gewebe als 128.
        const skala = staerke * (groesse / faeden) / 2;
        for (let y = 0; y < groesse; y++) {
            for (let x = 0; x < groesse; x++) {
                const links = hoehen[y * groesse + Gewebe._wickeln(x - 1, groesse)];
                const rechts = hoehen[y * groesse + Gewebe._wickeln(x + 1, groesse)];
                const oben = hoehen[Gewebe._wickeln(y - 1, groesse) * groesse + x];
                const unten = hoehen[Gewebe._wickeln(y + 1, groesse) * groesse + x];
                const dx = -(rechts - links) / 2 * skala;
                const dy = -(unten - oben) / 2 * skala;
                const laenge = Math.sqrt(dx * dx + dy * dy + 1);
                const k = (y * groesse + x) * 4;
                bytes[k] = Math.round((dx / laenge * 0.5 + 0.5) * 255);
                bytes[k + 1] = Math.round((dy / laenge * 0.5 + 0.5) * 255);
                bytes[k + 2] = Math.round((1 / laenge * 0.5 + 0.5) * 255);
                bytes[k + 3] = 255;
            }
        }
        return bytes;
    }

    /**
     * Wie oft die Kachel über ein Stück läuft.
     *
     * `uvMeter` sagt, wie viele Meter Stoff eine UV-Einheit sind — die Zahl
     * kommt aus der Rig-Datei (`Stoffuv`, Server). Ohne sie müsste die
     * Kachelgröße geraten werden, und weil jedes Schnittmuster sein UV auf
     * 0..1 legt, bekäme die Hose ein gröberes Gewebe als das T-Shirt
     * (gemessen 1,70 gegen 1,07 Meter je UV-Einheit).
     *
     * @param {number} uvMeter Meter Stoff je UV-Einheit
     * @param {number} kachelM Kantenlänge einer Kachel in Metern
     */
    static wiederholung(uvMeter, kachelM = Gewebe.KACHEL_M) {
        if (!(uvMeter > 0) || !(kachelM > 0)) return Gewebe.WIEDERHOLUNG_OHNE_MASS;
        return uvMeter / kachelM;
    }

    /**
     * Kantenlänge einer Kachel in Metern: 2 cm für 8 Fäden, also 2,5 mm je
     * Faden. Das ist grobes Leinen — und der Wert ist GEMESSEN, nicht
     * geschätzt.
     *
     * Im Browser auf einer reinen Stofffläche des T-Shirts (120×120
     * Bildpunkte, 100 % Stoff) die mittlere Helligkeitsdifferenz zum
     * Nachbarpunkt:
     *
     *     ohne Gewebe             0,50
     *     1,2 cm  (91 Kacheln)    0,83
     *     2,0 cm  (55 Kacheln)    1,10
     *     3,0 cm  (36 Kacheln)    0,89
     *
     * Die FEINERE Kachel bringt weniger Struktur ans Bild als die gröbere:
     * Bei 91 Wiederholungen liegt ein Faden unter der Größe eines
     * Bildpunkts, und die Mipmap-Stufe mittelt ihn weg — übrig bleibt ein
     * Streifenmuster aus dem Zusammenspiel mit dem Pixelraster. Noch gröber
     * (3 cm) fällt der Wert wieder, weil dann schlicht weniger Fäden im
     * Bild sind.
     */
    static KACHEL_M = 0.02;

    /** Ohne Maßangabe: eine Zahl, die für die üblichen Stücke passt. */
    static WIEDERHOLUNG_OHNE_MASS = 90;

    /**
     * Kantenlänge einer Kachel in Metern aus der Feinheit (Fäden je cm) und
     * der Fadenzahl je Kachel — 4 Fäden je cm bei 8 je Kachel sind die 2 cm
     * von `KACHEL_M`. Die Feinheit ist seit dem 11.09.2026 einstellbar.
     */
    static kachelmeter(faedenJeCm, faedenJeKachel = Gewebe.FAEDEN) {
        if (!(faedenJeCm > 0) || !(faedenJeKachel > 0)) return Gewebe.KACHEL_M;
        return faedenJeKachel / (faedenJeCm * 100);
    }

    static _wickeln(wert, groesse) {
        return ((wert % groesse) + groesse) % groesse;
    }
}
