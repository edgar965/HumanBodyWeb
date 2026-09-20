import * as THREE from 'three';
import { base64ToFloat32, base64ToUint32 } from '../gemeinsam/kodierung.js';

/**
 * Zielkaefig — das Zielnetz als Genesis-9-Käfig in EINER Three.js-Szene.
 *
 * Herausgelöst aus `Proportionen3dbuehne` (20.09.2026), als die Modellsicht
 * oben auf der Seite dasselbe Netz neben dem Ergebnis zeigen sollte (Edgar:
 * „3D links, 2D rechts … Wenn ich die Regler ändere, dann ändert sich gleich
 * das 3D Modell links"). Kein Renderer, keine Kamera — nur das Netz: die
 * erste Antwort von `zielnetz3d/` (mit Dreiecken und Gewicht) baut es
 * (`netzSetzen`), jede weitere tauscht die Punkte an Ort und Stelle
 * (`punkteSetzen`: Positionsattribut überschreiben, Normalen neu — 25.182
 * Punkte in Millisekunden). Matte Haut, ungepaarte Punkte (Gewicht 0) grau:
 * was dort steht, ist Modell, nicht Ziel. Dazu ein Gitter zum Zuschalten —
 * Donauwellen sieht man an den Kanten schneller als an der Schattierung;
 * es wird nur neu gebaut, wenn es sichtbar ist (50.000 Dreiecke).
 */
export class Zielkaefig {

    static HAUT = 0xd9b39c;
    static UNGEPAART = 0x8a8f99;

    /** @param szene die Szene, in der das Netz liegt */
    constructor(szene) {
        this.szene = szene;
        this.gruppe = new THREE.Group();
        this.gruppe.name = 'zielkaefig';
        this.szene.add(this.gruppe);
        this.netz = null;
        this.gitter = null;
        this.hoehe = null;
        this._gitterAn = false;
        this._gitterAlt = false;
    }

    get da() { return !!this.netz; }

    get visible() { return this.gruppe.visible; }
    set visible(an) { this.gruppe.visible = !!an; }

    /** Erste Antwort mit Dreiecken: Netz bauen. `netz`: `{dreiecke, gewicht}` (base64), sonst aus `antwort`. */
    netzSetzen(antwort, netz = null) {
        const dreieckeB64 = (netz || antwort).dreiecke;
        if (!dreieckeB64) return;
        const punkte = base64ToFloat32(antwort.punkte);
        const dreiecke = base64ToUint32(dreieckeB64);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geo.setIndex(new THREE.BufferAttribute(dreiecke, 1));
        geo.setAttribute('color', new THREE.BufferAttribute(this._farben((netz || antwort).gewicht, punkte.length / 3), 3));
        geo.computeVertexNormals();
        this._wegraeumen();
        this.netz = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
            vertexColors: true, roughness: 0.85, metalness: 0.0, side: THREE.DoubleSide,
        }));
        this.gruppe.add(this.netz);
        this.gitter = new THREE.LineSegments(new THREE.WireframeGeometry(geo),
            new THREE.LineBasicMaterial({ color: 0x223344, transparent: true, opacity: 0.35 }));
        this.gitter.visible = this._gitterAn;
        this.gruppe.add(this.gitter);
        this.hoehe = (antwort.hoehe_cm || 170) / 100;
    }

    /** Jede weitere Antwort: nur die Punkte tauschen, Normalen und Gitter neu. */
    punkteSetzen(antwort) {
        if (!this.netz) return;
        const punkte = base64ToFloat32(antwort.punkte);
        const lage = this.netz.geometry.attributes.position;
        if (punkte.length !== lage.array.length) return;
        lage.array.set(punkte);
        lage.needsUpdate = true;
        this.netz.geometry.computeVertexNormals();
        this.netz.geometry.computeBoundingSphere();
        this.hoehe = (antwort.hoehe_cm || this.hoehe * 100) / 100;
        this._gitterAlt = true;
        if (this.gitter && this.gitter.visible) this._gitterNeu();
    }

    /** Antwort anwenden: mit Dreiecken (oder `netz`) bauen, sonst die Punkte tauschen. */
    setzen(antwort, netz = null) {
        if (!this.netz && ((netz && netz.dreiecke) || antwort.dreiecke)) this.netzSetzen(antwort, netz);
        else this.punkteSetzen(antwort);
    }

    _gitterNeu() {
        if (!this.gitter || !this.netz) return;
        this.gitter.geometry.dispose();
        this.gitter.geometry = new THREE.WireframeGeometry(this.netz.geometry);
        this._gitterAlt = false;
    }

    gitterZeigen(an) {
        this._gitterAn = !!an;
        if (!this.gitter) return;
        this.gitter.visible = this._gitterAn;
        if (this._gitterAn && this._gitterAlt) this._gitterNeu();
    }

    _farben(gewichtB64, anzahl) {
        const farben = new Float32Array(anzahl * 3);
        const haut = new THREE.Color(Zielkaefig.HAUT), grau = new THREE.Color(Zielkaefig.UNGEPAART);
        const gewicht = gewichtB64 ? base64ToFloat32(gewichtB64) : null;
        for (let i = 0; i < anzahl; i++) {
            const f = gewicht && !(gewicht[i] > 0) ? grau : haut;
            farben[i * 3] = f.r; farben[i * 3 + 1] = f.g; farben[i * 3 + 2] = f.b;
        }
        return farben;
    }

    _wegraeumen() {
        if (this.netz) { this.gruppe.remove(this.netz); this.netz.geometry.dispose(); this.netz = null; }
        if (this.gitter) { this.gruppe.remove(this.gitter); this.gitter.geometry.dispose(); this.gitter = null; }
    }

    dispose() {
        this._wegraeumen();
        this.szene.remove(this.gruppe);
    }
}
