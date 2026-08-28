/**
 * Kleiderregionen — die fünf Bänder, in die ein Kleidungsstück zerfällt.
 *
 * WARUM DIESES MODUL (28.08.2026, Befund `doppelcode`): Die Tabelle stand
 * zweimal — in `scene/state.js` und in `viewer/state.js`, Wert für Wert
 * gleich. Sie war schon dabei auseinanderzulaufen: `REGION_IDS` gab es nur in
 * der Szenen-Fassung.
 *
 * WAS DIE ZAHLEN BEDEUTEN: `center` ist die Höhe im Kleidungsstück, 0 unten
 * und 1 oben. `RADIUS` ist die halbe Breite des Bandes — 0,20 bei Mitten im
 * Abstand von 0,20 heißt: Die Bänder berühren sich genau, und jeder Punkt
 * liegt in höchstens zwei davon. Wer den Radius ändert, ändert damit auch,
 * wie stark sich benachbarte Regler überlagern.
 *
 * DIE NAMEN SIND DRAHTFORMAT: Sie stehen so in gespeicherten Kleiderzuständen
 * (`region_weights`) und in den Bedienelementen (`pe-<id>`). Wer sie
 * umbenennt, macht gespeicherte Anpassungen still wirkungslos.
 */

/** Die fünf Bänder, von unten nach oben. Index = Reihenfolge in der Datei. */
export const REGION_DEFS = [
    { id: 'bottom', center: 0.10 },
    { id: 'lower',  center: 0.30 },
    { id: 'mid',    center: 0.50 },
    { id: 'upper',  center: 0.70 },
    { id: 'top',    center: 0.90 },
];

/** Halbe Bandbreite. Siehe Modulkopf — nicht unabhängig von `center` wählbar. */
export const REGION_RADIUS = 0.20;

/**
 * Dieselben Namen, von OBEN nach unten.
 *
 * Die Reihenfolge ist die der Bedienelemente: Im Panel steht „top" oben.
 * Deshalb ist das nicht einfach `REGION_DEFS.map(d => d.id)` — es ist dessen
 * Umkehrung, und genau das soll hier sichtbar sein.
 */
export const REGION_IDS = REGION_DEFS.map(d => d.id).reverse();
