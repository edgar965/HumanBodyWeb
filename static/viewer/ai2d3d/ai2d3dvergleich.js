/**
 * Ai2d3dvergleich — die Genesis-Figur aus der Perspektive eines Fotos rendern und mit dem Foto vergleichen (24.10.2026, Seite „2d-3d-AI“).
 *
 * Edgar: „aus dem Genesis Modell dann wiederum die Fotos aus den gleichen 4 Perspektiven. Diese Ergebnisfotos müssen übereinstimmen mit den Fotos der Eingabe.“ Gemessen wird im Browser:
 * - **Figur im Foto:** Abstand zum Grund (Summe |ΔR|+|ΔG|+|ΔB|) über `SCHWELLE_FOTO`. Gemessen 24.10.2026 an `Olesia1_vorne.jpg` (`_wegwerf/ai2d3d/maske_messen.py`): der Grund ist exakt 25/26/46
 *   (Abstand 0 am Bildrand); mit der ersten Schwelle 36 fielen 91.049 von 529.623 Figurpixeln weg — das schwarze Shirt, die dunklen Jeans. Die Gegenprobe (Wahrheit) lag damit bei 51,5 % statt nahe 100 %.
 * - **Figur im Rendering:** ein zweiter Durchgang auf reinem Grün (`SCHLUESSEL`) — der Umriss hängt so weder am Licht noch an dunkler Kleidung; durchscheinende Haarkarten bleiben durchscheinend
 *   (ein einfarbiges Ersatzmaterial machte aus jeder Karte ein Rechteck).
 * - **Umriss-Deckung** = Schnitt / Vereinigung der beiden Figurflächen (1 = deckungsgleich).
 * - **Farbabstand** = mittleres |Δ| je Kanal (0–255) dort, wo beide Figur sind — Licht der Szene und Netzstufe gehen mit ein, darum ist er auch bei der Wahrheit nicht 0.
 * Die Kamera folgt der Regel der Charakter-Seite (`Ai2d3dkamera`) auf der Hülle der GEZEIGTEN Figur: Größe und Lage werden dabei mit eingepasst — einen Fehler in der Körpergröße zeigt dieser Vergleich nicht.
 * Nur mit bekannter Kamera (Exporte); bei echten Fotos gibt es das Rendering, aber keine Zahl.
 */
import * as THREE from 'three';
import { Mesh3daizeichenflaeche } from '../mesh3dai/mesh3daizeichenflaeche.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';

export class Ai2d3dvergleich {
    static SCHWELLE_FOTO = 9;
    static SCHWELLE_SCHLUESSEL = 60;
    static GRUND = [25, 26, 46];
    static SCHLUESSEL = [0, 255, 0];

    /**
     * Die Figur in eine 2D-Leinwand rendern — mit ihren eigenen Materialien (wie die Fotos), ohne das Ersatzmaterial der Ansichtsart.
     * @param ansicht das Feld der Figur (`Mesh3daiansicht`: Szene, Licht) @param {THREE.Box3} box Hülle im Rahmen der Fotos @param {object} regel `{fov, rand, grund}`
     */
    static rendern(ansicht, box, winkel, rahmen, leinwand, breite, hoehe, regel, grundRgb = regel.grund || Ai2d3dvergleich.GRUND) {
        const kamera = new THREE.PerspectiveCamera(regel.fov, breite / hoehe, 0.01, 100);
        Ai2d3dkamera.stellen(kamera, box, winkel, rahmen, regel.rand);
        kamera.layers.enableAll();
        const grund = new THREE.Color().setRGB(...grundRgb.map(v => v / 255), THREE.SRGBColorSpace).getHex();
        Mesh3daizeichenflaeche.zeichnen(leinwand, breite, hoehe, grund, r => {
            const ersatz = ansicht.szene.overrideMaterial;
            ansicht.szene.overrideMaterial = null;
            r.render(ansicht.szene, kamera);
            ansicht.szene.overrideMaterial = ersatz;
        });
    }

    /** Pixel einer Quelle (Bild oder Leinwand) in der Größe `breite × hoehe`. */
    static _pixel(quelle, breite, hoehe) {
        const l = Object.assign(document.createElement('canvas'), { width: breite, height: hoehe });
        const k = l.getContext('2d', { willReadFrequently: true });
        k.drawImage(quelle, 0, 0, breite, hoehe);
        return k.getImageData(0, 0, breite, hoehe).data;
    }

    static _figur(p, o, g, schwelle) {
        return Math.abs(p[o] - g[0]) + Math.abs(p[o + 1] - g[1]) + Math.abs(p[o + 2] - g[2]) > schwelle;
    }

    /**
     * Foto gegen Rendering. @param {HTMLImageElement} foto @param {HTMLCanvasElement} rendering (auf dem Grund des Fotos) @param {HTMLCanvasElement} maske dasselbe Rendering auf `SCHLUESSEL`
     * @param {HTMLCanvasElement} ueber bekommt die Überlagerung (grau: beide Figur, rot: nur im Foto, türkis: nur im Rendering) @returns {{deckung: number, farbe: number|null, pixel: number}}
     */
    static messen(foto, rendering, maske, ueber, grund = Ai2d3dvergleich.GRUND) {
        const b = rendering.width, h = rendering.height, z = Ai2d3dvergleich;
        const f = z._pixel(foto, b, h), r = z._pixel(rendering, b, h), m = z._pixel(maske, b, h);
        Object.assign(ueber, { width: b, height: h });
        const k = ueber.getContext('2d'), bild = k.createImageData(b, h), aus = bild.data;
        let beide = 0, eines = 0, farbe = 0;
        for (let o = 0; o < aus.length; o += 4) {
            const inF = z._figur(f, o, grund, z.SCHWELLE_FOTO), inR = z._figur(m, o, z.SCHLUESSEL, z.SCHWELLE_SCHLUESSEL);
            let farbeAus = [grund[0], grund[1], grund[2]];
            if (inF && inR) {
                beide++;
                farbe += (Math.abs(f[o] - r[o]) + Math.abs(f[o + 1] - r[o + 1]) + Math.abs(f[o + 2] - r[o + 2])) / 3;
                farbeAus = [150, 150, 150];
            } else if (inF) {
                eines++;
                farbeAus = [230, 60, 60];
            } else if (inR) {
                eines++;
                farbeAus = [40, 200, 210];
            }
            aus.set([...farbeAus, 255], o);
        }
        k.putImageData(bild, 0, 0);
        return { deckung: beide + eines ? beide / (beide + eines) : 0, farbe: beide ? farbe / beide : null, pixel: beide };
    }

    /** Deutsche Zahl mit Prozent bzw. Einheit. */
    static text(m) {
        const p = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1 });
        return `Umriss-Deckung ${p.format(m.deckung * 100)} % · Farbabstand ${m.farbe === null ? '—' : p.format(m.farbe)} / 255`;
    }
}
