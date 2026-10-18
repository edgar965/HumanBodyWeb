import { state, THREE } from './state.js';
import { Modellexportinhalt } from './modellexport_inhalt.js';

/**
 * Modellansichten — die Figur als vier JPG: von vorn, links, rechts und hinten (Edgar, 18.10.2026: „Bei Modell als
 * jpg exportieren, exportiere 4 Bilder: Frontal, seitlich links, seitlich rechts, von hinten").
 *
 * Gerendert wird die Szene, wie sie dasteht — Pose, Licht, Hintergrund —, aber nur mit DIESER Figur: andere Figuren,
 * Boden, Gizmo, Knochenlinien und Auswahlhüllen sind für die Aufnahmen aus. Eigene Kamera, eigene Bildgröße; die
 * Leinwand bekommt danach Größe und Pixelverhältnis zurück. Abgegriffen wird wie in `Videoaufnahme`: `render`, dann
 * sofort `toBlob` — der Puffer gilt bis zum Ende der Aufgabe, `toBlob` kopiert ihn beim Aufruf.
 *
 * Die Richtungen sind die der FIGUR, nicht der Welt: „vorne" ist +Z ihrer Gruppe, auch wenn sie gedreht steht.
 * Dieselbe Tabelle wie `core/dienste/mesh3dansicht.py` (`ACHSEN`): links = Kamera bei +X (die linke Körperseite),
 * rechts = Kamera bei −X.
 */
export class Modellansichten {

    static BREITE = 1536;
    static HOEHE = 2048;
    static QUALITAET = 0.92;
    //: Senkrechter Öffnungswinkel — schmal, damit die Figur kaum perspektivisch verzerrt.
    static FOV = 20;
    //: Luft um die Figur, bezogen auf die größere Ausdehnung im Bild.
    static RAND = 1.08;
    //: Höchstens so viele Punkte je Netz für die Hülle — jeder Punkt wird gehäutet, das Netz hat bis 400.000.
    static PROBEN = 80000;
    static ANSICHTEN = { vorne: [0, 0, 1], links: [1, 0, 0], rechts: [-1, 0, 0], hinten: [0, 0, -1] };

    /** Dateinamen-Endungen in der Reihenfolge der Aufnahmen (`_vorne.jpg`, …). */
    static endungen() {
        return Object.keys(Modellansichten.ANSICHTEN).map((rolle) => `_${rolle}.jpg`);
    }

    /**
     * @param inst     die Figur
     * @param praefix  Namensstamm der Dateien (`MODELL`, der Server ersetzt ihn)
     * @returns [{name, blob}] — vier JPG
     */
    static async aufnehmen(inst, praefix) {
        const { renderer, scene } = state;
        scene.updateMatrixWorld(true);
        const gruppe = inst.group;
        const box = Modellansichten._huelle(inst);
        if (box.isEmpty()) throw new Error('Die Figur hat keine sichtbaren Netze.');
        const mitte = box.getCenter(new THREE.Vector3());
        const groesse = box.getSize(new THREE.Vector3());
        const zielWelt = mitte.clone().applyMatrix4(gruppe.matrixWorld);
        const kamera = new THREE.PerspectiveCamera(Modellansichten.FOV, Modellansichten.BREITE / Modellansichten.HOEHE);
        const halbTan = Math.tan(THREE.MathUtils.degToRad(Modellansichten.FOV / 2));

        const groesseVorher = renderer.getSize(new THREE.Vector2());
        const pixelVorher = renderer.getPixelRatio();
        // RENDERZIEL AUSDRÜCKLICH DIE LEINWAND (Edgar, 18.10.2026: „Matt1 hat schwarze jpg bilder"). Gemessen: Matt1 hatte
        // vier JPG zu je 19.190 Byte, alle Pixel 0; Edgars Tab warf beim Export davor 59-mal in
        // `Oberflaechenbindung._passt` (Client-Log); ein absichtlich stehengelassenes Renderziel ergibt hier genau
        // dieselben vier Dateien. Vermutet, nicht nachgewiesen: Die Ausnahme fiel im `RenderPass` des Auswahl-Composers,
        // der danach sein Ziel nicht zurückstellte — die Szene sah man weiter, weil sein letzter Pass selbst auf die
        // Leinwand zeichnet.
        const zielVorher = renderer.getRenderTarget();
        const autoClearVorher = renderer.autoClear;
        const scherenVorher = renderer.getScissorTest();
        const verborgen = Modellansichten._verbergen(scene, gruppe);
        const bilder = [];
        try {
            renderer.setRenderTarget(null);
            renderer.autoClear = true;
            renderer.setScissorTest(false);
            renderer.setPixelRatio(1);
            renderer.setSize(Modellansichten.BREITE, Modellansichten.HOEHE, false);
            for (const [rolle, [x, y, z]] of Object.entries(Modellansichten.ANSICHTEN)) {
                const seitlich = x !== 0;
                const breite = seitlich ? groesse.z : groesse.x;
                const tiefe = seitlich ? groesse.x : groesse.z;
                // Abstand bis zur VORDEREN Fläche der Hülle so, dass Höhe und Breite ins Bild passen.
                const abstand = Math.max(groesse.y / 2 / halbTan, breite / 2 / (halbTan * kamera.aspect))
                    * Modellansichten.RAND + tiefe / 2;
                kamera.position.copy(mitte).addScaledVector(new THREE.Vector3(x, y, z), abstand)
                    .applyMatrix4(gruppe.matrixWorld);
                kamera.up.set(0, 1, 0).transformDirection(gruppe.matrixWorld);
                kamera.lookAt(zielWelt);
                const entfernung = kamera.position.distanceTo(zielWelt);
                kamera.near = entfernung / 50;
                kamera.far = entfernung * 4;
                kamera.updateProjectionMatrix();
                renderer.render(scene, kamera);
                const blob = new Promise((fertig) => {
                    renderer.domElement.toBlob(fertig, 'image/jpeg', Modellansichten.QUALITAET);
                });
                bilder.push({ name: `${praefix}_${rolle}.jpg`, blob });
            }
        } finally {
            renderer.setPixelRatio(pixelVorher);
            renderer.setSize(groesseVorher.x, groesseVorher.y, false);
            renderer.setScissorTest(scherenVorher);
            renderer.autoClear = autoClearVorher;
            renderer.setRenderTarget(zielVorher);
            for (const obj of verborgen) obj.visible = true;
        }
        const fertig = await Promise.all(bilder.map((b) => b.blob));
        if (fertig.some((b) => !b)) throw new Error('Ansichtsbild leer (toBlob).');
        return bilder.map((b, i) => ({ name: b.name, blob: fertig[i] }));
    }

    /** Die Hülle der sichtbaren Netze im Raum der FIGURGRUPPE, mit Pose und Morphs (`getVertexPosition` häutet). */
    static _huelle(inst) {
        const box = new THREE.Box3();
        const umkehr = inst.group.matrixWorld.clone().invert();
        const lage = new THREE.Matrix4();
        const punkt = new THREE.Vector3();
        for (const netz of Modellexportinhalt.objekte(inst)) {
            const position = netz.geometry?.getAttribute('position');
            if (!position) continue;
            lage.multiplyMatrices(umkehr, netz.matrixWorld);
            const schritt = Math.max(1, Math.floor(position.count / Modellansichten.PROBEN));
            for (let i = 0; i < position.count; i += schritt) {
                netz.getVertexPosition(i, punkt);
                box.expandByPoint(punkt.applyMatrix4(lage));
            }
        }
        return box;
    }

    /**
     * Alles außer der Figur und den Lichtern ausblenden; gibt zurück, was dabei aus ging.
     *
     * Ein Zweig mit Licht darin bleibt stehen und wird darunter weiter geprüft — sonst ginge mit dem Boden einer
     * Bühnengruppe auch ihr Licht aus. In der Figur selbst gehen nur die Hilfen aus: Knochenmarkierung und die Hülle
     * des Randleuchtens (`randleuchten.js`, Kind des Netzes).
     */
    static _verbergen(scene, gruppe) {
        const verborgen = [];
        const aus = (obj) => {
            if (obj.visible !== false) { obj.visible = false; verborgen.push(obj); }
        };
        const hatLicht = (obj) => {
            let gefunden = false;
            obj.traverse((kind) => { if (kind.isLight) gefunden = true; });
            return gefunden;
        };
        const fuehrtZurFigur = (obj) => {
            for (let p = gruppe; p; p = p.parent) if (p === obj) return true;
            return false;
        };
        const pruefen = (obj) => {
            if (obj === gruppe) {
                gruppe.traverse((kind) => {
                    if (kind.userData?._boneOverlay || kind.userData?.randleuchten || kind.isSkeletonHelper) aus(kind);
                });
                return;
            }
            if (obj.isLight) return;
            if (fuehrtZurFigur(obj) || hatLicht(obj)) {
                for (const kind of obj.children) pruefen(kind);
                return;
            }
            aus(obj);
        };
        for (const kind of scene.children) pruefen(kind);
        return verborgen;
    }
}
