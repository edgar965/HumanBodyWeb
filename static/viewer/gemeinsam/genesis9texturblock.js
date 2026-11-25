import * as THREE from 'three';
import { Pufferabruf } from './pufferabruf.js';

/**
 * Genesis9texturblock — ein Bild als S3TC-Block mit Mip-Stufen (Weg C, `Texturweg`, Server `G9texturblock`, 19.10.2026).
 *
 * Datei: `G9BC` · uint32 Kopflänge · Kopf (JSON) · Vorschau (JPEG/PNG) · Stufe 0 … n (little-endian). Die Stufen stehen schon auf dem Kopf (WebGL dreht komprimierte Daten nicht);
 * die Textur ist eine `CompressedTexture` mit `flipY = false`. `textur.image` ist die Vorschau als Bitmap (gewendet wie jedes Bild des Vorrats) — das lesen die Rechnungen im
 * Browser (Hautton, Karten der Scham, Umfärbung), denn einen Block kann man nicht auf eine Leinwand zeichnen; three.js lädt bei einer `CompressedTexture` nur `mipmaps` hoch.
 */
export class Genesis9texturblock {
    static ART = 'application/x-g9bc';
    static FORMATE = { bc1: THREE.RGB_S3TC_DXT1_Format, bc3: THREE.RGBA_S3TC_DXT5_Format };

    /** Die leere Textur, die Materialien schon bekommen, bevor das Bild da ist. `image` bleibt leer, bis es kommt (`Genesis9texturen.holen` wartet darauf). */
    static leer() {
        const textur = new THREE.CompressedTexture([], 0, 0);
        textur.image = null;
        return textur;
    }

    /** Blob oder Ausschnitt `{puffer, ab}` (eines Bündels, ohne Kopie) → `{bild, stufen, format, breite, hoehe}` (`bild`: Bitmap der Vorschau). */
    static async lesen(quelle) {
        const puffer = quelle.puffer ?? await quelle.arrayBuffer(), ab = quelle.ab || 0;
        if (!Genesis9texturblock.erkannt(puffer, ab)) throw new Error('kein G9BC-Block');
        const laenge = new DataView(puffer).getUint32(ab + 4, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, ab + 8, laenge)));
        let lage = ab + 8 + laenge;
        const vorschau = new Blob([new Uint8Array(puffer, lage, kopf.vorschau.bytes)], { type: kopf.vorschau.art });
        lage += kopf.vorschau.bytes;
        const stufen = kopf.stufen.map(([width, height, bytes]) => {
            const stufe = { width, height, data: new Uint8Array(puffer, lage, bytes) };
            lage += bytes;
            return stufe;
        });
        const bild = await Pufferabruf.bild(vorschau, { imageOrientation: 'flipY', premultiplyAlpha: 'none' });     // im Worker (23.11.2026, `Pufferabruf.bild`)
        return { bild, stufen, format: kopf.format, breite: kopf.breite, hoehe: kopf.hoehe };
    }

    /** Beginnt bei `ab` ein Block (`G9BC`)? */
    static erkannt(puffer, ab = 0) {
        return puffer.byteLength >= ab + 8 && new DataView(puffer).getUint32(ab, false) === 0x47394243;
    }

    static ist(inhalt) {
        return !!inhalt?.stufen;
    }

    /** Den gelesenen Block an die Textur hängen (danach `needsUpdate`). `format` ist 'bc1'/'bc3' (Block) oder schon eine three.js-Konstante (UASTC, `Genesis9texturbasis`). */
    static setzen(textur, paket) {
        textur.mipmaps = paket.stufen;
        textur.format = typeof paket.format === 'number' ? paket.format : Genesis9texturblock.FORMATE[paket.format];
        textur.image = paket.bild;
        textur.userData.blockGroesse = { width: paket.breite, height: paket.hoehe };
    }
}
