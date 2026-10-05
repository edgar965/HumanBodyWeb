import { fn } from '../gemeinsam/registrierung.js';
import { Stueckmarkierung } from './stueckmarkierung.js';

/**
 * Auswahlaufhebung — Escape lässt ALLES los, was gerade gewählt ist.
 *
 * Edgar, 05.10.2026: „implementiere ESC, mit dem ich aus allen aktuellen Selektionen weg bin" —
 * auch das Verschieben (G) gehört dazu. Bis dahin wählte Escape nur die Figur ab
 * (`deselectCharacter`); die Knochenwahl und die markierten Zeilen im linken Reiter blieben,
 * und mit dem Fokus in einem Schieber oder Häkchen tat Escape gar nichts.
 *
 * Was `alles()` löst: Knochen, Figur samt Teilnetz, Hover und Verschiebe-Pfeile
 * (`deselectCharacter`), die markierte Zeile und die offenen Kategorien im linken Reiter
 * (`Stueckmarkierung.loeschen`), den Fokus eines Bedienelements.
 *
 * Escape gehört einem Textfeld, solange man darin schreibt (`schreibtText`): dort bricht es
 * die Eingabe ab und lässt die Szene in Ruhe.
 */
export class Auswahlaufhebung {

    /** `type` der Eingabefelder, in denen Escape dem Feld gehört (leer = Vorgabe `text`). */
    static TEXTFELDER = new Set(['', 'text', 'search', 'number', 'password', 'email', 'url', 'tel']);

    /** Schreibt man in diesem Element? Schieber, Häkchen und Knöpfe zählen nicht. */
    static schreibtText(ziel) {
        if (!ziel) return false;
        if (ziel.isContentEditable) return true;
        const art = String(ziel.tagName || '').toUpperCase();
        if (art === 'TEXTAREA' || art === 'SELECT') return true;
        return art === 'INPUT'
            && Auswahlaufhebung.TEXTFELDER.has(String(ziel.type || '').toLowerCase());
    }

    static alles() {
        fn._clearBoneSelection?.();
        fn.deselectCharacter?.();
        Stueckmarkierung.loeschen();
        const fokus = document.activeElement;
        if (fokus && fokus !== document.body) fokus.blur?.();
    }
}

// Über die Registrierung, damit `Greifen` (Escape während des Verschiebens) sie ohne Import erreicht.
fn.auswahlAufheben = () => Auswahlaufhebung.alles();
