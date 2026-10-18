import { Genesis9hautebenenwerte } from './genesis9hautebenenwerte.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Genesis9eigenehaut — eine selbst eingestellte Haut speichern und wieder wählen (18.10.2026).
 *
 * Edgar, 18.10.2026: „Auch Button zum speichern der Neuen Haut, mit hautnamen, die soll dann auch in die Haut Combo box erscheinen". Gespeichert wird ein REZEPT (Server:
 * `core/dienste/g9eigenehaut.py`): der Hautsatz darunter (`grund`, die gewählte Haut der Figur), die Hautebenen der Haut (ohne graue Haare), Glanz/Rauheit/Relief der Haut
 * (`teilmaterial.haut`) und die Texturmischung. In der Hautauswahl steht es als `eigen:<schluessel>`; der Server gibt dafür die Bilder des Grundsatzes, und `waehlen` legt die
 * Werte des Rezepts VOR dem Körperbau auf die Figur — der Bau zieht sie dann selbst nach (`Genesis9Modell.koerperAufbauen`: Texturmischung, Teilmaterial, Falten, Hautebenen).
 *
 * Wer danach eine gewöhnliche Haut wählt, behält die Regler (wie vorher: Hautebenen hängen nicht am Hautsatz).
 */
export class Genesis9eigenehaut {

    static ADRESSE = '/api/character/genesis9-figur/eigenehaut/';
    static PRAEFIX = 'eigen:';

    static ist(kennung) {
        return String(kennung || '').startsWith(Genesis9eigenehaut.PRAEFIX);
    }

    /** Das Rezept der Figur, wie es an den Server geht. */
    static rezept(inst, name) {
        const haut = new Set(Genesis9hautebenenwerte.hautfelder().map(f => f.name));
        const hautebenen = Object.fromEntries(Object.entries(inst.hautebenen || {}).filter(([k]) => haut.has(k)));
        const hautmischung = Object.fromEntries(Object.entries(inst.hautmischung || {}).filter(([k, v]) => !Genesis9eigenehaut.ist(k) && v > 0));
        return { name, grund: inst.haut || '', figur: inst.figur || '', hautebenen, teilmaterial: { ...(inst.teilmaterial?.haut || {}) }, hautmischung };
    }

    /** Der Name der gewählten eigenen Haut (für das Namensfeld) — leer bei einer gewöhnlichen. */
    static name(inst, plan) {
        if (!Genesis9eigenehaut.ist(inst.haut)) return '';
        return (plan?.haut || []).find(h => h.id === inst.haut)?.rezept?.name || '';
    }

    /** Gibt es schon eine eigene Haut mit diesem Namen (ohne Groß-/Kleinschreibung)? */
    static vorhanden(plan, name) {
        const gesucht = String(name || '').trim().toLowerCase();
        return (plan?.haut || []).some(h => Genesis9eigenehaut.ist(h.id) && String(h.rezept?.name || '').toLowerCase() === gesucht);
    }

    /**
     * Speichern; → der neue Eintrag der Hautauswahl (`{id, name, geschlecht, rezept}`). Trägt ihn in `plan.haut` ein (ersetzt einen gleichen) und stellt die Figur auf ihn —
     * ohne Neubau: der Grundsatz ist derselbe, den die Figur gerade trägt. Fehler des Servers kommen als `Error` mit seiner Meldung.
     */
    static async speichern(inst, plan, name) {
        let antwort;
        try {
            antwort = await Serverabruf.senden(Genesis9eigenehaut.ADRESSE, Genesis9eigenehaut.rezept(inst, name));
        } catch (fehler) {
            throw new Error(fehler?.daten?.fehler || fehler?.message || 'Speichern fehlgeschlagen');
        }
        const eintrag = antwort?.eintrag;
        if (!eintrag?.id) throw new Error(antwort?.fehler || 'Speichern fehlgeschlagen');
        if (plan) {
            plan.haut = [...(plan.haut || []).filter(h => h.id !== eintrag.id), eintrag];
        }
        inst.haut = eintrag.id;
        return { eintrag, ueberschrieben: Boolean(antwort.ueberschrieben) };
    }

    /**
     * Eine Haut der Auswahl wählen. Bei einer eigenen: erst die Werte des Rezepts auf die Figur (Hautebenen der Haut ganz ersetzt, graue Haare bleiben; `teilmaterial.haut`
     * und Texturmischung ersetzt), dann der Wechsel — der baut den Körper und legt alles neu auf.
     */
    static waehlen(inst, plan, kennung) {
        const rezept = Genesis9eigenehaut.ist(kennung) ? (plan?.haut || []).find(h => h.id === kennung)?.rezept : null;
        if (rezept) Genesis9eigenehaut.auflegen(inst, rezept);
        return inst.hautSetzen(kennung);
    }

    /** Die Werte eines Rezepts auf die Figur legen (ohne anzuwenden — das macht der folgende Körperbau). */
    static auflegen(inst, rezept) {
        const haut = new Set(Genesis9hautebenenwerte.hautfelder().map(f => f.name));
        const bleibt = Object.fromEntries(Object.entries(inst.hautebenen || {}).filter(([k]) => !haut.has(k)));
        const neu = Object.fromEntries(Object.entries(rezept.hautebenen || {}).filter(([k, v]) => haut.has(k) && Number.isFinite(Number(v))));
        inst.hautebenen = { ...bleibt, ...neu };
        inst.teilmaterial = { ...(inst.teilmaterial || {}) };
        if (Object.keys(rezept.teilmaterial || {}).length) inst.teilmaterial.haut = { ...rezept.teilmaterial };
        else delete inst.teilmaterial.haut;
        inst.hautmischung = { ...(rezept.hautmischung || {}) };
    }
}
