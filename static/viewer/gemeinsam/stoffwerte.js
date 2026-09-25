import * as THREE from 'three';
import { Gewebe } from './gewebe.js';
import { gewebeart } from './gewebearten.js';
import { Umfaerbung } from './umfaerbung.js';

/**
 * Stoffwerte — Rauheit, Metallgrad und Gewebe eines Genesis-Stücks (Daz, GC, MB).
 *
 * WARUM (Edgar, 25.09.2026: „auch die Material-Einstellungen fehlen"): Die aus
 * GarmentCode gebackenen Stücke (`G9gcstuecke`) hatten nur noch die Farbe
 * (`Umfaerbung`), der GarmentCode-Reiter dagegen Roughness, Metalness und das
 * Gewebe (`garmentcode_material.js`, `garmentcode_gewebe.js`). Dieselben drei
 * Werte liegen jetzt in den Werten des getragenen Stücks (`werte.stoff =
 * {rauheit, metall, gewebe}`) und gehen damit wie Farbe, Variante und Regler
 * mit der Figur in die Szene.
 *
 * DAS GEWEBE IST EINE NORMALKARTE und ersetzt die des Stücks — eine Daz-Jeans
 * hat eine eigene. Die bleibt am Material gemerkt (`userData.eigeneNormalen`)
 * und kommt zurück, sobald das Gewebe auf „glatt"/aus steht. Die Kachelgröße
 * braucht das Stoffmaß (Meter je UV-Einheit); das GC-Stück bringt es nicht mit,
 * darum wird es am Netz gemessen (`uvMeter`: 3D-Kantenlänge gegen UV-Kantenlänge).
 *
 * Kacheln wie `Garmentstoff.kachel` (Szene) — hier eigen, weil dieses Modul in
 * `gemeinsam/` liegt (Studio und Szene) und nicht in die Szene greifen darf.
 */
export class Stoffwerte {

    static _kacheln = {};
    /** Bis zu so vielen Kanten misst `uvMeter` (jede n-te). */
    static STICHPROBE = 20000;

    /** Die Werte eines getragenen Stücks auf seine Netze; liefert die Zahl der Materialien. */
    static stueck(inst, kennung, werte) {
        const stoff = werte?.stoff;
        if (!stoff || typeof stoff !== 'object') return 0;
        let gesetzt = 0;
        for (const { netz } of Umfaerbung.netze(inst, kennung)) {
            for (const { netz: kind, material } of Umfaerbung.materialien(netz)) {
                if (!Umfaerbung.faerbbar(material)) continue;
                gesetzt += Stoffwerte.material(material, stoff, kind.geometry);
            }
        }
        return gesetzt;
    }

    static material(material, stoff, geometrie = null) {
        if (typeof stoff.rauheit === 'number' && 'roughness' in material) {
            material.roughness = stoff.rauheit;
        }
        if (typeof stoff.metall === 'number' && 'metalness' in material) {
            material.metalness = stoff.metall;
        }
        if (stoff.gewebe && typeof stoff.gewebe === 'object') {
            Stoffwerte.gewebe(material, stoff.gewebe, geometrie);
        }
        material.needsUpdate = true;
        return 1;
    }

    static gewebe(material, gewebe, geometrie) {
        const daten = material.userData;
        if (!('eigeneNormalen' in daten)) daten.eigeneNormalen = material.normalMap || null;
        const art = gewebeart(gewebe.art);
        const staerke = Number(gewebe.staerke);
        const hatUv = !!geometrie?.attributes?.uv;
        if (!hatUv || !art.hoehe || !(staerke > 0)) {
            material.normalMap = daten.eigeneNormalen;
            daten.gewebe = null;
            return 0;
        }
        if (!(daten.uvMeter > 0)) daten.uvMeter = Stoffwerte.uvMeter(geometrie);
        const karte = Stoffwerte.kachel(gewebe.art).clone();
        const wie_oft = Gewebe.wiederholung(
            daten.uvMeter, Gewebe.kachelmeter(Number(gewebe.faeden) || art.faedenJeCm, art.faedenJeKachel));
        karte.repeat.set(wie_oft, wie_oft);
        karte.needsUpdate = true;
        material.normalMap = karte;
        material.normalScale = new THREE.Vector2(staerke, staerke);
        if ('sheenRoughness' in material) material.sheenRoughness = art.glanzstreuung;
        daten.gewebe = { ...gewebe };
        return wie_oft;
    }

    /** Meter Stoff je UV-Einheit: Summe der 3D-Kantenlängen durch die der UV-Kanten. */
    static uvMeter(geometrie) {
        const pos = geometrie?.attributes?.position;
        const uv = geometrie?.attributes?.uv;
        if (!pos || !uv) return 0;
        const index = geometrie.index ? geometrie.index.array : null;
        const n = index ? index.length : pos.count;
        const schritt = Math.max(3, Math.floor(n / Stoffwerte.STICHPROBE / 3) * 3);
        let raum = 0;
        let flaeche = 0;
        for (let i = 0; i + 2 < n; i += schritt) {
            const a = index ? index[i] : i;
            const b = index ? index[i + 1] : i + 1;
            raum += Math.hypot(pos.getX(a) - pos.getX(b), pos.getY(a) - pos.getY(b),
                               pos.getZ(a) - pos.getZ(b));
            flaeche += Math.hypot(uv.getX(a) - uv.getX(b), uv.getY(a) - uv.getY(b));
        }
        return flaeche > 0 ? raum / flaeche : 0;
    }

    static kachel(artname) {
        if (Stoffwerte._kacheln[artname]) return Stoffwerte._kacheln[artname];
        const art = gewebeart(artname);
        const karte = new THREE.DataTexture(
            Gewebe.normalfeld(Gewebe.GROESSE, art.faedenJeKachel, Gewebe.STAERKE, art.hoehe),
            Gewebe.GROESSE, Gewebe.GROESSE, THREE.RGBAFormat);
        karte.wrapS = THREE.RepeatWrapping;
        karte.wrapT = THREE.RepeatWrapping;
        karte.generateMipmaps = true;
        karte.minFilter = THREE.LinearMipmapLinearFilter;
        karte.magFilter = THREE.LinearFilter;
        karte.anisotropy = 16;
        karte.needsUpdate = true;
        Stoffwerte._kacheln[artname] = karte;
        return karte;
    }
}
