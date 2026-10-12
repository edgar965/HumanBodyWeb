import { Protokoll } from './protokoll.js';

/**
 * Anatomiearbeit — Bild und Füllen der Anatomie-Karten auf einem Worker rechnen lassen (Hauptfaden-Seite von `anatomiearbeiter.js`; 12.10.2026).
 *
 * EIN Auftrag je Stück (`eigner`): Kommt für dasselbe Stück ein neuer, bevor der alte fertig ist (Haut noch einmal gewechselt), ist der alte überholt — sein
 * Worker wird beendet und der Auftrag meldet `VERALTET`. Verschiedene Stücke rechnen nebeneinander, je ein Worker. Nach jedem Auftrag wird der Worker beendet
 * (Neustart ~50 ms gegen 1,5 s Rechnung): er hält keinen Speicher und keinen Faden, während nichts zu tun ist.
 *
 * Fehlt der Pfad (die Seite hat kein `<meta name="anatomiearbeiter">`, etwa das Studio) oder fällt der Worker aus (Pfad falsch, Fehler in der Rechnung), liefert
 * `rechnen` null, und `Anatomiebacken.bild` rechnet auf dem Hauptfaden — langsamer, aber dasselbe Ergebnis. Nach dem ersten Ausfall wird es nicht wieder versucht.
 */
export class Anatomiearbeit {

    /** Ergebnis eines überholten Auftrags. */
    static VERALTET = 'veraltet';

    static ausgefallen = false;
    /** Stück -> {id, arbeiter, weiter} des laufenden Auftrags. */
    static _offen = new WeakMap();
    static _zaehler = 0;

    /** Der Pfad des Workers aus der Vorlage (mit Fassung); null, wenn die Seite keinen kennt (das Szenenbündel hat kein sinnvolles `import.meta.url`). */
    static pfad() {
        return typeof document !== 'undefined' ? document.querySelector('meta[name="anatomiearbeiter"]')?.content || null : null;
    }

    /** Gibt es einen Worker zu haben? (Kein Pfad in der Vorlage, kein `Worker` im Browser oder ein früherer Ausfall: nein.) */
    static verfuegbar() {
        return !Anatomiearbeit.ausgefallen && typeof Worker !== 'undefined' && !!Anatomiearbeit.pfad();
    }

    /**
     * @param auftrag  `{zu, st, ha, gruppe, fenster, breite, hoehe, uvKarte}` wie bei `Anatomierechnung.rechnen`. Die Felder werden kopiert (die Zuordnung
     *                 liegt noch im Zwischenspeicher des Stücks); die Pixel der Fenster gehen mit, sie sind danach leer.
     * @param eigner   das Netz des Stücks
     * @returns {Promise<object|string|null>} `{farbe, normal, rauheit}`, `VERALTET` oder null (kein Worker, oder er ist ausgefallen)
     */
    static rechnen(auftrag, eigner) {
        if (!Anatomiearbeit.verfuegbar()) return Promise.resolve(null);
        const pfad = Anatomiearbeit.pfad();
        Anatomiearbeit.abbrechen(eigner);
        let arbeiter;
        try {
            arbeiter = new Worker(pfad, { type: 'module' });
        } catch (fehler) {
            return Anatomiearbeit._ausfall(`nicht gestartet: ${fehler.message}`);
        }
        const id = ++Anatomiearbeit._zaehler;
        return new Promise((weiter) => {
            Anatomiearbeit._offen.set(eigner, { id, arbeiter, weiter });
            arbeiter.onmessage = (ereignis) => Anatomiearbeit._angekommen(eigner, id, ereignis.data);
            arbeiter.onerror = (ereignis) => {
                ereignis.preventDefault?.();
                Anatomiearbeit._beenden(eigner, id, null, `Worker: ${ereignis.message || 'abgebrochen'}`);
            };
            const kopien = Anatomiearbeit._kopien(auftrag);
            arbeiter.postMessage({ typ: 'rechnen', id, ...kopien.nachricht }, kopien.puffer);
        });
    }

    /** Ein laufender Auftrag für dieses Stück ist überholt. */
    static abbrechen(eigner) {
        const offen = Anatomiearbeit._offen.get(eigner);
        if (offen) Anatomiearbeit._beenden(eigner, offen.id, Anatomiearbeit.VERALTET);
    }

    /**
     * Kompakte Kopien für den Worker. Die Felder der Geometrien sind oft Ausschnitte eines großen Puffers (die Netzantwort); ein Ausschnitt würde mit dem GANZEN
     * Puffer geklont. `slice` kopiert nur den Ausschnitt, und die Kopie wird übertragen. Ein Feld, das zweimal vorkommt (`st.uv` und `uvKarte` ohne `flipY`),
     * wird einmal kopiert.
     */
    static _kopien(a) {
        const gemerkt = new Map(), puffer = new Set();
        const kopie = (feld) => {
            if (!feld) return feld;
            if (!gemerkt.has(feld)) {
                const k = feld.slice();
                gemerkt.set(feld, k);
                puffer.add(k.buffer);
            }
            return gemerkt.get(feld);
        };
        const alle = (objekt) => Object.fromEntries(Object.entries(objekt).map(([name, wert]) => [name, ArrayBuffer.isView(wert) ? kopie(wert) : wert]));
        const fenster = a.fenster.map((gruppe) => gruppe && Object.fromEntries(Object.entries(gruppe).map(([name, f]) => {
            if (f) puffer.add(f.daten.buffer);                     // frisch aus `getImageData`: gehört niemandem sonst
            return [name, f];
        })));
        const nachricht = { zu: alle(a.zu), st: alle(a.st), ha: alle(a.ha), gruppe: kopie(a.gruppe), fenster, breite: a.breite, hoehe: a.hoehe, uvKarte: kopie(a.uvKarte) };
        return { nachricht, puffer: [...puffer] };
    }

    static _angekommen(eigner, id, daten) {
        if (daten?.typ === 'fertig') Anatomiearbeit._beenden(eigner, id, daten.ergebnis);
        else if (daten?.typ === 'fehler') Anatomiearbeit._beenden(eigner, id, null, daten.meldung);
    }

    /** Den Auftrag `id` abschließen: Worker beenden, Versprechen erfüllen. Ein fremdes `id` (überholt) tut nichts. */
    static _beenden(eigner, id, ergebnis, fehler = null) {
        const offen = Anatomiearbeit._offen.get(eigner);
        if (!offen || offen.id !== id) return;
        Anatomiearbeit._offen.delete(eigner);
        offen.arbeiter.terminate();
        if (fehler) Anatomiearbeit._ausfall(fehler);
        offen.weiter(ergebnis);
    }

    static _ausfall(grund) {
        Anatomiearbeit.ausgefallen = true;
        Protokoll.warnung('Anatomiearbeit', `Anatomie-Karten ohne Worker, der Hauptfaden rechnet selbst: ${grund}`);
        return Promise.resolve(null);
    }
}
