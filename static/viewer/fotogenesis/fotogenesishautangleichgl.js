/**
 * Fotogenesishautangleichgl — rechnet die Hautkacheln eines Tests auf der Karte des Browsers neu, sobald ein Regler sich bewegt (05.11.2026, `Fotogenesishautangleich`).
 *
 * Für jede Kachel EIN Ziel im Renderer der Seite (`Meshgenesiszeichenflaeche`): erst das Original über die ganze Kachel, dann die Dreiecke des Genesis-Netzes im UV-Raum, jedes ein paar Pixel größer,
 * damit der Rand der Inseln mitkommt. Je Punkt die Tonverschiebung Δ (Log von linear RGB) und der Anteil der neuen Zeichnung, zwischen den Punkten dieselbe Mischung wie `Hautangleich._texel`.
 * Farbe = mix(Original, Zeichnung, Anteil) · e^Δ. Der Rest des Bilds (Haare, Flecken, Brustwarzen) bleibt also, bis „Zeichnung ersetzen“ ihn auf ungesehener Haut tauscht; beide Bilder tragen denselben Ton. Das Ziel ist SRGB8_ALPHA8: Der Shader schreibt linear, die Karte kodiert. Aus demselben Ziel kommt das JPEG beim Speichern.
 * Die Kachel ersetzt die Bilder der Figur nur beim Zeichnen (`Fotogenesishautangleich._tauschen`); andere Bilder im Feld bleiben unberührt.
 */
import * as THREE from 'three';

const ECKEN = `precision highp float;
precision highp int;
precision highp sampler2D;
in vec3 position;
uniform sampler2D uDelta;
out vec2 vUv;
out vec4 vDelta;
void main() {
    vUv = position.xy;
    int i = int(position.z + 0.5);
    vDelta = position.z < 0.0 ? vec4(0.0) : texelFetch(uDelta, ivec2(i % ${512}, i / ${512}), 0);
    gl_Position = vec4(position.xy * 2.0 - 1.0, 0.0, 1.0);
}`;

const FLAECHE = `precision highp float;
in vec2 vUv;
in vec4 vDelta;
uniform sampler2D uBild;
uniform sampler2D uZeichnung;
out vec4 farbe;
void main() {
    farbe = vec4(mix(texture(uBild, vUv).rgb, texture(uZeichnung, vUv).rgb, vDelta.a) * exp(vDelta.rgb), 1.0);
}`;

export class Fotogenesishautangleichgl {
    static BREITE = 512;
    /** So viele Pixel wachsen die Dreiecke nach außen. */
    static RAND = 2.5;

    /**
     * @param {THREE.WebGLRenderer} renderer @param kopf `felder.json` @param {Float32Array} felder @param {ArrayBuffer} netz
     * @param originale {kachel: THREE.Texture} @param zeichnung {kachel: THREE.Texture} gleicher Ton, Zeichnung gesehener Haut (`Hautzeichnung`)
     * @param vorlage Karte der Figur, deren Filter das Ziel übernimmt
     */
    constructor(renderer, kopf, felder, netz, originale, zeichnung, vorlage) {
        this.renderer = renderer;
        this.kopf = kopf;
        this.felder = felder;
        const b = Fotogenesishautangleichgl.BREITE;
        this.delta = new Float32Array(b * Math.ceil(kopf.punkte / b) * 4);
        this.deltabild = new THREE.DataTexture(this.delta, b, Math.ceil(kopf.punkte / b), THREE.RGBAFormat, THREE.FloatType);
        this.deltabild.minFilter = this.deltabild.magFilter = THREE.NearestFilter;
        this.kamera = new THREE.Camera();
        this.kacheln = new Map(kopf.kacheln.map(k => [k.kachel, this._kachel(k, netz, originale[k.kachel], zeichnung[k.kachel], vorlage)]));
    }

    _kachel(k, netz, original, zeichnung, vorlage) {
        const uv = new Float32Array(netz, k.uv_ab, k.dreiecke * 6), punkte = new Uint32Array(netz, k.punkte_ab, k.dreiecke * 3);
        const lage = new Float32Array((k.dreiecke * 3 + 6) * 3), rand = Fotogenesishautangleichgl.RAND / this.kopf.seite;
        lage.set([0, 0, -1, 1, 0, -1, 1, 1, -1, 0, 0, -1, 1, 1, -1, 0, 1, -1]);
        for (let t = 0; t < k.dreiecke; t++) {
            const mx = (uv[t * 6] + uv[t * 6 + 2] + uv[t * 6 + 4]) / 3, my = (uv[t * 6 + 1] + uv[t * 6 + 3] + uv[t * 6 + 5]) / 3;
            for (let e = 0; e < 3; e++) {
                const x = uv[t * 6 + e * 2], y = uv[t * 6 + e * 2 + 1], l = Math.hypot(x - mx, y - my) || 1, ziel = 18 + (t * 3 + e) * 3;
                lage[ziel] = x + (x - mx) / l * rand;
                lage[ziel + 1] = y + (y - my) / l * rand;
                lage[ziel + 2] = punkte[t * 3 + e];
            }
        }
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        const material = new THREE.RawShaderMaterial({ glslVersion: THREE.GLSL3, vertexShader: ECKEN, fragmentShader: FLAECHE, depthTest: false, depthWrite: false, side: THREE.DoubleSide,
                                                      uniforms: { uDelta: { value: this.deltabild }, uBild: { value: original }, uZeichnung: { value: zeichnung } } });
        const netzteil = new THREE.Mesh(geo, material);
        netzteil.frustumCulled = false;
        const szene = new THREE.Scene();
        szene.add(netzteil);
        const ziel = new THREE.WebGLRenderTarget(this.kopf.seite, this.kopf.seite, { colorSpace: THREE.SRGBColorSpace, depthBuffer: false, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter,
                                                                                     magFilter: THREE.LinearFilter, wrapS: vorlage.wrapS, wrapT: vorlage.wrapT, anisotropy: vorlage.anisotropy });
        return { szene, ziel };
    }

    /**
     * Δ je Punkt aus den Reglern (`bezug` −1…1, sonst 0…1), wie `Hautangleich.delta`: d = B − T, dunkler als der Bezug zieht `dunkel`, heller zieht `hell`, wenig Vertrauen zieht `unsichtbar` in beide
     * Richtungen. Die Züge rechnen zusammen, 1 − (1 − a)(1 − u): Kein Griff überdeckt den anderen, nur der Weg zum Bezug wird kürzer. `bezug` verschiebt die ganze Haut.
     * Alpha: Anteil des Bilds mit der neuen Zeichnung, (1 − v) · `zeichnung`. Alles auf 0 lässt die Haut, wie sie ist. Spalten von `felder.bin`: T, B nah, B weit (je 3), v, Gewicht.
     */
    _rechnen({ dunkel, hell, unsichtbar, zeichnung, bezug, reichweite }) {
        const f = this.felder, d = this.delta, { punkte, spalten, weich_log: weich, bezug_log: spanne } = this.kopf, r = reichweite, k = bezug * spanne;
        for (let i = 0; i < punkte; i++) {
            const a = i * spalten, w = f[a + 10];
            const d0 = (1 - r) * f[a + 3] + r * f[a + 6] - f[a], d1 = (1 - r) * f[a + 4] + r * f[a + 7] - f[a + 1], d2 = (1 - r) * f[a + 5] + r * f[a + 8] - f[a + 2];
            const s = Math.min(Math.max(((d0 + d1 + d2) / 3 + weich) / (2 * weich), 0), 1);
            const zug = 1 - (1 - (hell + (dunkel - hell) * s * s * (3 - 2 * s))) * (1 - (1 - f[a + 9]) * unsichtbar);
            d[i * 4] = w * (zug * d0 + k);
            d[i * 4 + 1] = w * (zug * d1 + k);
            d[i * 4 + 2] = w * (zug * d2 + k);
            d[i * 4 + 3] = w * (1 - f[a + 9]) * zeichnung;
        }
        this.deltabild.needsUpdate = true;
    }

    /** Alle Kacheln nach den Reglern neu. */
    anwenden(werte) {
        this._rechnen(werte);
        const r = this.renderer, vorher = r.getRenderTarget(), auto = r.autoClear;
        r.autoClear = false;
        for (const { szene, ziel } of this.kacheln.values()) {
            r.setRenderTarget(ziel);
            r.render(szene, this.kamera);
        }
        r.setRenderTarget(vorher);
        r.autoClear = auto;
    }

    /** Die Kachel als JPEG (Blob), oben = Bildzeile 0 wie die Datei. */
    async jpeg(kachel) {
        const s = this.kopf.seite, roh = new Uint8Array(s * s * 4);
        this.renderer.readRenderTargetPixels(this.kacheln.get(kachel).ziel, 0, 0, s, s, roh);
        const leinwand = document.createElement('canvas');
        leinwand.width = leinwand.height = s;
        const bild = new ImageData(s, s);
        for (let y = 0; y < s; y++) bild.data.set(roh.subarray((s - 1 - y) * s * 4, (s - y) * s * 4), y * s * 4);
        leinwand.getContext('2d').putImageData(bild, 0, 0);
        return new Promise((fertig, fehler) => leinwand.toBlob(b => (b ? fertig(b) : fehler(new Error('JPEG nicht erzeugt'))), 'image/jpeg', 0.94));
    }
}
