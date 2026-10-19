import { Serverabruf } from './serverabruf.js';
import { Netzpaket } from './netzpaket.js';
import { Protokoll } from './protokoll.js';
import { Nutzerruhe } from './nutzerruhe.js';
import { Netzstufenstand } from './netzstufenstand.js';

/**
 * Genesis9vorrat — die Anzeigen einer Genesis-Figur dauerhaft auf dem Server ablegen lassen (19.10.2026).
 *
 * Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden" und
 * „mach die Speicherung einstellbar, bei Einstellungen - Charakter. Default: alles bis ultrafein". Der Server legt eine Netzantwort dauerhaft ab — über
 * Code-Änderungen hinweg (`core/dienste/g9modellvorrat.py`) —, wenn die Anfrage eine ANZEIGE ist (Kopf `X-G9-Vorrat`). Hier steht, welche das sind:
 *
 * 1. Alles, was während eines Ladevorgangs angefragt wird (`laden`: `Genesis9aufbau.progressiv`, Stufenwechsel, Nachladen der Stufe) — die Figur, wie sie
 *    geladen oder gespeichert wurde. Ein Reglerzug ist kein Ladevorgang: Zwischenstellungen kämen sonst alle auf die Platte.
 * 2. Danach jede Anfrage mit derselben Stellung wie beim Laden (Strg+Alt+H zurück auf eine Stufe, ein zweiter Stufenwechsel).
 * 3. Nach „Modell speichern" und nach dem Laden eines gespeicherten Modells im Charakter füllt `fuellen` die übrigen Stufen bis zur Einstellung VORAB
 *    (Kopf `X-G9-Vorrat-Nur`: der Server rechnet und legt ab, schickt aber nichts) — nach Ruhe, eine Anfrage nach der anderen.
 *
 * Die Stellung ist Adresse ohne Stufe plus Rumpf (wie `Genesis9antwortspeicher`): Sie bestimmt die Antwort, nicht die Stufe.
 */
export class Genesis9vorrat {

    static KOPF = 'X-G9-Vorrat';
    static KOPF_NUR = 'X-G9-Vorrat-Nur';
    static STUFEN = ['grob', 'fein', 'ultrafein'];
    /** Die Stufe in der Adresse der Vorab-Anfrage: grob = Käfig, fein = die Einstellung (auch bei gesetztem Keks), ultrafein = wie der Keks von Strg+Alt+H. */
    static ADRESSSTUFE = { grob: '0', fein: 'einstellung', ultrafein: '3' };

    /** `ui_prefs.netzvorrat` (Einstellungen → Charakter): aus | grob | fein | ultrafein. */
    static wahl = 'ultrafein';

    /** Für den Körper: der Rumpf, wie ihn `Genesis9materialabruf` jetzt bauen würde (eingetragen dort — ein Import hierher wäre ein Ring). */
    static koerperNutzlast = null;

    static einstellen(wahl) {
        Genesis9vorrat.wahl = Genesis9vorrat.STUFEN.includes(wahl) || wahl === 'aus' ? wahl : 'ultrafein';
    }

    static stellung(adresse, nutzlast) {
        return JSON.stringify([adresse.replace(/[?&]stufen=[^&]*/, ''), nutzlast]);
    }

    /** Während `arbeit` läuft, sind alle Anfragen der Figur Anzeigen (siehe oben, 1.). */
    static async laden(inst, arbeit) {
        if (!inst) return arbeit();
        inst._vorratLaedt = (inst._vorratLaedt || 0) + 1;
        try {
            return await arbeit();
        } finally {
            inst._vorratLaedt -= 1;
        }
    }

    /**
     * Der Kopf für eine Netzanfrage der Figur (`teil`: `koerper` oder `kleid:<Kennung>`) — mit `X-G9-Vorrat`, wenn sie eine Anzeige ist. Merkt jede Anfrage
     * (`_vorratAnfragen`) und die Anzeigen (`_vorratAnzeige`) für `fuellen`.
     */
    static kopf(inst, teil, adresse, nutzlast) {
        if (!inst || Genesis9vorrat.wahl === 'aus') return {};
        const stellung = Genesis9vorrat.stellung(adresse, nutzlast);
        (inst._vorratAnfragen ??= new Map()).set(teil, { adresse, nutzlast, stellung });
        const anzeigen = inst._vorratAnzeige ??= new Map();
        if (inst._vorratLaedt > 0) anzeigen.set(teil, { adresse, nutzlast, stellung });
        return anzeigen.get(teil)?.stellung === stellung ? { [Genesis9vorrat.KOPF]: '1' } : {};
    }

    /** Der Stand JETZT gilt als Anzeige (nach „Modell speichern"): die letzten Anfragen je Teil, der Körper mit dem Rumpf von jetzt. */
    static festhalten(inst) {
        const anzeigen = inst._vorratAnzeige = new Map();
        for (const [teil, anfrage] of inst._vorratAnfragen || []) {
            if (teil.startsWith('kleid:') && !inst.kleidung?.[teil.slice('kleid:'.length)]) continue;   // ausgezogen
            let { adresse, nutzlast } = anfrage;
            if (teil === 'koerper' && Genesis9vorrat.koerperNutzlast) nutzlast = Genesis9vorrat.koerperNutzlast(inst);
            anzeigen.set(teil, { adresse, nutzlast, stellung: Genesis9vorrat.stellung(adresse, nutzlast) });
        }
    }

    /**
     * Alle Stufen bis zur Einstellung für die Anzeigen der Figur auf dem Server ablegen lassen. Wartet auf das sichtbare Laden (`inst.fein`) und auf Ruhe;
     * ein zweiter Aufruf während eines laufenden tut nichts. Ein Fehler steht im Protokoll und hält die übrigen Anfragen nicht an.
     */
    static async fuellen(inst) {
        if (!inst || Genesis9vorrat.wahl === 'aus' || inst._vorratFuellt) return 0;
        inst._vorratFuellt = true;
        const t0 = performance.now();
        let n = 0;
        try {
            await Promise.resolve(inst.fein).catch(() => {});
            const stufen = Genesis9vorrat.STUFEN.slice(0, Genesis9vorrat.STUFEN.indexOf(Genesis9vorrat.wahl) + 1);
            for (const stufe of stufen) {
                for (const [teil, anfrage] of [...(inst._vorratAnzeige || [])]) {
                    if (Netzstufenstand.entsorgt(inst)) return n;
                    await Nutzerruhe.abwarten(() => Netzstufenstand.entsorgt(inst));
                    if (await Genesis9vorrat._ablegen(anfrage, stufe, teil)) n += 1;
                }
            }
        } finally {
            inst._vorratFuellt = false;
        }
        Protokoll.info('Genesis9vorrat', `${inst.presetName || inst.id}: ${n} Anzeigen vorab abgelegt (bis ${Genesis9vorrat.wahl}, ${Math.round(performance.now() - t0)} ms)`);
        return n;
    }

    /** Stufe + Stellung, die in diesem Seitenleben schon vorab abgelegt sind: dieselbe Figur in mehreren Feldern (Mesh3D-AI) fragt nur einmal. */
    static _abgelegt = new Set();

    static async _ablegen({ adresse, nutzlast, stellung }, stufe, teil) {
        const ohne = adresse.replace(/[?&]stufen=[^&]*/, '');
        const ziel = `${ohne}${ohne.includes('?') ? '&' : '?'}stufen=${Genesis9vorrat.ADRESSSTUFE[stufe]}`;
        const merke = `${stufe}|${stellung}`;
        if (Genesis9vorrat._abgelegt.has(merke)) return false;
        Genesis9vorrat._abgelegt.add(merke);
        try {
            const antwort = await fetch(ziel, {
                method: 'POST', body: JSON.stringify(nutzlast),
                headers: { 'Content-Type': 'application/json', Accept: `${Netzpaket.ANNAHME}, application/json`, ...Serverabruf._csrfKopf(),
                           [Genesis9vorrat.KOPF]: '1', [Genesis9vorrat.KOPF_NUR]: '1' },
            });
            if (antwort.ok) return true;
            Protokoll.warnung('Genesis9vorrat', `${teil} ${stufe}: HTTP ${antwort.status}`);
        } catch (fehler) {
            Protokoll.warnung('Genesis9vorrat', `${teil} ${stufe}: ${fehler.message}`);
        }
        Genesis9vorrat._abgelegt.delete(merke);                      // gescheitert: ein späterer Lauf darf es noch einmal versuchen
        return false;
    }
}
