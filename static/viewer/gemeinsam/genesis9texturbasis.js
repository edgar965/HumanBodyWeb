/**
 * Genesis9texturbasis — ein Bild als UASTC (KTX2) mit Mip-Stufen (/Charakter/, `Texturweg` 'uastc', Server `G9texturbasis`, 19.10.2026).
 *
 * Datei: `G9KX` · uint32 Kopflänge · Kopf (JSON) · Vorschau (JPEG/PNG) · KTX2 (little-endian). Den KTX2-Teil wandelt three.js' `KTX2Loader` in Workern für die
 * Grafikkarte (hier BC7; ohne BC7 das Beste, was der Browser kann); der Wandler (basis_transcoder, WASM) kommt aus three.js' eigenem Ordner `examples/jsm/libs/basis/`
 * derselben Fassung wie die Importkarte. Das Ergebnis hat dieselbe Form wie ein S3TC-Block (`Genesis9texturblock.lesen`): `{bild, stufen, format, breite, hoehe}` —
 * `Genesis9texturblock.setzen` hängt beides gleich an die Textur. Die Stufen stehen auf dem Kopf (`basisu -y_flip`), `textur.image` ist die Vorschau.
 */
export class Genesis9texturbasis {
    static ART = 'application/x-g9kx';
    static _lader = null;
    static _bereit = null;

    /** Den Lader einrichten (`Texturweg.anmelden`, vor der ersten Figur) — er braucht den Renderer, um zu wissen, welche Formate die Karte kann. */
    static einrichten(renderer) {
        if (!Genesis9texturbasis._bereit) {
            Genesis9texturbasis._bereit = import('three/addons/loaders/KTX2Loader.js').then(({ KTX2Loader }) => {
                const lader = new KTX2Loader().setTranscoderPath(import.meta.resolve('three/addons/libs/basis/'));
                lader.detectSupport(renderer);
                Genesis9texturbasis._lader = lader;
                return lader;
            });
        }
        return Genesis9texturbasis._bereit;
    }

    /** Blob → `{bild, stufen, format, breite, hoehe}`. Wirft, wenn der Wandler nicht lädt oder die Datei kaputt ist (der Aufrufer holt dann den S3TC-Block). */
    static async lesen(blob) {
        if (!Genesis9texturbasis._bereit) throw new Error('KTX2-Lader nicht eingerichtet');
        const puffer = await blob.arrayBuffer();
        const magie = new TextDecoder().decode(new Uint8Array(puffer, 0, 4));
        if (magie !== 'G9KX') throw new Error('kein G9KX-Block');
        const laenge = new DataView(puffer).getUint32(4, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 8, laenge)));
        const lage = 8 + laenge;
        const vorschau = new Blob([new Uint8Array(puffer, lage, kopf.vorschau.bytes)], { type: kopf.vorschau.art });
        const ktx2 = puffer.slice(lage + kopf.vorschau.bytes, lage + kopf.vorschau.bytes + kopf.ktx2);     // eigener Puffer: der Worker übernimmt ihn
        const lader = await Genesis9texturbasis._bereit;
        const [textur, bild] = await Promise.all([
            new Promise((fertig, fehler) => lader.parse(ktx2, fertig, fehler)),
            createImageBitmap(vorschau, { imageOrientation: 'flipY', premultiplyAlpha: 'none' }),
        ]);
        const paket = { bild, stufen: textur.mipmaps, format: textur.format, breite: kopf.breite, hoehe: kopf.hoehe };
        textur.mipmaps = [];
        textur.dispose();                                 // nie hochgeladen — nur die Stufen werden gebraucht
        return paket;
    }
}
