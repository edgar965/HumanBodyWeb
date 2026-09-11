import * as THREE from 'three';
import { GarmentcodeGeometrie } from '../scene/garmentcode_geometrie.js';
import { Garmentstoff } from '../scene/garmentcode_stoff.js';
import { Protokoll } from './protokoll.js';

/**
 * Garmentcodestueck — ein gespeichertes GarmentCode-Stück in die Bühne holen.
 *
 * ANLASS (Edgar, 11.09.2026): „laden des Female1 Modells lädt nicht die
 * Kleider (GarmentCode) des Modells". Die Vorgabe führt je Verfahren eine
 * Liste — `garments` (MakeHuman-Kleidung, per Server angepasst) und seit dem
 * 08.09.2026 `garmentcode` (`GarmentcodeAblage`: `{stueck, rig_url, ordner,
 * material}`). `Vorgabefigur` las nur die erste; `Female1.json` trägt zwei
 * GarmentCode-Stücke und keine `garments` — die Figur kam nackt.
 *
 * Geladen wird dieselbe Rig-Datei wie in der Szene (`rig_url`): Punkte,
 * Dreiecke, UVs, je Punkt Knochenname und Gewicht. Hier entsteht daraus ein
 * STARRES Netz; gebunden wird es erst, wenn die Figur ihr Skelett hat —
 * das baut der Skinner nachträglich (`studio/garmentcodebindung.js`). Die
 * Rohdaten bleiben deshalb am Netz (`userData.gcRig`), genau wie in
 * `scene/garmentcode_anziehen.js`.
 *
 * GEMEINSAM SEIT DEM 11.09.2026 (aus `TheatreJS/src/laden/`): Auch das BVH
 * Studio lud zu einer Vorgabe nur `garments` und `hair_style` — Edgar:
 * „Female1 lädt nicht die GarmentCode". Theatre (`Skinner`) und Studio
 * (`Spurzubehoer`) holen das Stück jetzt von hier; gebunden wird es mit
 * `garmentcodebindung.js` daneben.
 *
 * Nicht neu simuliert: Die Drapierung kostet rund 25 s, das Nachladen der
 * fertigen Datei Millisekunden. Fehlt der Ergebnisordner, fällt nur dieses
 * Stück aus — gemeldet, die Figur bleibt stehen.
 */
export class Garmentcodestueck {

    /** Kennzeichen am Netz, mit dem der Skinner es später erkennt. */
    static KENNUNG = 'gcRig';

    /**
     * @param {Object} eintrag  {stueck, rig_url, material} aus der Vorgabe
     */
    constructor(eintrag) {
        this.eintrag = eintrag;
    }

    /** Kurzform: Rig holen und Netz zurückgeben. */
    static async laden(eintrag) {
        return new Garmentcodestueck(eintrag).netz();
    }

    async netz() {
        const daten = await this._rig();
        return this.aufbauen(daten);
    }

    async _rig() {
        const antwort = await fetch(this.eintrag.rig_url, { cache: 'no-store' });
        if (!antwort.ok) {
            throw new Error(`Rig nicht ladbar (${antwort.status}): ${this.eintrag.rig_url}`);
        }
        return antwort.json();
    }

    /** Derselbe Schritt mit schon geladenen Daten — so ist er prüfbar. */
    aufbauen(daten) {
        const geometrie = GarmentcodeGeometrie.aus(daten);
        const material = Garmentstoff.neu(
            Garmentcodestueck.materialwerte(this.eintrag.material),
            { hatUv: !!geometrie.attributes.uv, uvMeter: daten.uv_meter });
        const netz = new THREE.Mesh(geometrie, material);
        netz.castShadow = true;
        netz.receiveShadow = true;
        netz.frustumCulled = false;      // das Netz verlässt beim Posieren die Box
        netz.name = `garmentcode_${String(this.eintrag.stueck || 'kleidung')
            .replace(/[^a-z0-9_-]/gi, '_')}`;
        Object.assign(netz.userData, {
            isGarment: true,
            gcStueck: this.eintrag.stueck,
            [Garmentcodestueck.KENNUNG]: daten,
            beschriftung: `${this.eintrag.stueck || 'Kleidung'} (GarmentCode)`,
        });
        Protokoll.debug('garmentcodestueck', '✓ geladen:', this.eintrag.stueck,
                        geometrie.attributes.position.count, 'Punkte');
        return netz;
    }

    /**
     * Das gespeicherte Material in die Form von `Garmentstoff.werte`:
     * Die Szenendatei schreibt die Farbe als `#rrggbb`, das Material will
     * eine Zahl.
     */
    static materialwerte(material) {
        if (!material) return null;
        let farbe = material.farbe;
        if (typeof farbe === 'string') {
            farbe = parseInt(farbe.replace(/^#/, ''), 16);
            if (!Number.isFinite(farbe)) farbe = null;
        }
        return {
            farbe: farbe ?? null,
            rauheit: typeof material.rauheit === 'number' ? material.rauheit : null,
            metall: typeof material.metall === 'number' ? material.metall : null,
            gewebe: material.gewebe && typeof material.gewebe === 'object'
                ? { ...material.gewebe } : null,
        };
    }
}
