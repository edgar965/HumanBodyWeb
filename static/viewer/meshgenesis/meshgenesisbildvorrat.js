/**
 * Meshgenesisbildvorrat — die Bilder der Anzeigenetze (`Meshgenesisflaechennetz.textur`): jedes Bild GLEICHEN INHALTS einmal dekodiert und einmal auf der Karte (23.11.2026, Edgar:
 * „löse das“ — lange Bilder beim Laden der Foto-Genesis-Testseite).
 *
 * Gemessen an iphone_mit_lidar_dycheck_space_out: die Hose der Kleiderbibliothek hat 13 Materialien mit 13 Bildern `m0.jpg` … `m12.jpg`, alle 2048², alle mit demselben SHA-256; am
 * Oberteil 3 von 4 Alpha-Bildern gleich. Jedes wurde dekodiert und hochgeladen (2048² mit Mip-Stufen) — in den Sekunden danach Bilder von 100–120 ms, in denen der Hauptfaden nichts tat
 * und die Grafikseite arbeitete. Der ETag des Servers (Änderungszeit + Größe) beweist keine Gleichheit; darum hier der Inhalt: Länge und FNV-1a über alle Bytes, bei einem Treffer
 * Byte für Byte verglichen (geht auch ohne `crypto.subtle`, das es über die LAN-Adresse ohne HTTPS nicht gibt). Gleiche Bilder teilen die `Source` der ersten Textur — three.js (r170)
 * lädt eine Quelle mit gleichem Schlüssel (Farbraum, Filter, Anisotropie …) nur einmal hoch (`WebGLTextures.initTexture`); ein anderer Farbraum bekommt weiter seine eigene Kopie.
 *
 * Wie bisher (22.11.2026, Ladezeit des Zauberers): `createImageBitmap` außerhalb des Hauptfadens, `imageOrientation: 'flipY'` statt Threes `flipY` (gilt für Bitmaps nicht), ohne
 * Vormultiplikation und ohne Farbumrechnung — so lud three das `<img>` hoch; auf die Karte je Aufgabe EIN Bild (`Texturweg.einreihen`, 23.11.2026: 18 Kleiderbilder 2048² hielten ein Bild
 * 447 ms an). Scheitert ein Bild, bleibt die Textur leer wie bisher.
 */
import * as THREE from 'three';
import { Pufferabruf } from '../gemeinsam/pufferabruf.js';
import { Texturweg } from '../gemeinsam/texturweg.js';

export class Meshgenesisbildvorrat {
    static OPTIONEN = { imageOrientation: 'flipY', premultiplyAlpha: 'none', colorSpaceConversion: 'none' };
    /** `${Länge}:${FNV}` → [{bytes, erste: THREE.Texture, fertig: Promise (Bild hängt an `erste`)}] */
    static _inhalte = new Map();

    /** Eine Textur, gleich zurück; das Bild kommt nach, dann `danach()`. Farbraum, Anisotropie … setzt der Aufrufer gleich danach (sie gehören zum Schlüssel der geteilten Quelle). */
    static textur(adresse, danach) {
        const textur = new THREE.Texture();
        textur.flipY = false;
        Meshgenesisbildvorrat._einsetzen(adresse, textur).then(danach, () => {});
        return textur;
    }

    static async _einsetzen(adresse, textur) {
        const antwort = await fetch(adresse, { credentials: 'same-origin' });
        if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
        const bytes = new Uint8Array(await antwort.arrayBuffer());
        const schluessel = `${bytes.length}:${Meshgenesisbildvorrat.fnv(bytes)}`;
        const liste = Meshgenesisbildvorrat._inhalte.get(schluessel) ?? [];
        Meshgenesisbildvorrat._inhalte.set(schluessel, liste);
        const gleich = liste.find(e => Meshgenesisbildvorrat.gleich(e.bytes, bytes));
        if (gleich) {
            await gleich.fertig;
            // dieselbe Quelle: three lädt sie nicht noch einmal hoch; `version` statt `needsUpdate` (das erhöhte auch die Fassung der Quelle und lüde neu)
            textur.source = gleich.erste.source;
            textur.version++;
            return;
        }
        const eintrag = { bytes, erste: textur, fertig: null };
        liste.push(eintrag);
        // im Worker (`Pufferabruf.bild`, 23.11.2026): das Spiegeln und Umrechnen beim Auflösen kostete im Hauptfaden 6–13 ms je 2048²-Bild
        eintrag.fertig = Pufferabruf.bild(new Blob([bytes], { type: antwort.headers.get('Content-Type') || '' }), Meshgenesisbildvorrat.OPTIONEN)
            .then(bild => Texturweg.einreihen(textur, () => { textur.image = bild; textur.needsUpdate = true; }));
        await eintrag.fertig;
    }

    /** FNV-1a (32 Bit) über alle Bytes. */
    static fnv(bytes) {
        let h = 0x811c9dc5;
        for (let i = 0; i < bytes.length; i++) h = Math.imul(h ^ bytes[i], 0x01000193);
        return h >>> 0;
    }

    static gleich(a, b) {
        if (a.length !== b.length) return false;
        for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
        return true;
    }
}
