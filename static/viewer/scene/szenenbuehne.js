import { TransformControls } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Buehne } from '../gemeinsam/buehne.js';

/**
 * Szenenbuehne — die Bühne der Szene-Seite: der gemeinsame Aufbau aus `Buehne`
 * plus das Verschiebewerkzeug, das nur diese Seite hat.
 *
 * Aus `boot.js init()` herausgeloest (Umbau 16.08.2026): Die ersten 60 Zeilen
 * von `init()` bauten Renderer, Szene, Kamera, drei Lichter und Gitter mit
 * genau denselben Zahlen, die auch `character_core.createSceneSetup()` und
 * `animations.js` verwenden — dreifach dasselbe. Jetzt eine Stelle.
 */
export class Szenenbuehne {

    /** Fällt die Breite des Rahmens aus, gilt dieser Mindestwert. */
    static MIN_BREITE = 100;

    bauen() {
        state.canvas = document.getElementById('viewer-canvas');
        this.rahmen = state.canvas.parentElement;
        // Die Szene-Seite nimmt die Maße ihres Rahmens und lässt `setSize` die
        // CSS-Größe der Leinwand mitsetzen.
        const teile = Buehne.bauen(state.canvas, { masse: 'rahmen', stil: true });
        state.renderer = teile.renderer;
        state.scene = teile.scene;
        state.camera = teile.camera;
        state.controls = teile.controls;
        state.keyLight = teile.keyLight;
        state.fillLight = teile.fillLight;
        state.backLight = teile.backLight;
        state.ambientLight = teile.ambient;
        this._werkzeug();
        window.addEventListener('resize', () => this.groesseAnpassen());
        return this;
    }

    masse() {
        return [Math.max(this.rahmen.clientWidth, Szenenbuehne.MIN_BREITE),
                this.rahmen.clientHeight || window.innerHeight];
    }

    /**
     * Verschiebewerkzeug. Seit three.js r169 ist TransformControls selbst kein
     * Object3D mehr — in die Szene gehört `getHelper()`.
     */
    _werkzeug() {
        const werkzeug = new TransformControls(state.camera, state.canvas);
        werkzeug.setMode('translate');
        werkzeug.setSpace('world');
        werkzeug.enabled = false;
        state.transformControls = werkzeug;
        state.transformHelper = werkzeug.getHelper();
        state.transformHelper.visible = false;
        state.scene.add(state.transformHelper);

        // Während des Ziehens darf die Kamera nicht mitdrehen.
        werkzeug.addEventListener('dragging-changed', ereignis => {
            state.controls.enabled = !ereignis.value;
            state.transformDragging = ereignis.value;
        });
        werkzeug.addEventListener('objectChange', () => {
            fn.updateCharacterListUI();
            fn.markDirty();
        });
    }

    groesseAnpassen() {
        const [breite, hoehe] = this.masse();
        state.renderer.setSize(breite, hoehe);
        state.camera.aspect = breite / hoehe;
        state.camera.updateProjectionMatrix();
    }
}
