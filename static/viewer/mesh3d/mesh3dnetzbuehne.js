import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Meshfigurlicht } from '../meshfigur/meshfigurlicht.js';
import { Meshfigurnetze } from '../meshfigur/meshfigurnetze.js';
import { Mesh3dbuehnengroesse } from './mesh3dbuehnengroesse.js';

/**
 * Mesh3dnetzbuehne — die Karte „Mesh-Ansicht“ der Jobseite „Mesh-3D“ (12.10.2026): NUR das Netz der Datei, mittig, unter der 3D-Ansicht.
 *
 * Edgar: „mach eine zweite 3D View im Job wo ich NUR das Mesh sehen kann, mit der gleichen Beleuchtung wie das 3D Modell, das Mesh soll in die Mitte kommen. Die neue 3D View soll darunter
 * kommen, auch einstellbar in Größe.“ Eigene Leinwand, eigene Szene, eigene Kamera — aber dieselben Teile wie die erste Ansicht: das Netz lädt `Meshfigurnetze` (Lage der Erkennung, bei
 * Kopfnetz mit den Schnittebenen am Hals; das Netz steht hier bei x = 0 statt 1,5 m links der Figur), das Licht stellt `Meshfigurlicht` (dieselbe Klasse wie in `Meshfigurbuehne`), der
 * Renderer hat dieselben Einstellungen (sRGB, kein Tonemapping), die Leinwand dieselbe Pixelgrenze (`Meshfigurbuehne.MAX_PIXEL`). Kein Bodengitter, keine Figur, kein Haar, keine Kleider.
 * Das Netz wird mit `diffus` geladen (Metall 0 statt des glTF-Vorgabewerts 1, siehe `Meshfigurnetze`) — sonst stünde es im selben Licht fast schwarz da.
 *
 * Die Kamera passt sich dem Netz an, sobald es geladen ist: Drehpunkt = Mitte seines Kastens (also mitten im Bild, auch wenn die Lage der Erkennung das Netz nicht um x = 0 und z = 0
 * zentriert), Abstand so, dass es mit Rand hineinpasst. Wer die Ansicht angefasst hat, behält seine Kamera — nur ein NEUES Netz (anderer Eingang oder andere Lage) passt sie wieder ein.
 * Höhe und Breite stellt `Mesh3dbuehnengroesse` (Regler und Ziehgriff).
 */
export class Mesh3dnetzbuehne {
    static SCHLUESSEL = 'mesh3d.netzansicht.hoehe';
    static SCHLUESSEL_BREITE = 'mesh3d.netzansicht.breite';
    /** Luft um das Netz beim Einpassen (Faktor auf den nötigen Abstand). */
    static RAND = 1.15;

    /** @param {object} seite die „Seite“ der Bühne (`Mesh3dbuehne.adapter`): `dateiAdresse(ordner, name)` und `netzWartet()` */
    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('netz-buehne');
        this.hinweis = document.getElementById('netz-hinweis');
        this._kinder = 0;
        this._angefasst = false;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine Mesh-Ansicht: ${fehler.message}`); return; }
        this.netze = new Meshfigurnetze(seite, this.szene, text => this._melden(text), { diffus: true });
        this.groesse = new Mesh3dbuehnengroesse(this.feld, document.getElementById('netz-groesse'), document.getElementById('netz-groesse-wert'), Mesh3dnetzbuehne.SCHLUESSEL,
            { regler: document.getElementById('netz-breite'), wert: document.getElementById('netz-breite-wert'), schluessel: Mesh3dnetzbuehne.SCHLUESSEL_BREITE });
    }

    _melden(text) { if (this.hinweis) { this.hinweis.textContent = text; this.hinweis.hidden = !text; } }

    _buehne() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'meshfigur-leinwand';
        this.feld.appendChild(this.canvas);
        // Wie `Meshfigurbuehne._buehne`: gleiche Einstellungen, damit dasselbe Netz hier wie dort aussieht.
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.localClippingEnabled = true;
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(30, 1, 0.05, 50);
        this.kamera.position.set(0, 1.0, 4.4);
        this.steuerung = new OrbitControls(this.kamera, this.canvas);
        this.steuerung.target.set(0, 0.9, 0);
        this.steuerung.enableDamping = true;
        this.steuerung.addEventListener('start', () => { this._angefasst = true; });
        Meshfigurlicht.einrichten(this.szene, this.kamera);
        new ResizeObserver(() => this._groesse()).observe(this.feld);
        const lauf = () => {
            if (!document.hidden && this.canvas.getClientRects().length) this.bild();
            requestAnimationFrame(lauf);
        };
        requestAnimationFrame(lauf);
    }

    /** Ein Bild zeichnen (die Schleife ruft es nur, wenn die Ansicht sichtbar ist; im verdeckten Tab von Hand). */
    bild() {
        this._nachziehen();
        this.steuerung.update();
        this.renderer.render(this.szene, this.kamera);
    }

    /** Leinwand an den Behälter anpassen, mit derselben Pixelgrenze wie die erste Ansicht; ausgeblendet gibt sie ihren Speicher frei. */
    _groesse() {
        const b = this.feld.clientWidth, h = this.feld.clientHeight;
        if (!b || !h) {
            this.renderer.setPixelRatio(1);
            this.renderer.setSize(1, 1, false);
            return;
        }
        const dichte = Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(Meshfigurbuehne.MAX_PIXEL / (b * h)));
        this.renderer.setPixelRatio(Math.max(0.5, dichte));
        this.renderer.setSize(b, h);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
        if (!this._angefasst && this._kinder) this._einpassen();
    }

    /** Der Zustand des Auftrags „Mesh to 3D“ (`/api/meshfigur/<id>/zustand/`), oder null, solange es ihn nicht gibt. */
    zeigen(z) {
        if (!this.renderer) return;
        if (!z) { this._melden('Noch kein Netz — die Ansicht erscheint, sobald der Auftrag „Mesh to 3D“ das Netz übernommen hat.'); return; }
        // `zeigen` lädt nur neu, wenn Eingang oder Lage sich geändert haben; das neue Netz kommt unsichtbar und leer, `_nachziehen` passt die Kamera an, sobald es da ist.
        if (this.netze.zeigen(z)) {
            this.netze.sichtbar(true);
            this._kinder = 0;
            this._angefasst = false;
        }
        this._meldung();
    }

    _meldung() {
        if (this.seite.netzWartet?.()) this._melden('Die Vorschau des Netzes wird gebaut …');
        else if (!this.netze.gruppe) this._melden('Noch kein Netz …');
        else this._melden(this._kinder ? '' : 'Netz wird geladen …');
    }

    /** Das Netz kommt asynchron (je Teil ein Ladevorgang): ändert sich die Zahl der geladenen Teile, wird eingepasst und die Meldung nachgezogen. */
    _nachziehen() {
        const kinder = this.netze.gruppe?.children.length || 0;
        if (kinder === this._kinder) return;
        this._kinder = kinder;
        if (kinder && !this._angefasst) this._einpassen();
        this._meldung();
    }

    /** Kamera auf die Mitte des Netz-Kastens richten und so weit zurücknehmen, dass es mit Rand ins Bild passt. */
    _einpassen() {
        const gruppe = this.netze.gruppe;
        if (!gruppe) return;
        gruppe.updateMatrixWorld(true);
        const kasten = new THREE.Box3().setFromObject(gruppe);
        if (kasten.isEmpty()) return;
        const mitte = kasten.getCenter(new THREE.Vector3()), groesse = kasten.getSize(new THREE.Vector3());
        const tan = Math.tan(THREE.MathUtils.degToRad(this.kamera.fov / 2));
        const hoch = groesse.y / 2 / tan;
        const breit = Math.max(groesse.x, groesse.z) / 2 / (tan * Math.max(this.kamera.aspect, 0.1));
        const abstand = Math.max(hoch, breit) * Mesh3dnetzbuehne.RAND + groesse.z / 2;
        this.steuerung.target.copy(mitte);
        this.kamera.position.set(mitte.x, mitte.y, mitte.z + abstand);
        this.kamera.near = Math.max(0.01, abstand / 200);
        this.kamera.far = abstand * 20 + groesse.length();
        this.kamera.updateProjectionMatrix();
        this.steuerung.update();
    }
}
