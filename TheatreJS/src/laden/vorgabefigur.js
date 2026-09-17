import { HumanbodyModell }
    from '../../../static/viewer/gemeinsam/humanbodymodell.js';
import { Koerperfrage } from '../../../static/viewer/gemeinsam/koerperfrage.js';
import { Figurlage } from './figurlage.js';
import { Buehnenschatten } from './buehnenschatten.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Vorgabefigur — eine Figur samt Haaren und Kleidung aus einer Vorgabe in die
 * Bühne des Theatre stellen.
 *
 * SEIT 13.09.2026 BAUT DAS THEATRE NICHTS MEHR SELBST (Edgar: „Alle HTML-
 * Seiten … sollen die Figur NICHT selber bauen, sondern eine globale Klasse
 * nutzen"): Netz, Lippen, Details, Haare, Kleidung und GarmentCode kommen
 * aus `HumanbodyModell.bauen()` (`gemeinsam/humanbodymodell.js`). Vorher
 * standen hier Netzbau (`figurnetz.js`), Kleidung (`kleidungsnetz.js`) und
 * Haare noch einmal — und das Theatre hatte weder Lippen noch Brauen.
 *
 * UNGEHÄUTET: Das Theatre bindet seine Figuren erst, wenn Skelett und
 * Gewichte da sind (`studio/skinner.js`, `autoUmwandeln`) — Kleidung kommt
 * darum als `SkinnedMesh` mit `needsBinding`, GarmentCode-Stücke starr mit
 * ihrer Rig-Datei, Haare als `Mesh`; der Skinner bindet alle drei.
 *
 * Was das Theatre an der Gruppe erwartet (`userData`): `presetName`,
 * `bodyType`, `morphs`, `meta` (Figurpanel, Nachladen), bei erzeugten
 * Modellen `isGeneratedModel`, `isSkinnedMesh`, `skinnedMesh`, `skeleton`,
 * `rootBone`, `rigifySkelObj` (Animationssystem). Dazu `modell` — die
 * Figur selbst, damit das Figurpanel nach Morphs die Details nachzieht.
 */
export class Vorgabefigur {

    /**
     * @param {Object} werkzeuge  { inTheatre } — das Anmelden bei Theatre.js
     */
    constructor(werkzeuge) {
        this.werkzeuge = werkzeuge;
    }

    /**
     * Figur laden und in die Szene setzen.
     * @param {import('three').Scene} scene
     * @param {Object} vorgabe
     * @param {string} name  Anzeigename fuer Theatre
     * @param {Object} lage  {x, angleichen, vorbildHoehe} aus dem Figurwahl-
     *        Dialog, oder null — dann bleibt die Figur im Ursprung
     */
    async laden(scene, vorgabe, name, lage = null) {
        const modell = new HumanbodyModell(name, vorgabe);
        await modell.bauen({ zubehoer: true });
        const gruppe = modell.group;
        Buehnenschatten.an(gruppe);
        scene.add(gruppe);
        this._kennzeichnen(gruppe, modell, vorgabe, name);
        // Lage VOR der Anmeldung: Theatre.js nimmt die Position als Startwert.
        Figurlage.anwenden(gruppe, lage);
        // Das Theatre-Objekt bleibt an der Gruppe (Schlüssel in
        // `userData.theatreSchluessel`): Wer die Figur entfernt, meldet es
        // darüber ab (`studio/figurentfernen.js`).
        gruppe.userData.theatreObjekt = this.werkzeuge.inTheatre(gruppe, name);
        Protokoll.debug('vorgabefigur', '✓ Figur gebaut:', name,
                        `${gruppe.children.length} Teile`);
        return gruppe;
    }

    /** Werte, die spaeter fuers Nachladen und die Panels gebraucht werden. */
    _kennzeichnen(gruppe, modell, vorgabe, name) {
        gruppe.userData.modell = modell;
        gruppe.userData.presetName = name;
        gruppe.userData.bodyType = modell.generatedConfig
            ? 'generated' : (vorgabe.body_type || Koerperfrage.VORGABE_KOERPER);
        if (modell.generatedConfig) {
            gruppe.userData.isGeneratedModel = true;
            Vorgabefigur._skelettMerken(gruppe, modell);
            return;
        }
        gruppe.userData.morphs = Koerperfrage.morphs(vorgabe);
        gruppe.userData.meta = { ...(vorgabe.meta || {}) };
    }

    /** Das Animationssystem sucht diese vier Angaben an der Gruppe. */
    static _skelettMerken(gruppe, modell) {
        if (!modell.skelett || !modell.bodyMesh?.isSkinnedMesh) return;
        Object.assign(gruppe.userData, {
            isSkinnedMesh: true,
            skinnedMesh: modell.bodyMesh,
            skeleton: modell.skelett.skeleton,
            rootBone: modell.skelett.rootBone,
            // Vollstaendiges Rigify-Objekt fuer das Retarget (boneByName usw.)
            rigifySkelObj: modell.skelett,
        });
    }
}
