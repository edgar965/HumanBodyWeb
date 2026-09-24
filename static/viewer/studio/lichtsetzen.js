import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';

/**
 * Alt+Klick in der 3D-Ansicht: setzt das gewählte Licht oder Szenenobjekt an
 * die angeklickte Stelle.
 *
 * Aus szenenmenue.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `setupViewportContextMenu()` hatte 96 Zeilen).
 */
export class Lichtsetzen {
    /** Unter dieser Höhe wird das Licht angehoben — sonst leuchtet es von unten. */
    static MINDESTHOEHE = 0.5;
    /** Um so viel über den Treffpunkt, wenn angehoben wird. */
    static ANHEBUNG = 2;

    /** @param {HTMLCanvasElement} canvas */
    constructor(canvas) {
        this.canvas = canvas;
        this.strahl = new THREE.Raycaster();
        this.zeiger = new THREE.Vector2();
        canvas.addEventListener('click', (e) => this._klick(e));
    }

    _klick(e) {
        if (!e.altKey || e.button !== 0) return;
        const spur = state.project.tracks[state.selectedTrackIdx];
        if (!spur) return;
        const istLicht = spur.type === 'light' && spur.light
                         && !spur.light.isAmbientLight;
        const istObjekt = spur.type === 'scene_object'
                          && spur.subtype === 'custom' && spur.mesh;
        if (!istLicht && !istObjekt) return;

        this._strahlSetzen(e);
        const stelle = this._treffpunkt(istObjekt ? spur.mesh : null);
        if (!stelle) return;
        if (istLicht) this._lichtSetzen(spur, stelle);
        else this._objektSetzen(spur, stelle);
        fn.updateProperties();
    }

    _strahlSetzen(e) {
        const rahmen = this.canvas.getBoundingClientRect();
        this.zeiger.x = ((e.clientX - rahmen.left) / rahmen.width) * 2 - 1;
        this.zeiger.y = -((e.clientY - rahmen.top) / rahmen.height) * 2 + 1;
        this.strahl.setFromCamera(this.zeiger, state.camera);
    }

    /**
     * Der Punkt, den der Strahl trifft — ersatzweise die Bodenebene.
     * @param {THREE.Object3D|null} eigenes das eigene Netz, das nicht zählt
     */
    _treffpunkt(eigenes) {
        const treffer = this.strahl
            .intersectObjects(state.scene.children, true)
            .filter(t => Lichtsetzen._zaehlt(t.object, eigenes));
        if (treffer.length > 0) return treffer[0].point.clone();
        const boden = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
        const punkt = new THREE.Vector3();
        return this.strahl.ray.intersectPlane(boden, punkt) ? punkt : null;
    }

    /** Lichter, Helferlinien und das Gitter sind keine Zielflächen. */
    static _zaehlt(objekt, eigenes) {
        if (!objekt.visible || objekt.isLight) return false;
        if (objekt.type?.includes('Helper')) return false;
        if (objekt.type === 'GridHelper') return false;
        // Ein Szenenobjekt würde sich sonst selbst treffen.
        if (eigenes && (objekt === eigenes
                        || eigenes.getObjectById?.(objekt.id))) return false;
        return true;
    }

    _lichtSetzen(spur, stelle) {
        spur.light.position.copy(stelle);
        if (stelle.y < Lichtsetzen.MINDESTHOEHE) {
            spur.light.position.y = Math.max(stelle.y + Lichtsetzen.ANHEBUNG,
                                             Lichtsetzen.ANHEBUNG);
        }
        spur.light.target?.updateMatrixWorld();
        spur.lightHelper?.update?.();
        fn.serverLog?.('light_moved', `track=${spur.name}`);
    }

    _objektSetzen(spur, stelle) {
        spur.mesh.position.copy(stelle);
        fn.serverLog?.('object_moved', `track=${spur.name}`);
    }
}
