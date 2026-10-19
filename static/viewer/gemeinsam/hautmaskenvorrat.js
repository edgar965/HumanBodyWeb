import { Anatomiehash } from './anatomiehash.js';
import { Feldpaket } from './feldpaket.js';
import { Genesis9vorrat } from './genesis9vorrat.js';
import { Hautarbeit } from './hautarbeit.js';
import { Netzstufenstand } from './netzstufenstand.js';
import { Protokoll } from './protokoll.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Hautmaskenvorrat — die Haut-Maske (`Hautrechnung.rechnen`) dauerhaft auf dem Server (19.10.2026, `core/dienste/g9hautmasken.py`).
 *
 * Edgar, 19.10.2026: „hautmaske ablegen, so dass alles schnell beim laden ist". Die Maske rechnete bei jedem Laden neu — am feinen Körper 2,8 s im Worker
 * (Leerlauf), 7–14 s bei belasteter CPU, auf ultrafein länger —, und so lange stand „Haut unter der Kleidung" in der Anzeige rechts unten. Sie hängt nur an
 * der Eingabe und am Code. Der Schlüssel ist ein Hash (`Anatomiehash.feld`, FNV über die Bits, zwei Startwerte) über
 *
 *   die Punkte des Körpers IN RUHE (`Hautverdeckung.lage`: ohne die Gelenkkorrekturen einer laufenden Bewegung), seinen vollen Index, je Stück Punkte (in Ruhe),
 *   Dreiecke, Schlüssel und Einstellungen (`tiefe`, `starr`, `nahe`, `ersatz`) in ihrer Reihenfolge;
 *
 * der Ordner ist die Fassung des Codes der Rechnung (Meta `hautmaskenfassung`, `{% jsfassung %}`: Inhalts-Hash über `hautarbeiter.js` und alles, was es
 * importiert). Ohne die Meta (eine Seite ohne sie) wird nichts gesucht und nichts abgelegt.
 *
 * Abgelegt wird, was der Worker liefert (gepackt mit `Feldpaket`, gzip), außer den Normalen, wenn kein Ersatzstück dabei ist — `Hautverdeckung.anwenden` liest sie
 * nur dann. Die Einstellung Einstellungen → Charakter (`Genesis9vorrat.wahl`) gilt wie für die Netzantworten: „Aus" nichts, sonst die Stufen bis zur gewählten.
 * Ein Fehler beim Holen oder Ablegen steht im Protokoll; die Maske wird dann wie bisher gerechnet.
 */
export class Hautmaskenvorrat {

    static ADRESSE = '/api/character/genesis9-figur/hautmasken/';
    /** Ergebnis eines überholten Auftrags (wie `Hautarbeit.VERALTET`). */
    static VERALTET = Hautarbeit.VERALTET;

    /** Die Fassung des Codes, mit dem diese Seite geladen wurde — leer ohne Meta. */
    static fassung() {
        if (typeof document === 'undefined') return '';
        return document.querySelector('meta[name="hautmaskenfassung"]')?.content || '';
    }

    /** Wird die Maske einer Figur auf `stufe` (grob | fein | ultrafein) abgelegt und gesucht? */
    static an(stufe) {
        const wahl = Genesis9vorrat.wahl, stufen = Genesis9vorrat.STUFEN;
        const i = stufen.indexOf(stufe);
        return wahl !== 'aus' && i >= 0 && i <= stufen.indexOf(wahl);
    }

    /** Der Schlüssel der Eingabe (wie `Hautarbeit.rechnen` sie bekommt). */
    static schluessel(pos, index, stoffe) {
        const felder = [pos, index];
        const einstellungen = [];
        for (const s of stoffe) {
            felder.push(s.punkte, s.dreiecke);
            einstellungen.push([s.schluessel, s.tiefe ?? null, !!s.starr, s.nahe ?? null, !!s.ersatz]);
        }
        const text = JSON.stringify(einstellungen);
        felder.push(Uint32Array.from(text, (c) => c.codePointAt(0)));
        return [Anatomiehash.SEED_A, Anatomiehash.SEED_B]
            .map((start) => felder.reduce((h, f) => Anatomiehash.feld(h, f), start).toString(36).padStart(7, '0')).join('');
    }

    /**
     * Wie `Hautarbeit.rechnen`, aber zuerst im Vorrat nachsehen und ein frisch gerechnetes Ergebnis ablegen.
     * @returns das Ergebnis (aus dem Vorrat mit `ausVorrat: true`), `VERALTET` oder null (kein Worker — dann rechnet `Hautverdeckung` selbst)
     */
    static async rechnen(inst, pos, index, stoffe) {
        const fassung = Hautmaskenvorrat.fassung(), stufe = Netzstufenstand.stufeVon(inst);
        const schluessel = fassung && Hautmaskenvorrat.an(stufe) ? Hautmaskenvorrat.schluessel(pos, index, stoffe) : null;
        if (schluessel) {
            const abgelegt = await Hautmaskenvorrat.holen(fassung, schluessel, pos.length / 3, stoffe.length);
            if (abgelegt) return abgelegt;
        }
        const ergebnis = await Hautarbeit.rechnen(pos, index, stoffe, inst?.id ?? '');
        if (schluessel && ergebnis && ergebnis !== Hautarbeit.VERALTET) Hautmaskenvorrat.ablegen(fassung, schluessel, stufe, ergebnis, stoffe);
        return ergebnis;
    }

    /** Die abgelegte Maske — oder null (nicht da, passt nicht, Fehler). `punkte`/`stuecke`: zur Probe, ob sie zu dieser Eingabe gehört. */
    static async holen(fassung, schluessel, punkte, stuecke) {
        try {
            const antwort = await fetch(`${Hautmaskenvorrat.ADRESSE}${fassung}/${schluessel}/`);
            if (!antwort.ok || !antwort.body) return null;
            const ergebnis = await Feldpaket.ungzip(antwort.body);
            if (ergebnis?.maske?.length !== punkte || ergebnis.randabstaende?.length !== stuecke) {
                Protokoll.warnung('Hautmaskenvorrat', `Abgelegte Maske ${schluessel} passt nicht zur Figur — sie wird neu gerechnet`);
                return null;
            }
            ergebnis.ausVorrat = true;
            return ergebnis;
        } catch (fehler) {
            Protokoll.warnung('Hautmaskenvorrat', `Maske nicht geholt: ${fehler.message}`);
            return null;
        }
    }

    /**
     * Ein frisch gerechnetes Ergebnis ablegen. Gepackt wird SOFORT (eine Kopie): `Hautverdeckung.anwenden` schreibt danach in die Felder (`weg`, `einzug`).
     * Hochgeladen wird im Hintergrund; das Versprechen meldet, ob der Server es angenommen hat.
     */
    static ablegen(fassung, schluessel, stufe, ergebnis, stoffe) {
        const roh = { ...ergebnis, normalen: stoffe.some((s) => s.ersatz) ? ergebnis.normalen : null };
        let paket;
        try {
            paket = Feldpaket.packen(roh);
        } catch (fehler) {
            Protokoll.warnung('Hautmaskenvorrat', `Maske nicht gepackt: ${fehler.message}`);
            return Promise.resolve(false);
        }
        return Hautmaskenvorrat._senden(fassung, schluessel, stufe, paket);
    }

    static async _senden(fassung, schluessel, stufe, paket) {
        try {
            const strom = new Blob([paket]).stream().pipeThrough(new CompressionStream('gzip'));
            const formular = new FormData();
            formular.append('maske', await new Response(strom).blob(), 'maske.bin');
            const antwort = await fetch(`${Hautmaskenvorrat.ADRESSE}${fassung}/${schluessel}/?stufe=${encodeURIComponent(stufe)}`,
                                        { method: 'POST', body: formular, headers: Serverabruf._csrfKopf() });
            return antwort.ok;
        } catch (fehler) {
            Protokoll.warnung('Hautmaskenvorrat', `Maske nicht abgelegt: ${fehler.message}`);
            return false;
        }
    }
}
