import * as THREE from 'three';

/**
 * Meshfotogewicht — Live-Vorschau der Vertexfarben bei Reglerbewegung (26.09.2026 abends,
 * Edgar: „direkte interaktive Ausgabe des 3D Modells je nach Angabe in den Dialogen").
 *
 * JS-Port von `VideoToBVH/wrappers/mesh_fototextur.py::fototextur_vertexfarben` — DIESELBE
 * Formel (Blickachsen, Gewicht, Bereich, Laplace-Füllung), damit „Textur übernehmen" (Server,
 * echter Export) zum selben Bild führt wie diese Vorschau. Läuft komplett im Browser, ohne
 * Server-Rundtrip — nur die freigestellten Fotos werden einmal geladen.
 *
 * Nur sinnvoll, wenn das Netz Vertexfarben trägt (`textur_quelle` `fotos`/`fusion_fotos`);
 * bei einer Formmodell-eigenen Textur (PBR/Hunyuan-Malerei) bleibt die Vorschau aus.
 */

const ACHSEN = {
    vorne: { blick: [0, 0, 1], u: [-1, 0, 0], v: [0, 1, 0] },
    hinten: { blick: [0, 0, -1], u: [1, 0, 0], v: [0, 1, 0] },
    rechts: { blick: [1, 0, 0], u: [0, 0, 1], v: [0, 1, 0] },
    links: { blick: [-1, 0, 0], u: [0, 0, -1], v: [0, 1, 0] },
};

//: Netze über dieser Eckenzahl bekommen keine Live-Vorschau (der Hauptthread würde spürbar
//: stocken, ohne Web Worker) — „Textur übernehmen" rechnet unabhängig davon serverseitig.
const MAX_LIVE_ECKEN = 300_000;

export class Meshfotogewicht {

    constructor(dateiAdresseFn) {
        this._dateiAdresse = dateiAdresseFn;
        this._bilder = new Map(); // rolle -> {breite, hoehe, daten: Uint8ClampedArray(RGBA)}
    }

    static aktiv(ergebnis) {
        return !!ergebnis && (ergebnis.textur_quelle === 'fotos' || ergebnis.textur_quelle === 'fusion_fotos');
    }

    /** Lädt die freigestellten Fotos der vier Rollen einmalig (Cache bleibt bis zum nächsten Aufruf). */
    async vorbereiten(bilder) {
        this._bilder.clear();
        await Promise.all(bilder
            .filter(b => ACHSEN[b.rolle])
            .map(b => this._bildLaden(b.rolle, b.datei.replace(/\.[^.]+$/, '') + '.png')));
    }

    async _bildLaden(rolle, name) {
        const url = this._dateiAdresse('vorbereitet', name);
        const bild = await new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error('Foto nicht geladen: ' + name));
            img.src = url;
        });
        const leinwand = document.createElement('canvas');
        leinwand.width = bild.width;
        leinwand.height = bild.height;
        const ctx = leinwand.getContext('2d');
        ctx.drawImage(bild, 0, 0);
        this._bilder.set(rolle, { breite: bild.width, hoehe: bild.height, daten: ctx.getImageData(0, 0, bild.width, bild.height).data });
    }

    /** Ob eine Live-Neuberechnung sinnvoll ist (Fotos geladen, Netz nicht zu groß). */
    bereit(anzahlEcken) {
        return this._bilder.size > 0 && anzahlEcken <= MAX_LIVE_ECKEN;
    }

    /** Schreibt neu gemischte Vertexfarben in `geometry` (`bilderZustand`: aktuelle
     *  `{rolle, gewicht, bereich}` je Foto, wie im Formular/Regler gerade eingestellt). */
    anwenden(geometry, bilderZustand) {
        if (!geometry.attributes.normal) geometry.computeVertexNormals();
        const pos = geometry.attributes.position.array;
        const nrm = geometry.attributes.normal.array;
        const n = pos.length / 3;
        const farbe = new Float64Array(n * 3);
        const gewicht = new Float64Array(n);

        for (const rolle of Object.keys(ACHSEN)) {
            const eintrag = bilderZustand.find(b => b.rolle === rolle);
            const bild = this._bilder.get(rolle);
            if (!eintrag || !bild) continue;
            const faktor = (eintrag.gewicht ?? 100) / 100;
            if (faktor <= 0) continue;
            this._rolleAnwenden(ACHSEN[rolle], bild, eintrag.bereich, faktor, pos, nrm, n, farbe, gewicht);
        }

        const ergebnisFarbe = new Float32Array(n * 3);
        const getroffen = new Uint8Array(n);
        for (let i = 0; i < n; i++) {
            if (gewicht[i] > 1e-6) {
                ergebnisFarbe[i * 3] = farbe[i * 3] / gewicht[i];
                ergebnisFarbe[i * 3 + 1] = farbe[i * 3 + 1] / gewicht[i];
                ergebnisFarbe[i * 3 + 2] = farbe[i * 3 + 2] / gewicht[i];
                getroffen[i] = 1;
            } else {
                ergebnisFarbe[i * 3] = ergebnisFarbe[i * 3 + 1] = ergebnisFarbe[i * 3 + 2] = 0.6;
            }
        }
        this._laplaceFuellen(geometry, ergebnisFarbe, getroffen);

        if (!geometry.attributes.color || geometry.attributes.color.array.length !== ergebnisFarbe.length) {
            geometry.setAttribute('color', new THREE.BufferAttribute(ergebnisFarbe, 3));
        } else {
            geometry.attributes.color.array.set(ergebnisFarbe);
            geometry.attributes.color.needsUpdate = true;
        }
    }

    _rolleAnwenden(achsen, bild, bereich, faktor, pos, nrm, n, farbe, gewicht) {
        const { blick, u: uAchse, v: vAchse } = achsen;
        const { breite: w, hoehe: h, daten } = bild;
        const uArr = new Float64Array(n);
        const vArr = new Float64Array(n);
        const blickArr = new Float64Array(n);
        let uMin = Infinity, uMax = -Infinity, vMin = Infinity, vMax = -Infinity;
        for (let i = 0; i < n; i++) {
            const x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
            const u = x * uAchse[0] + y * uAchse[1] + z * uAchse[2];
            const v = x * vAchse[0] + y * vAchse[1] + z * vAchse[2];
            uArr[i] = u;
            vArr[i] = v;
            if (u < uMin) uMin = u;
            if (u > uMax) uMax = u;
            if (v < vMin) vMin = v;
            if (v > vMax) vMax = v;
            blickArr[i] = nrm[i * 3] * blick[0] + nrm[i * 3 + 1] * blick[1] + nrm[i * 3 + 2] * blick[2];
        }
        const spanne = Math.max(uMax - uMin, vMax - vMin, 1e-6) * 1.02; // 2 % Rand wie beim Zuschnitt
        const mitteU = (uMax + uMin) / 2;
        const mitteV = (vMax + vMin) / 2;
        for (let i = 0; i < n; i++) {
            if (blickArr[i] <= 0.15) continue;
            const nu = (uArr[i] - mitteU) / spanne + 0.5;
            const nv = 1 - ((vArr[i] - mitteV) / spanne + 0.5);
            if (nu < 0 || nu >= 1 || nv < 0 || nv >= 1) continue;
            if (bereich && (nu < bereich[0] || nu > bereich[2] || nv < bereich[1] || nv > bereich[3])) continue;
            const px = Math.min(w - 1, Math.max(0, Math.round(nu * (w - 1))));
            const py = Math.min(h - 1, Math.max(0, Math.round(nv * (h - 1))));
            const idxBild = (py * w + px) * 4;
            if (daten[idxBild + 3] <= 8) continue; // Alpha der Freistellung
            const wBlick = Math.min(1, blickArr[i]) ** 2 * faktor;
            farbe[i * 3] += (daten[idxBild] / 255) * wBlick;
            farbe[i * 3 + 1] += (daten[idxBild + 1] / 255) * wBlick;
            farbe[i * 3 + 2] += (daten[idxBild + 2] / 255) * wBlick;
            gewicht[i] += wBlick;
        }
    }

    _laplaceFuellen(geometry, farbe, getroffen, schritte = 8) {
        if (!geometry.index || getroffen.every(x => x)) return;
        const index = geometry.index.array;
        const n = farbe.length / 3;
        const nachbarn = Array.from({ length: n }, () => []);
        for (let f = 0; f < index.length; f += 3) {
            const a = index[f], b = index[f + 1], c = index[f + 2];
            nachbarn[a].push(b, c);
            nachbarn[b].push(a, c);
            nachbarn[c].push(a, b);
        }
        let bekannt = getroffen;
        for (let schritt = 0; schritt < schritte && !bekannt.every(x => x); schritt++) {
            const neu = bekannt.slice();
            for (let i = 0; i < n; i++) {
                if (bekannt[i]) continue;
                let sx = 0, sy = 0, sz = 0, anzahl = 0;
                for (const j of nachbarn[i]) {
                    if (!bekannt[j]) continue;
                    sx += farbe[j * 3]; sy += farbe[j * 3 + 1]; sz += farbe[j * 3 + 2];
                    anzahl++;
                }
                if (anzahl > 0) {
                    farbe[i * 3] = sx / anzahl; farbe[i * 3 + 1] = sy / anzahl; farbe[i * 3 + 2] = sz / anzahl;
                    neu[i] = 1;
                }
            }
            bekannt = neu;
        }
    }
}
