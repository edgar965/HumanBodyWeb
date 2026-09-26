/**
 * Animationsentfernung — was nach dem Löschen einer Animation im Szene-Reiter
 * zu geschehen hat.
 *
 * Edgar, 12.09.2026: „nach löschen einer Animation geht der Tab zu, die alte
 * Animation bleibt usw. Es soll der Eintrag verschwinden, auf die nächste
 * Animation selektiert werden, und die aktuelle Animation soll stoppen."
 *
 * Vorher holte das Kontextmenü nach dem Löschen nur den Baum neu: alle Ordner
 * wieder zugeklappt (`Kategoriekasten.bauen` kennt keinen alten Zustand), die
 * gelöschte Animation lief auf der Figur weiter, ihr Name stand noch im
 * Figurmerker jeder Figur, die sie einmal gewählt hatte — und Play hätte beim
 * nächsten Mal eine Datei geladen, die es nicht mehr gibt.
 *
 * Reihenfolge hier: NACHFOLGER BESTIMMEN, solange der Eintrag noch im Baum
 * steht — dann stoppen, vergessen, Baum neu (Ordner offen wie vorher),
 * Nachfolger wählen. Gewählt heisst: hervorgehoben und für die Figur gemerkt,
 * wie nach einem Klick — nur ohne Laden. Play startet ihn dann. Was wirklich
 * gelöscht wird, entscheidet `Animationsmenue` (Rückfrage mit dem Namen).
 *
 * Die Entscheidungen (`nachfolger`, `nach`) laufen ohne DOM und ohne Three.js,
 * damit sie in Node prüfbar sind; die zwei DOM-Leser stehen getrennt darunter.
 */
export class Animationsentfernung {

    /**
     * Der Eintrag, der nach dem Löschen gewählt wird: der nächste im selben
     * Ordner, sonst der vorige dort, sonst der nächste, sonst der vorige der
     * ganzen Liste — oder null, wenn nichts übrig bleibt.
     * @param {Array<{name: string, url: string, category: string}>} eintraege
     *        in Baumreihenfolge, MIT dem zu löschenden Eintrag
     */
    static nachfolger(eintraege, kategorie, name) {
        const liste = Array.isArray(eintraege) ? eintraege : [];
        const i = liste.findIndex(
            (e) => e.name === name && e.category === kategorie);
        if (i < 0) return null;
        const imOrdner = (e) => e.category === kategorie;
        const danach = liste.slice(i + 1);
        const davor = liste.slice(0, i).reverse();
        return danach.find(imOrdner) || davor.find(imOrdner)
            || danach[0] || davor[0] || null;
    }

    /**
     * Nach dem Löschen von `anim` (name, url) aus `kategorie`.
     *
     * @param {Object} umfeld
     * @param {Array} umfeld.eintraege  der Baum VOR dem Neubau (siehe `eintraege`)
     * @param {Object} umfeld.state     `currentAnimUrl`, `currentAnimName`, `selectedCharacterId`
     * @param {Object} umfeld.fn        `stopAnimation`, `animationMarkieren`
     * @param {Object} umfeld.merker    Figurmerker (`animationVergessen`, `animationMerken`)
     * @param {Function} umfeld.baumNeu holt den Baum neu (async)
     * @param {Function} [umfeld.meldung] Zeile unter den Knöpfen — sonst
     *        stünde dort weiter „<gelöschte> · 22 Spuren · 3,0 s"
     * @returns {Promise<{gestoppt: boolean, gewaehlt: Object|null}>}
     */
    static async nach(anim, kategorie, umfeld) {
        const { eintraege, state, fn, merker, baumNeu, meldung } = umfeld;
        const gewaehlt = Animationsentfernung.nachfolger(
            eintraege, kategorie, anim.name);
        const lief = Animationsentfernung.laeuft(state, anim);
        if (lief) {
            fn.stopAnimation(true);
            state.currentAnimName = '';
        }
        merker.animationVergessen(anim.url);
        await baumNeu();
        if (gewaehlt) {
            fn.animationMarkieren(gewaehlt.name);
            if (state.selectedCharacterId) {
                merker.animationMerken(state.selectedCharacterId, gewaehlt);
            }
            state.currentAnimName = gewaehlt.name;
        }
        if (meldung) {
            meldung(gewaehlt
                ? `„${anim.name}" gelöscht — „${gewaehlt.name}" gewählt.`
                : `„${anim.name}" gelöscht.`);
        }
        return { gestoppt: lief, gewaehlt };
    }

    /**
     * Läuft gerade DIESE Animation? Über die Adresse, nicht nur den Namen:
     * zwei Ordner dürfen gleichnamige Dateien führen.
     */
    static laeuft(state, anim) {
        if (anim.url && state.currentAnimUrl === anim.url) return true;
        return !state.currentAnimUrl && !!anim.name
            && state.currentAnimName === anim.name;
    }

    // -- DOM-Leser ----------------------------------------------------------

    /** Die Einträge des Baums als Daten, in Baumreihenfolge. */
    static eintraege(baum) {
        if (!baum) return [];
        return Array.from(baum.querySelectorAll('.anim-item')).map((e) => ({
            name: e.dataset.name || '',
            url: e.dataset.url || '',
            category: e.dataset.category || '',
        }));
    }

    /**
     * Die Namen der offenen Ordner — damit der Neubau sie offen lässt. Der
     * Name ist der zweite `span` im Kopf; der erste ist der Pfeil, der
     * dritte die Zahl (`Kategoriekasten.bauen`).
     */
    static offeneOrdner(baum) {
        if (!baum) return new Set();
        return new Set(Array.from(
            baum.querySelectorAll('.anim-category.open .anim-category-header'))
            .map((kopf) => kopf.querySelector('span:nth-child(2)')?.textContent)
            .map((text) => (text || '').trim())
            .filter(Boolean));
    }
}
