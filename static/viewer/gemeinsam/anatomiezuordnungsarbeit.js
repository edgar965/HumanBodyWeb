import { Anatomiearbeit } from './anatomiearbeit.js';
import { Anatomiemitte } from './anatomiemitte.js';
import { Anatomiezuordnungsteil } from './anatomiezuordnungsteil.js';
import { Protokoll } from './protokoll.js';

/**
 * Anatomiezuordnungsarbeit — die Zuordnung des Anatomie-Stücks (Texel → Stelle der Haut) auf mehreren Workern nebeneinander (19.10.2026, Hauptfaden-Seite).
 *
 * Edgar, 19.10.2026: „fixe alle offenen punkte" — offen war „die erste ultrafeine Hautfarbe dauert einmal etwa 35 s". Gemessen an Damira0 (Mesh3D-AI, ultrafein): die Zuordnung
 * allein 22,2 s auf dem Hauptfaden; mit den exakten Vorfiltern in `Anatomiezuordnung` 13,5 s. Hier teilen sich bis zu `TEILE` Worker die Stück-Dreiecke in Abschnitten
 * (`Anatomiezuordnungsteil`), der Hauptfaden führt sie in Reihenfolge zusammen — dasselbe Ergebnis wie ein Lauf. Derselbe Worker wie für Bild und Füllen
 * (`anatomiearbeiter.js`, Nachricht `zuordnung`), je Abschnitt einer, danach beendet.
 *
 * null (der Aufrufer rechnet wie bisher auf dem Hauptfaden): kein Worker zu haben, ein Abschnitt gescheitert, oder das Stück hängt weit vor der Haut (`Anatomiemitte` braucht
 * alle Dreiecke auf einmal).
 */
export class Anatomiezuordnungsarbeit {

    /** Höchstens so viele Worker (neben Haut-Maske, Bildern, Server); dazu nie mehr als Kerne − 2. */
    static TEILE = 4;
    /** Unter so vielen Stück-Dreiecken je Abschnitt lohnt kein weiterer Worker. */
    static MINDESTENS = 512;
    static _zaehler = 0;

    static async rechnen(stueck, haut, breite, hoehe) {
        if (!Anatomiearbeit.verfuegbar()) return null;
        const dreiecke = Math.floor(stueck.index.length / 3);
        const kerne = (typeof navigator !== 'undefined' && navigator.hardwareConcurrency) || 4;
        const n = Math.max(1, Math.min(Anatomiezuordnungsarbeit.TEILE, kerne - 2, Math.floor(dreiecke / Anatomiezuordnungsarbeit.MINDESTENS)));
        const t0 = performance.now();
        const ha = Anatomiezuordnungsteil.knapp(haut);
        const st = { pos: stueck.pos.slice(), uv: stueck.uv.slice(), index: stueck.index.slice(), normal: stueck.normal ? stueck.normal.slice() : null };
        const grenzen = Array.from({ length: n + 1 }, (_, i) => Math.round(i * dreiecke / n));
        const teile = await Promise.all(grenzen.slice(0, n).map((von, i) => Anatomiezuordnungsarbeit._teil(st, ha, breite, hoehe, von, grenzen[i + 1])));
        if (teile.some(t => !t)) return null;
        const fern = teile.reduce((s, t) => s + t.fern, 0);
        if (fern > Anatomiemitte.ANTEIL * dreiecke) return null;
        const zu = Anatomiezuordnungsteil.zusammen(teile, breite, hoehe);
        Protokoll.debug('Anatomiezuordnung', `${zu.anzahl} Texel in ${n} Workern, ${Math.round(performance.now() - t0)} ms`);
        return zu;
    }

    /** Ein Abschnitt in einem eigenen Worker: das Ergebnis von `Anatomiezuordnungsteil.rechnen` — oder null (Fehler; der Aufrufer rechnet selbst). */
    static _teil(st, ha, breite, hoehe, von, bis) {
        let arbeiter;
        try {
            arbeiter = new Worker(Anatomiearbeit.pfad(), { type: 'module' });
        } catch (fehler) {
            Protokoll.warnung('Anatomiezuordnung', `Worker nicht gestartet: ${fehler.message}`);
            return Promise.resolve(null);
        }
        const id = ++Anatomiezuordnungsarbeit._zaehler;
        return new Promise((weiter) => {
            const ende = (ergebnis, meldung = null) => {
                arbeiter.terminate();
                if (meldung) Protokoll.warnung('Anatomiezuordnung', `Abschnitt ${von}–${bis}: ${meldung}`);
                weiter(ergebnis);
            };
            arbeiter.onmessage = (ereignis) => {
                const d = ereignis.data;
                if (d?.id !== id) return;
                if (d.typ === 'fertig') ende(d.ergebnis); else ende(null, d.meldung || 'Fehler');
            };
            arbeiter.onerror = (ereignis) => { ereignis.preventDefault?.(); ende(null, ereignis.message || 'abgebrochen'); };
            // Kopien: jeder Worker bekommt seine eigenen (eine Übertragung nähme sie den übrigen weg).
            const kopie = (f) => (f ? f.slice() : f);
            arbeiter.postMessage({ typ: 'zuordnung', id, breite, hoehe, von, bis,
                                   st: { pos: kopie(st.pos), uv: kopie(st.uv), index: kopie(st.index), normal: kopie(st.normal) }, ha: { pos: kopie(ha.pos), ecken: kopie(ha.ecken) } });
        });
    }
}
