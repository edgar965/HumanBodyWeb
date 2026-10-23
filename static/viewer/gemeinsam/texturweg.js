import { Genesis9texturbasis } from './genesis9texturbasis.js';

/**
 * Texturweg — wie die Bilder der Genesis-Figuren auf die Grafikkarte kommen (19.10.2026).
 *
 * Edgar, nach der Untersuchung „ein Bildersatz kostet 1,7–2,8 s, weil 15 von 22 Bildern 4096² sind“: „mach alle 3, per Option einstellbar, default: A“
 * (Einstellungen → Mesh3D-AI, `Mesh3daitexturwahl`). Die SEITE wählt im Kopf — `<meta name="texturweg" content="klein" data-kante="1024">` —, wie bei `Schnellanzeige`;
 * ohne die Zeile (Charakter, Studio …) bleibt alles wie bisher.
 *
 *   klein        A  Adresse mit `kante=1024`: der Server liefert verkleinerte Kopien (`G9texturkopie`)
 *   verteilt     B  volle Bilder; jedes geht in einer eigenen Aufgabe des Browsers auf die Karte (`einreihen` → `renderer.initTexture`), dazwischen kommt die Seite zum Zug
 *   komprimiert  C  Adresse mit `format=bc`: S3TC-Block mit Mip-Stufen (`G9texturblock`, `Genesis9texturblock`); ohne S3TC im Browser fällt `anmelden` auf A zurück
 *   uastc           Adresse mit `format=uastc` (und `raum=lin` für Bilder ohne Farbe): UASTC/KTX2 (`G9texturbasis`, `Genesis9texturbasis`), bis der Server es kodiert hat
 *                   der Block von C — nur /Charakter/ (Einstellungen → Charakter, `Szenentexturwahl`, 19.10.2026: „mach das“ nach dem KTX2-Versuch)
 * `data-rueckfall` sagt, was ohne S3TC gilt: fehlt es, 'klein' (Mesh3D-AI); /Charakter/ schreibt "" (volle Bilder wie bisher — verkleinert taugt dort nicht).
 */
export class Texturweg {
    static META = 'texturweg';
    static _meta = typeof document !== 'undefined' ? document.querySelector?.(`meta[name="${Texturweg.META}"]`) : null;
    /** '' (wie bisher), 'klein', 'verteilt', 'komprimiert' oder 'uastc' — gelesen beim Laden des Moduls. */
    static art = Texturweg._meta?.content || '';
    static kante = Number(Texturweg._meta?.dataset?.kante) || 1024;
    static rueckfall = Texturweg._meta?.dataset?.rueckfall ?? 'klein';
    /** Weg B: `(textur) => void` lädt EIN Bild auf die Karte — gesetzt von `anmelden`. */
    static hochladen = null;
    static _reihe = [];
    static _laeuft = false;

    /** Was an die Adresse eines Bibliotheksbildes gehört (`Genesis9texturen.adresse`, Bündel): '' oder `kante=…`, `format=bc`, `format=uastc[&raum=lin]`.
     *  `srgb`: Farbbild (Albedo) — nur bei UASTC Teil der Adresse, der Server kodiert Farbe und Daten verschieden. */
    static abfrage(srgb = true) {
        if (Texturweg.art === 'klein') return `kante=${Texturweg.kante}`;
        if (Texturweg.art === 'komprimiert') return 'format=bc';
        if (Texturweg.art === 'uastc') return srgb ? 'format=uastc' : 'format=uastc&raum=lin';
        return '';
    }

    /** Kommen die Bilder als komprimierte Textur mit Mip-Stufen (Block oder UASTC)? Dann ist die leere Textur eine `CompressedTexture`. */
    static komprimiert() {
        return Texturweg.art === 'komprimiert' || Texturweg.art === 'uastc';
    }

    /**
     * Die Seite meldet ihren Renderer, bevor die erste Figur lädt: Weg B lädt über ihn hoch; Weg C braucht S3TC (sRGB für die Farbbilder) — fehlt es, gilt
     * `rueckfall`, mit Meldung in der Konsole (sonst stünden die Figuren schwarz da: three.js lässt ein unbekanntes Format mit einer Warnung leer). UASTC braucht S3TC
     * ebenso (bis zur fertigen Fassung kommt der Block) und richtet den KTX2-Lader ein.
     */
    static anmelden(renderer) {
        if (Texturweg.komprimiert() && !(renderer.extensions.has('WEBGL_compressed_texture_s3tc') && renderer.extensions.has('WEBGL_compressed_texture_s3tc_srgb'))) {
            console.warn(`Texturweg: S3TC fehlt in diesem Browser — Bilder kommen ${Texturweg.rueckfall === 'klein' ? 'verkleinert (Weg A)' : 'in voller Größe wie bisher'} statt komprimiert.`);
            Texturweg.art = Texturweg.rueckfall;
        }
        if (Texturweg.art === 'verteilt') Texturweg.hochladen = textur => renderer.initTexture(textur);
        if (Texturweg.art === 'uastc') {
            Genesis9texturbasis.einrichten(renderer).catch(fehler => console.warn(`Texturweg: KTX2-Lader nicht geladen (${fehler.message}) — die Bilder kommen als S3TC-Block`));
        }
    }

    /**
     * Ein angekommenes Bild einsetzen: `setzen()` hängt es an die Textur. Weg B reiht ein — je Aufgabe des Browsers EIN Bild, gleich danach auf der Karte; das nächste Zeichnen
     * findet nichts mehr hochzuladen. Sonst sofort (die Karte lädt beim nächsten Zeichnen, wie bisher). Das Versprechen löst sich, wenn das Bild an der Textur hängt.
     */
    static einreihen(textur, setzen) {
        if (Texturweg.art !== 'verteilt' || !Texturweg.hochladen) {
            setzen();
            return Promise.resolve();
        }
        return new Promise(fertig => {
            Texturweg._reihe.push({ textur, setzen, fertig });
            if (!Texturweg._laeuft) Texturweg._abarbeiten();
        });
    }

    static async _abarbeiten() {
        Texturweg._laeuft = true;
        while (Texturweg._reihe.length) {
            await Texturweg._naechsteAufgabe();
            const { textur, setzen, fertig } = Texturweg._reihe.shift();
            setzen();
            try { Texturweg.hochladen(textur); } catch (fehler) { console.warn(`Texturweg: Hochladen gescheitert (${fehler.message}) — das nächste Zeichnen lädt es`); }
            fertig();
        }
        Texturweg._laeuft = false;
    }

    /** Eine neue Aufgabe des Browsers — über einen MessageChannel, nicht `setTimeout`: ein verdeckter Tab drosselt Zeitgeber auf 1 s und mehr. */
    static _naechsteAufgabe() {
        return new Promise(weiter => {
            const kanal = new MessageChannel();
            kanal.port1.onmessage = () => { kanal.port1.close(); weiter(); };
            kanal.port2.postMessage(0);
        });
    }
}
