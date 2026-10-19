import { Protokoll } from './protokoll.js';

/**
 * Hautarbeit — die Haut-Maske auf einem Worker rechnen lassen (Hauptfaden-Seite von `hautarbeiter.js`).
 *
 * EIN Worker zur Zeit, Aufträge in einer Warteschlange. Ein neuer Auftrag DERSELBEN Figur (`kennung`: ein Stück kam oder ging, der Körper wurde neu gebaut)
 * überholt ihren alten — läuft er, wird der Worker beendet; wartet er, fällt er heraus; beide melden `VERALTET`. Aufträge ANDERER Figuren warten, bis der
 * laufende fertig ist. Bis 19.10.2026 überholte jeder neue Auftrag jeden alten: Auf Mesh3D-AI (Ziel und Ergebnis, zwei Figuren) brach die Maske der zweiten
 * Figur die der ersten ab, und niemand plante sie neu — die erste Figur blieb ohne Maske (gesehen im Serverlog des Maskenvorrats: angefragt, nie abgelegt).
 * Nach jedem Auftrag wird der Worker beendet (Neustart ~50 ms gegen 3 s Rechnung); so hält er keinen Speicher und keinen Faden, während nichts zu tun ist.
 *
 * Fällt der Worker aus (Pfad falsch, Fehler in der Rechnung), liefert `rechnen` null, und `Hautverdeckung` rechnet selbst auf
 * dem Hauptfaden — langsamer, aber dasselbe Ergebnis. Nach dem ersten Ausfall wird es gar nicht erst wieder versucht.
 */
export class Hautarbeit {

    /** Ergebnis eines überholten Auftrags. */
    static VERALTET = 'veraltet';

    static ausgefallen = false;
    /** Der laufende Auftrag `{id, kennung, weiter, arbeiter}` — oder null. */
    static _laufend = null;
    /** Wartende Aufträge `{id, kennung, weiter, kopien}` in der Reihenfolge ihres Eingangs. */
    static _warteschlange = [];
    static _zaehler = 0;

    /**
     * Der Pfad des Workers: die Vorlage kennt ihn mit Fassung (das Szenenbündel hat kein sinnvolles `import.meta.url`).
     */
    static pfad() {
        const meta = typeof document !== 'undefined' ? document.querySelector('meta[name="hautarbeiter"]')?.content : null;
        return meta || new URL('./hautarbeiter.js', import.meta.url).href;
    }

    /**
     * @param pos      Punkte des Körpers (Ruhelage) — wird kopiert (beim Eingang, nicht erst beim Start)
     * @param index    der volle Index — wird kopiert
     * @param stoffe   `Hautverdeckung.stoffe(inst)`; vom Netz geht nur Zahlenwerk mit, kopiert
     * @param kennung  wessen Maske (die Figur): ein neuer Auftrag mit derselben Kennung überholt den alten
     * @returns {Promise<object|string|null>} das Ergebnis von `Hautrechnung.rechnen`, `VERALTET` oder null (kein Worker)
     */
    static rechnen(pos, index, stoffe, kennung = '') {
        if (Hautarbeit.ausgefallen || typeof Worker === 'undefined') return Promise.resolve(null);
        Hautarbeit.abbrechen(kennung);
        const id = ++Hautarbeit._zaehler;
        const kopien = Hautarbeit._kopien(pos, index, stoffe);
        return new Promise((weiter) => {
            Hautarbeit._warteschlange.push({ id, kennung, weiter, kopien });
            Hautarbeit._naechster();
        });
    }

    /** Die Aufträge einer Figur sind überholt (ohne Kennung: alle). */
    static abbrechen(kennung = null) {
        const betrifft = (a) => kennung === null || a.kennung === kennung;
        const bleiben = [];
        for (const a of Hautarbeit._warteschlange) {
            if (betrifft(a)) a.weiter(Hautarbeit.VERALTET); else bleiben.push(a);
        }
        Hautarbeit._warteschlange = bleiben;
        const laufend = Hautarbeit._laufend;
        if (laufend && betrifft(laufend)) Hautarbeit._beenden(laufend.id, Hautarbeit.VERALTET);
    }

    /** Den nächsten wartenden Auftrag starten, wenn keiner läuft. */
    static _naechster() {
        if (Hautarbeit._laufend || !Hautarbeit._warteschlange.length) return;
        const auftrag = Hautarbeit._warteschlange.shift();
        let arbeiter;
        try {
            arbeiter = new Worker(Hautarbeit.pfad(), { type: 'module' });
        } catch (fehler) {
            Hautarbeit._ausfall(`nicht gestartet: ${fehler.message}`);
            for (const a of [auftrag, ...Hautarbeit._warteschlange.splice(0)]) a.weiter(null);
            return;
        }
        const { id } = auftrag;
        Hautarbeit._laufend = { id, kennung: auftrag.kennung, weiter: auftrag.weiter, arbeiter };
        arbeiter.onmessage = (ereignis) => Hautarbeit._angekommen(id, ereignis.data);
        arbeiter.onerror = (ereignis) => {
            ereignis.preventDefault?.();
            Hautarbeit._beenden(id, null, `Worker: ${ereignis.message || 'abgebrochen'}`);
        };
        arbeiter.postMessage({ typ: 'rechnen', id, ...auftrag.kopien.nachricht }, auftrag.kopien.puffer);
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

    /** Den laufenden Auftrag `id` abschließen: Worker beenden, Versprechen erfüllen, den nächsten starten. Ein fremdes `id` (überholt) tut nichts. */
    static _beenden(id, ergebnis, fehler = null) {
        const laufend = Hautarbeit._laufend;
        if (!laufend || laufend.id !== id) return;
        Hautarbeit._laufend = null;
        laufend.arbeiter.terminate();
        if (fehler) Hautarbeit._ausfall(fehler);
        laufend.weiter(ergebnis);
        if (Hautarbeit.ausgefallen) {
            for (const a of Hautarbeit._warteschlange.splice(0)) a.weiter(null);       // der Hauptfaden rechnet selbst
        } else {
            Hautarbeit._naechster();
        }
    }

    static _ausfall(grund) {
        Hautarbeit.ausgefallen = true;
        Protokoll.warnung('Hautarbeit', `Haut-Maske ohne Worker, der Hauptfaden rechnet selbst: ${grund}`);
        return Promise.resolve(null);
    }
}
