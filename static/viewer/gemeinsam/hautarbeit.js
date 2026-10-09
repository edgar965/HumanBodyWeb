import { Protokoll } from './protokoll.js';

/**
 * Hautarbeit — die Haut-Maske auf einem Worker rechnen lassen (Hauptfaden-Seite von `hautarbeiter.js`).
 *
 * EIN Auftrag zur Zeit: Kommt ein neuer, bevor der alte fertig ist (ein Stück kam oder ging, der Körper wurde neu gebaut), ist
 * der alte überholt — der Worker wird beendet und der Auftrag meldet `VERALTET`. Nach jedem Auftrag wird der Worker beendet
 * (Neustart ~50 ms gegen 3 s Rechnung); so hält er keinen Speicher und keinen Faden, während nichts zu tun ist.
 *
 * Fällt der Worker aus (Pfad falsch, Fehler in der Rechnung), liefert `rechnen` null, und `Hautverdeckung` rechnet selbst auf
 * dem Hauptfaden — langsamer, aber dasselbe Ergebnis. Nach dem ersten Ausfall wird es gar nicht erst wieder versucht.
 */
export class Hautarbeit {

    /** Ergebnis eines überholten Auftrags. */
    static VERALTET = 'veraltet';

    static ausgefallen = false;
    static _arbeiter = null;
    static _offen = null;
    static _zaehler = 0;

    /**
     * Der Pfad des Workers: die Vorlage kennt ihn mit Fassung (das Szenenbündel hat kein sinnvolles `import.meta.url`).
     */
    static pfad() {
        const meta = typeof document !== 'undefined' ? document.querySelector('meta[name="hautarbeiter"]')?.content : null;
        return meta || new URL('./hautarbeiter.js', import.meta.url).href;
    }

    /**
     * @param pos     Punkte des Körpers (Ruhelage) — wird kopiert
     * @param index   der volle Index — wird kopiert
     * @param stoffe  `Hautverdeckung.stoffe(inst)`; vom Netz geht nur Zahlenwerk mit, kopiert
     * @returns {Promise<object|string|null>} das Ergebnis von `Hautrechnung.rechnen`, `VERALTET` oder null (kein Worker)
     */
    static rechnen(pos, index, stoffe) {
        if (Hautarbeit.ausgefallen || typeof Worker === 'undefined') return Promise.resolve(null);
        Hautarbeit.abbrechen();
        let arbeiter;
        try {
            arbeiter = new Worker(Hautarbeit.pfad(), { type: 'module' });
        } catch (fehler) {
            return Hautarbeit._ausfall(`nicht gestartet: ${fehler.message}`);
        }
        const id = ++Hautarbeit._zaehler;
        Hautarbeit._arbeiter = arbeiter;
        return new Promise((weiter) => {
            Hautarbeit._offen = { id, weiter };
            arbeiter.onmessage = (ereignis) => Hautarbeit._angekommen(id, ereignis.data);
            arbeiter.onerror = (ereignis) => {
                ereignis.preventDefault?.();
                Hautarbeit._beenden(id, null, `Worker: ${ereignis.message || 'abgebrochen'}`);
            };
            const kopien = Hautarbeit._kopien(pos, index, stoffe);
            arbeiter.postMessage({ typ: 'rechnen', id, ...kopien.nachricht }, kopien.puffer);
        });
    }

    /** Ein laufender Auftrag ist überholt. */
    static abbrechen() {
        const offen = Hautarbeit._offen;
        if (!offen) return;
        Hautarbeit._beenden(offen.id, Hautarbeit.VERALTET);
    }

    /**
     * Kompakte Kopien für den Worker. Die Felder der Geometrien sind oft Ausschnitte eines großen Puffers (die Netzantwort);
     * ein Ausschnitt würde mit dem GANZEN Puffer geklont. `slice` kopiert nur den Ausschnitt, und die Kopie wird übertragen.
     */
    static _kopien(pos, index, stoffe) {
        const nachricht = {
            pos: pos.slice(), index: index.slice(),
            stoffe: stoffe.map((s) => ({ schluessel: s.schluessel, punkte: s.punkte.slice(), dreiecke: s.dreiecke.slice(),
                                         tiefe: s.tiefe, starr: s.starr, nahe: s.nahe, ersatz: s.ersatz })),
        };
        const puffer = [nachricht.pos.buffer, nachricht.index.buffer];
        for (const s of nachricht.stoffe) puffer.push(s.punkte.buffer, s.dreiecke.buffer);
        return { nachricht, puffer: [...new Set(puffer)] };
    }

    static _angekommen(id, daten) {
        if (daten?.typ === 'fertig') Hautarbeit._beenden(id, daten.ergebnis);
        else if (daten?.typ === 'fehler') Hautarbeit._beenden(id, null, daten.meldung);
    }

    /** Den Auftrag `id` abschließen: Worker beenden, Versprechen erfüllen. Ein fremdes `id` (überholt) tut nichts. */
    static _beenden(id, ergebnis, fehler = null) {
        const offen = Hautarbeit._offen;
        if (!offen || offen.id !== id) return;
        Hautarbeit._offen = null;
        Hautarbeit._arbeiter?.terminate();
        Hautarbeit._arbeiter = null;
        if (fehler) Hautarbeit._ausfall(fehler);
        offen.weiter(ergebnis);
    }

    static _ausfall(grund) {
        Hautarbeit.ausgefallen = true;
        Protokoll.warnung('Hautarbeit', `Haut-Maske ohne Worker, der Hauptfaden rechnet selbst: ${grund}`);
        return Promise.resolve(null);
    }
}
