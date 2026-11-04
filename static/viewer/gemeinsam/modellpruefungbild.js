import * as THREE from 'three';
import { Gezeichneterpunkt } from './gezeichneterpunkt.js';

/**
 * Modellpruefungbild — die Bilder der Modellprüfung (`Modellpruefung`, 02.11.2026): eigener Renderer (600 × 800), ohne Szenenlicht, Grund blau. Was rot gezeichnet
 * wird, ist ein Befund: der Körper, wo Stoff sein muss (Deckung), die Fußhaut von unten (Schuhe). Die Frisur allein unter weißem Licht für die Farbprobe.
 *
 * Während `zeichnen…` läuft, sind die übrigen Kinder der Szene aus, der Körper trägt ein Farbmaterial (rot/schwarz je Punkt) — alles synchron, ohne `await`, damit
 * die Szene dazwischen kein Bild zeichnet; `ende()` stellt alles zurück.
 * Mit `mitMarken` trägt jede Ansicht die Prüfpunkte ein, die dort auf einem roten Pixel vorn liegen (`_sicht`, Tiefe auf SICHT_M) — die Marken der 3D-Ansicht.
 */
export class Modellpruefungbild {

    static B = 600;
    static H = 800;
    static SICHT_M = 0.01;
    static ANSICHTEN = [['vorne', 0, 1, 0], ['links', 1, 0, 0], ['rechts', -1, 0, 0], ['hinten', 0, -1, 0], ['vorne_links', Math.SQRT1_2, Math.SQRT1_2, 0],
        ['vorne_rechts', -Math.SQRT1_2, Math.SQRT1_2, 0], ['hinten_links', Math.SQRT1_2, -Math.SQRT1_2, 0], ['hinten_rechts', -Math.SQRT1_2, -Math.SQRT1_2, 0],
        ['oben', 0, 0.6, 0.8]];        // keine Ansicht von unten: unter den Rock zu sehen ist kein Fehler

    constructor(inst, mitBildern, mitMarken = false) {
        this.inst = inst;
        this.mitBildern = mitBildern;
        this.mitMarken = mitMarken;
        this.bilder = [];
        const { B, H } = Modellpruefungbild;
        this.r = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
        this.r.setPixelRatio(1); this.r.setSize(B, H, false); this.r.outputColorSpace = THREE.SRGBColorSpace; this.r.setClearColor(0x0000ff, 1);
        const leinwand = document.createElement('canvas'); leinwand.width = B; leinwand.height = H;
        this.ctx = leinwand.getContext('2d', { willReadFrequently: true });
        this.kam = new THREE.PerspectiveCamera(30, B / H, 0.05, 60);
        this.rote = new Map();          // Farbmaterial je Material der Szene, mit dessen lageverändernden Eingriffen (`Gezeichneterpunkt.eingriffe`)
        this.zurueck = [];
    }

    /** Szene vorbereiten: andere Kinder aus, Hintergrund weg, Körper mit Punktfarbe `farbe` (Float32Array 3n, Rot = Befund), `aus` (Netze) unsichtbar. */
    anfangen(farbe, aus = []) {
        const g = this.inst.group, szene = g.parent;
        const andere = szene.children.filter((c) => c !== g && c.visible);
        g.traverse((o) => { if (o.visible && (o.isLine || o.isPoints || o.isSprite || /Helper/.test(o.type))) andere.push(o); });     // Skelettlinien u. Ä.
        const hg = szene.background, sicht = aus.map((o) => o.visible);
        andere.forEach((c) => { c.visible = false; });
        aus.forEach((o) => { o.visible = false; });
        szene.background = null;
        this.zurueck.push(() => {
            aus.forEach((o, i) => { o.visible = sicht[i]; });
            szene.background = hg;
            andere.forEach((c) => { c.visible = true; });
        });
        this.farbe = this._punktfarbe(this.inst.bodyMesh, farbe);
    }

    /** Netze mit Punktfarbe: je Netz `werte[k]` (je Punkt 1 = rot, 0 = schwarz) — das Daz-Anatomie-Stück, rot nur unter Stoff (`Modellpruefungdeckung`). */
    punktfarben(netze, werte) {
        netze.forEach((o, k) => {
            const f = new Float32Array(3 * werte[k].length);
            werte[k].forEach((w, i) => { f[3 * i] = w; });
            this._punktfarbe(o, f);
        });
    }

    /**
     * `netz` zeichnet bis `ende()` mit der Punktfarbe `farbe` (Float32Array 3n) → das Farbattribut. Die Punkte liegen wie in der Szene (Hauteinzug, Naht,
     * Weichgewebe) — ohne den Einzug stach das Anatomie-Stück unter der Hose durch (Damira, 02.11.2026 abends; `Gezeichneterpunkt`).
     */
    _punktfarbe(netz, farbe) {
        const geo = netz.geometry, vorher = geo.getAttribute('color'), stoff = netz.material;
        geo.setAttribute('color', new THREE.BufferAttribute(farbe, 3));
        netz.material = Array.isArray(stoff) ? stoff.map((s) => this._rot(s)) : this._rot(stoff);
        this.zurueck.push(() => {
            netz.material = stoff;
            if (vorher) geo.setAttribute('color', vorher); else geo.deleteAttribute('color');
        });
        return geo.getAttribute('color');
    }

    _rot(quelle) {
        if (!this.rote.has(quelle)) this.rote.set(quelle, Gezeichneterpunkt.eingriffe(quelle, new THREE.MeshBasicMaterial({ vertexColors: true })));
        return this.rote.get(quelle);
    }

    /** Ein Bild → `{rot, schwarz, hell, mittel}` (Grund blau zählt nicht). */
    zeichnen(rolle, kamera) {
        const { B, H } = Modellpruefungbild;
        this.r.render(this.inst.group.parent, kamera);
        this.ctx.clearRect(0, 0, B, H); this.ctx.drawImage(this.r.domElement, 0, 0);
        if (this.mitBildern) this.bilder.push({ rolle, url: this.r.domElement.toDataURL('image/png') });
        const px = this.ctx.getImageData(0, 0, B, H).data;
        let rot = 0, schwarz = 0, hell = 0;
        const summe = [0, 0, 0];
        for (let i = 0; i < px.length; i += 4) {
            const r = px[i], g = px[i + 1], b = px[i + 2];
            if (b > 200 && r < 40 && g < 40) continue;
            if (r > 128 && g < 60 && b < 60) rot++;
            else if (r + g + b < 30) schwarz++;
            else { hell++; summe[0] += r; summe[1] += g; summe[2] += b; }
        }
        return { rot, schwarz, hell, mittel: summe.map((s) => Math.round(s / Math.max(hell, 1))) };
    }

    /** Neun Ansichten um die Hülle (Mitte, Höhe) → `[{rolle, rote_px}]`; `punkte` (Prüfpunkte, siehe `_sicht`) auf rotem Pixel vorn werden markiert. */
    rundum(mitte, hoehe, punkte = []) {
        const ab = hoehe / 2 / Math.tan(15 * Math.PI / 180) * 1.1, aus = [];
        for (const [rolle, rx, rz, ry] of Modellpruefungbild.ANSICHTEN) {
            this.kam.position.set(mitte.x + rx * ab, mitte.y + ry * ab, mitte.z + rz * ab);
            this.kam.up.set(0, 1, 0); this.kam.lookAt(mitte); this.kam.updateMatrixWorld(true); this.kam.updateProjectionMatrix();
            aus.push({ rolle, rote_px: this.zeichnen(`deckung_${rolle}`, this.kam).rot });
            this._markieren(this.kam, punkte);
        }
        return aus;
    }

    /** Wie das letzte Bild, aber mit Tiefe: `punkte` vorn auf rotem Pixel markieren (nur mit `mitMarken`). */
    _markieren(kamera, punkte) {
        if (!this.mitMarken || !punkte.length) return;
        const sichtbar = [];
        this.inst.group.traverseVisible((o) => { if (o.isMesh) sichtbar.push(o); });
        const t = this.tiefe(kamera, sichtbar), f = t.farbe;
        for (const p of punkte) this._sicht(kamera, t.tiefe, p, (j) => f[4 * j] > 128 && f[4 * j + 1] < 60 && f[4 * j + 2] < 60);
    }

    /**
     * Prüfpunkt `p = {lage: Float32Array 3m (Welt), idx: [Punkt …], marke: Uint8Array m}`: jeder Punkt aus `idx`, der in `kamera` innerhalb des Bildes auf ein Pixel mit
     * `treffer(j)` fällt und dort vorn liegt (Abstand zur Tiefe `tiefe` < SICHT_M), bekommt `marke` = 1. Pixel j zählt von unten (wie `readRenderTargetPixels`).
     */
    _sicht(kamera, tiefe, p, treffer) {
        const { B, H, SICHT_M } = Modellpruefungbild, v = new THREE.Vector3(), e = kamera.matrixWorldInverse.elements;
        const m = new THREE.Matrix4().multiplyMatrices(kamera.projectionMatrix, kamera.matrixWorldInverse);
        for (const i of p.idx) {
            const x = p.lage[3 * i], y = p.lage[3 * i + 1], z = p.lage[3 * i + 2];
            v.set(x, y, z).applyMatrix4(m);
            const px = Math.floor((v.x + 1) / 2 * B), py = Math.floor((v.y + 1) / 2 * H);
            if (px < 0 || py < 0 || px >= B || py >= H) continue;
            const j = py * B + px, d = tiefe[4 * j], vz = -(e[2] * x + e[6] * y + e[10] * z + e[14]);
            if (d > 0 && Math.abs(d - vz) < SICHT_M && treffer(j)) p.marke[i] = 1;
        }
    }

    /**
     * Stoff, der auf grüner Haut liegt (Punktfarbe G, z. B. die Hände): sechs Nahbilder um `kiste`, je Bild Haut nur mit dem Körper, Tiefe des Körpers und der
     * `schalen` getrennt — Stoff zählt, wo er höchstens `aufM` vor der Haut liegt (ein Ärmel, der davor hängt, liegt weiter weg). → schlechteste Ansicht
     * `{rolle, haut_px, auf_px, anteil}`. `punkte`: Handpunkte und (mit `stoff`) gebackene Schalenpunkte, markiert, wo sie auf einem solchen Pixel vorn liegen.
     */
    stoffAuf(kiste, koerper, schalen, rolle, aufM, punkte = []) {
        const { B, H } = Modellpruefungbild;
        const m = kiste.getCenter(new THREE.Vector3()), s = kiste.getSize(new THREE.Vector3());
        const ab = (Math.max(s.x, s.y, s.z) / 2 + 0.03) / Math.tan(15 * Math.PI / 180);
        let schlecht = { rolle, haut_px: 0, auf_px: 0, anteil: 0 }, bild = null;
        for (const [name, rx, ry, rz] of [['vorne', 0, 0, 1], ['hinten', 0, 0, -1], ['links', 1, 0, 0], ['rechts', -1, 0, 0], ['oben', 0, 1, 0], ['unten', 0, -1, 0]]) {
            this.kam.position.set(m.x + rx * ab, m.y + ry * ab, m.z + rz * ab);
            this.kam.up.set(0, ry ? 0 : 1, ry ? -1 : 0); this.kam.lookAt(m); this.kam.updateMatrixWorld(true); this.kam.updateProjectionMatrix();
            const k = this.tiefe(this.kam, [koerper]), st = this.tiefe(this.kam, schalen);
            let haut = 0, auf = 0;
            const rot = new Uint8Array(B * H);
            for (let i = 0; i < B * H; i++) {
                if (!(k.farbe[4 * i + 1] > 128 && k.farbe[4 * i] < 60)) continue;
                haut++;
                const dk = k.tiefe[4 * i], ds = st.tiefe[4 * i];
                if (ds > 0 && ds < dk && dk - ds < aufM) { auf++; rot[i] = 1; }
            }
            if (this.mitMarken) for (const p of punkte) this._sicht(this.kam, p.stoff ? st.tiefe : k.tiefe, p, (j) => rot[j]);
            const besser = haut > 0 && (!schlecht.haut_px || auf > schlecht.auf_px);         // schlechteste Ansicht, sonst die erste mit Haut
            if (besser) schlecht = { rolle: `${rolle}_${name}`, haut_px: haut, auf_px: auf, anteil: +(auf / haut).toFixed(4) };
            if (this.mitBildern && (besser || !bild)) bild = { rolle, k, rot };
        }
        if (bild) {                                                     // Haut grau, Stoff auf der Haut rot, Grund blau; Zeilen von unten nach oben gelesen
            const d = this.ctx.createImageData(B, H);
            for (let y = 0; y < H; y++) for (let x = 0; x < B; x++) {
                const i = (H - 1 - y) * B + x, o = 4 * (y * B + x), leer = bild.k.tiefe[4 * i] <= 0;
                d.data.set(bild.rot[i] ? [255, 0, 0, 255] : (leer ? [0, 0, 255, 255] : [90, 90, 90, 255]), o);
            }
            this.ctx.putImageData(d, 0, 0);
            this.bilder.push({ rolle: bild.rolle, url: this.ctx.canvas.toDataURL('image/png') });
        }
        return schlecht;
    }

    /** Ein Bild mit nur `sichtbar` → `{farbe: RGBA Uint8, tiefe: Float32 (R = Abstand vor der Kamera in m, ≤ 0 = leer)}`, Zeilen von unten. */
    tiefe(kamera, sichtbar) {
        const { B, H } = Modellpruefungbild;
        const g = this.inst.group, szene = g.parent, vorher = [];
        if (!this.ziel) {
            this.ziel = new THREE.WebGLRenderTarget(B, H, { depthTexture: new THREE.DepthTexture(B, H), depthBuffer: true });
            this.lin = new THREE.WebGLRenderTarget(B, H, { type: THREE.FloatType });
            this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
                uniforms: { tiefe: { value: null }, nah: { value: 0.05 }, fern: { value: 60 }, ortho: { value: 0 } },
                vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4( position.xy, 0.0, 1.0 ); }',
                fragmentShader: `#include <packing>
uniform sampler2D tiefe; uniform float nah; uniform float fern; uniform float ortho; varying vec2 vUv;
void main() { float d = texture2D( tiefe, vUv ).x;
    float z = ortho > 0.5 ? orthographicDepthToViewZ( d, nah, fern ) : perspectiveDepthToViewZ( d, nah, fern );
    gl_FragColor = vec4( d >= 1.0 ? -1.0 : -z, 0.0, 0.0, 1.0 ); }`,
            }));
            this.quadSzene = new THREE.Scene(); this.quadSzene.add(this.quad);
            this.quadKam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        }
        g.traverse((o) => { if (o.isMesh) { vorher.push([o, o.visible]); o.visible = sichtbar.includes(o); } });
        try {
            this.r.setRenderTarget(this.ziel); this.r.render(szene, kamera);
            const farbe = new Uint8Array(4 * B * H), tiefe = new Float32Array(4 * B * H);
            this.r.readRenderTargetPixels(this.ziel, 0, 0, B, H, farbe);
            Object.assign(this.quad.material.uniforms, { tiefe: { value: this.ziel.depthTexture }, nah: { value: kamera.near }, fern: { value: kamera.far },
                ortho: { value: kamera.isOrthographicCamera ? 1 : 0 } });
            this.r.setRenderTarget(this.lin); this.r.render(this.quadSzene, this.quadKam);
            this.r.readRenderTargetPixels(this.lin, 0, 0, B, H, tiefe);
            return { farbe, tiefe };
        } finally {
            this.r.setRenderTarget(null);
            for (const [o, v] of vorher) o.visible = v;
        }
    }

    /** Senkrecht von unten auf die Kiste der Füße (orthografisch); `punkte` wie bei `rundum`. */
    vonUnten(kiste, punkte = []) {
        const { B, H } = Modellpruefungbild;
        const m = kiste.getCenter(new THREE.Vector3()), s = kiste.getSize(new THREE.Vector3()), halb = Math.max(s.x, s.z * H / B) / 2 + 0.05;
        const ortho = new THREE.OrthographicCamera(-halb, halb, halb * H / B, -halb * H / B, 0.01, 10);
        ortho.position.set(m.x, kiste.min.y - 1, m.z); ortho.up.set(0, 0, -1); ortho.lookAt(m.x, kiste.min.y + 1, m.z);
        ortho.updateMatrixWorld(true); ortho.updateProjectionMatrix();
        const z = this.zeichnen('fuesse_unten', ortho);
        this._markieren(ortho, punkte);
        return z;
    }

    /** Nur `netze` sichtbar, weißes Licht, Blick von vorn. */
    allein(netze, rolle) {
        const g = this.inst.group, szene = g.parent, sicht = new Map();
        g.traverse((o) => { if (o.isMesh) { sicht.set(o, o.visible); o.visible = netze.includes(o); } });
        const licht = new THREE.HemisphereLight(0xffffff, 0xffffff, 2.5);
        szene.add(licht);
        try {
            const kiste = new THREE.Box3(); netze.forEach((o) => kiste.expandByObject(o));
            const m = kiste.getCenter(new THREE.Vector3()), s = Math.max(...kiste.getSize(new THREE.Vector3()).toArray());
            this.kam.position.set(m.x, m.y + 0.1, m.z + s / 2 / Math.tan(15 * Math.PI / 180) * 1.2);
            this.kam.lookAt(m); this.kam.updateMatrixWorld(true); this.kam.updateProjectionMatrix();
            return this.zeichnen(rolle, this.kam);
        } finally {
            szene.remove(licht); licht.dispose();
            for (const [o, v] of sicht) o.visible = v;
        }
    }

    ende() {
        while (this.zurueck.length) this.zurueck.pop()();
        if (this.ziel) { this.ziel.depthTexture.dispose(); this.ziel.dispose(); this.lin.dispose(); this.quad.geometry.dispose(); this.quad.material.dispose(); }
        for (const m of this.rote.values()) m.dispose();
        this.r.dispose(); this.r.forceContextLoss();
    }
}
