import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Engine2d3dKleiderGesichtsbuehne — EIN kleiner, eigenständiger three.js-Betrachter für den Reiter „Gesicht" (07.10.2026):
 * lädt genau eine GLB, zeichnet nummerierte Mess-Linien darüber und richtet die Kamera auf ihre Ausdehnung aus. Zweimal
 * verwendet (Mesh, Modell) — bewusst NICHT die große geteilte Bühne (`Meshfigurbuehne`): die braucht dreißig Module und
 * zeigt die ganze Figur; hier reicht ein Ausschnitt um das Gesicht.
 */
export class Engine2d3dKleiderGesichtsbuehne {

    /** Farbe der Mess-Linien und ihrer Nummern-Marken. */
    static LINIENFARBE = 0xffd23f;
    /** Farbe je Schnitt-Kategorie (horizontal/vertikal/diagonal) — deutlich von der Linienfarbe unterschieden. */
    static SCHNITTFARBEN = { horizontal: 0x4fd4ff, vertikal: 0xff4fd4, diagonal: 0xa6ff4f };

    constructor(container) {
        this.container = container;
        this.szene = new THREE.Scene();
        this.szene.background = new THREE.Color(0x11141c);
        this.kamera = new THREE.PerspectiveCamera(35, 1, 0.01, 10);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        container.appendChild(this.renderer.domElement);
        this.steuerung = new OrbitControls(this.kamera, this.renderer.domElement);
        this.steuerung.enableDamping = true;
        this.szene.add(new THREE.AmbientLight(0xffffff, 0.9));
        const licht = new THREE.DirectionalLight(0xffffff, 1.1);
        licht.position.set(0.3, 1, 1);
        this.szene.add(licht);
        this.linien = new THREE.Group();
        this.szene.add(this.linien);
        this.schnittGruppe = new THREE.Group();
        this.szene.add(this.schnittGruppe);
        this._linienBox = new THREE.Box3();
        this._schnittBox = new THREE.Box3();
        this._lauft = true;
        this._beobachter = new ResizeObserver(() => this._groesse());
        this._beobachter.observe(container);
        this._groesse();
        this._takt();
    }

    _groesse() {
        const b = this.container.getBoundingClientRect();
        if (!b.width || !b.height) return;
        this.renderer.setSize(b.width, b.height);
        this.kamera.aspect = b.width / b.height;
        this.kamera.updateProjectionMatrix();
    }

    _takt() {
        if (!this._lauft) return;
        requestAnimationFrame(() => this._takt());
        this.steuerung.update();
        this.renderer.render(this.szene, this.kamera);
    }

    /**
     * Die GLB laden und der Szene hinzufügen — die Kamera richtet erst `zeichnen()` aus (dort steht die
     * Gesichts-Ausdehnung). `ausrichtung`: optionale 4×4-Matrix (zeilenweise, wie `scan_lage.npz`), die das rohe
     * TRELLIS-Netz in denselben Raum wie die Landmarken dreht/verschiebt — ohne sie steht das Mesh woanders als
     * seine eigenen Mess-Linien (Befund 07.10.2026, Reiter zeigte nur die Linien, das Netz lag daneben).
     */
    async laden(url, ausrichtung = null) {
        const gltf = await new GLTFLoader().loadAsync(url);
        if (ausrichtung) gltf.scene.applyMatrix4(new THREE.Matrix4().set(...ausrichtung.flat()));
        // Das rohe TRELLIS-Netz hat vereinzelt umgekehrte Dreiecks-Wicklung (Befund 07.10.2026: mit der
        // Standard-Seite `FrontSide` blieb die ganze Fläche unsichtbar, nur die Linien waren zu sehen) —
        // in diesem reinen Diagnose-Betrachter stört `DoubleSide` nichts, zeigt aber auch verdrehte Flächen.
        gltf.scene.traverse(teil => { if (teil.isMesh) teil.material.side = THREE.DoubleSide; });
        this.szene.add(gltf.scene);
        return gltf.scene;
    }

    /** `[{nummer, a:[x,y,z], b:[x,y,z]}]` als nummerierte Linien zeichnen (Meter). Kamera-Rahmen: `rahmen()`. */
    zeichnen(strecken) {
        this.linien.clear();
        const box = new THREE.Box3();
        const material = new THREE.LineBasicMaterial({
            color: Engine2d3dKleiderGesichtsbuehne.LINIENFARBE, depthTest: false, transparent: true,
        });
        for (const { nummer, a, b } of strecken) {
            const von = new THREE.Vector3(...a), bis = new THREE.Vector3(...b);
            const geometrie = new THREE.BufferGeometry().setFromPoints([von, bis]);
            this.linien.add(new THREE.Line(geometrie, material));
            this.linien.add(this._marke(nummer, von.clone().add(bis).multiplyScalar(0.5)));
            box.expandByPoint(von);
            box.expandByPoint(bis);
        }
        this._linienBox = box;
    }

    /**
     * Ebenen-Schnitte zeichnen (Edgar, 07.10.2026: „mach schnitte alle paar cm horizontal, vertikal und
     * diagonal, mach die alle und zeige sie auf dem Tab") — `ebenen`: `[{kategorie, nummer, mesh:[[[x,y,z],
     * [x,y,z]],…], modell:[...]}, …]` von `Engine2d3dKleiderGesichtsvergleich._schnitte`, `feld`: 'mesh' oder
     * 'modell' (dieser Betrachter zeigt nur SEINE Flaeche). Alle Segmente EINER Kategorie in EINER
     * `LineSegments`-Geometrie (nicht ein Objekt je Segment — bei mehreren tausend Segmenten sonst spuerbar
     * langsam). Kamera-Rahmen: `rahmen()`.
     */
    schnitte(ebenen, feld) {
        this.schnittGruppe.clear();
        const box = new THREE.Box3();
        const nachKategorie = new Map();
        for (const ebene of ebenen) {
            const segmente = ebene[feld];
            if (!segmente || !segmente.length) continue;
            if (!nachKategorie.has(ebene.kategorie)) nachKategorie.set(ebene.kategorie, []);
            nachKategorie.get(ebene.kategorie).push(...segmente);
        }
        for (const [kategorie, segmente] of nachKategorie) {
            const positionen = new Float32Array(segmente.length * 6);
            segmente.forEach((segment, i) => {
                positionen.set([...segment[0], ...segment[1]], i * 6);
                box.expandByPoint(new THREE.Vector3(...segment[0]));
                box.expandByPoint(new THREE.Vector3(...segment[1]));
            });
            const geometrie = new THREE.BufferGeometry();
            geometrie.setAttribute('position', new THREE.BufferAttribute(positionen, 3));
            const material = new THREE.LineBasicMaterial({
                color: Engine2d3dKleiderGesichtsbuehne.SCHNITTFARBEN[kategorie] ?? 0xffffff,
                transparent: true, opacity: 0.8,
            });
            this.schnittGruppe.add(new THREE.LineSegments(geometrie, material));
        }
        this._schnittBox = box;
    }

    /** Kamera auf Mitte + Ausdehnung von Linien UND Schnitten zusammen richten — nach `zeichnen()`/`schnitte()` aufrufen. */
    rahmen() {
        const box = this._linienBox.clone().union(this._schnittBox);
        this._ausrichten(box);
    }

    /** Eine runde Nummern-Marke (Canvas-Sprite, immer zur Kamera gedreht) an der Mitte einer Strecke. */
    _marke(nummer, position) {
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 64;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(17, 20, 28, 0.88)';
        ctx.beginPath();
        ctx.arc(32, 32, 27, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#' + Engine2d3dKleiderGesichtsbuehne.LINIENFARBE.toString(16).padStart(6, '0');
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 30px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(String(nummer), 32, 35);
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
            map: new THREE.CanvasTexture(canvas), depthTest: false,
        }));
        sprite.position.copy(position);
        sprite.scale.setScalar(0.022);
        return sprite;
    }

    /** Kamera auf Mitte + Ausdehnung der gezeichneten Strecken — mit etwas Rand, damit die Marken nicht am Bildrand kleben. */
    _ausrichten(box) {
        if (box.isEmpty()) return;
        const mitte = box.getCenter(new THREE.Vector3());
        const ausdehnung = Math.max(box.getSize(new THREE.Vector3()).length(), 0.08);
        const abstand = ausdehnung * 1.5;
        this.steuerung.target.copy(mitte);
        this.kamera.position.set(mitte.x, mitte.y, mitte.z + abstand);
        this.kamera.near = abstand / 50;
        this.kamera.far = abstand * 30;
        this.kamera.updateProjectionMatrix();
        this.steuerung.update();
    }

    /** Bei Verlassen des Reiters für immer (die Seite wird nicht neu geladen) — Takt und Beobachter stoppen. */
    aufraeumen() {
        this._lauft = false;
        this._beobachter.disconnect();
    }
}
