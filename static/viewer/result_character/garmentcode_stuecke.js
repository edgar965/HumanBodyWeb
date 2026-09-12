import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Garmentcodestueck } from '../gemeinsam/garmentcodestueck.js';
import { Garmentcodebindung } from '../gemeinsam/garmentcodebindung.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Figurhaut } from '../gemeinsam/figurhaut.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * GarmentcodeStuecke — die GarmentCode-Stücke einer Modellvorgabe an die
 * Figur der Ergebnisseite hängen.
 *
 * ANLASS (Edgar, 12.09.2026): „im unteren 3D Modellbereich werden keine
 * GarmentCode zum Modell geladen". `presets.js` las aus der Vorgabe
 * `cloth`, `hair_style` und `garments` (MakeHuman) — die Liste `garmentcode`
 * (seit 08.09.2026, `{stueck, rig_url, ordner, material}`) nicht. Derselbe
 * Fehler war am 11.09.2026 im Theatre (`Skinner`) und im BVH Studio
 * (`Spurzubehoer`) behoben worden; die Ergebnisseite blieb aus. Geladen und
 * gebunden wird mit denselben Klassen (`gemeinsam/garmentcodestueck.js`,
 * `gemeinsam/garmentcodebindung.js`): Rig-Datei holen, starres Netz, dann
 * ans Skelett der Figur häuten — wie `Spurzubehoer.garmentcode()`.
 *
 * Die Stücke liegen in einer eigenen Gruppe (`state.garmentcodeGroup`):
 * `Garmentcodebindung.binden` tauscht die Kinder der übergebenen Gruppe aus,
 * so trifft es nicht die Bühne selbst. Kleidung ausblenden (`Knopfleiste`)
 * und der Wechsel des Körpertyps (`reloadBodyMesh`) fassen die Gruppe mit an.
 *
 * DIE HAUT UNTER DEN STÜCKEN WIRD NICHT GEZEICHNET (Edgar, 12.09.2026: „bei
 * einer animation mit Female2 scheint die Haut durch das Kleid"): Nach dem
 * Binden läuft `Figurhaut.anwenden` — dieselbe Maske wie in der Szene und
 * im Studio (`gemeinsam/figurhaut.js`, Befund vom 11.09.2026 dort). Zwei
 * Flächen, die Millimeter auseinanderliegen und getrennt gehäutet werden,
 * kommen sich an jedem Gelenk nahe; was nicht gezeichnet wird, kommt nicht
 * durch. Gehen die Stücke (`entfernen`), kommt der volle Index zurück.
 */
export class GarmentcodeStuecke {

    static NAME = 'garmentcode';

    /** Alle Stücke einer Vorgabe laden und binden; die alten vorher weg. */
    static async laden(eintraege) {
        GarmentcodeStuecke.entfernen();
        if (!eintraege?.length) return 0;
        if (!state.isSkinned || !state.rigifySkeleton || !state.bodyMesh) {
            Protokoll.warnung('result_character',
                              'GarmentCode: Figur ohne Skelett, nichts gebunden');
            return 0;
        }
        const gruppe = GarmentcodeStuecke.gruppe();
        for (const eintrag of eintraege) {
            try {
                gruppe.add(await Garmentcodestueck.laden(eintrag));
            } catch (fehler) {
                Protokoll.warnung('result_character',
                                  `GarmentCode „${eintrag.stueck}":`, fehler.message);
            }
        }
        const gebunden = new Garmentcodebindung(state.rigifySkeleton)
            .binden(gruppe, state.bodyMesh);
        gruppe.visible = state.clothesVisible;
        Protokoll.debug('result_character',
                        `GarmentCode: ${gebunden}/${eintraege.length} gebunden`);
        GarmentcodeStuecke.hautMaskieren();
        return gebunden;
    }

    /** Die Figur, wie `Figurhaut` sie liest: Körper plus Gruppe der Stücke. */
    static figur() {
        return { mesh: state.bodyMesh, group: state.garmentcodeGroup, name: 'Ergebnis' };
    }

    static hautMaskieren() {
        try {
            return Figurhaut.anwenden(GarmentcodeStuecke.figur());
        } catch (fehler) {
            Protokoll.warnung('result_character', 'Hautmaske:', fehler.message);
            return null;
        }
    }

    /** Die Gruppe in der Bühne — angelegt beim ersten Stück. */
    static gruppe() {
        if (!state.garmentcodeGroup) {
            state.garmentcodeGroup = new THREE.Group();
            state.garmentcodeGroup.name = GarmentcodeStuecke.NAME;
            state.scene.add(state.garmentcodeGroup);
        }
        return state.garmentcodeGroup;
    }

    static entfernen() {
        const gruppe = state.garmentcodeGroup;
        if (!gruppe) return;
        for (const netz of [...gruppe.children]) {
            Netzentsorgung.entfernen(gruppe, netz);
        }
        Figurhaut.aufheben(GarmentcodeStuecke.figur());
    }

    /** Mit der übrigen Kleidung ein- und ausblenden. */
    static sichtbar(sichtbar) {
        if (state.garmentcodeGroup) state.garmentcodeGroup.visible = sichtbar;
    }
}

// Für `mesh_loading.js`, das wegen des Importkreises über `fn` ruft.
fn.loadGarmentcode = (eintraege) => GarmentcodeStuecke.laden(eintraege);
fn.removeAllGarmentcode = () => GarmentcodeStuecke.entfernen();
