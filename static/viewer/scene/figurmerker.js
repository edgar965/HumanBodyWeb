import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Figurmerker — was je Figur zuletzt offen und gewählt war.
 *
 * WARUM (06.09.2026, Edgar): „Merke dir den letzten Tab und die Auswahl, die
 * ich beim letzten Mal hatte, als ich auf einem Modell geklickt habe, und
 * öffne diese Property beim nächsten Mal, wenn ich die Person auswähle."
 *
 * Vorher sprang jede Figurauswahl auf „Eigenschaften" zurück
 * (`populateProperties`) — auch wer im Animation-Reiter nur die Figur wechseln
 * wollte, landete bei den Reglern und musste zurückklicken.
 *
 * Gemerkt wird je Figur-Kennung: der Reiter, die gewählte Animation (Name,
 * Adresse, Kategorie) und das gewählte Kleidungsstück. Ablage im
 * sessionStorage — dieselbe Lebensdauer wie die Szene selbst (`session.js`);
 * die Kennungen der Figuren überstehen einen Reload (`toJSON`/`fromJSON`
 * tragen sie mit). Ohne sessionStorage (Node, Privatfenster) bleibt der
 * Zettel im Speicher der Seite.
 *
 * Kein Import von `state.js`: Die Klasse kennt nur Kennungen, damit sie in
 * Node ohne Three.js prüfbar ist (`test_js_figurmerker`).
 */
export class Figurmerker {

    static SCHLUESSEL = 'scene.figurmerker';
    /** {id: {tab, animation: {name, url, category}, kleider}} — erst beim ersten Zugriff gelesen. */
    static _zettel = null;

    // ------------------------------------------------------------------ Lesen

    static tab(id) {
        return Figurmerker._eintrag(id).tab || null;
    }

    static animation(id) {
        return Figurmerker._eintrag(id).animation || null;
    }

    static kleider(id) {
        return Figurmerker._eintrag(id).kleider || null;
    }

    // ---------------------------------------------------------------- Merken

    static tabMerken(id, tab) {
        Figurmerker._setzen(id, 'tab', tab || null);
    }

    /** `wahl` = {name, url, category} oder null (nichts gewählt). */
    static animationMerken(id, wahl) {
        const eintrag = wahl && wahl.url
            ? { name: wahl.name || '', url: wahl.url, category: wahl.category || '' }
            : null;
        Figurmerker._setzen(id, 'animation', eintrag);
    }

    static kleiderMerken(id, kennung) {
        Figurmerker._setzen(id, 'kleider', kennung || null);
    }

    /** Beim Löschen der Figur — sonst wächst der Zettel mit jeder Sitzung. */
    static vergessen(id) {
        if (!id) return;
        const alle = Figurmerker._alle();
        if (!(id in alle)) return;
        delete alle[id];
        Figurmerker._speichern();
    }

    /** Alles vergessen — Szene neu, Tests. */
    static leeren() {
        Figurmerker._zettel = {};
        Figurmerker._speichern();
    }

    // ---------------------------------------------------------------- Ablage

    static _eintrag(id) {
        if (!id) return {};
        return Figurmerker._alle()[id] || {};
    }

    static _setzen(id, feld, wert) {
        if (!id) return;
        const alle = Figurmerker._alle();
        alle[id] = { ...(alle[id] || {}), [feld]: wert };
        Figurmerker._speichern();
    }

    static _alle() {
        if (!Figurmerker._zettel) Figurmerker._zettel = Figurmerker._laden();
        return Figurmerker._zettel;
    }

    static _ablage() {
        return typeof sessionStorage === 'undefined' ? null : sessionStorage;
    }

    static _laden() {
        const ablage = Figurmerker._ablage();
        if (!ablage) return {};
        try {
            const gelesen = JSON.parse(ablage.getItem(Figurmerker.SCHLUESSEL) || '{}');
            return gelesen && typeof gelesen === 'object' ? gelesen : {};
        } catch (fehler) {
            Protokoll.debug('figurmerker', 'Zettel nicht lesbar', fehler);
            return {};
        }
    }

    static _speichern() {
        const ablage = Figurmerker._ablage();
        if (!ablage) return;
        try {
            ablage.setItem(Figurmerker.SCHLUESSEL, JSON.stringify(Figurmerker._zettel));
        } catch (fehler) {
            Protokoll.debug('figurmerker', 'Zettel nicht speicherbar', fehler);
        }
    }
}
