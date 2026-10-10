/**
 * Stueckhaut — ein verschweißtes Ersatzstück (Scham aus einer .blend) sieht an der Naht aus wie die Haut (09.10.2026).
 *
 * WARUM (Edgar, 09.10.2026, mit Bild: „der ‚Steg' am Ende der Vulva, zum Anus, der muss weg" und „die Texturanpassung an die
 * Umgebung, warum machst du keine Interpolation der Textur?"): Rand und Normalen des Stücks gehen in die der Haut über, die Farbe
 * und das Licht nicht. Das Stück hat ein einfaches Material (Standard, keine Haut-Zusätze); die Haut hat Durchlicht (Gewicht 0,85, Farbe
 * aus dem Preset, Dünnheit `dicke` je Punkt). Gesehen im Chrome (09.10.2026, „cute girl", Ansicht von hinten unten; Bild, keine
 * Zahl): im untersten Band das Stück grau-braun, die Haut orange; mit dem Durchlicht auf dem Stück (Dünnheit des nächsten
 * Hautpunkts) lag es im Ton der Haut. Gemessen (Texturfarbe ohne Licht, 439 Punkte des Stücks auf der Haut): die Farbkarten liegen
 * im Median 1 % auseinander (Verhältnis 1,01/0,99/0,99), im untersten Band (270 Punkte) 7 % im Grün.
 *
 * HIER, bei jedem Nähen (`hautloch.js`): (1) Das Durchlicht der Haut geht auf das Material des Stücks (`Genesis9haut.durchlicht`), die
 * Dünnheit je Punkt aus dem nächsten Hautpunkt (`dicke`-Attribut). (2) Die Farbe der Haut an der Stelle des Stücks (Mittel der nächsten
 * Hautpunkte, je aus der Karte der eigenen Materialgruppe gelesen) geht als Attribut ans Netz; der Shader mischt sie am Rand in die
 * Farbe des Stücks (`stueckhautpatch.js`, Rechnung `stueckhautrechnung.js`) — nur dort, wo das Stück auf der Haut liegt.
 */
import * as THREE from 'three';
import { Genesis9haut } from './genesis9haut.js';
import { Stueckhautpatch } from './stueckhautpatch.js';
import { Stueckhautrechnung } from './stueckhautrechnung.js';

export class Stueckhaut {

    /** sRGB-Byte → linear (Tabelle). */
    static _LUT = Float32Array.from({ length: 256 }, (_, i) => {
        const c = i / 255;
        return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });
    /** Gelesene Karten (Pixel je Bild), damit jede nur einmal vom Bild geholt wird. */
    static _pixel = new WeakMap();
    /** Halbe Kantenlänge (Texel) des Quadrats, über das die Farbe einer Stelle gemittelt wird. */
    static LESE_R = 2;

    /**
     * @param netz         Netz des Stücks
     * @param koerper      Netz der Haut (`inst.bodyMesh`)
     * @param naht         Ergebnis von `Stuecknaht.verschiebung`
     * @returns Bericht `{mitFarbe, durchlicht}` oder null (nichts zu tun)
     */
    static angleichen(netz, koerper, naht) {
        const hg = koerper?.geometry, g = netz.geometry;
        const uv = hg?.attributes?.uv, normal = hg?.attributes?.normal, voll = hg?.userData?.indexVoll;
        if (!uv || !normal || !voll || !naht.weg) return null;
        const mats = Array.isArray(koerper.material) ? koerper.material : [koerper.material];
        const gruppe = Stueckhaut._gruppen(hg, voll), gemerkt = new Map();
        const farbe = (j) => {
            if (!gemerkt.has(j)) gemerkt.set(j, Stueckhaut._farbe(mats[gruppe[j]], uv.array[2 * j], uv.array[2 * j + 1]));
            return gemerkt.get(j);
        };
        const haut = { pos: hg.attributes.position.array, normal: normal.array, dicke: hg.getAttribute('dicke')?.array || null, farbe };
        const r = Stueckhautrechnung.rechnen(Stueckhaut._lage(g.attributes.position.array, naht.werte), naht, haut);
        Stueckhautpatch.eintragen(netz, r.farbe, r.misch);
        return { mitFarbe: r.mitFarbe, durchlicht: Stueckhaut._durchlicht(netz, g, mats, r.dicke) };
    }

    /** Punkte des Stücks nach dem Randversatz (so liegt es in Ruhelage am Ring). */
    static _lage(punkte, werte) {
        const aus = new Float32Array(punkte.length);
        for (let i = 0; i < aus.length; i++) aus[i] = punkte[i] + (werte ? werte[i] : 0);
        return aus;
    }

    /** Materialgruppe je Hautpunkt (aus dem vollen Index), je Geometrie einmal. */
    static _gruppen(hg, voll) {
        if (hg.userData.punktGruppe?.length === hg.attributes.position.count) return hg.userData.punktGruppe;
        const aus = new Int16Array(hg.attributes.position.count).fill(-1);
        for (const gr of voll.gruppen) for (let k = gr.start; k < gr.start + gr.count; k++) aus[voll.index[k]] = gr.materialIndex;
        hg.userData.punktGruppe = aus;
        return aus;
    }

    /** Die Farbe (linear) der Karte des Materials an der UV-Stelle — Mittel über ein kleines Quadrat; ohne Karte die Farbe des Materials. */
    static _farbe(material, u, v) {
        const bild = material?.map?.image;
        if (!bild?.width) return material?.color ? [material.color.r, material.color.g, material.color.b] : [1, 1, 1];
        let pix = Stueckhaut._pixel.get(bild);
        if (!pix) {
            const c = new OffscreenCanvas(bild.width, bild.height), x = c.getContext('2d', { willReadFrequently: true });
            x.drawImage(bild, 0, 0);
            pix = x.getImageData(0, 0, bild.width, bild.height);
            Stueckhaut._pixel.set(bild, pix);
        }
        // Die Bilder der Haut kommen mit `imageOrientation: 'flipY'` (`genesis9texturen.js`): Zeile = v · Höhe (gemessen 09.10.2026).
        const cx = Math.floor((((u % 1) + 1) % 1) * pix.width), cy = Math.floor(Math.min(0.9999, Math.max(0, v)) * pix.height), r = Stueckhaut.LESE_R;
        const s = [0, 0, 0];
        let n = 0;
        for (let j = -r; j <= r; j++) for (let i = -r; i <= r; i++) {
            const o = 4 * (Math.min(pix.height - 1, Math.max(0, cy + j)) * pix.width + Math.min(pix.width - 1, Math.max(0, cx + i)));
            s[0] += Stueckhaut._LUT[pix.data[o]]; s[1] += Stueckhaut._LUT[pix.data[o + 1]]; s[2] += Stueckhaut._LUT[pix.data[o + 2]]; n++;
        }
        const f = material.color ? [material.color.r, material.color.g, material.color.b] : [1, 1, 1];
        return [s[0] / n * f[0], s[1] / n * f[1], s[2] / n * f[2]];
    }

    /** Das Durchlicht der Haut (das erste Material mit Durchlicht) auf das Material des Stücks und die Dünnheit je Punkt ans Netz — true, wenn es etwas zu tun gab. */
    static _durchlicht(netz, g, mats, dicke) {
        const quelle = mats.map((m) => m?.userData?.genesis9?.durchlicht).find((d) => d);
        if (!quelle || !dicke) return false;
        const rgb = { r: 0, g: 0, b: 0 };
        quelle.farbe.getRGB(rgb, THREE.SRGBColorSpace);
        const alt = g.getAttribute('dicke');
        if (alt && alt.array.length === dicke.length) { alt.array.set(dicke); alt.needsUpdate = true; }
        else g.setAttribute('dicke', new THREE.BufferAttribute(Float32Array.from(dicke), 1));
        const liste = Array.isArray(netz.material) ? netz.material : [netz.material];
        for (const mat of liste) {
            if (mat && !mat.userData?.genesis9?.durchlicht) Genesis9haut.durchlicht(mat, { gewicht: quelle.gewicht, farbe: [rgb.r, rgb.g, rgb.b] });
        }
        return true;
    }
}
