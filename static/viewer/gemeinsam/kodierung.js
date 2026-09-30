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

/**
 * Ein Feld, das SCHON ein Puffer ist (Binärpaket), als EIGENE Kopie.
 *
 * WARUM DIESE FUNKTION (30.09.2026): Seit die Netzdaten als Binärpaket kommen
 * (`netzpaket.js`), steht in `daten.vertices` kein base64-String mehr, sondern fertig
 * ein `Float32Array`. Diese eine Stelle macht daraus einen Umbau von drei Funktionen
 * statt von ~150 Aufrufstellen: `base64ToFloat32(daten.vertices)` bleibt überall stehen.
 * Eine Antwort, die noch JSON liefert, läuft weiter über base64 — beide Formen dürfen
 * nebeneinander leben, bis jeder Weg umgestellt ist.
 *
 * WARUM KOPIERT WIRD, OBWOHL DAS PAKET GERADE DAS SPAREN SOLLTE: `blenderToThreeCoords`
 * arbeitet IN PLACE, und zwar an sechs Stellen (`netzgeometrie.js`, `netzpunkte.js` ×3,
 * `mhproxy_verformung.js`, `vergleichsnetz.js`). Aus base64 kam bisher immer ein frischer
 * Puffer, also war das sicher. Eine Sicht auf den Antwortpuffer wäre es nicht: Wer
 * dasselbe Feld zweimal liest, dreht zweimal — und bekommt eine Figur, die um 90° gekippt
 * neben der Szene liegt, ohne Fehlermeldung. Genau davor warnt der Kopf von
 * `netzgeometrie.js`, weil es dort schon einmal passiert ist.
 *
 * Die Kopie ist ein `memcpy` und damit weit billiger als das, was sie ersetzt (base64
 * dekodieren: 83 ms je 42 MB, gemessen 18.09.2026). Der Gewinn des Pakets bleibt: ein
 * Drittel weniger Bytes auf der Leitung, kein base64 auf beiden Seiten, kein JSON-Parse
 * über einen hundert Megabyte langen String.
 *
 * Der Typ wird NICHT umgedeutet: Wer `base64ToUint32` auf ein Float32Array ruft, hat auf
 * dem Server den falschen Typ gesetzt — das gehört dort behoben (`Netzfeld.ERLAUBT`),
 * eine Umdeutung hier würde die Bytes still verfälschen.
 */
function eigeneKopie(wert) {
    return ArrayBuffer.isView(wert) ? wert.slice() : null;
}

/** base64 (oder fertiger Puffer) -> Float32Array (Vertices, Normalen, Gewichte). */
export function base64ToFloat32(b64) {
    const fertig = eigeneKopie(b64);
    if (fertig) return fertig;
    const bytes = base64ToBytes(b64);
    return new Float32Array(bytes.buffer);
}

/** base64 (oder fertiger Puffer) -> Uint32Array (Dreiecksindizes). */
export function base64ToUint32(b64) {
    const fertig = eigeneKopie(b64);
    if (fertig) return fertig;
    const bytes = base64ToBytes(b64);
    return new Uint32Array(bytes.buffer);
}

/** base64 (oder fertiger Puffer) -> Uint16Array (Knochenindizes). */
export function base64ToUint16(b64) {
    const fertig = eigeneKopie(b64);
    if (fertig) return fertig;
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

/**
 * Typisierten Puffer -> base64. Die eine Stelle, an der kodiert wird.
 *
 * WARUM STUECKWEISE (28.08.2026, Befund `doppelcode`): Es gab VIER Fassungen
 * in drei Bauarten. Zwei arbeiteten stueckweise wie hier, die dritte
 * (`viewer/utils.js`) haengte Zeichen fuer Zeichen an eine Zeichenkette an —
 * bei 70.851 Punkten sind das 850.212 Durchlaeufe mit je einer neuen
 * Zeichenkette. `String.fromCharCode.apply` auf Stuecken von 32.768 Bytes
 * macht daraus 26 Aufrufe.
 *
 * Die Stueckgroesse ist kein Feinschliff: `apply` legt jedes Byte als eigenes
 * Argument auf den Aufrufstapel. Bei einem Puffer am Stueck (850 KB) ist das
 * ein `RangeError: Maximum call stack size exceeded` — genau deshalb steht in
 * den beiden aelteren Fassungen dieselbe Zahl.
 *
 * Der TYP spielt beim Kodieren keine Rolle: Gelesen werden die Bytes. Die
 * beiden benannten Fassungen darunter gibt es nur, damit an der Aufrufstelle
 * steht, was drinsteckt.
 */
export function pufferZuBase64(puffer) {
    const bytes = new Uint8Array(puffer.buffer, puffer.byteOffset,
                                 puffer.byteLength);
    const stueck = 32768;
    let binaer = '';
    for (let i = 0; i < bytes.length; i += stueck) {
        binaer += String.fromCharCode.apply(
            null, bytes.subarray(i, Math.min(i + stueck, bytes.length)));
    }
    return btoa(binaer);
}

/** Float32Array -> base64 (Punkte, Normalen, Gewichte, Matrizen). */
export function float32ToBase64(f32) { return pufferZuBase64(f32); }

/** Uint32Array -> base64 (Dreiecksindizes). */
export function uint32ToBase64(u32) { return pufferZuBase64(u32); }

/**
 * base64 -> Uint8Array. Die eine Stelle, an der dekodiert wird (auch fuer uint8-Gewichte).
 *
 * `Uint8Array.fromBase64` (Chrome 140+) statt `atob` + Schleife: gemessen an 42 MB
 * (Ursula Stufe 2) 83 ms gegen 955 ms — die Schleife war der groesste Posten
 * des Browsers je Netzbau (18.09.2026 nachts). Ohne die Funktion der alte Weg.
 */
export function base64ToBytes(b64) {
    // Aus einem Binärpaket kommen die uint8-Gewichte schon als Puffer (`eigenhaut.js`,
    // Kodierung `u16u8`) — dann ist nichts zu dekodieren.
    if (ArrayBuffer.isView(b64)) {
        return b64 instanceof Uint8Array
            ? b64 : new Uint8Array(b64.buffer, b64.byteOffset, b64.byteLength);
    }
    if (typeof Uint8Array.fromBase64 === 'function') return Uint8Array.fromBase64(b64);
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
    static ausFloat32(f32) { return float32ToBase64(f32); }
    static ausUint32(u32) { return uint32ToBase64(u32); }
}
