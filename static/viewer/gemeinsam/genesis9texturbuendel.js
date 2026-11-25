import { Pufferabruf } from './pufferabruf.js';
import { Seitenabbruch } from './seitenabbruch.js';
import { Texturweg } from './texturweg.js';

/**
 * Genesis9texturbuendel — die Bilder EINES Netzes in EINER Anfrage holen und auseinandernehmen (24.11.2026, herausgelöst aus `Genesis9texturen`, Server `core/api/g9texturbuendel.py`).
 *
 * GET (19.10.2026), damit der Browser es behält (ETag, ein unverändertes Bündel kommt als 304 aus seinem Speicher — vorher übertrug jedes Laden alles neu, an Mann1 48,6 MB in 5,2 s).
 * Format der Antwort: `[4 Byte Kopflänge][Kopf][Bild 1][Bild 2] …`; was zu groß fürs Bündel war (`art: null` im Kopf), kommt einzeln.
 *
 * `wege`: `bild(pfad, quelle, eintrag)` nimmt ein Bild (Blob oder Ausschnitt `{puffer, ab, bytes, type}`), `einzeln(pfad, eintrag)` holt eines allein. `offen` (Pfad → Eintrag) wird dabei leer.
 */
export class Genesis9texturbuendel {

    static ADRESSE = '/api/character/genesis9-figur/texturbuendel/';
    /** Länger darf die Adresse des Bündels nicht werden (Daphnes Anfragezeile) — sonst POST, das der Browser nicht behält. */
    static ADRESSE_MAX = 12000;
    /** Kasten der Texturen im CacheStorage (`Pufferabruf`). */
    static KASTEN = 'texturen-1';

    /**
     * Kommen die GPU-Blöcke über den Worker (24.11.2026, Edgar: „EdgarNeu laden … muss in 2 s laden“)? Im Hauptfaden las jedes Bündel sein Strom in hunderten Häppchen, zwischen denen die
     * Figur gebaut wurde (22 MB lagen 1,0–1,1 s nach der Antwort vor, aus Chromes Speicher); der verwarf die 11-MB-Blöcke außerdem zwischen zwei Ladungen. Im Worker läuft das Lesen weiter,
     * und der Kasten hält sie. Nur mit GPU-Blöcken (`Texturweg.komprimiert`): die Bilder der anderen Wege sind klein.
     */
    static perWorker() {
        return Texturweg.komprimiert() && typeof caches !== 'undefined' && !Pufferabruf.ausgefallen;
    }

    /** Das Bündel holen und jedes Bild weiterreichen. Scheitert etwas, kommt jedes Bild, das noch fehlt, einzeln (wie vor dem 23.09.2026). */
    static async holen(offen, abfrage, wege) {
        const B = Genesis9texturbuendel;
        try {
            const pfade = [...offen.keys()], wahl = abfrage ? `?${abfrage}` : '';
            const adresse = `${B.ADRESSE}${wahl || '?'}${wahl ? '&' : ''}${pfade.map(p => `p=${encodeURIComponent(p)}`).join('&')}`;
            if (adresse.length <= B.ADRESSE_MAX && B.perWorker()) {
                B._teilen(await Pufferabruf.holen(adresse, null, { kasten: B.KASTEN }), offen, wege);
            } else {
                const signal = Seitenabbruch.signal;           // endet beim Verlassen der Seite (30.10.2026, `Seitenabbruch`)
                const antwort = adresse.length <= B.ADRESSE_MAX ? await fetch(adresse, { signal })
                    : await fetch(B.ADRESSE + wahl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pfade }), signal });
                if (!antwort.ok || !antwort.body) throw new Error(`HTTP ${antwort.status}`);
                await B._lesen(antwort.body.getReader(), offen, wege);
            }
        } catch (fehler) {
            // Was noch fehlt (kein Bündel, Strom abgerissen): einzeln — nach einem Abbruch beim Verlassen erst, wenn die Seite doch bleibt.
            await Seitenabbruch.geblieben();
        }
        for (const [pfad, eintrag] of offen) wege.einzeln(pfad, eintrag);
    }

    /** Ein ganzes Bündel in einem Puffer: jedes Bild als Ausschnitt (ohne Kopie); was zu groß fürs Bündel war, bleibt in `offen`. */
    static _teilen(puffer, offen, wege) {
        const laenge = new DataView(puffer).getUint32(0);
        let ab = 4 + laenge;
        for (const teil of JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge))).teile || []) {
            const eintrag = offen.get(teil.pfad), bytes = teil.art && teil.bytes ? teil.bytes : 0;
            if (eintrag && bytes) {
                offen.delete(teil.pfad);
                wege.bild(teil.pfad, { puffer, ab, bytes, type: teil.art }, eintrag);
            }
            ab += bytes;
        }
    }

    /** Dasselbe aus dem Strom: jedes Bild, sobald SEINE Bytes da sind, nicht erst nach dem ganzen Bündel (19.10.2026). */
    static async _lesen(leser, offen, wege) {
        const stuecke = [];                            // {start, daten}: empfangen, absolute Lage im Strom
        let da = 0, teile = null, naechster = 0, versatz = 0;
        const bereich = (von, bis) => stuecke.filter(s => s.start < bis && s.start + s.daten.length > von)
            .map(s => s.daten.subarray(Math.max(0, von - s.start), Math.min(s.daten.length, bis - s.start)));
        const kopie = (von, bis) => { const aus = new Uint8Array(bis - von); let p = 0; for (const t of bereich(von, bis)) { aus.set(t, p); p += t.length; } return aus; };
        for (;;) {
            const { done, value } = await leser.read();
            if (value?.length) { stuecke.push({ start: da, daten: value }); da += value.length; }
            if (!teile && da >= 4) {
                const laenge = new DataView(kopie(0, 4).buffer).getUint32(0);
                if (da >= 4 + laenge) {
                    teile = JSON.parse(new TextDecoder().decode(kopie(4, 4 + laenge))).teile || [];
                    versatz = 4 + laenge;
                    // zu groß fürs Bündel: gleich einzeln holen (24.11.2026 — vorher erst, wenn die Bilder davor gelesen waren: EdgarNeu sechs 4096er ab 1,2 statt 0,5 s)
                    for (const teil of teile) {
                        const eintrag = teil.art && teil.bytes ? null : offen.get(teil.pfad);
                        if (eintrag) { offen.delete(teil.pfad); wege.einzeln(teil.pfad, eintrag); }
                    }
                }
            }
            while (teile && naechster < teile.length) {
                const teil = teile[naechster], eintrag = offen.get(teil.pfad);
                const groesse = teil.art && teil.bytes ? teil.bytes : 0;
                if (da < versatz + groesse) break;
                naechster += 1;
                if (eintrag) {
                    offen.delete(teil.pfad);
                    wege.bild(teil.pfad, new Blob(bereich(versatz, versatz + groesse), { type: teil.art }), eintrag);
                }
                versatz += groesse;
            }
            while (stuecke.length && stuecke[0].start + stuecke[0].daten.length <= versatz) stuecke.shift();     // Gelesenes freigeben
            if (done) return;
        }
    }
}
