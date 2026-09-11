import { Figurwahldialog }
    from '../../../static/viewer/gemeinsam/figurwahldialog.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';
import { Sequenzspuren } from '../laden/sequenzspuren.js';
import { Figurpanel } from './panels/figurpanel.js';

/**
 * Figurtausch — Rechtsklick auf die Figur im Eigenschaften-Feld: Modell
 * austauschen.
 *
 * ANLASS (Edgar, 11.09.2026): „im rechten Bereich möchte ich bei einer
 * ausgewählten Person bei dem Modell einen Rechtsklick, mit dem ich das
 * Modell austauschen kann. Es soll ein Popup kommen, wo ich ein anderes
 * Modell (das gespeichert ist) auswählen kann."
 *
 * Das Popup ist der Figurwahl-Dialog mit nur dem HumanBody-Reiter (die
 * gespeicherten Vorgaben), ohne Lage-Felder: Die neue Figur nimmt Ort und
 * Drehung der alten. Was sonst noch an der alten hing — Größenangleich,
 * Schieberwerte — nicht; sie ist ein anderes Modell.
 *
 * DIE ANIMATION BLEIBT: Lief auf der alten Figur ein Clip, wird er auf die
 * neue gelegt (derselbe Weg wie beim Klick in der BVH-Bibliothek). Ein
 * Austausch, nach dem die neue Figur in Bindehaltung steht, wäre keiner.
 *
 * Rückgängig ist ein Schritt (`Figurentfernen.ersetzen`): alte Figur zurück,
 * neue weg — und die Animation wieder auf der alten.
 */
export class Figurtausch {

    static KENNUNG = 'figurtausch-dialog';
    static ZIEL = 'properties-content';
    static KOPF = '.pnl-kopf';

    /**
     * @param {Object} teile { auswahl, figurenlader, figurentfernen,
     *                         animationslauf, figurpanel }
     */
    constructor({ auswahl, figurenlader, figurentfernen, animationslauf, figurpanel }) {
        this.auswahl = auswahl;
        this.figurenlader = figurenlader;
        this.figurentfernen = figurentfernen;
        this.animationslauf = animationslauf;
        this.figurpanel = figurpanel;
        this.dialog = new Figurwahldialog({
            lader: { modell: (name) => this.tauschen(name) },
            quellen: ['modell'],
            titel: 'Modell austauschen', knopf: 'Austauschen',
            symbol: 'fa-exchange-alt', lage: false,
            kennung: Figurtausch.KENNUNG,
        });
    }

    verdrahten() {
        document.getElementById(Figurtausch.ZIEL)?.addEventListener('contextmenu', (e) => {
            if (!e.target.closest(Figurtausch.KOPF) || !this.auswahl.figur) return;
            e.preventDefault();
            this.dialog.oeffnen();
        });
        return this;
    }

    /** Die gewählte Figur gegen die Vorgabe `name` tauschen. */
    async tauschen(name) {
        const alt = this.auswahl.figur;
        if (!alt) return null;
        const neu = await this.figurenlader.modell(name, { x: alt.position.x });
        Figurtausch.lageUebernehmen(alt, neu);
        this.figurentfernen.ersetzen(alt, neu, (figur) => this.nachziehen(figur));
        Protokoll.debug('figurtausch', '✓', alt.userData.presetName, '→', name);
        return neu;
    }

    /** Nach jedem Wechsel: Eigenschaften-Feld und laufende Animation. */
    nachziehen(figur) {
        this.figurpanel.zeigen(figur);
        const [kategorie, ...rest] = (this.animationslauf.name || '').split('/');
        if (!rest.length) return;
        this.animationslauf.laden(kategorie, rest.join('/'))
            .catch(fehler => Protokoll.warnung('figurtausch', 'Animation nicht übernommen:', fehler));
    }

    /**
     * Ort und Drehung der alten Figur übernehmen — auch in der Zeitleiste:
     * Die Theatre-Spuren der neuen Figur tragen sonst den Ort vom Laden.
     */
    static lageUebernehmen(alt, neu) {
        neu.position.copy(alt.position);
        neu.rotation.copy(alt.rotation);
        const objekt = neu.userData.theatreObjekt;
        if (!objekt) return;
        const grad = Figurpanel.GRAD;
        Sequenzspuren.setzen(objekt, [
            [['position', 'x'], 0, neu.position.x],
            [['position', 'y'], 0, neu.position.y],
            [['position', 'z'], 0, neu.position.z],
            [['rotation', 'x'], 0, neu.rotation.x * grad],
            [['rotation', 'y'], 0, neu.rotation.y * grad],
            [['rotation', 'z'], 0, neu.rotation.z * grad],
        ]);
    }
}
