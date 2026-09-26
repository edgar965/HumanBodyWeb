import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Figurmerker } from './figurmerker.js';

/**
 * Animationszugriff — die Ladefunktion der Szene global erreichbar, für die
 * Konsole und die Prüfung im Chrome (Edgar, 24.09.2026: „mach die
 * Ladefunktion global erreichbar"). Bis dahin ging eine Animation nur über
 * einen Klick in den Baum des Reiters „Animation", und der entsteht erst,
 * wenn der Reiter offen ist (`reiterinhalt.js`).
 *
 *     await __animation.figur('Female with Clothes')   // Modell holen und auswählen
 *     await __animation.laden('A_Results', '001_ShyrinKurz_smplx')
 *     __animation.stellen(229)          // Bild wie in der Zeitanzeige
 *     __animation.stand()
 *
 * `laden` tut dasselbe wie der Klick (markieren, je Figur merken, laden) —
 * gemeint ist die AUSGEWÄHLTE Figur. `stellen` rechnet das Bild wie
 * `Szenenschleife.zeitanzeige` (Zeit / Abstand der ersten beiden Schlüssel)
 * und hält die Animation dort an.
 */
export class Animationszugriff {

    static BIBLIOTHEK = '/api/character/animations/';

    static async laden(kategorie, name) {
        const daten = await Serverabruf.json(Animationszugriff.BIBLIOTHEK);
        const anim = (daten.categories?.[kategorie] || []).find(a => a.name === name);
        if (!anim) throw new Error(`Animation ${kategorie}/${name} nicht in der Bibliothek`);
        fn.animationMarkieren?.(anim.name);
        Figurmerker.animationMerken(state.selectedCharacterId,
                                    { name: anim.name, url: anim.url, category: kategorie });
        state.currentAnimName = anim.name;
        await fn.loadBVHAnimation(anim.url, anim.name, anim.frames || 0);
        return Animationszugriff.stand();
    }

    /** Ein gespeichertes Modell in die Szene holen und auswählen — `laden` gilt dann ihr.
     *  „Datei → Laden…" öffnet dagegen den Dateidialog des Browsers, und der hält
     *  eine ferngesteuerte Seite an. */
    static async figur(name) {
        const inst = await fn.addCharacterFromPreset(name);
        if (inst?.id) fn.selectCharacter(inst.id);
        return { id: inst?.id, quelle: inst?.quelle, name };
    }

    static stellen(bild) {
        const aktion = state.currentAction;
        const clip = aktion?.getClip();
        if (!clip) throw new Error('keine Animation geladen');
        aktion.paused = true;
        state.playing = false;
        aktion.time = Math.min(clip.duration, Math.max(0, bild * Animationszugriff._bildzeit(clip)));
        // Eine pausierte Aktion wertet ihre Spuren trotzdem aus — nur die Zeit steht.
        state.mixer?.update(0);
        return Animationszugriff.stand();
    }

    static stand() {
        const aktion = state.currentAction;
        const clip = aktion?.getClip();
        if (!clip) return { name: state.currentAnimName || '', geladen: false };
        const bildzeit = Animationszugriff._bildzeit(clip);
        return {
            name: state.currentAnimName || clip.name, geladen: true,
            bild: Math.floor(aktion.time / bildzeit), bilder: Math.round(clip.duration / bildzeit),
            zeit: aktion.time, dauer: clip.duration, pausiert: aktion.paused,
        };
    }

    static _bildzeit(clip) {
        return clip.tracks[0]?.times?.[1] || 1 / 30;
    }
}

window.__animation = Animationszugriff;
