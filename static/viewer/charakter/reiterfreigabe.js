import { fn } from '../gemeinsam/registrierung.js';

/**
 * Welche Reiter ohne Figur überhaupt etwas zeigen.
 *
 * Edgar, 08.09.2026: „Wenn kein Modell angeklickt ist, sollen auch die nicht
 * aktiven Einträge im Menü links ausgegraut sein."
 *
 * Vorher waren alle neun anklickbar. Sechs davon zeigten dann nur einen
 * Hinweis („Kein Charakter gewählt"), und man erfuhr das erst nach dem Klick
 * — bei GarmentCode nach dem Klick auf einen Reiter mit fünf Bereichen, von
 * denen keiner etwas tat.
 *
 * DREI BLEIBEN OFFEN, und das ist kein Versehen:
 * * **Szene** — Licht, Kamera, Hintergrund gehören zur Szene, nicht zur Figur.
 * * **Modell** — der Modellbauer ERZEUGT eine Figur; er braucht keine.
 * * **Animation** — die Bibliothek lässt sich durchsehen, umbenennen und
 *   aufräumen, auch wenn niemand sie gerade abspielt.
 *
 * Ein ausgegrauter Reiter wird auch nicht mehr angeklickt: `initTabs` fragt
 * `frei()`, sonst wäre das Grau eine Behauptung und der Klick käme durch.
 */
export class Reiterfreigabe {

    /** Reiter, die eine gewählte Figur brauchen. */
    static BRAUCHT_FIGUR = ['eigenschaften', 'kleider', 'assets',
                            'garmentcode', 'rigging', 'finalize'];

    /** Der Reiter, auf den gewechselt wird, wenn der aktive wegfällt. */
    static AUSWEICH = 'szene';

    static anwenden(hatFigur) {
        let aktiverFiel = false;
        for (const name of Reiterfreigabe.BRAUCHT_FIGUR) {
            const reiter = document.querySelector(
                `.panel-tab[data-tab="${name}"]`);
            if (!reiter) continue;
            reiter.classList.toggle('hb-gesperrt', !hatFigur);
            reiter.title = hatFigur ? '' : 'Zuerst einen Charakter auswählen';
            if (!hatFigur && reiter.classList.contains('active')) {
                aktiverFiel = true;
            }
        }
        // Ein gesperrter Reiter darf nicht offen stehen bleiben: Sein Inhalt
        // gehört zu einer Figur, die es nicht mehr gibt.
        if (aktiverFiel) fn.switchTab?.(Reiterfreigabe.AUSWEICH);
        return aktiverFiel;
    }

    /** Ist dieser Reiter gerade bedienbar? */
    static frei(name) {
        const reiter = document.querySelector(`.panel-tab[data-tab="${name}"]`);
        return !reiter || !reiter.classList.contains('hb-gesperrt');
    }
}
