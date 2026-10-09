/**
 * Nutzerruhe — hat der Nutzer gerade die Hand an der Szene?
 *
 * WARUM (Edgar, 09.10.2026: „ich brauche schnelles Anzeigen, damit ich drehen und vergrößern kann … die feine Stufe nur nach
 * Ruhe, in kleinen Häppchen laden"): Die feine Stufe einer Genesis-9-Figur (`Genesis9aufbau`, 2 Unterteilungen, ~1 Mio. Punkte
 * in 11 Netzen) kam bisher gleich nach dem Käfig und hielt den Hauptfaden gemessen 15,7 s und danach 71 s an — in dieser Zeit
 * ließ sich die Figur nicht drehen. Der Aufbau wartet jetzt auf Ruhe: keine Zeigerbewegung, kein Rad, keine Taste seit
 * `RUHE_MS`, und keine gedrückte Taste der Maus. Wer gerade dreht, hält ihn an; wer die Figur anschaut, bekommt sie scharf.
 *
 * Gemessen wird an Eingaben, nicht an der Zeit: Ein versteckter Tab bekommt keine und gilt sofort als ruhig.
 */
export class Nutzerruhe {

    /** So lange darf nichts bewegt worden sein. */
    static RUHE_MS = 1500;
    /** Ereignisse, die „die Hand ist an der Szene" heißen. */
    static EREIGNISSE = ['pointermove', 'pointerdown', 'wheel', 'keydown', 'touchstart', 'touchmove'];

    static _letzte = performance.now();
    static _gedrueckt = 0;
    static _hoert = false;

    /** Einmal an das Fenster hängen (beim ersten Gebrauch). */
    static _anmelden() {
        if (Nutzerruhe._hoert || typeof window === 'undefined') return;
        Nutzerruhe._hoert = true;
        const merken = () => { Nutzerruhe._letzte = performance.now(); };
        for (const art of Nutzerruhe.EREIGNISSE) {
            window.addEventListener(art, merken, { passive: true, capture: true });
        }
        window.addEventListener('pointerdown', () => { Nutzerruhe._gedrueckt += 1; }, { passive: true, capture: true });
        const los = () => { Nutzerruhe._gedrueckt = Math.max(0, Nutzerruhe._gedrueckt - 1); merken(); };
        window.addEventListener('pointerup', los, { passive: true, capture: true });
        window.addEventListener('pointercancel', los, { passive: true, capture: true });
        window.addEventListener('blur', () => { Nutzerruhe._gedrueckt = 0; }, { passive: true });
    }

    /** Ist seit `ms` nichts bewegt worden und keine Maustaste gedrückt? */
    static ruhig(ms = Nutzerruhe.RUHE_MS) {
        Nutzerruhe._anmelden();
        return Nutzerruhe._gedrueckt === 0 && performance.now() - Nutzerruhe._letzte >= ms;
    }

    /**
     * Warten, bis Ruhe ist — sofort, wenn schon. `abbruch`: eine Funktion, die true liefert, wenn nicht mehr gewartet werden
     * soll (der Export braucht die feine Stufe jetzt, `Figuraufbaustand.warten`).
     */
    static async abwarten(abbruch = null, ms = Nutzerruhe.RUHE_MS) {
        Nutzerruhe._anmelden();
        while (!Nutzerruhe.ruhig(ms)) {
            if (abbruch && abbruch()) return;
            await new Promise((weiter) => setTimeout(weiter, 250));
        }
    }

    /** Dem Browser einen Atemzug geben — zwischen zwei schweren Schritten, damit Eingaben dazwischen drankommen. */
    static atmen() {
        return new Promise((weiter) => setTimeout(weiter, 0));
    }
}
