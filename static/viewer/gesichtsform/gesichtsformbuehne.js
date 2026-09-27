import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';

/**
 * Gesichtsformbuehne — die Figur der Seite „Gesichtsform" in 3D, mit den Schnittlinien darauf.
 *
 * Die Figur ist `Genesis9Modell` (wie Szene und Auftragsseite) mit der Stellung samt Kopf-Eigen und den
 * Kacheln. Der Server rechnet in derselben Lage (Käfig, Füße auf 0) — die Rahmen der Antwort
 * (`ursprung`, `achsen`: x', y', z' in Welt) passen also direkt: ein Profilpunkt (u, z) eines Schnitts
 * bei `lage` liegt bei ursprung + lage·Ebenenachse + u·Querachse + z·z'. Blau die Figur, rot das Ziel,
 * 0,3 mm vor der Fläche, damit sie nicht darin verschwinden.
 */
export class Gesichtsformbuehne {

    static VOR = 0.3;

    constructor(feld, hinweis) {
        this.feld = feld;
        this.hinweis = hinweis;
        this.modell = null;
        this._stand = null;
        this.linien = new THREE.Group();
        const zeichner = this.zeichner = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        zeichner.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        zeichner.outputColorSpace = THREE.SRGBColorSpace;
        feld.appendChild(zeichner.domElement);
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(25, 1, 0.02, 20);
        this.steuerung = new OrbitControls(this.kamera, zeichner.domElement);
        this.steuerung.enableDamping = true;
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0xc8c2ba, 1.3));
        const licht = new THREE.DirectionalLight(0xffffff, 1.0);
        licht.position.set(1, 1.5, 2);
        this.kamera.add(licht);
        this.szene.add(this.kamera, this.linien);
        new ResizeObserver(() => this._groesse()).observe(feld);
        const lauf = () => {
            this.steuerung.update();
            zeichner.render(this.szene, this.kamera);
            requestAnimationFrame(lauf);
        };
        requestAnimationFrame(lauf);
    }

    _groesse() {
        const b = this.feld.clientWidth || 600, h = this.feld.clientHeight || 500;
        this.zeichner.setSize(b, h);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
    }

    _melden(text) { this.hinweis.textContent = text; this.hinweis.hidden = !text; }

    /** Die Figur bauen, wenn sich Stellung oder Kacheln geändert haben. */
    async figur(daten) {
        const stand = JSON.stringify([daten.stellung, daten.fototextur]);
        if (stand === this._stand) return;
        this._stand = stand;
        this._melden('Figur wird gebaut …');
        const neu = new Genesis9Modell('gesichtsform', {
            figur: 'basis', regler: { ...daten.stellung }, presetName: daten.titel, fototextur: daten.fototextur || {},
        });
        await neu.bauen();
        if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
        this.modell = neu;
        this.szene.add(neu.group);
        this._melden('');
        if (!this._gestellt) { this.ansicht('vorn', daten.rahmen); this._gestellt = true; }
    }

    async wert(regler, wert) {
        if (this.modell) await this.modell.reglerSetzen(regler, wert);
    }

    ansicht(art, rahmen = this.rahmen) {
        if (!rahmen) return;
        this.rahmen = rahmen;
        const o = new THREE.Vector3(...rahmen.ursprung), [x, y, z] = rahmen.achsen.map(a => new THREE.Vector3(...a));
        const ziel = o.clone().addScaledVector(y, -0.02);
        const schraeg = z.clone().add(x.clone().multiplyScalar(0.7));
        const richtung = art === 'seite' ? x.clone() : art === 'schraeg' ? schraeg : z;
        this.kamera.position.copy(ziel).addScaledVector(richtung.normalize(), 0.62);
        this.kamera.up.copy(y);
        this.steuerung.target.copy(ziel);
    }

    /** Linien der Figur (`block`: ist oder ergebnis, mit Rahmen) und des Ziels (im Rahmen der Figur). */
    schnittlinien(block, ziel, sichtbar = true) {
        this.linien.clear();
        this.linien.visible = sichtbar;
        if (!block) return;
        this.linien.add(this._linie(block.schnitte, block.rahmen, 0x3f7fe0));
        if (ziel) this.linien.add(this._linie(ziel, block.rahmen, 0xe0443a));
    }

    _linie(schnitte, rahmen, farbe) {
        const o = new THREE.Vector3(...rahmen.ursprung), achsen = rahmen.achsen.map(a => new THREE.Vector3(...a));
        const punkte = [];
        for (const p of schnitte || []) {
            const [ebene, quer] = p.art === 'waagerecht' ? [achsen[1], achsen[0]] : [achsen[0], achsen[1]];
            const ort = (i) => o.clone().addScaledVector(ebene, p.lage / 1000).addScaledVector(quer, p.u[i] / 1000)
                .addScaledVector(achsen[2], (p.z[i] + Gesichtsformbuehne.VOR) / 1000);
            for (let i = 1; i < p.u.length; i++) {
                if (p.z[i] === null || p.z[i - 1] === null) continue;
                punkte.push(ort(i - 1), ort(i));
            }
        }
        const geo = new THREE.BufferGeometry().setFromPoints(punkte);
        return new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: farbe, depthTest: true }));
    }
}
