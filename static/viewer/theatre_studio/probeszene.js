import * as THREE from 'three';

/**
 * Die Probeszene der Theatre-Studio-Seite: Gitter, ein Würfel, zwei Lichter.
 *
 * Sie ist bewusst schlicht — die Seite prüft, ob Theatres Bedienoberfläche
 * überhaupt erscheint und ihre Werte ankommen, nicht die Darstellung.
 *
 * Aus dem Inline-Modul in `theatre_studio.html` herausgelöst (Umbau
 * 27.08.2026).
 */
export class Probeszene {
    /** @param {HTMLCanvasElement} canvas */
    constructor(canvas) {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x222222);

        this.camera = new THREE.PerspectiveCamera(
            75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 2, 10);

        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);

        this.scene.add(new THREE.GridHelper(20, 20));
        this.wuerfel = Probeszene._wuerfel();
        this.scene.add(this.wuerfel);
        this.scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        this.licht = new THREE.PointLight(0xffffff, 1, 100);
        this.licht.position.set(5, 5, 5);
        this.scene.add(this.licht);

        window.addEventListener('resize', () => this._groesse());
        this._zeichnen();
    }

    static _wuerfel() {
        const wuerfel = new THREE.Mesh(
            new THREE.BoxGeometry(2, 2, 2),
            new THREE.MeshStandardMaterial({ color: 0x7c5cbf }));
        wuerfel.position.y = 1;
        return wuerfel;
    }

    _groesse() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    _zeichnen() {
        requestAnimationFrame(() => this._zeichnen());
        this.renderer.render(this.scene, this.camera);
    }
}
