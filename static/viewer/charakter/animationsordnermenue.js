import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Bibliothekskanal } from '../gemeinsam/bibliothekskanal.js';
import { Kontextmenue } from '../gemeinsam/kontextmenue.js';
import { Figurmerker } from './figurmerker.js';

/**
 * Kontextmenü auf den ORDNERN im Animationsbaum des Szene-Reiters —
 * umbenennen und löschen.
 *
 * Edgar, 16.10.2026: „Ich mache ein Kontextmenü bei dem Ordner, sodass ich den
 * auch umbenennen kann, löschen kann. Wenn der umbenannt wird, dann wird auch
 * der Pfad auf dem lokalen Rechner umbenannt."
 *
 * ES IST DERSELBE ENDPUNKT WIE BEI DEN DATEIEN (`Animationsmenue`):
 * `/api/character/bvh-manage/` mit `rename_folder` und `delete_folder`. Der
 * Ordner ist ein Verzeichnis unter `3DObjects/animations/bvh/<Ordner>/`; der
 * Server benennt DIESES Verzeichnis um und zieht gespeicherte Studio-Projekte
 * nach (`Bvhordner.umbenennen`).
 *
 * GELÖSCHT WIRD NICHT VON DER PLATTE: Ein Ordner mit Inhalt geht in
 * `bvh/.trash/` (Mixamo allein hat über 2.300 Dateien). Die Rückfrage nennt
 * deshalb Name, Anzahl und Ziel — „Wirklich löschen?" allein sagt nicht, WAS
 * gleich weg ist.
 *
 * Was nach dem Vorgang auf DIESER Seite stimmen muss, steht hier und nicht im
 * Baumaufbau (`animation.js` ist schon über der Grenze): die gemerkte Auswahl
 * je Figur (`Figurmerker`) und die gerade laufende Animation.
 */
export class Animationsordnermenue {

    static ENDPUNKT = '/api/character/bvh-manage/';
    static BVH_ADRESSE = '/api/character/bvh/';

    /**
     * Das Menü an den Ordnerkopf hängen.
     *
     * @param kopf      der Kopf des Ordners im Baum
     * @param kategorie Name des Ordners (roher Text)
     * @param anzahl    Animationen darin (für die Rückfrage)
     * @param umfeld    `{state, fn, baumNeu, meldung}` — `state.currentAnimUrl`,
     *                  `fn.stopAnimation`, `baumNeu()` holt den Baum neu,
     *                  `meldung(text)` schreibt unter die Knöpfe
     */
    static binden(kopf, kategorie, anzahl, umfeld) {
        Kontextmenue.binden(kopf, () => [
            { symbol: 'fa-pen', text: 'Ordner umbenennen',
              tun: () => Animationsordnermenue.umbenennen(kopf, kategorie, umfeld) },
            { symbol: 'fa-trash', text: 'Ordner löschen',
              tun: () => Animationsordnermenue.loeschen(kategorie, anzahl, umfeld) },
        ]);
    }

    static async umbenennen(kopf, kategorie, umfeld) {
        const neu = (prompt(`Neuer Name für den Ordner „${kategorie}":`, kategorie) || '').trim();
        if (!neu || neu === kategorie) return false;
        const antwort = await Animationsordnermenue._senden('rename_folder',
            { category: kategorie, new_name: neu });
        if (!antwort) return false;
        Animationsordnermenue.umbenannt(kategorie, neu, umfeld.state);
        // Der Neubau liest die offenen Ordner aus dem Baum, wie er VOR dem Neubau
        // steht — mit dem alten Namen im Kopf bliebe der umbenannte Ordner zu.
        const text = kopf.querySelector('span:nth-child(2)');
        if (text) text.textContent = neu;
        await umfeld.baumNeu();
        umfeld.meldung?.(Animationsordnermenue._umbenennungstext(kategorie, neu, antwort));
        return true;
    }

    static async loeschen(kategorie, anzahl, umfeld) {
        if (!confirm(`Ordner „${kategorie}" mit ${anzahl} Animationen löschen?\n\n`
                     + 'Der Ordner wird in den Papierkorb der Bibliothek verschoben '
                     + '(3DObjects/animations/bvh/.trash/), nicht von der Platte entfernt.')) {
            return false;
        }
        const antwort = await Animationsordnermenue._senden('delete_folder',
            { category: kategorie, with_content: true });
        if (!antwort) return false;
        Animationsordnermenue.geloescht(kategorie, umfeld);
        await umfeld.baumNeu();
        umfeld.meldung?.(`Ordner „${kategorie}" gelöscht (${antwort.files ?? anzahl} Animationen im Papierkorb).`);
        return true;
    }

    /**
     * Ein Ordner heißt jetzt anders — auf diese Seite ziehen: gemerkte Auswahl
     * je Figur und die laufende Animation. Läuft nach der eigenen Umbenennung
     * UND wenn ein anderer Tab sie meldet (`Bibliothekskanal`).
     */
    static umbenannt(alt, neu, state) {
        Figurmerker.ordnerUmbenannt(alt, neu);
        const rest = Animationsordnermenue._restDerAdresse(state.currentAnimUrl, alt);
        if (rest !== null) {
            state.currentAnimUrl = `${Animationsordnermenue.BVH_ADRESSE}`
                + `${encodeURIComponent(neu)}/${rest}`;
        }
    }

    /** Ein Ordner ist weg: laufende Animation daraus stoppen, Merker leeren. */
    static geloescht(kategorie, { state, fn }) {
        if (Animationsordnermenue._restDerAdresse(state.currentAnimUrl, kategorie) !== null) {
            fn.stopAnimation(true);
            state.currentAnimName = '';
            state.currentAnimUrl = '';
        }
        Figurmerker.ordnerVergessen(kategorie);
    }

    /**
     * Der Teil der Adresse NACH dem Ordner, wenn sie in `kategorie` zeigt,
     * sonst `null`. Der Ordnername steht in der Adresse mal roh (so liefert
     * ihn die Liste: `…/bvh/Bandai 1/…`), mal kodiert — verglichen wird
     * dekodiert.
     */
    static _restDerAdresse(url, kategorie) {
        const vorn = Animationsordnermenue.BVH_ADRESSE;
        if (!url || !url.startsWith(vorn)) return null;
        const teile = url.slice(vorn.length).split('/');
        let ordner = teile[0];
        try { ordner = decodeURIComponent(ordner); } catch (fehler) { /* roh lassen */ }
        return ordner === kategorie ? teile.slice(1).join('/') : null;
    }

    static _umbenennungstext(alt, neu, antwort) {
        const clips = antwort.clips_updated || 0;
        return `Ordner „${alt}" heißt jetzt „${neu}"`
            + (clips ? ` — ${clips} Clips in gespeicherten Projekten angepasst.` : '.');
    }

    static async _senden(aktion, daten) {
        try {
            const antwort = await Serverabruf.senden(Animationsordnermenue.ENDPUNKT,
                                                     { action: aktion, ...daten });
            // Die anderen Tabs (Studio, Animationen, weitere Szenen) holen ihren Baum neu.
            Bibliothekskanal.melden(aktion, daten);
            return antwort || {};
        } catch (fehler) {
            alert(`Fehler: ${fehler.message || fehler}`);
            return null;
        }
    }
}
