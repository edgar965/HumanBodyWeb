/**
 * Ai2d3dpshumannetzbilder — PSHumans rekonstruiertes Netz (GLB im Feld „Netz“, Art 'pshuman') aus dem Winkel eines Bildplatzes gerendert, für die Ansichten
 * „Netz“, „Netz farbig“ und „Netz-Normale“ der PSHuman-Eingabe (03.11.2026, Edgar: „die erfundenen Bilder in auswählbarer Ansicht (Textur, Normale, Mesh usw)“).
 *
 * Kamera orthografisch wie PSHumans sechs Ansichten (`six_human_pose`), Winkel der Fotojobs: Kamera bei (sin w, 0, cos w) um die Mitte des Netzes — das
 * Netz steht in PSHumans Achsen (x rechts, y oben, z zum Vorderfoto, `pshuman_ansichtsjob.py`), w = 90 sieht also die linke Körperseite. Alle Winkel mit
 * demselben Maßstab (Person so hoch wie in PSHumans Ansichten, 740 von 768; Seitenverhältnis 3:5 wie die Plätze). Ein Renderer für alle Bilder; das Netz wird erst beim
 * ersten Bild geladen (rund 11 MB), jedes Bild einmal gerechnet und als PNG-Adresse gemerkt.
 *   netz         grau, beleuchtet (Umgebungslicht + Licht aus der Kamera)
 *   netzfarbe    die Punktfarben der Datei (PSHumans Farbe aus den Ansichten), beleuchtet
 *   netznormale  Normalen im Kamera-Raum als Farbe (`MeshNormalMaterial`) — zum Vergleich mit PSHumans Normalenbildern
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export class Ai2d3dpshumannetzbilder {
    static BREITE = 307;
    static HOEHE = 512;
    static ARTEN = ['netz', 'netzfarbe', 'netznormale'];

    constructor(adresse) {
        this.adresse = adresse;
        this._szene = null;
        this._bilder = new Map();
    }

    _laden() {
        this._szene ??= new Promise((fertig, fehler) => new GLTFLoader().load(this.adresse, gltf => fertig(this._aufbauen(gltf.scene)), undefined, fehler));
        return this._szene;
    }

    _aufbauen(netz) {
        const szene = new THREE.Scene();
        szene.add(netz);
        const kasten = new THREE.Box3().setFromObject(netz);
        const mitte = kasten.getCenter(new THREE.Vector3()), groesse = kasten.getSize(new THREE.Vector3());
        const h = groesse.y * 768 / 740 / 2, b = h * Ai2d3dpshumannetzbilder.BREITE / Ai2d3dpshumannetzbilder.HOEHE;
        const kamera = new THREE.OrthographicCamera(-b, b, h, -h, 0.01, 100 * Math.max(groesse.x, groesse.y, groesse.z));
        const licht = new THREE.DirectionalLight(0xffffff, 2.0);
        licht.target.position.copy(mitte);
        szene.add(new THREE.AmbientLight(0xffffff, 1.0), licht, licht.target);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
        renderer.setPixelRatio(1);
        renderer.setSize(Ai2d3dpshumannetzbilder.BREITE, Ai2d3dpshumannetzbilder.HOEHE, false);
        renderer.setClearColor(0x000000, 0);
        const materialien = {
            netz: new THREE.MeshStandardMaterial({ color: 0xbdbdbd, roughness: 0.85, metalness: 0 }),
            netzfarbe: null,
            netznormale: new THREE.MeshNormalMaterial(),
        };
        return { szene, kamera, licht, renderer, mitte, abstand: 10 * Math.max(groesse.x, groesse.y, groesse.z), materialien };
    }

    /** PNG-Adresse des Netzes aus `winkel` (Grad) in der Ansicht `art`. */
    async bild(winkel, art) {
        if (!Ai2d3dpshumannetzbilder.ARTEN.includes(art)) throw new Error(`Ai2d3dpshumannetzbilder: unbekannte Ansicht ${art}`);
        const schluessel = `${art}:${winkel}`;
        if (!this._bilder.has(schluessel)) {
            this._bilder.set(schluessel, this._laden().then(s => {
                const w = THREE.MathUtils.degToRad(Number(winkel));
                s.kamera.position.set(s.mitte.x + Math.sin(w) * s.abstand, s.mitte.y, s.mitte.z + Math.cos(w) * s.abstand);
                s.kamera.up.set(0, 1, 0);
                s.kamera.lookAt(s.mitte);
                s.kamera.updateProjectionMatrix();
                s.licht.position.copy(s.kamera.position);
                s.szene.overrideMaterial = s.materialien[art];
                s.renderer.render(s.szene, s.kamera);
                return s.renderer.domElement.toDataURL('image/png');
            }));
        }
        return this._bilder.get(schluessel);
    }
}
