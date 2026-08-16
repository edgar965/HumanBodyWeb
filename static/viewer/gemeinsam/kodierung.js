/**
 * Kodierung — Binaerdaten des Servers in Three.js-Puffer umsetzen.
 *
 * WARUM DIESES MODUL (Umbau 15.08.2026): `base64ToFloat32`, `base64ToUint32` und
 * `blenderToThreeCoords` standen SECHSMAL im Projekt — in animations.js,
 * character_core.js, photo_to_3d/helpers.js, scene/utils.js, viewer/utils.js und
 * viewer_compare.js. Alle sechs Fassungen waren funktional gleich und
 * unterschieden sich nur in Variablennamen (`bin` gegen `binary`, `u8` gegen
 * `bytes`). Sechs Kopien heissen: sechs Stellen, an denen eine Korrektur
 * gemacht werden muss — und fuenf, an denen sie vergessen wird.
 *
 * Die alten Fundstellen exportieren jetzt aus diesem Modul weiter, damit die
 * rund 150 Aufrufstellen unveraendert bleiben.
 */

/** base64 -> Float32Array (Vertices, Normalen, Gewichte). */
export function base64ToFloat32(b64) {
    const bytes = base64ToBytes(b64);
    return new Float32Array(bytes.buffer);
}

/** base64 -> Uint32Array (Dreiecksindizes). */
export function base64ToUint32(b64) {
    const bytes = base64ToBytes(b64);
    return new Uint32Array(bytes.buffer);
}

/** base64 -> Uint16Array (Knochenindizes). */
export function base64ToUint16(b64) {
    const bytes = base64ToBytes(b64);
    return new Uint16Array(bytes.buffer);
}

/**
 * Blender (Z oben) -> Three.js (Y oben), IN PLACE.
 *
 * Die Umrechnung ist eine Drehung um die X-Achse: y_neu = z, z_neu = -y. Sie
 * arbeitet auf dem uebergebenen Puffer, um bei 70.000 Vertices keine zweite
 * Kopie anzulegen.
 */
export function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
    return buf;
}

/** base64 -> Uint8Array. Die eine Stelle, an der dekodiert wird. */
function base64ToBytes(b64) {
    const binaer = atob(b64);
    const bytes = new Uint8Array(binaer.length);
    for (let i = 0; i < binaer.length; i++) bytes[i] = binaer.charCodeAt(i);
    return bytes;
}

/** Fassade fuer neuen Code — dieselben Funktionen als Klasse. */
export class Kodierung {
    static zuFloat32(b64) { return base64ToFloat32(b64); }
    static zuUint32(b64) { return base64ToUint32(b64); }
    static zuUint16(b64) { return base64ToUint16(b64); }
    static blenderNachThree(buf) { return blenderToThreeCoords(buf); }
}
