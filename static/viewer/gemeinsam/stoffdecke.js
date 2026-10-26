import { Pass } from 'three/addons/postprocessing/Pass.js';

/**
 * Stoffdecke — die eigenen Stücke, deren Form erst im Shader entsteht, nach der Auswahlaura NOCH EINMAL zeichnen (26.10.2026, Edgar mit Bild: „der Schleier bei dem Oberteil ist
 * aber noch immer da?“).
 *
 * WARUM: `OutlinePass` rendert Maske und Tiefe mit EIGENEM Material (`overrideMaterial`) — ohne den Vertex-Shader der Schale (`EigenkleidGLSL`: Sitz, Brücke, Fall). Die Maske ist
 * deshalb der Umriss der HAUT, und das Glühen um ihn liegt ohne Tiefentest über dem Bild — auch über dem Stoff, der seitlich und unter der Brust weiter absteht: ein heller,
 * streifiger Schleier (im Chrome gesehen; ohne Auswahl verschwindet er).
 *
 * WIE: nach den Aura-Pässen nur die Schalen in denselben Puffer (Farbe + Tiefe der Szene aus dem `RenderPass`, ohne Löschen, Tiefentest ≤): wo Stoff vorn liegt, deckt er das
 * Glühen; außen um das Stück bleibt es. Während des Zeichnens ist alles andere unsichtbar (Lichter bleiben), der Hintergrund aus und die Schattenkarte wird nicht neu
 * gerechnet (sonst wäre sie ohne die übrigen Netze). Gezeichnet wird nur, wenn ein solches Stück sichtbar ist. Der Rock (`Eigenrock`, echte Geometrie) braucht das nicht.
 */
export class Stoffdecke extends Pass {

    constructor(szene, kamera) {
        super();
        this.scene = szene;
        this.camera = kamera;
        this.needsSwap = false;
    }

    /** Ein Netz, dessen Form erst im Shader entsteht: Schale oder Kragen eines eigenen Stücks (alles mit `userData.eigenkleid` außer dem Rock). */
    static schale(o) {
        const art = o.userData?.eigenkleid;
        return typeof art === 'string' && !art.endsWith('rock');
    }

    /** Was ohne Tiefentest über der Szene liegt (Knochenanzeige, Griffe) — wird mitgezeichnet, sonst deckte der Stoff es zu. */
    static ohneTiefe(o) {
        return [o.material].flat().some(m => m?.depthTest === false);
    }

    render(renderer, _writeBuffer, readBuffer) {
        const schalen = [], aus = [];
        this.scene.traverseVisible((o) => {
            if (Stoffdecke.schale(o)) schalen.push(o);
            else if ((o.isMesh || o.isLine || o.isPoints || o.isSprite) && !Stoffdecke.ohneTiefe(o)) aus.push(o);
        });
        if (!schalen.length) return;
        const hintergrund = this.scene.background, autoClear = renderer.autoClear, schatten = renderer.shadowMap.autoUpdate;
        for (const o of aus) o.visible = false;
        this.scene.background = null;
        renderer.autoClear = false;
        renderer.shadowMap.autoUpdate = false;
        try {
            renderer.setRenderTarget(this.renderToScreen ? null : readBuffer);
            renderer.render(this.scene, this.camera);
        } finally {
            for (const o of aus) o.visible = true;
            this.scene.background = hintergrund;
            renderer.autoClear = autoClear;
            renderer.shadowMap.autoUpdate = schatten;
        }
    }
}
