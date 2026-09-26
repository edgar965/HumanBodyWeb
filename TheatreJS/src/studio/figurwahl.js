import { UmaModell } from '../../../static/viewer/gemeinsam/umamodell.js';
import { Figurwahldialog }
    from '../../../static/viewer/gemeinsam/figurwahldialog.js';
import { Katalogpflege } from '../../../static/viewer/charakter/katalogpflege.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';
import { Figurlage } from '../laden/figurlage.js';
import { Buehnenschatten } from '../laden/buehnenschatten.js';
import { Theatreanmeldung } from '../laden/theatreanmeldung.js';

/**
 * Figurwahl — „Datei → Modell laden" öffnet den Figurwahl-Dialog.
 *
 * ANLASS (Edgar, 11.09.2026): „Datei - Modell laden funktioniert nicht, das
 * soll so funktionieren wie bei /humanbody/scene/, mit dem gleichen Popup."
 * Der Menüpunkt schaltete bis dahin nur auf den Reiter „Modelle" der
 * rechten Leiste um — und der war unter der Studio-Werkzeugleiste kaum zu
 * sehen. Jetzt kommt derselbe Dialog wie in der Szene
 * (`gemeinsam/figurwahldialog.js`), mit Lage und Größenangleich.
 *
 * WELCHE REITER DAS THEATRE ZEIGT: nur die Figurarten, die es auch tragen
 * kann. HumanBody-Modelle gehen den vollen Weg (Skelett, Animation, Kleidung,
 * GarmentCode); UMA-Figuren baut `UmaModell` (`gemeinsam/umamodell.js`, seit
 * 13.09.2026 dieselbe Klasse wie in der Szene: Skelett unter der Gruppe,
 * nach +Z gedreht, auf 1,68 m) und stehen still — auswählbar, verschiebbar,
 * entfernbar. SMPL, MakeHuman und UMA Python bräuchten die Animationswege
 * der Szene-Seite, die es hier nicht gibt; ein Reiter, der lädt und dann
 * nichts zeigt, wäre schlechter als keiner.
 *
 * DIE LAGE: wie in der Szene 1,5 m rechts neben der zuletzt geladenen Figur,
 * auf deren Höhe; ohne Figur im Ursprung.
 */
export class Figurwahl {

    static ABSTAND_M = Figurwahldialog.ABSTAND_M;

    /**
     * @param {Object} teile { scene, figuren, figurenlader, auswahl }
     */
    constructor({ scene, figuren, figurenlader, auswahl }) {
        this.scene = scene;
        this.figuren = figuren;
        this.figurenlader = figurenlader;
        this.auswahl = auswahl;
        this.dialog = new Figurwahldialog({
            lader: {
                modell: (name, lage) => this.humanbody(name, lage),
                uma: (name, lage) => this.uma(name, lage),
            },
            vorgaben: () => this.vorgaben(),
            pflege: Katalogpflege,
        });
    }

    verdrahten() {
        document.getElementById('menu-model-load')
            ?.addEventListener('click', () => this.dialog.oeffnen());
        return this;
    }

    /** Rechts neben der zuletzt geladenen Figur, auf deren Höhe. */
    vorgaben() {
        const vorbild = this.figuren[this.figuren.length - 1] || null;
        return {
            x: vorbild ? Number((vorbild.position.x + Figurwahl.ABSTAND_M).toFixed(2)) : 0,
            angleichen: Boolean(vorbild),
            vorbildHoehe: vorbild ? Figurlage.hoehe(vorbild) : 0,
        };
    }

    // -- Lader ----------------------------------------------------------------

    async humanbody(name, lage) {
        const figur = await this.figurenlader.modell(name, lage);
        Protokoll.debug('figurwahl', '✓ HumanBody geladen:', name, 'bei x =', figur.position.x);
        return figur;
    }

    /** Eine UMA-Figur über `UmaModell` — still, aber als Figur der Bühne. */
    async uma(name, lage) {
        const modell = await new UmaModell(`uma_${Date.now()}`, { datei: name }).bauen();
        const gruppe = modell.group;
        Buehnenschatten.an(gruppe);
        const anzeige = String(name).replace(/\.glb$/i, '');
        Object.assign(gruppe.userData, {
            isCharacter: true, presetName: modell.presetName, bodyType: modell.bodyType, modell,
            // Kein Rigify-Netz: Der Skinner soll nicht versuchen, es umzuwandeln.
            isSkinnedMesh: true,
        });
        this.scene.add(gruppe);
        Figurlage.anwenden(gruppe, lage);
        gruppe.userData.theatreObjekt = Theatreanmeldung.anmelden(
            gruppe, gruppe.userData.presetName, 'Character');
        this.figuren.push(gruppe);
        this.auswahl.figurVormerken(gruppe);
        Protokoll.debug('figurwahl', '✓ UMA geladen:', anzeige, 'bei x =', gruppe.position.x);
        return gruppe;
    }
}
