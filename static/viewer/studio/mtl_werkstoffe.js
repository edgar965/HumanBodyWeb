/**
 * Mtlwerkstoffe — eine MTL-Datei in Three.js-Materialien uebersetzen.
 *
 * Aus `mtl_laden.js` herausgeloest (30.08.2026, Befund `jsfunktionen`):
 * `_parseMtlAndBuildMaterials` war auf 90 Zeilen gewachsen und tat drei
 * Dinge hintereinander, die schon im Quelltext durchnummeriert waren —
 * zerlegen, Texturen laden, Materialien bauen. Jetzt drei Methoden.
 *
 * WARUM VON HAND GEPARST: Der eingebaute MTLLoader scheitert an Pfaden, wie
 * sie Blender und 3ds Max schreiben — Rueckstriche, `./`-Vorsatz, absolute
 * Pfade. Und Texturen liegen im Buendel FLACH, auch wenn die MTL einen
 * Unterpfad nennt; deshalb wird jede Textur unter beiden Namen gesucht.
 */
import * as THREE from 'three';
import { Protokoll } from '../gemeinsam/protokoll.js';

export class Mtlwerkstoffe {

    /** Vorgabewerte fuer jedes Material — matt, kaum metallisch, beidseitig. */
    static GRUNDWERTE = { roughness: 0.85, metalness: 0.02, side: THREE.DoubleSide };

    /**
     * Den Text einer MTL-Datei in ein Woerterbuch zerlegen.
     * @param {string} text Inhalt der MTL-Datei
     * @returns {object} { Materialname: { Kd, map_Kd, … } }
     */
    static zerlegen(text) {
        const eintraege = {};
        let aktuell = null;
        for (const roh of text.split(/\r?\n/)) {
            const zeile = roh.trim();
            if (!zeile || zeile.startsWith('#')) continue;
            const teile = zeile.split(/\s+/);
            const befehl = teile[0];
            if (befehl === 'newmtl') {
                aktuell = { name: teile.slice(1).join(' ') };
                eintraege[aktuell.name] = aktuell;
                continue;
            }
            if (!aktuell) continue;
            Mtlwerkstoffe._eigenschaft(aktuell, befehl, teile);
        }
        return eintraege;
    }

    /** Eine Zeile in den aktuellen Eintrag schreiben. */
    static _eigenschaft(eintrag, befehl, teile) {
        const wert = teile.slice(1).join(' ');
        if (befehl === 'Kd') eintrag.Kd = teile.slice(1, 4).map(parseFloat);
        else if (befehl === 'Ka') eintrag.Ka = teile.slice(1, 4).map(parseFloat);
        else if (befehl === 'Ks') eintrag.Ks = teile.slice(1, 4).map(parseFloat);
        else if (/^map_kd$/i.test(befehl)) eintrag.map_Kd = wert;
        else if (/^map_ks$/i.test(befehl)) eintrag.map_Ks = wert;
        else if (/^map_ka$/i.test(befehl)) eintrag.map_Ka = wert;
        else if (/^(map_bump|bump)$/i.test(befehl)) eintrag.map_Bump = wert;
        else if (/^map_ns$/i.test(befehl)) eintrag.map_Ns = wert;
        else if (/^(d|tr)$/i.test(befehl)) eintrag.opacity = parseFloat(teile[1]);
        else if (befehl === 'Ns') eintrag.shininess = parseFloat(teile[1]);
    }

    /**
     * Eine Textur laden — unter dem angegebenen Pfad ODER dem blossen Namen.
     * @param {string} basisPfad Ordner der MTL-Datei (mit Schraegstrich am Ende)
     * @param {string} rohangabe Der Wert aus der MTL, evtl. mit Optionen davor
     * @returns {Promise<THREE.Texture|null>}
     */
    static async textur(basisPfad, rohangabe) {
        // MTL-Optionen ignorieren (z. B. "-s 1 1 -o 0 0 0 datei.png").
        const worte = rohangabe.split(/\s+/).filter(w => w && !w.startsWith('-'));
        const angabe = (worte[worte.length - 1] || rohangabe)
            .replace(/\\/g, '/').replace(/^\.\//, '');
        const dateiname = angabe.split('/').pop();
        if (!dateiname) return null;
        const kandidaten = dateiname === angabe ? [angabe] : [angabe, dateiname];
        const lader = new THREE.TextureLoader();
        for (const kandidat of kandidaten) {
            try {
                const tex = await lader.loadAsync(basisPfad + kandidat);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                tex.colorSpace = THREE.SRGBColorSpace;
                tex.needsUpdate = true;
                Protokoll.debug('MTL', `Textur geladen: ${kandidat}`);
                return tex;
            } catch (e) {
                Protokoll.debug('MTL', `Textur-Kandidat ${kandidat} nicht ladbar`, e);
            }
        }
        Protokoll.warnung('MTL', `Textur NICHT GEFUNDEN: "${rohangabe}" — getestet: `
            + kandidaten.map(k => basisPfad + k).join(', '));
        return null;
    }

    /**
     * Aus den zerlegten Eintraegen fertige Materialien bauen.
     * @param {object} eintraege Ergebnis von `zerlegen`
     * @param {string} basisPfad Ordner der MTL-Datei
     * @returns {Promise<object>} { Name: THREE.MeshStandardMaterial }
     */
    static async bauen(eintraege, basisPfad) {
        const materialien = {};
        for (const [name, eintrag] of Object.entries(eintraege)) {
            const werte = { ...Mtlwerkstoffe.GRUNDWERTE };
            werte.color = (eintrag.Kd && eintrag.Kd.length === 3)
                ? new THREE.Color(eintrag.Kd[0], eintrag.Kd[1], eintrag.Kd[2])
                : new THREE.Color(0xffffff);
            for (const [feld, ziel] of [['map_Kd', 'map'], ['map_Ks', 'roughnessMap'],
                                        ['map_Bump', 'normalMap']]) {
                if (!eintrag[feld]) continue;
                const tex = await Mtlwerkstoffe.textur(basisPfad, eintrag[feld]);
                if (tex) werte[ziel] = tex;
            }
            if (eintrag.opacity != null && eintrag.opacity < 1) {
                werte.transparent = true;
                werte.opacity = eintrag.opacity;
            }
            const material = new THREE.MeshStandardMaterial(werte);
            material.name = name;
            materialien[name] = material;
        }
        return materialien;
    }
}
