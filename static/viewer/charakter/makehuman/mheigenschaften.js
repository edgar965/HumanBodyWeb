import { fn } from '../../gemeinsam/registrierung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Mhkatalog } from './mhkatalog.js';
import { Mhkopfzeile } from './mhkopfzeile.js';
import { Mhkoerperregler } from './mhkoerperregler.js';
import { Mhhautregler } from './mhhautregler.js';
import { Mhgetragen } from './mhgetragen.js';
import { Mhkatalogliste } from './mhkatalogliste.js';
import { Mhmodellierer } from './mhmodellierer.js';

/**
 * Mheigenschaften — der Eigenschaften-Reiter einer MakeHuman-Figur.
 *
 * Was diese Figur hat: ein Basisnetz mit drei Teilen, MakeHumans „Smooth",
 * eine Haut aus Farbe und Materialwerten, und die Garderobe der 181
 * `.mhclo`-Stücke, die auf genau diesen Körper passen.
 *
 * Dazu MakeHumans 269 Modellierregler (`mhmodellierer.js`) — Geschlecht,
 * Alter, Rasse, Muskeln, Gewicht, Größe, Proportionen und die Detailregler
 * für Kopf, Rumpf, Arme und Beine. Sie kommen aus dem MakeHuman-Upstream
 * unter `A:\3DTools\MakeHuman` (06.09.2026 geholt, siehe dort
 * `HERKUNFT.md`).
 *
 * Der Steckbrief des Servers (Teilenamen, Flächenzahlen) wird EINMAL geholt
 * und an der Figur gemerkt: Beim Umschalten zwischen zwei Figuren würde er
 * sonst jedes Mal neu über die Leitung gehen.
 */
export class Mheigenschaften {

    static BEREICH = 'prop-makehuman-section';
    static _steckbrief = null;

    static async fuellen(inst) {
        const bereich = document.getElementById(Mheigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        Mhkopfzeile.angleichen(inst);
        Mheigenschaften._kleider(inst);
        Mhmodellierer.fuellen(inst,
            document.getElementById('prop-mh-figur-modellieren'));
        Mhhautregler.fuellen(inst, document.getElementById('prop-mh-figur-haut'));
        Mhkoerperregler.fuellen(inst,
            document.getElementById('prop-mh-figur-teile'),
            await Mheigenschaften._teileAngebot());
    }

    static leeren() {
        document.getElementById(Mheigenschaften.BEREICH)
            ?.classList.add('hb-versteckt');
    }

    /** Getragene Stücke und Katalog — beide nach jeder Änderung neu. */
    static _kleider(inst) {
        const auffrischen = () => Mheigenschaften.nachKleiderwechsel(inst);
        Mhgetragen.fuellen(inst,
            document.getElementById('prop-mh-figur-getragen'), auffrischen);
        Mhkatalogliste.fuellen(inst,
            document.getElementById('prop-mh-figur-katalog'), auffrischen);
    }

    /**
     * Nach An- oder Ausziehen: Listen neu — und den KÖRPER neu holen. Welche
     * Haut ausgeblendet wird, steht in den `delete_verts` der getragenen
     * Stücke, ändert sich also mit jedem Wechsel.
     */
    static async nachKleiderwechsel(inst) {
        Mheigenschaften._kleider(inst);
        fn.updateEquippedList?.(inst);
        await Mhkoerperregler.neuAufbauen(inst, 'MakeHuman-Kleidung');
    }

    /** Die drei Netzteile mit ihren Flächenzahlen, einmal je Seite. */
    static async _teileAngebot() {
        if (Mheigenschaften._steckbrief) {
            return Mheigenschaften._steckbrief.teile;
        }
        try {
            const figuren = await Mhkatalog.liste();
            Mheigenschaften._steckbrief = figuren[0] || null;
        } catch (fehler) {
            Protokoll.warnung('MhFigur', 'Steckbrief nicht abrufbar', fehler);
        }
        return Mheigenschaften._steckbrief?.teile || [];
    }
}
