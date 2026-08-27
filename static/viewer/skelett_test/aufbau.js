import { Testzustand } from './testzustand.js';
import { loadRetargetConfig } from '../retarget_hybrid.js';
import { loadRigifySkeleton } from '../skeleton_test.js';
import { loadAnimationTree, bindPlaybackControls } from './animationsliste.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Sichtschalter } from './sichtschalter.js';
import { Testszene } from './testszene.js';

/**
 * Aufbau der Vergleichsseite: Szene, Umschalter, Zeichenschleife.
 *
 * Aus skeleton_test.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 27.08.2026 (Befund `jsfunktionen`): `init()` hatte 103 Zeilen. Szene
 * und Schalter stehen jetzt in `Testszene` bzw. `Sichtschalter`.
 */

export async function init() {
    // Ohne die Zuordnungstabelle kann die Seite nichts vergleichen. Der Abruf
    // wirft bei einem Serverfehler (`Serverabruf` prueft den Status) —
    // ungefangen bliebe die Seite leer, mit einer stillen Rejection in der
    // Konsole. Gefunden mit skills2 `jsfaenger` am 16.08.2026.
    try {
        await loadRetargetConfig();
    } catch (fehler) {
        Protokoll.fehler('Skelett-Test', 'Retarget-Konfiguration nicht ladbar:',
                         fehler);
        const platz = document.getElementById('viewer-canvas')?.parentElement;
        if (platz) {
            platz.insertAdjacentHTML('afterbegin',
                '<p class="st-fehler">Retarget-Konfiguration nicht ladbar: '
                + fehler.message + '</p>');
        }
        return;
    }

    Testszene.aufbauen(document.getElementById('viewer-canvas'));
    window.addEventListener('resize', onResize);
    Sichtschalter.binden();
    bindPlaybackControls();
    animate();

    // Fuer Playwright und die Browserkonsole.
    window.camera = Testzustand.camera;
    window.controls = Testzustand.controls;
    window.scene = Testzustand.scene;
    window.skeletons = Testzustand.skeletons;

    loadRigifySkeleton();
    loadAnimationTree();
}

export function onResize() {
    const container = Testzustand.renderer.domElement.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;
    Testzustand.renderer.setSize(w, h);
    Testzustand.labelRenderer.setSize(w, h);
    Testzustand.camera.aspect = w / h;
    Testzustand.camera.updateProjectionMatrix();
}

export function animate() {
    requestAnimationFrame(animate);
    const dt = Testzustand.clock.getDelta();
    Testzustand.controls.update();

    if (Testzustand.mixer && Testzustand.playing) Testzustand.mixer.update(dt);

    Testzustand.labelRenderer.render(Testzustand.scene, Testzustand.camera);
    Testzustand.renderer.render(Testzustand.scene, Testzustand.camera);

    // Bildrate
    Testzustand.frameCount++;
    Testzustand.fpsAccum += dt;
    if (Testzustand.fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = Testzustand.frameCount;
        Testzustand.frameCount = 0;
        Testzustand.fpsAccum = 0;
    }
}
