import * as THREE from 'three';
import { Netzentsorgung } from './netzentsorgung.js';
import { base64ToFloat32 } from './kodierung.js';

/**
 * Umapythonnetz — das Körpernetz einer UMA-Python-Figur bauen.
 *
 * WARUM EIGENE MATERIALIEN JE SLOT (Edgar, 08.09.2026: „der mann hat einen
 * kaputten Kopf … die Auflösung ist miserabel")
 * ====================================================================
 * UMA setzt eine Figur aus acht Slots zusammen, und drei davon sind keine
 * Haut: `UMA30_Eyelashes` (160 Punkte), `UMA30_Eyes` (578) und
 * `UMA30_InnerMouth` (1.668). In Unity tragen sie eigene Materialien mit
 * Alphakanal — in einem einzigen hautfarbenen Netz standen sie als
 * undurchsichtige Flächen quer im Gesicht.
 *
 * Der Server liefert die Dreiecksbereiche (`netz.gruppen`); hier wird
 * daraus je Bereich eine Materialgruppe. Das ist EIN Netz mit mehreren
 * Materialien, nicht mehrere Netze: Die Punkte gehören zusammen, und beim
 * Häuten muss die Bindung dieselbe bleiben.
 *
 * DIE TEXTUREN KOMMEN ALS EIGENE ADRESSEN (08.09.2026)
 * =====================================================
 * Edgar: „UMA und UMA Python sehen noch leicht unterschiedlich aus, z.B.
 * bei der Haut." Die Geometrie war da längst deckungsgleich mit Unitys
 * eigenem Bau — es fehlte das Bild darauf.
 *
 * UMA legt seine Texturen als Dateien im Projekt ab, ein Overlay je Slot.
 * Die Antwort nennt nur die ARTEN (`gruppe.texturen`), das Bild kommt über
 * `/api/umapython/textur/…`: Fünf bis acht PNG base64 in derselben Antwort
 * wie das Netz brächten sie auf ein Vielfaches der jetzigen 3,9 MB, und
 * einzeln geladen liegen sie danach im Zwischenspeicher des Browsers.
 *
 * Ein ATLAS ist nicht nötig — anders als in Unity, wo ein Renderer
 * möglichst wenige Materialien haben soll. Hier gibt es ohnehin je Slot
 * eine Materialgruppe, und die UV liegen je Slot in [0,1] (gemessen über
 * alle acht: u 0,001..0,996). Die Namen UDIM1001..1005 sind also nur
 * Namen; einen Kachelversatz abzuziehen wäre falsch.
 *
 * DIE NORMALEN KOMMEN VOM SERVER
 * ==============================
 * `computeVertexNormals()` mittelt nur über Punkte, die sich einen Index
 * teilen. An den Slotnähten führt UMA getrennte Punkte — gemessen liegen
 * 1.450 der 16.277 Punkte (8,9 %) geometrisch doppelt, und die selbst
 * gerechnete Normale weicht bei 7,6 % der Punkte um über 20 Grad von der
 * mitgelieferten ab (max 133 Grad). Sichtbar war das als harte Kante quer
 * über Stirn und Hals — eine Naht, wo keine ist.
 */
export class Umapythonnetz {

    /** Hautton — die Overlays (Texturen) rechnet der Port nicht mit. */
    static HAUT = 0xc9a086;

    /** Was kein Hautmaterial bekommt. Farbe und Deckkraft je Slot. */
    static SONDER = {
        UMA30_Eyelashes: { color: 0x2b2119, roughness: 0.6, opacity: 0.85 },
        UMA30_Eyes: { color: 0xf2f0ec, roughness: 0.25, metalness: 0.05 },
        UMA30_InnerMouth: { color: 0x6d3b3b, roughness: 0.7 },
    };

    /**
     * @param netz  `{punkte, normalen, dreiecke, gruppen}` vom Server
     * @returns {THREE.Mesh}
     */
    static bauen(netz, name, beschriftung, rasse = null) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
            new THREE.Float32BufferAttribute(netz.punkte, 3));
        if (netz.normalen?.length === netz.punkte.length) {
            geo.setAttribute('normal',
                new THREE.Float32BufferAttribute(netz.normalen, 3));
        } else {
            geo.computeVertexNormals();
        }
        if (netz.uv?.length) {
            geo.setAttribute('uv',
                new THREE.Float32BufferAttribute(netz.uv, 2));
        }
        geo.setIndex(netz.dreiecke);
        const material = Umapythonnetz._materialien(geo, netz.gruppen, rasse);
        geo.userData.gruppen = geo.groups.map(g => ({ ...g }));       // unverändert — der Stoffschwung stellt `count` einer laufenden Gruppe auf 0
        const mesh = new THREE.Mesh(geo, material);
        mesh.name = name;
        mesh.userData.beschriftung = beschriftung;
        return mesh;
    }

    /**
     * Materialgruppen aus den Slotbereichen — oder ein einziges Material.
     *
     * Ohne Gruppen (ältere Antwort) bleibt es beim Hautmaterial: Die Figur
     * sieht dann aus wie vorher, statt dass gar nichts kommt.
     */
    static _materialien(geo, gruppen, rasse) {
        if (!Array.isArray(gruppen) || !gruppen.length) {
            return Umapythonnetz._haut();
        }
        // JE GRUPPE EIN EIGENES MATERIAL, auch für die Haut: Die fünf
        // Körperslots tragen verschiedene Texturen (UDIM1001..1005), und
        // ein gemeinsames Material könnte nur eine davon zeigen.
        const liste = [];
        for (const gruppe of gruppen) {
            const sonder = Umapythonnetz.SONDER[gruppe.name];
            const material = sonder
                ? new THREE.MeshStandardMaterial({
                    roughness: 0.6, metalness: 0.0, side: THREE.DoubleSide,
                    transparent: sonder.opacity !== undefined, ...sonder })
                : Umapythonnetz._haut();
            geo.addGroup(gruppe.index_ab, gruppe.index_anzahl, liste.length);
            liste.push(material);
            Umapythonnetz._texturen(material, gruppe, rasse, !!sonder);
        }
        return liste;
    }

    /**
     * Die Texturen des Slots nachladen und einhängen.
     *
     * NACHLADEN, NICHT WARTEN: Die Figur steht sofort in ihrem Hautton da
     * und wird schärfer, sobald die Bilder kommen. Andersherum sähe der
     * Nutzer sekundenlang nichts.
     *
     * `colorSpace` MUSS gesetzt sein: Eine Albedo-Textur ohne sRGB kommt
     * in Three.js zu hell und flau heraus — sie sieht dann aus wie ein
     * Fehler der Textur und ist einer der Farbraumangabe.
     *
     * `flipY` BLEIBT AUF DEM STANDARD (true). Der erste Versuch setzte es
     * auf false — der Reflex aus dem glTF-Umfeld, wo der Exporter die UV
     * schon gedreht hat. Hier kommen sie roh aus Unity, und dort läuft v
     * wie in WebGL. Gemessen am Bild: mit false saß ein roter Fleck
     * mitten auf der Stirn, dazu rötliche Bahnen an Oberarmen und
     * Oberschenkeln; mit true sitzen Brustwarzen, Nabel, Fingernägel und
     * Augenbrauen dort, wo sie hingehören. Die Textur lädt in beiden
     * Fällen fehlerfrei — der Unterschied ist nur im Bild zu sehen.
     */
    static _texturen(material, gruppe, rasse, istSonder) {
        const arten = gruppe.texturen || [];
        if (!rasse || !arten.length) return;
        const lader = new THREE.TextureLoader();
        const adresse = art => '/api/umapython/textur/'
            + `${encodeURIComponent(rasse)}/${encodeURIComponent(gruppe.name)}`
            + `/${art}/`;
        if (arten.includes('albedo')) {
            lader.load(adresse('albedo'), bild => {
                bild.colorSpace = THREE.SRGBColorSpace;
                material.map = bild;
                // Die Hautfarbe ist jetzt im Bild; ein zweiter Farbton
                // darüber machte es dunkler als in Unity.
                if (!istSonder) material.color.setHex(0xffffff);
                material.needsUpdate = true;
            }, undefined, () => {});
        }
        if (arten.includes('normalen')) {
            lader.load(adresse('normalen'), bild => {
                material.normalMap = bild;
                material.needsUpdate = true;
            }, undefined, () => {});
        }
    }

    static _haut() {
        return new THREE.MeshStandardMaterial({
            color: Umapythonnetz.HAUT, roughness: 0.85,
            metalness: 0.0, side: THREE.DoubleSide,
        });
    }

    /** Was ein Reglerzug nicht ändert — der Nachfolger teilt es mit dem alten Netz. */
    static BLEIBT = ['normal', 'uv', 'skinIndex', 'skinWeight'];

    /**
     * Ein Reglerzug (25.11.2026, Edgar: „alle regler unter 0,2 s“): neue Punkte (die Normalen hängen nicht an der DNA), alles andere vom stehenden Netz — auch Materialien und Texturen. Bis dahin lud jeder Zug
     * alle 14 Bilder neu, gemessen 1,4–1,8 s Stillstand in `texSubImage2D`; die alten blieben auf der Karte liegen (`Material.dispose` gibt Texturen nicht frei).
     *
     * Ein NEUES `SkinnedMesh`, nicht das alte mit anderen Punkten: Am Netz selbst erkennen Stoffschwung und Auswahl, dass sich die Figur geändert hat.
     *
     * @param alt   das stehende, gehäutete Netz; es verlässt die Gruppe, seine Geometrie wird frei
     * @param netz  `{punkte}` als Puffer
     */
    static umformen(gruppe, alt, netz) {
        const von = alt.geometry, geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(base64ToFloat32(netz.punkte), 3));
        for (const name of Umapythonnetz.BLEIBT) {
            if (!von.attributes[name]) continue;
            geo.setAttribute(name, von.attributes[name]);
            von.deleteAttribute(name);                      // sonst gäbe `dispose` den geteilten Puffer mit frei
        }
        geo.setIndex(von.index);
        von.setIndex(null);
        geo.userData.gruppen = von.userData.gruppen || [];
        for (const g of geo.userData.gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
        const neu = new THREE.SkinnedMesh(geo, alt.material);
        Object.assign(neu, { name: alt.name, visible: alt.visible, frustumCulled: false, castShadow: alt.castShadow, receiveShadow: alt.receiveShadow, userData: { ...alt.userData } });
        gruppe.remove(alt);
        von.dispose();
        return neu;
    }

    /** Ein Netz samt Material freigeben — vor einem vollen Neubau (Rasse, Kleidung). */
    static entfernen(gruppe, name) {
        const alt = gruppe.getObjectByName(name);
        if (!alt) return;
        gruppe.remove(alt);
        Netzentsorgung.entfernen(alt);
    }
}
