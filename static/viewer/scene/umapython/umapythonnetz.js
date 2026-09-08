import * as THREE from 'three';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';

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
    static bauen(netz, name, beschriftung) {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position',
            new THREE.Float32BufferAttribute(netz.punkte, 3));
        if (netz.normalen?.length === netz.punkte.length) {
            geo.setAttribute('normal',
                new THREE.Float32BufferAttribute(netz.normalen, 3));
        } else {
            geo.computeVertexNormals();
        }
        geo.setIndex(netz.dreiecke);
        const material = Umapythonnetz._materialien(geo, netz.gruppen);
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
    static _materialien(geo, gruppen) {
        const haut = Umapythonnetz._haut();
        if (!Array.isArray(gruppen) || !gruppen.length) return haut;
        const liste = [haut];
        for (const gruppe of gruppen) {
            const sonder = Umapythonnetz.SONDER[gruppe.name];
            let nummer = 0;
            if (sonder) {
                nummer = liste.length;
                liste.push(new THREE.MeshStandardMaterial({
                    roughness: 0.6, metalness: 0.0, side: THREE.DoubleSide,
                    transparent: sonder.opacity !== undefined,
                    ...sonder,
                }));
            }
            geo.addGroup(gruppe.index_ab, gruppe.index_anzahl, nummer);
        }
        return liste;
    }

    static _haut() {
        return new THREE.MeshStandardMaterial({
            color: Umapythonnetz.HAUT, roughness: 0.85,
            metalness: 0.0, side: THREE.DoubleSide,
        });
    }

    /** Ein Netz samt Material freigeben — beim Tausch nach einem Reglerzug. */
    static entfernen(gruppe, name) {
        const alt = gruppe.getObjectByName(name);
        if (!alt) return;
        gruppe.remove(alt);
        Netzentsorgung.entfernen(alt);
    }
}
