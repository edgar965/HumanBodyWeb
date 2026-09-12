import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Netzgeometrie } from '../../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Eigenhaut } from '../../gemeinsam/eigenhaut.js';

/**
 * Mhkleidstueck — ein MakeHuman-Kleidungsstück an der MakeHuman-Figur.
 *
 * WAS HIER NICHT STEHT, IST DER PUNKT: kein Offset, keine Steifigkeit, kein
 * Maßstab, kein Y-Versatz, kein „Push Outside". Die sieben Regler in
 * `mhproxy_anpassen.js` gibt es, weil dort ein MakeHuman-Stück auf einen
 * FREMDEN Körper gebracht wird. Hier ist der Träger der Körper, für den das
 * Stück entworfen wurde — die `.mhclo` sagt für jeden Stoffpunkt genau, wo er
 * liegt. Es bleibt das Aussehen: Farbe, Rauheit, Metallanteil, Deckkraft.
 *
 * Die Punkte kommen in Three-Achsen und auf demselben Boden wie das Basisnetz
 * (`drehen = false`, siehe `MhFigur`).
 *
 * TEXTUR VOR FARBE, UND DIE TEXTUR KOMMT SPÄTER
 * =============================================
 * Mit Textur wird die Materialfarbe WEISS — sonst multipliziert sie in das
 * Bild und färbt das Stück ein zweites Mal. Und das Bild trifft erst nach dem
 * Netz ein: Wer in der Zwischenzeit dasselbe Stück auszieht, hätte sonst eine
 * Textur an einem freigegebenen Material hängen. Deshalb der Vergleich mit dem
 * Material, das GERADE an der Figur hängt (derselbe Befund wie in
 * `mhproxynetz.js`, 18.08.2026).
 */
export class Mhkleidstueck {

    static ADRESSE = '/api/character/mh-figur/garderobe/';

    /** Vorgabe-Aussehen; die Farbe zählt nur ohne Textur und ohne .mhmat. */
    static WERTE = { farbe: '#8d94a8', rauheit: 80, metall: 0, deckkraft: 100 };

    /**
     * Der Name des Netzes in `clothMeshes`.
     *
     * `mhk_` und NICHT `mh_`: Die Vorsilbe `mh_` schaltet in
     * `properties._updatePropContext` den Reiter „MakeHuman Eigenschaften"
     * auf — den mit den Fit-Reglern für die HumanBody-Figur. Die wären hier
     * wirkungslos und würden bei jedem Zug eine Anpassung am falschen Körper
     * anstoßen.
     */
    static schluessel(kennung) {
        return `mhk_${kennung}`;
    }

    constructor(figur, kennung, werte = null) {
        this.figur = figur;
        this.kennung = kennung;
        this.werte = { ...Mhkleidstueck.WERTE, ...(werte || {}) };
        /**
         * Kam die Farbe aus einer gespeicherten Szene (oder Sitzung)?
         *
         * Beim ERSTEN Anziehen gilt, was die `.mhmat` des Stücks sagt — der
         * Anzug ist weiß, weil er weiß ist. Nach dem Wiederherstellen gilt,
         * was der Nutzer eingestellt hat. Ohne diese Unterscheidung war ein
         * blau gefärbter Anzug nach dem Neuladen der Seite wieder weiß, und
         * das Farbfeld zeigte es nicht einmal an.
         */
        this.eigeneFarbe = Boolean(werte && werte.farbe);
    }

    get schluessel() {
        return Mhkleidstueck.schluessel(this.kennung);
    }

    // ----------------------------------------------------------------- laden

    async anlegen() {
        // POST mit der Reglerstellung: Der Stoff wird auf den GEFORMTEN
        // Körper gerechnet, nicht auf das Basisnetz.
        const daten = await Serverabruf.senden(
            `${Mhkleidstueck.ADRESSE}${this.kennung}/netz/`,
            this.figur.formung());
        if (daten.fehler) throw new Error(daten.fehler);
        this.altesNetzWeg();
        const geometrie = Netzgeometrie.bauen(daten, THREE, null, false);
        /** @type {THREE.Mesh|THREE.SkinnedMesh} */
        let netz = new THREE.Mesh(geometrie, this.werkstoff(daten));
        netz.name = this.schluessel;
        // An MakeHumans eigenes Rig binden — sonst bleibt der Stoff beim
        // Abspielen stehen, während der Träger davonläuft (07.09.2026).
        // Die Gewichte kommen aus derselben `.mhclo`-Zuordnung, an der der
        // Stoff ohnehin hängt.
        // Die Rohgewichte bleiben am Netz. `load()` zieht die Kleidung
        // ZUERST an — da gibt es das Skelett noch nicht —, und jeder
        // Reglerzug baut es neu. `MhFigur._kleiderBinden` bindet daraus
        // nach (Edgar, 07.09.2026: „Kleider von MakeHuman animieren immer
        // noch nicht").
        netz.userData.hautgewichte = daten.hautgewichte || null;
        if (this.figur.skelett && daten.hautgewichte) {
            netz = Eigenhaut.binden(netz, this.figur.skelett, daten.hautgewichte);
        }
        this.figur.clothMeshes[this.schluessel] = netz;
        Eigenhaut.einhaengen(this.figur.group, netz, this.figur.skelett);
        // Die WIRKLICH gesetzte Farbe merken: Sie kann aus der `.mhmat`
        // kommen. Sonst zeigte das Farbfeld im Panel eine andere Farbe als
        // das Stück in der Szene.
        this.figur.kleidung[this.kennung] = {
            ...this.werte,
            farbe: '#' + netz.material.color.getHexString(),
            mitTextur: Boolean(daten.has_texture),
        };
        Protokoll.debug('MhKleid',
            `${this.kennung}: ${daten.vertex_count} Punkte, `
            + `${daten.face_count} Dreiecke`);
        return netz;
    }

    altesNetzWeg() {
        const altes = this.figur.clothMeshes[this.schluessel];
        if (!altes) return;
        // Die TEXTUR zuerst: `material.dispose()` gibt sie NICHT mit frei.
        altes.material?.map?.dispose();
        Netzentsorgung.ausAblage(this.figur.group, this.figur.clothMeshes,
                                 this.schluessel);
    }

    // -------------------------------------------------------------- Material

    werkstoff(daten) {
        const deckkraft = (this.werte.deckkraft ?? 100) / 100;
        const werkstoff = new THREE.MeshStandardMaterial({
            color: this.materialfarbe(daten),
            roughness: (this.werte.rauheit ?? 80) / 100,
            metalness: (this.werte.metall ?? 0) / 100,
            side: THREE.DoubleSide,
            // Hält den Stoff vor der Haut, sonst blitzt sie an flachen
            // Stellen durch (Z-Fighting).
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
            transparent: deckkraft < 1, opacity: deckkraft,
        });
        this.texturNachladen(werkstoff, daten);
        return werkstoff;
    }

    materialfarbe(daten) {
        if (daten.has_texture) return new THREE.Color(1, 1, 1);
        if (this.eigeneFarbe) return new THREE.Color(this.werte.farbe);
        if (daten.mat_color) {
            return new THREE.Color(daten.mat_color[0], daten.mat_color[1],
                                   daten.mat_color[2]);
        }
        return new THREE.Color(this.werte.farbe);
    }

    texturNachladen(werkstoff, daten) {
        if (!daten.has_texture || !daten.texture_name) return;
        const adresse = `${Mhkleidstueck.ADRESSE}${this.kennung}/textur/`
            + `${encodeURIComponent(daten.texture_name)}/`;
        new THREE.TextureLoader().load(adresse, textur => {
            if (this.figur.clothMeshes[this.schluessel]?.material !== werkstoff) {
                textur.dispose();      // zu spät — das Netz ist schon ersetzt
                return;
            }
            textur.colorSpace = THREE.SRGBColorSpace;
            werkstoff.map = textur;
            werkstoff.needsUpdate = true;
        }, undefined, () => Protokoll.warnung(
            'MhKleid', 'Textur nicht ladbar:', daten.texture_name));
    }

    /**
     * Aussehen ändern, ohne neu zu laden.
     *
     * Die Farbe wirkt nur ohne Textur: Mit Bild ist das Material weiß, und
     * eine Farbe darauf würde es einfärben statt zu ersetzen.
     */
    static aussehen(figur, kennung, werte) {
        const netz = figur.clothMeshes[Mhkleidstueck.schluessel(kennung)];
        const gemerkt = figur.kleidung[kennung];
        if (!netz || !gemerkt) return;
        Object.assign(gemerkt, werte);
        const werkstoff = netz.material;
        if (!werkstoff.map) werkstoff.color.set(gemerkt.farbe);
        werkstoff.roughness = (gemerkt.rauheit ?? 80) / 100;
        werkstoff.metalness = (gemerkt.metall ?? 0) / 100;
        werkstoff.opacity = (gemerkt.deckkraft ?? 100) / 100;
        werkstoff.transparent = werkstoff.opacity < 1;
        werkstoff.needsUpdate = true;
    }
}
