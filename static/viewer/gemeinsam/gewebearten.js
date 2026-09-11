import { Gewebe } from './gewebe.js';

/**
 * Gewebearten — die Bindungen, zwischen denen der Reiter wählen lässt.
 *
 * AUFTRAG (Edgar, 11.09.2026): „du hast ja jetzt auch die Textur eingebaut,
 * kannst du auswahlmöglichkeiten für Textur bei dem Bereich Farbe/Material
 * hinzufügen". Bis dahin gab es genau eine Struktur, die Leinwandbindung
 * aus `gewebe.js`, mit fester Fadenzahl und fester Stärke.
 *
 * GERECHNET, NICHT GELADEN — wie die Leinwand: Jede Art ist ein Höhenfeld
 * `hoehe(x, y, breite)` in 0..1 über eine Kachel von `faedenJeKachel` Fäden
 * je Kante. Die Kachel muss KACHELN (das prüft `test_js_gewebearten`): Die
 * Fadenzahl je Kachel ist deshalb ein Vielfaches der Musterperiode — 2 bei
 * Leinwand, 3 bei Köper.
 *
 * Je Art stehen die Vorgaben, die der Reiter beim Umschalten einstellt:
 * `faedenJeCm` (wie fein), `staerke` (wie stark sich die Bindung im Licht
 * abzeichnet, = `normalScale`) und `glanzstreuung` (`sheenRoughness`: Satin
 * wirft den Glanzsaum hart zurück, ein Strick weich). Die Zahlen sind
 * Anfangswerte zum Weiterdrehen, keine Messwerte.
 *
 *   leinwand   über eins, unter eins — Baumwolle, Leinen, Popeline
 *   koeper     über zwei, unter eins, versetzt — die Diagonale des Denim
 *   jersey     Maschen in Reihen, V über V — T-Shirt, Leggings
 *   satin      lange Flottungen, fast glatt — der Glanz macht den Stoff
 *   glatt      keine Struktur (das Aussehen bis zum 10.09.2026)
 */
export const GEWEBEARTEN = {
    leinwand: {
        titel: 'Leinwand',
        faedenJeKachel: 8, faedenJeCm: 4, staerke: 0.45, glanzstreuung: 0.8,
        hoehe: (x, y, breite) => Gewebe.hoehe(x, y, breite),
    },
    koeper: {
        titel: 'Köper (Denim)',
        faedenJeKachel: 6, faedenJeCm: 4, staerke: 0.55, glanzstreuung: 0.8,
        hoehe: (x, y, breite) => koeper(x, y, breite),
    },
    jersey: {
        titel: 'Jersey (Strick)',
        faedenJeKachel: 8, faedenJeCm: 3, staerke: 0.5, glanzstreuung: 0.9,
        hoehe: (x, y, breite) => jersey(x, y, breite),
    },
    satin: {
        titel: 'Satin',
        faedenJeKachel: 8, faedenJeCm: 8, staerke: 0.15, glanzstreuung: 0.3,
        hoehe: (x, y, breite) => satin(x, y, breite),
    },
    glatt: {
        titel: 'Glatt (ohne Gewebe)',
        faedenJeKachel: 8, faedenJeCm: 4, staerke: 0.0, glanzstreuung: 0.8,
        hoehe: null,
    },
};

/** Die Vorgabe — was ein Stück ohne Angabe bekommt. */
export const GEWEBE_VORGABE = 'leinwand';

/** Die Art zu einem Namen, sonst die Vorgabe. */
export function gewebeart(name) {
    return GEWEBEARTEN[name] || GEWEBEARTEN[GEWEBE_VORGABE];
}

function frac(v) {
    return v - Math.floor(v);
}

function mod(v, n) {
    return ((v % n) + n) % n;
}

/**
 * Köper 2/1: Der Kettfaden läuft über ZWEI Schussfäden und unter einen,
 * jede Reihe um einen Faden versetzt — daraus die Diagonale.
 *
 * Dieselben Bausteine wie die Leinwand (`Gewebe.hoehe`): runder
 * Querschnitt je Faden, eine Welle über die Länge, das Maximum von beiden.
 * Die Welle hat Periode 3 statt 2: über der Mitte der beiden „über"-Reihen
 * am höchsten, in der „unter"-Reihe am tiefsten.
 */
function koeper(x, y, breite) {
    const langK = x / breite, langS = y / breite;
    const kette = Math.floor(langK), schuss = Math.floor(langS);
    const rundK = Math.sin(Math.PI * (langK - kette));
    const rundS = Math.sin(Math.PI * (langS - schuss));
    // Kette `kette` liegt in Reihe `s` oben, wenn (s - kette) mod 3 in {0, 1}.
    const phiK = mod(langS - kette, 3);
    const welleK = Math.cos(2 * Math.PI * (phiK - 1) / 3);
    // Der Schuss liegt oben, wo die Kette unten liegt: (k - schuss) mod 3 == 1.
    const phiS = mod(langK - schuss, 3);
    const welleS = Math.cos(2 * Math.PI * (phiS - 1.5) / 3);
    const hK = Gewebe.AMPLITUDE * welleK + Gewebe.DICKE * rundK;
    const hS = Gewebe.AMPLITUDE * welleS + Gewebe.DICKE * rundS;
    return (Math.max(hK, hS) + Gewebe.AMPLITUDE)
        / (2 * Gewebe.AMPLITUDE + Gewebe.DICKE);
}

/**
 * Jersey: Maschenstäbchen — in jeder Zelle ein V aus zwei runden Schenkeln,
 * die Spitze unten in der Mitte, die Arme oben bei 15 und 85 % der Breite.
 * So bleibt zwischen den Stäbchen eine Rille, und die V stehen in Säulen
 * übereinander statt als Zickzack nebeneinander. Die Zelle ist quadratisch,
 * damit die Kachel kachelt.
 */
function jersey(x, y, breite) {
    const u = frac(x / breite), v = frac(y / breite);
    const schraege = 0.35;                     // Arm: 0,35 Breite je Höhe
    const d = Math.abs(Math.abs(u - 0.5) - schraege * v) / Math.sqrt(1 + schraege * schraege);
    const dicke = 0.16;
    const q = Math.min(1, d / dicke);
    return Math.sqrt(1 - q * q);              // runder Faden, 0 am Rand
}

/**
 * Satin: Der Kettfaden flottet über viele Schussfäden, sichtbar bleiben
 * nur die parallelen Fäden selbst — feine Rillen, keine Kreuzungen.
 */
function satin(x, y, breite) {
    return Math.sin(Math.PI * frac(x / breite));
}
