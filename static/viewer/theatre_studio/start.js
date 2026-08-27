import theatreStudio from '@theatre/studio';
import theatreCore from '@theatre/core';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Probeszene } from './probeszene.js';
import { Studiozustand } from './studiozustand.js';
import { Theatreobjekte } from './theatreobjekte.js';

/**
 * Einstiegspunkt der Theatre-Studio-Probeseite.
 *
 * UMBAU 27.08.2026: Der ganze Ablauf stand als 140-zeiliges Inline-Modul in
 * `theatre_studio.html`, mit einem Dutzend `console.log` statt `Protokoll`.
 *
 * ZWEI FEHLER, DIE DABEI ANS LICHT KAMEN
 * ======================================
 * 1. Die Importkarte zeigte auf `dist/core.esm.js` und `dist/studio.esm.js` —
 *    Dateinamen aus Theatre 0.4/0.5. In 0.7 gibt es sie nicht, jsDelivr
 *    antwortete mit 404, und die Seite blieb auf „Initializing Studio…"
 *    stehen. Siehe `_importmap.html`.
 * 2. Theatre 0.7 ist CommonJS. Das jsDelivr-Bündel (`/+esm`) hat deshalb NUR
 *    einen Standardexport — `import { getProject } from '@theatre/core'`
 *    wirft. Die Namen kommen aus dem Standardobjekt.
 */

/**
 * Beide Buendel kommen als CommonJS ueber `/+esm` und haben deshalb nur einen
 * Standardexport. Was DARIN steckt, ist je Paket verschieden:
 *
 *     @theatre/core     module.exports = __toCommonJS(...)  -> die Namen direkt
 *     @theatre/studio   module.exports = Rq(...)            -> noch ein `default`
 *
 * Deshalb einmal auspacken, statt auf eine der beiden Formen zu wetten.
 */
const auspacken = (buendel) => buendel?.default ?? buendel;
const studio = auspacken(theatreStudio);
const { getProject } = auspacken(theatreCore);

Studiozustand.setzen('Studio wird gestartet …', Studiozustand.LAEUFT);

try {
    studio.initialize();
    window.studio = studio;
    Studiozustand.setzen('Studio gestartet', Studiozustand.GUT);
} catch (fehler) {
    Studiozustand.setzen('Fehlgeschlagen: ' + fehler.message,
                         Studiozustand.FEHLER);
    Protokoll.fehler('Theatre-Studio', 'studio.initialize() gescheitert:',
                     fehler);
}

const projekt = getProject('Studio Debug');
const blatt = projekt.sheet('Main');
window.project = projekt;
window.sheet = blatt;
Studiozustand.benennen('Studio Debug', 'Main', Theatreobjekte.ANZAHL);

const szene = new Probeszene(document.getElementById('studio-canvas'));
new Theatreobjekte(blatt, szene);

/** Theatres Bedienoberfläche hängt sich selbst in den Seitenrumpf. */
class Oberflaechenprobe {
    /** So lange bekommt Theatre Zeit, seine Oberfläche aufzubauen. */
    static FRIST_MS = 2000;
    /** Kennung des Wurzelelements, das Theatre anlegt. */
    static WURZEL = 'theatrejs-studio-root';

    static spaeterPruefen() {
        setTimeout(() => Oberflaechenprobe._pruefen(),
                   Oberflaechenprobe.FRIST_MS);
    }

    /**
     * Theatre baut seine Oberfläche in einen SCHATTEN-DOM — `children` bleibt
     * deshalb leer, auch wenn alles da ist. Die alte Fassung dieser Seite
     * zählte `children` und meldete darum dauerhaft „Studio UI not rendering",
     * obwohl der Schattenwurzel zwei Kinder und 6,8 kB Markup hingen
     * (nachgemessen 27.08.2026).
     */
    static _inhalt(wurzel) {
        if (!wurzel) return 0;
        return (wurzel.shadowRoot?.children.length ?? 0)
               + wurzel.children.length;
    }

    static _pruefen() {
        const wurzel = document.getElementById(Oberflaechenprobe.WURZEL);
        if (Oberflaechenprobe._inhalt(wurzel) > 0) {
            Studiozustand.setzen('Studio-Oberfläche aktiv',
                                 Studiozustand.GUT);
            return;
        }
        Studiozustand.setzen('Studio-Oberfläche erscheint nicht',
                             Studiozustand.WARNUNG);
        Protokoll.warnung('Theatre-Studio',
                          'Wurzelelement leer — versuche studio.ui.restore()');
        window.studio?.ui?.restore?.();
    }
}

Oberflaechenprobe.spaeterPruefen();
