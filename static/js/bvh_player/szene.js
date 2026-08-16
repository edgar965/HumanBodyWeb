/**
 * Spielerszene — die 3D-Ansicht des BVH-Spielers samt Knochennummern.
 *
 * Aus bvh_player.js herausgeloest (Umbau 16.08.2026).
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/** Hoehe, wenn der Behaelter (noch) keine hat. */
const NOTHOEHE = 400;

export class Spielerszene {
    constructor(behaelter) {
        this.behaelter = behaelter;
        this.nummernZeigen = true;

        const breite = behaelter.clientWidth;
        const hoehe = behaelter.clientHeight || NOTHOEHE;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);
        this.camera = new THREE.PerspectiveCamera(60, breite / hoehe, 0.1, 1000);
        this.camera.position.set(0, 100, 300);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(breite, hoehe);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        behaelter.appendChild(this.renderer.domElement);

        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.1;
        this.controls.target.set(0, 80, 0);
        this.controls.update();

        this._beschriftungBauen();
        this._lichtUndRaster();
    }

    _beschriftungBauen() {
        this.behaelter.style.position = 'relative';
        this.beschriftung = document.createElement('canvas');
        this.beschriftung.style.cssText = 'position:absolute;top:0;left:0;'
            + 'width:100%;height:100%;pointer-events:none;z-index:10';
        this.behaelter.appendChild(this.beschriftung);
        this.stift = this.beschriftung.getContext('2d');
    }

    _lichtUndRaster() {
        this.scene.add(new THREE.GridHelper(400, 20, 0x2a2a4a, 0x1f1f3a));
        this.scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const licht = new THREE.DirectionalLight(0xffffff, 0.8);
        licht.position.set(50, 200, 100);
        this.scene.add(licht);
    }

    /** Knochennummern ueber die 3D-Ansicht zeichnen. */
    nummernZeichnen(skelett) {
        if (!this.stift) return;
        const cw = this.behaelter.clientWidth;
        const ch = this.behaelter.clientHeight || NOTHOEHE;
        this.beschriftung.width = cw;
        this.beschriftung.height = ch;
        this.stift.clearRect(0, 0, cw, ch);
        if (!this.nummernZeigen || !skelett?.sichtbar) return;

        this.stift.font = 'bold 12px monospace';
        this.stift.textAlign = 'center';
        this.stift.textBaseline = 'bottom';
        const punkt = new THREE.Vector3();
        skelett.format.reihenfolge.forEach((name, nummer) => {
            const knochen = skelett.knochen[name];
            if (!knochen) return;
            knochen.getWorldPosition(punkt);
            punkt.project(this.camera);
            if (punkt.z < -1 || punkt.z > 1) return;   // hinter der Kamera
            const sx = (punkt.x * 0.5 + 0.5) * cw;
            const sy = (-punkt.y * 0.5 + 0.5) * ch;
            const text = String(nummer);
            const breite = this.stift.measureText(text).width + 6;
            this.stift.fillStyle = 'rgba(0,0,0,0.7)';
            this.stift.fillRect(sx - breite / 2, sy - 16, breite, 16);
            this.stift.fillStyle = '#fbbf24';
            this.stift.fillText(text, sx, sy - 2);
        });
    }

    /** Kamera so setzen, dass das Skelett das Bild fuellt. */
    ausrichten(wurzel, format) {
        const kasten = new THREE.Box3();
        const punkt = new THREE.Vector3();
        wurzel.traverse((kind) => {
            if (!kind.isBone || !format.namen.has(kind.name)) return;
            kind.getWorldPosition(punkt);
            kasten.expandByPoint(punkt);
        });
        const mitte = new THREE.Vector3();
        const groesse = new THREE.Vector3();
        kasten.getCenter(mitte);
        kasten.getSize(groesse);

        this.controls.target.copy(mitte);
        const gross = Math.max(groesse.x, groesse.y, groesse.z);
        const winkel = this.camera.fov * Math.PI / 180;
        const abstand = gross / (2 * Math.tan(winkel / 2)) * 1.3;
        this.camera.position.set(mitte.x, mitte.y, mitte.z + abstand);
        this.controls.update();
    }

    zeichnen() {
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    groesseAnpassen() {
        const w = this.behaelter.clientWidth;
        const h = this.behaelter.clientHeight || NOTHOEHE;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }

    fehler(text) {
        this.behaelter.innerHTML = '<div style="color:#e94560;padding:2rem;'
            + `text-align:center;">${text}</div>`;
    }
}
