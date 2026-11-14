import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Figurmerker } from './figurmerker.js';
import { Posenabsatz } from './posenabsatz.js';

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
    /** Schlüssel der Figuren, die `figur()` in diesem Tab geholt hat. */
    static GEHOLT = 'scene.animationszugriff.geholt';

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
     *  Was ein früherer Aufruf geholt hat, kommt vorher aus der Szene (Edgar, 12.11.2026:
     *  „du lädst ständig neue Modelle in die Szene, lösche alte Modelle bevor du neue
     *  lädst" — nach einem Nachmittag Proben standen fünf Figuren im Tab, die Sitzung
     *  stellte sie bei jedem Neuladen wieder her). Figuren, die nicht von hier stammen,
     *  bleiben. Nach dem Entfernen `laden` neu aufrufen: die Animation bewegt sonst nichts.
     *  „Datei → Laden…" öffnet dagegen den Dateidialog des Browsers, und der hält
     *  eine ferngesteuerte Seite an. */
    static async figur(name) {
        Animationszugriff.aufraeumen();
        const inst = await fn.addCharacterFromPreset(name);
        if (inst?.id) {
            fn.selectCharacter(inst.id);
            Animationszugriff._merken([...Animationszugriff._geholt(), inst.id]);
        }
        return { id: inst?.id, quelle: inst?.quelle, name };
    }

    /** Die von `figur()` geholten Figuren aus der Szene nehmen; gibt ihre Zahl zurück. Danach ist keine
     *  Figur gewählt, wenn die gewählte dabei war — `laden` lädt dann nichts („keine Animation geladen“):
     *  erst eine Figur wählen (Klick auf ihre Zeile in `#character-list`) oder `figur()` rufen. */
    static aufraeumen() {
        let weg = 0;
        for (const id of Animationszugriff._geholt()) {
            if (state.characters.has(id)) { fn.deleteCharacter(id); weg++; }
        }
        Animationszugriff._merken([]);
        return weg;
    }

    /** Je Tab gemerkt (`sessionStorage`, wie die Szene in `session.js`): übersteht das Neuladen. */
    static _geholt() {
        try {
            const ids = JSON.parse(sessionStorage.getItem(Animationszugriff.GEHOLT) || '[]');
            return Array.isArray(ids) ? ids : [];
        } catch (e) {
            return [];
        }
    }

    static _merken(ids) {
        try { sessionStorage.setItem(Animationszugriff.GEHOLT, JSON.stringify(ids)); } catch (e) { /* ohne Speicher gilt nur dieser Seitenaufruf */ }
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
        Posenabsatz.nachMixer();          // die Fußhaltung der Schuhe wieder auf die neu gestellten Füße (12.11.2026)
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
