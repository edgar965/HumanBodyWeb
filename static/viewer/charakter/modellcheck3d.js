import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Eigenkleidbacken } from '../gemeinsam/eigenkleidbacken.js';
import { Modellcheckbefunde } from './modellcheckbefunde.js';
import { Modellcheckmarken } from './modellcheckmarken.js';
import { state } from './state.js';

/**
 * Modellcheck3d — die 3D-Ansicht im Modell Check (02.11.2026, Edgar: „Mach auch eine 3D View im Popup wo die Fehler rot angezeigt werden, der rest per Default nur
 * grau, aber mit toggle buttons: Textur, Kleider, Drahtmodell, Mesh“, dann „bei Model Check mach genau die gleiche Erzeugung des Modells wie im Haupt View“).
 * Gezeichnet wird DIE Figur der Szene — dieselben Netze, Stoffe, Shader-Eingriffe (Hauteinzug und Naht am Anatomie-Stück, Oberflächenbindung der Kleidung,
 * Eigenkleid-Schalen) und Lichter wie im Haupt-View, mit eigener Kamera und eigenem Renderer (Tonung und Farbraum vom Haupt-Renderer). Während eines Bildes sind die
 * übrigen Kinder der Szene aus und der Hintergrund weg — synchron, die Szene zeichnet dazwischen nicht. Der erste Bau (ein Abzug mit eigenen Netzen) zeigte die
 * Scham anders als der View: ohne den Einzug klaffte die Naht.
 * Rot (`Modellcheckmarken`, über demselben Tiefenpuffer): ohne Wahl die Befunde der DURCHGEFALLENEN Prüfungen; überfährt man eine Zeile der Befundtabelle, nur
 * dieser Befund, dazu seine Punkte über allem; ein Klick auf die Zeile fährt die Kamera hin (`hervorheben`). Gebackene Eigenkleider (Handstoff, Säume) als ihr
 * gebackenes Netz — die Ansicht hält sie, bis sie schließt. Die Fläche wächst mit dem Dialog (Größe veränderbar, gemerkt).
 * Schalter: Textur (aus = dasselbe Bild in Grau, Rot bleibt), Kleider, Drahtmodell (die Kanten derselben Netze dunkel darüber), Mesh (Flächen). Hintergrund weiß
 * (Edgar, 02.11.2026).
 */
export class Modellcheck3d {

    static HOEHE_PX = 520;                  // nur, solange die Fläche noch keine Höhe hat
    static VORGABE = { textur: false, kleider: true, draht: false, mesh: true };
    static MISCHUNG = `uniform sampler2D tBild; uniform sampler2D tDraht; uniform float uGrau; uniform float uDraht; varying vec2 vUv;
void main() {
    vec4 c = texture2D( tBild, vUv );
    vec3 f = c.a > 0.0 ? c.rgb / c.a : vec3( 0.0 );                  // durchsichtiger Grund: Ränder und Haar vormultipliziert
    bool rot = f.r > 0.98 && f.g < 0.02 && f.b < 0.02;
    if ( uGrau > 0.5 && !rot ) f = vec3( dot( f, vec3( 0.2126, 0.7152, 0.0722 ) ) );
    gl_FragColor = vec4( f, 1.0 );
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
    gl_FragColor.rgb = mix( vec3( 1.0 ), gl_FragColor.rgb, c.a );     // Hintergrund weiß, nach der Tonung (sonst grau)
    if ( uDraht > 0.5 ) gl_FragColor.rgb = mix( gl_FragColor.rgb, vec3( 0.004 ), 0.85 * texture2D( tDraht, vUv ).a );
}`;

    /** `huelle`: Element mit den Knöpfen `[data-schalter]` und der Fläche `[data-modellcheck="leinwand"]`. */
    constructor(huelle) {
        this.huelle = huelle;
        this.schalter = { ...Modellcheck3d.VORGABE };
        this.befunde = [];
        huelle.querySelectorAll('[data-schalter]').forEach((k) => k.addEventListener('click', () => {
            this.schalter[k.dataset.schalter] = !this.schalter[k.dataset.schalter];
            this._knoepfe();
            this.zeichnen();
        }));
        this._knoepfe();
    }

    /** Die Figur `inst` zeigen, rot die durchgefallenen `befunde` (`Modellcheckbefunde.sammeln`); `gebacken`: die gebackenen Eigenkleider der Prüfung — gehören ab hier der Ansicht. */
    zeigen(inst, gebacken, befunde) {
        this.weg();
        this.inst = inst;
        this.gebacken = gebacken;
        this.befunde = befunde;
        this.schalter = { ...Modellcheck3d.VORGABE };                    // jede Prüfung beginnt grau, mit Kleidern, ohne Drahtmodell
        this._knoepfe();
        const leinwand = this.huelle.querySelector('[data-modellcheck="leinwand"]'), haupt = state.renderer;
        this.r = new THREE.WebGLRenderer({ antialias: false });
        this.r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        if (haupt) {
            Object.assign(this.r, { toneMapping: haupt.toneMapping, toneMappingExposure: haupt.toneMappingExposure, outputColorSpace: haupt.outputColorSpace });
            Object.assign(this.r.shadowMap, { enabled: haupt.shadowMap.enabled, type: haupt.shadowMap.type });
        }
        leinwand.replaceChildren(this.r.domElement);
        this.kam = new THREE.PerspectiveCamera(30, 1, 0.02, 100);
        this.bild = new THREE.WebGLRenderTarget(1, 1, { samples: 4, type: THREE.HalfFloatType });
        this.drahtBild = new THREE.WebGLRenderTarget(1, 1, { samples: 4 });
        this.mischung = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
            uniforms: { tBild: { value: this.bild.texture }, tDraht: { value: this.drahtBild.texture }, uGrau: { value: 1 }, uDraht: { value: 0 } },
            vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4( position.xy, 0.0, 1.0 ); }',
            fragmentShader: Modellcheck3d.MISCHUNG, depthTest: false, depthWrite: false }));
        this.mischSzene = new THREE.Scene();
        this.mischSzene.add(this.mischung);
        this.mischKam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        this.marken = new Modellcheckmarken();
        this.marken.setzen(inst, befunde.filter((b) => b.fehler));
        const kiste = new THREE.Box3().setFromObject(inst.bodyMesh, true), mitte = kiste.getCenter(new THREE.Vector3());
        this.mitte = mitte;
        this.kam.position.set(mitte.x, mitte.y, mitte.z + (kiste.max.y - kiste.min.y) / 2 / Math.tan(15 * Math.PI / 180) * 1.15);
        this.steuer = new OrbitControls(this.kam, this.r.domElement);
        this.steuer.target.copy(mitte);
        this.steuer.update();
        this.steuer.addEventListener('change', () => this.zeichnen());
        this.beobachter = new ResizeObserver(() => this._groesse(leinwand));
        this.beobachter.observe(leinwand);
        this._groesse(leinwand);
    }

    /** Nur `befund` rot (mit seinen Punkten über allem), `null` = alle durchgefallenen; `fokus`: Kamera auf den Befund. */
    hervorheben(befund, fokus = false) {
        if (!this.r) return;
        this.marken.setzen(this.inst, befund ? [befund] : this.befunde.filter((b) => b.fehler), Boolean(befund));
        if (befund && fokus) this._fokus(befund);
        this.zeichnen();
    }

    /** Kamera auf den Befund: von der Körperachse aus nach außen auf die Stelle, so nah, dass sie ein gutes Drittel des Bilds füllt. */
    _fokus(befund) {
        const kiste = Modellcheckbefunde.kiste(this.inst, befund);
        if (kiste.isEmpty()) return;
        const mitte = kiste.getCenter(new THREE.Vector3()), groesse = Math.max(kiste.getSize(new THREE.Vector3()).length(), 0.12);
        const blick = mitte.clone().sub(new THREE.Vector3(this.mitte.x, mitte.y, this.mitte.z));
        if (blick.lengthSq() < 0.0025) blick.copy(this.kam.position).sub(this.steuer.target);          // auf der Achse (Schritt, Scheitel): Blickrichtung behalten
        this.steuer.target.copy(mitte);
        this.kam.position.copy(mitte).addScaledVector(blick.normalize(), groesse * 1.4 / Math.tan(15 * Math.PI / 180));
        this.steuer.update();
    }

    /** Ein Bild: Figur der Szene in `bild`, Marken darüber, Drahtmodell, dann gemischt (Grau, Kanten) auf die Leinwand. */
    _bild() {
        const g = this.inst?.group, szene = g?.parent, r = this.r;
        if (!r || !szene) return;
        const vorher = [], aus = (o) => { vorher.push([o, o.visible]); o.visible = false; };
        for (const c of szene.children) if (c !== g && c.visible && !c.isLight) aus(c);
        g.traverse((o) => { if (o.visible && (o.isLine || o.isPoints || o.isSprite || /Helper/.test(o.type))) aus(o); });
        const netze = [];
        g.traverseVisible((o) => { if (o.isMesh) netze.push(o); });
        if (!this.schalter.kleider) netze.filter((o) => Modellcheckbefunde.istKleid(o)).forEach(aus);
        const sichtbar = netze.filter((o) => o.visible);
        const hg = szene.background;
        szene.background = null;
        try {
            this.marken.vorBild(this.inst, this.schalter.kleider);
            r.autoClear = false;
            r.setRenderTarget(this.bild);
            r.setClearColor(0x000000, 0);                                        // Grund durchsichtig, weiß wird er in der Mischung
            r.clear();
            if (this.schalter.mesh) r.render(szene, this.kam);
            else { sichtbar.forEach(aus); r.render(szene, this.kam); }               // Lichter, Matrizen, Skelett wie sonst — ohne Flächen
            r.render(this.marken.szene, this.kam);
            if (this.schalter.draht) this._draht(szene, sichtbar);
            r.setRenderTarget(null);
            Object.assign(this.mischung.material.uniforms, { uGrau: { value: this.schalter.textur ? 0 : 1 }, uDraht: { value: this.schalter.draht ? 1 : 0 },
                tBild: { value: this.bild.texture }, tDraht: { value: this.drahtBild.texture } });
            r.render(this.mischSzene, this.mischKam);
        } finally {
            r.autoClear = true;
            szene.background = hg;
            for (const [o, v] of vorher.reverse()) o.visible = v;
        }
    }

    /** Kanten derselben Netze mit ihren eigenen Stoffen (`wireframe` ändert nur den Zeichenaufruf, nicht das Programm); verdeckt durch die Flächen davor. */
    _draht(szene, netze) {
        const r = this.r, stoffe = new Set();
        for (const o of netze) for (const m of [o.material].flat()) if (m) stoffe.add(m);
        const vorher = [...stoffe].map((m) => [m, m.wireframe, m.colorWrite, m.polygonOffset, m.polygonOffsetFactor, m.polygonOffsetUnits, m.visible]);
        const zeigen = (o, v) => { o.visible = v; };
        r.setRenderTarget(this.drahtBild);
        r.setClearColor(0x000000, 0);
        r.clear();
        try {
            if (this.schalter.mesh) {
                for (const m of stoffe) Object.assign(m, { colorWrite: false, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
                r.render(szene, this.kam);
            } else netze.forEach((o) => zeigen(o, true));
            for (const [m, , c, po, pf, pu] of vorher) Object.assign(m, { colorWrite: c, polygonOffset: po, polygonOffsetFactor: pf, polygonOffsetUnits: pu, wireframe: true });
            r.render(szene, this.kam);
        } finally {
            for (const [m, w, c, po, pf, pu, v] of vorher) Object.assign(m, { wireframe: w, colorWrite: c, polygonOffset: po, polygonOffsetFactor: pf, polygonOffsetUnits: pu, visible: v });
            if (!this.schalter.mesh) netze.forEach((o) => zeigen(o, false));
        }
    }

    _knoepfe() {
        this.huelle.querySelectorAll('[data-schalter]').forEach((k) => {
            const an = Boolean(this.schalter[k.dataset.schalter]);
            k.classList.toggle('an', an);
            k.setAttribute('aria-pressed', String(an));
        });
    }

    _groesse(leinwand) {
        const b = leinwand.clientWidth, h = leinwand.clientHeight || Modellcheck3d.HOEHE_PX;
        if (!this.r || !b) return;
        this.r.setSize(b, h);
        const pr = this.r.getPixelRatio();
        this.bild.setSize(Math.round(b * pr), Math.round(h * pr));
        this.drahtBild.setSize(Math.round(b * pr), Math.round(h * pr));
        this.kam.aspect = b / h;
        this.kam.updateProjectionMatrix();
        this.zeichnen(true);
    }

    /** Ein Bild — gebündelt auf den nächsten Frame, `sofort` ohne (der Dialog öffnet auch in einem verdeckten Tab). */
    zeichnen(sofort = false) {
        if (!this.r) return;
        if (sofort) { this._bild(); return; }
        if (this._frame) return;
        this._frame = requestAnimationFrame(() => { this._frame = 0; this._bild(); });
    }

    weg() {
        if (!this.r) return;
        if (this._frame) cancelAnimationFrame(this._frame);
        this._frame = 0;
        this.beobachter?.disconnect();
        this.steuer?.dispose();
        this.marken.weg();
        this.bild.dispose(); this.drahtBild.dispose();
        this.mischung.geometry.dispose(); this.mischung.material.dispose();
        this.r.dispose(); this.r.forceContextLoss(); this.r.domElement.remove();
        Eigenkleidbacken.weg(this.gebacken);
        this.r = null; this.inst = null; this.gebacken = []; this.befunde = []; this.marken = null;
    }
}
