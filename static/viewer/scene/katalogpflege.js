import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Katalogpflege — Modelle und UMA-Figuren umbenennen oder löschen.
 *
 * Edgar, 06.09.2026: „Mach auch Möglichkeiten zum Umbenennen und Löschen der
 * Modelle aus dem Dialog." Beides verändert Dateien auf der Platte, deshalb
 * steht vor dem Löschen eine Rückfrage mit dem NAMEN darin — nicht bloß
 * „Wirklich löschen?", sondern was genau verschwindet.
 *
 * Bei einer UMA-Figur betrifft es GLB und Beipackzettel zusammen und, falls
 * der Zeiger `aktuell.json` auf sie zeigt, auch den (Server: `Umaablage`).
 */
export class Katalogpflege {

    static ADRESSEN = {
        uma: {
            umbenennen: '/api/character/katalog/uma/umbenennen/',
            loeschen: '/api/character/katalog/uma/loeschen/',
            was: 'Figur',
        },
        modell: {
            umbenennen: '/api/character/katalog/modell/umbenennen/',
            loeschen: '/api/character/katalog/modell/loeschen/',
            was: 'Modell',
        },
    };

    /**
     * Nach einem neuen Namen fragen und umbenennen.
     *
     * @returns der neue Name, oder null wenn abgebrochen
     */
    static async umbenennen(art, name) {
        const adressen = Katalogpflege.ADRESSEN[art];
        const anzeige = Katalogpflege.ohneEndung(name);
        const eingabe = window.prompt(`Neuer Name für ${adressen.was} „${anzeige}":`, anzeige);
        if (eingabe === null) return null;
        const neu = eingabe.trim();
        if (!neu || neu === anzeige) return null;
        const antwort = await Serverabruf.json(adressen.umbenennen, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ alt: name, neu: Katalogpflege.mitEndung(neu, name) }),
        });
        return antwort.name;
    }

    /**
     * Rückfragen und löschen.
     *
     * @returns true, wenn gelöscht wurde
     */
    static async loeschen(art, name) {
        const adressen = Katalogpflege.ADRESSEN[art];
        const anzeige = Katalogpflege.ohneEndung(name);
        const zusatz = art === 'uma'
            ? '\n\nGelöscht werden die GLB und ihr Beipackzettel.'
            : '';
        if (!window.confirm(`${adressen.was} „${anzeige}" endgültig löschen?${zusatz}`)) {
            return false;
        }
        await Serverabruf.json(adressen.loeschen, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
        return true;
    }

    /** `Uma_X.glb` → `Uma_X`; ein Modellname bleibt, wie er ist. */
    static ohneEndung(name) {
        return name.replace(/\.glb$/i, '');
    }

    /** Die Endung des alten Namens an den neuen hängen, falls sie fehlt. */
    static mitEndung(neu, alt) {
        if (!/\.glb$/i.test(alt)) return neu;
        return /\.glb$/i.test(neu) ? neu : `${neu}.glb`;
    }
}
