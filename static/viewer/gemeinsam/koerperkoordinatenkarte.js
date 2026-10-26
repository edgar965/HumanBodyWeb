import { Protokoll } from './protokoll.js';

/**
 * Koerperkoordinatenkarte — die Karte „wo auf dem Körper liegt dieser Texel“ für die eigenen Stücke (Stufe K2a, 25.10.2026), einmal je Seite geholt.
 *
 * Der Server rechnet sie im Speicher (`G9koerperkoordinaten`, Endpunkt `G9koerperkoordinatenapi`) und schickt sie mit ETag und `no-cache`: der Browser fragt bei jedem
 * Laden nach und bekommt 304, solange der Serverprozess dieselbe Karte hält. Aufbau des Bilds im Kopf von `g9koerperkoordinaten.py`; die Kopfzeilen sagen, welche
 * Kachel in welcher Zeile steht (`X-Kacheln`), die Seite je Kachel, die Stufe der Kettennummer, den Bereich der Höhe und die Längen der Grundfigur.
 *
 * Dekodiert wird OHNE Vormultiplikation und Farbumrechnung (`createImageBitmap`) und auf der CPU gelesen (`lesen`, Regel wie `texelFetch`: Texel, kein Filter) —
 * ein gefilterter oder umgerechneter Wert wäre eine andere Kette bzw. ein falscher 16-Bit-Anteil. Die Werte je Punkt gehen als Attribut an den Shader
 * (`Koerperkoordinatenpunkte`), nicht als Textur: so lassen sich die Doppel an UV-Nähten verschweißen.
 */
export class Koerperkoordinatenkarte {

    static ADRESSE = '/api/character/genesis9-figur/koerperkoordinaten.png';
    static _versprechen = null;

    /** → `{pixel, breite, zeile: Map(kachel → Zeile), seite, stufe, hoehe, anteil: [unten, oben], laengen: [Rumpf, Arm, Bein], ms}`; ein Fehlschlag wird beim
     *  nächsten Mal neu versucht. */
    static holen() {
        if (!Koerperkoordinatenkarte._versprechen) {
            Koerperkoordinatenkarte._versprechen = Koerperkoordinatenkarte._laden().catch((fehler) => {
                Koerperkoordinatenkarte._versprechen = null;
                throw fehler;
            });
        }
        return Koerperkoordinatenkarte._versprechen;
    }

    static zahlen(text) {
        return String(text || '').split(',').filter(t => t.trim() !== '').map(Number);
    }

    static async _laden() {
        const t0 = performance.now();
        const antwort = await fetch(Koerperkoordinatenkarte.ADRESSE, { cache: 'no-cache' });
        if (!antwort.ok) {
            let grund = `HTTP ${antwort.status}`;
            try { grund = (await antwort.json()).fehler || grund; } catch (fehler) { /* stumm gewollt: die Antwort war kein JSON, der Status reicht */ }
            throw new Error(`Körperkoordinaten nicht geladen: ${grund}`);
        }
        const k = name => antwort.headers.get(name);
        const kacheln = Koerperkoordinatenkarte.zahlen(k('X-Kacheln'));
        const seite = Number(k('X-Seite')), stufe = Number(k('X-Stufe'));
        const hoehe = Koerperkoordinatenkarte.zahlen(k('X-Hoehe')), laengen = Koerperkoordinatenkarte.zahlen(k('X-Laengen'));
        const anteil = Koerperkoordinatenkarte.zahlen(k('X-Anteil'));
        if (!kacheln.length || !seite || !stufe || hoehe.length !== 2 || laengen.length !== 3 || anteil.length !== 2) {
            throw new Error('Körperkoordinaten: Kopfzeilen fehlen (X-Kacheln, X-Seite, X-Stufe, X-Hoehe, X-Anteil, X-Laengen)');
        }
        const bild = await createImageBitmap(await antwort.blob(), { premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
        if (bild.width !== 2 * seite || bild.height !== kacheln.length * seite) {
            throw new Error(`Körperkoordinaten: Bild ${bild.width} × ${bild.height}, erwartet ${2 * seite} × ${kacheln.length * seite}`);
        }
        // Bytes lesen: Alpha ist überall 255, also keine Vormultiplikation; das PNG trägt kein Farbprofil.
        const leinwand = new OffscreenCanvas(bild.width, bild.height);
        const kontext = leinwand.getContext('2d', { willReadFrequently: true });
        kontext.drawImage(bild, 0, 0);
        const pixel = kontext.getImageData(0, 0, bild.width, bild.height).data;
        bild.close();
        const ms = Math.round(performance.now() - t0);
        Protokoll.debug('Körperkoordinaten', `Karte ${2 * seite} × ${kacheln.length * seite}, Kacheln ${kacheln.join(', ')} (${ms} ms)`);
        return { pixel, breite: 2 * seite, zeile: new Map(kacheln.map((kachel, i) => [kachel, i])), seite, stufe, hoehe, anteil, laengen, ms };
    }

    /** Ein Texel auf der CPU, wie der Shader ihn liest → `[Kette, Anteil, Höhe, Winkel]` (Winkel 0…1, 0 = vorn); `zeile` die Kachelzeile, `u`/`v` die UV. */
    static lesen(karte, zeile, u, v) {
        const s = karte.seite;
        const x = Math.min(Math.floor(Math.min(Math.max(u, 0), 1) * s), s - 1);
        const y = Math.min(Math.floor((1 - Math.min(Math.max(v, 0), 1)) * s), s - 1) + zeile * s;
        const a = 4 * (y * karte.breite + x), b = a + 4 * s, p = karte.pixel;
        return [Math.round(p[a] / karte.stufe),
            karte.anteil[0] + (p[a + 1] * 256 + p[a + 2]) / 65535 * (karte.anteil[1] - karte.anteil[0]),
            karte.hoehe[0] + (p[b] * 256 + p[b + 1]) / 65535 * (karte.hoehe[1] - karte.hoehe[0]),
            p[b + 2] / 256];
    }
}
