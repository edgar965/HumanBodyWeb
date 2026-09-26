/**
 * Kamerafolge — die Kamera fährt der Figur nach, wie ein Kamerawagen.
 *
 * WARUM (11.09.2026): `136_28` geht 4,3 Körperlängen weit. Beim Browser-
 * Video steht die Kamera, wo der Nutzer sie hingestellt hat, und die Figur
 * ist nach zwei Sekunden aus dem Bild. Der Server-Weg hat seine Kamera
 * längst an der Figur (`filmrender.py`, `_kamera`); hier holt das Häkchen
 * „Kamera folgt" dasselbe nach.
 *
 * NUR IN DER BODENEBENE (x, z). Die Höhe bleibt, wie sie steht: Das Becken
 * hebt und senkt sich bei jedem Schritt um rund drei Zentimeter, und eine
 * Kamera, die dem folgt, wippt mit — im Bild sähe die Figur still und der
 * Boden bewegt aus. Bezug ist das Becken (`DEF-spine`), der Wurzelknochen
 * des Rigify-Rigs; es trägt die Wurzelbewegung der BVH.
 *
 * Ohne Three.js-Import: Es werden nur Zahlen aus `position`, `target` und
 * `matrixWorld.elements` gelesen — so läuft die Klasse in Node und ist
 * prüfbar (`test_js_kamerafolge.py`).
 */
export class Kamerafolge {
    static BEZUGSKNOCHEN = 'DEF-spine';

    /**
     * @param inst     Figur (mit `bodyMesh.skeleton`)
     * @param camera   Kamera mit `position` und `updateMatrixWorld()`
     * @param controls Steuerung mit `target` und `update()` (OrbitControls)
     */
    constructor(inst, camera, controls) {
        this.knochen = Kamerafolge.bezugsknochen(inst);
        this.camera = camera;
        this.controls = controls;
        this.start = null;
    }

    /** Das Becken der Figur — oder die Wurzel, wenn es keines gibt. */
    static bezugsknochen(inst) {
        const knochen = inst?.bodyMesh?.skeleton?.bones || [];
        return knochen.find((k) => k.name === Kamerafolge.BEZUGSKNOCHEN) || knochen[0] || null;
    }

    /** Weltlage des Bezugsknochens, frisch gerechnet. */
    _figur() {
        const k = this.knochen;
        if (!k) return [0, 0, 0];
        k.updateWorldMatrix?.(true, false);
        const m = k.matrixWorld.elements;
        return [m[12], m[13], m[14]];
    }

    /** Ausgangslage merken: Figur, Kamera, Blickpunkt. */
    starten() {
        const p = this.camera.position, z = this.controls?.target;
        this.start = {
            figur: this._figur(),
            kamera: [p.x, p.y, p.z],
            ziel: z ? [z.x, z.y, z.z] : null,
        };
        return this;
    }

    /** Versatz der Figur seit dem Start — nur in der Bodenebene. */
    static versatz(start, jetzt) {
        return [jetzt[0] - start[0], 0, jetzt[2] - start[2]];
    }

    /** Kamera und Blickpunkt um den Weg der Figur mitnehmen. */
    nachfuehren() {
        if (!this.start) return null;
        const v = Kamerafolge.versatz(this.start.figur, this._figur());
        const { kamera, ziel } = this.start;
        this.camera.position.set(kamera[0] + v[0], kamera[1] + v[1], kamera[2] + v[2]);
        if (ziel && this.controls?.target) {
            this.controls.target.set(ziel[0] + v[0], ziel[1] + v[1], ziel[2] + v[2]);
        }
        // Reine Verschiebung: Die Blickrichtung bleibt, nur die Matrix muss
        // vor dem Rendern frisch sein.
        this.camera.updateMatrixWorld?.(true);
        return v;
    }

    /** Alles zurück, wie es vor der Aufnahme stand. */
    beenden() {
        if (!this.start) return;
        const { kamera, ziel } = this.start;
        this.camera.position.set(kamera[0], kamera[1], kamera[2]);
        if (ziel && this.controls?.target) this.controls.target.set(ziel[0], ziel[1], ziel[2]);
        this.controls?.update?.();
        this.camera.updateMatrixWorld?.(true);
        this.start = null;
    }
}
