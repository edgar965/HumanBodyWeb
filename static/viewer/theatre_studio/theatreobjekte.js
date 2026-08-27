/**
 * Bindet Kamera, Licht und Würfel der Probeszene an Theatre-Objekte.
 *
 * Aus dem Inline-Modul in `theatre_studio.html` herausgelöst (Umbau
 * 27.08.2026): drei fast gleiche Blöcke aus `sheet.object(...)` und
 * `onValuesChange(...)` standen dort untereinander.
 */
export class Theatreobjekte {
    /** So viele Objekte trägt die Probeszene. */
    static ANZAHL = 3;

    /**
     * @param {Object} blatt das Theatre-Sheet
     * @param {import('./probeszene.js').Probeszene} szene
     */
    constructor(blatt, szene) {
        this.blatt = blatt;
        this.szene = szene;
        this._kamera();
        this._licht();
        this._wuerfel();
    }

    /** Ein Ort als Theatre-Werteobjekt. */
    static ort(vektor) {
        return { x: vektor.x, y: vektor.y, z: vektor.z };
    }

    _kamera() {
        const kamera = this.szene.camera;
        this.blatt.object('Camera', {
            position: Theatreobjekte.ort(kamera.position),
            fov: kamera.fov,
        }).onValuesChange(w => {
            kamera.position.set(w.position.x, w.position.y, w.position.z);
            kamera.fov = w.fov;
            kamera.updateProjectionMatrix();
        });
    }

    _licht() {
        const licht = this.szene.licht;
        this.blatt.object('Light', {
            position: Theatreobjekte.ort(licht.position),
            intensity: licht.intensity,
        }).onValuesChange(w => {
            licht.position.set(w.position.x, w.position.y, w.position.z);
            licht.intensity = w.intensity;
        });
    }

    _wuerfel() {
        const wuerfel = this.szene.wuerfel;
        this.blatt.object('Cube', {
            position: { x: 0, y: 1, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            color: { r: 0.48, g: 0.36, b: 0.75 },
        }).onValuesChange(w => {
            wuerfel.position.set(w.position.x, w.position.y, w.position.z);
            wuerfel.rotation.set(w.rotation.x, w.rotation.y, w.rotation.z);
            wuerfel.material.color.setRGB(w.color.r, w.color.g, w.color.b);
        });
    }
}
