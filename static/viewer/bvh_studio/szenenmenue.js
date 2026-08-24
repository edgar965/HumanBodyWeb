import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { state } from './state.js';
/**
 * Kontextmenue und Klickauswahl in der 3D-Ansicht des Studios.
 *
 * Aus index.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Viewport context menu — right-click in 3D scene to set light position
// =========================================================================
export function setupViewportContextMenu() {
    const menu = document.getElementById('viewport-context-menu');
    if (menu) menu.style.display = 'none';

    const canvas = state.renderer?.domElement || document.getElementById('studio-canvas');
    if (!canvas) return;

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Alt+Click in 3D-Szene: Licht oder Scene-Object an Klick-Position setzen
    canvas.addEventListener('click', (e) => {
        if (!e.altKey || e.button !== 0) return;
        const track = state.project.tracks[state.selectedTrackIdx];
        if (!track) return;
        const isLight = track.type === 'light' && track.light && !track.light.isAmbientLight;
        const isSceneObj = track.type === 'scene_object' && track.subtype === 'custom' && track.mesh;
        if (!isLight && !isSceneObj) return;

        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, state.camera);
        // Gegen Mesh-Szene raycasten (ohne Lichter/Helper/Grid/selbst)
        const selfMesh = isSceneObj ? track.mesh : null;
        const intersects = raycaster.intersectObjects(state.scene.children, true).filter(h => {
            const o = h.object;
            if (!o.visible || o.isLight) return false;
            if (o.type?.includes('Helper')) return false;
            if (o.type === 'GridHelper') return false;
            // Bei Scene-Object: eigenes Mesh ignorieren (würde sich selbst treffen)
            if (selfMesh && (o === selfMesh || selfMesh.getObjectById?.(o.id))) return false;
            return true;
        });
        let hitPoint = null;
        if (intersects.length > 0) hitPoint = intersects[0].point.clone();
        else {
            const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
            const hit = new THREE.Vector3();
            if (raycaster.ray.intersectPlane(plane, hit)) hitPoint = hit;
        }
        if (!hitPoint) return;

        if (isLight) {
            track.light.position.copy(hitPoint);
            if (hitPoint.y < 0.5) track.light.position.y = Math.max(hitPoint.y + 2, 2);
            track.light.target?.updateMatrixWorld();
            track.lightHelper?.update?.();
            fn.serverLog?.('light_moved', `track=${track.name}`);
        } else if (isSceneObj) {
            track.mesh.position.copy(hitPoint);
            fn.serverLog?.('object_moved', `track=${track.name}`);
        }
        fn.updateProperties();
    });

    // Links-Klick: Licht-Helper oder Scene-Object auswählen. Wir sammeln ALLE Kandidaten
    // und wählen den NÄCHSTEN Treffer — sonst "gewinnt" ein Licht-Cone weit hinten gegen
    // den Boden direkt vor der Kamera.
    canvas.addEventListener('mousedown', (e) => {
        if (e.button !== 0 || e.altKey || e.shiftKey || e.ctrlKey) return;
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, state.camera);

        // Filtert Raycast-Hits: Objekt und alle Vorfahren müssen visible sein.
        // Three.js raycast matcht auch visible=false Objekte (by design).
        const isVisibleInTree = (obj) => {
            for (let o = obj; o; o = o.parent) if (o.visible === false) return false;
            return true;
        };
        let best = null;  // { dist, trackIdx }
        for (let i = 0; i < state.project.tracks.length; i++) {
            const t = state.project.tracks[i];
            let hits = null;
            // Licht-Helper nur wenn User die Helferlinien eingeschaltet hat (track.lightVisible).
            // Für den Kegel (indicator) reicht ein Hit — er ist immer da wenn coneVisible.
            if (t.type === 'light' && t.lightHelper) {
                const targets = [];
                if (t.lightVisible && t.lightHelper.spotHelper) targets.push(t.lightHelper.spotHelper);
                if (t.coneVisible !== false && t.lightHelper.originCone) targets.push(t.lightHelper.originCone);
                for (const tgt of targets) {
                    const h = raycaster.intersectObject(tgt, true).filter(x => isVisibleInTree(x.object) && x.distance > 0.01);
                    if (h.length > 0 && (!hits || h[0].distance < hits[0].distance)) hits = h;
                }
            } else if (t.type === 'scene_object' && t.mesh) {
                hits = raycaster.intersectObject(t.mesh, true).filter(x => isVisibleInTree(x.object) && x.distance > 0.01);
            }
            if (!hits || hits.length === 0) continue;
            const d = hits[0].distance;
            if (best === null || d < best.dist) best = { dist: d, trackIdx: i };
        }
        if (best) fn.selectTrack?.(best.trackIdx);
    });
}
