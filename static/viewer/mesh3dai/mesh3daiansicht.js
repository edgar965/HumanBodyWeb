/**
 * Mesh3daiansicht — EIN 3D-Feld der Seite „Mesh3D-AI“ (14.10.2026): zeigt je nach Art die Eingabe (Punktwolke der Außenfläche), die gewünschte Ausgabe (Genesis-Modell in der Pose) oder die Ausgabe des Netzes
 * (mit Fehlerpunkten und dem Soll als Geist). Was gezeichnet wird, bestimmt der Zeichner der Zeile (`Mesh3daibereiche`: ganzer Körper, Gesicht, Hände/Füße, Kleider); die Ansicht hält nur Leinwand, Licht und Kamera.
 *
 * Gezeichnet wird nur auf Anforderung (`zeigen`, Ziehen mit der Maus, Größenänderung), nie in einer Dauerschleife — zwölf Felder belasten die Grafikkarte sonst ohne Grund, und in einem verdeckten Tab
 * liefe `requestAnimationFrame` ohnehin nicht. Die drei Felder einer Zeile sind gekoppelt (`koppeln`): wer eines dreht, dreht alle, damit Eingabe, Soll und Ausgabe aus demselben Winkel zu vergleichen sind.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';

export class Mesh3daiansicht {
    static GRUND = 0x1b1f27;
    static GRUND_WOLKE = 0x5a6170;

    /**
     * @param {HTMLElement} feld das Element, in das die Leinwand kommt
     * @param {string} art 'eingabe' | 'soll' | 'ausgabe'
     * @param {{zeichnen: (inhalt: THREE.Group, art: string, d: object) => void}} zeichner
     * @param {{position: number[], ziel: number[], boden: boolean}} kamera Standort und Blickziel in m; `boden` = Raster auf y = 0
     */
    constructor(feld, art, zeichner, kamera) {
        this.feld = feld;
        this.art = art;
        this.zeichner = zeichner;
        this.gekoppelt = [];
        this._sperre = false;
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.setClearColor(Mesh3daiansicht.GRUND, 1);
        feld.appendChild(this.renderer.domElement);
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(35, 3 / 4, 0.02, 50);
        this.kamera.position.fromArray(kamera.position);
        this.steuerung = new OrbitControls(this.kamera, this.renderer.domElement);
        this.steuerung.target.fromArray(kamera.ziel);
        this.steuerung.update();
        this.steuerung.addEventListener('change', () => this._geaendert());
        this.szene.add(new THREE.HemisphereLight(0xdfe8ff, 0x303642, 1.1));
        const licht = new THREE.DirectionalLight(0xffffff, 1.6);
        licht.position.set(2, 4, 3);
        this.szene.add(licht);
        if (kamera.boden) this.szene.add(new THREE.GridHelper(3, 12, 0x4a5366, 0x2f3644));
        this.inhalt = new THREE.Group();
        this.szene.add(this.inhalt);
        this.hinweis = document.createElement('div');
        this.hinweis.className = 'mesh3dai-leer';
        this.hinweis.textContent = 'noch keine Probe';
        feld.appendChild(this.hinweis);
        // Nur zeichnen, was im Fenster steht (15.10.2026): jedes Feld hat einen eigenen WebGL-Kontext, und „Textur“ lud die 10 Bilder (2048 px) in ALLE 15 Kontexte zugleich hoch —
        // gemessen 4,5 s Stillstand des Hauptfadens nach dem ersten Klick. Ein verdecktes Feld merkt sich den Auftrag und zeichnet, sobald es ins Bild kommt.
        this._imBild = false;
        this._offen = false;
        new IntersectionObserver(eintraege => {
            this._imBild = eintraege[eintraege.length - 1].isIntersecting;
            if (this._imBild && this._offen) this.zeichnen();
        }, { rootMargin: '200px' }).observe(feld);
        new ResizeObserver(() => this._groesse()).observe(feld);
        this._groesse();
    }

    /** Die Ansichten gleich drehen lassen (alle untereinander). */
    static koppeln(ansichten) {
        for (const a of ansichten) a.gekoppelt = ansichten.filter(b => b !== a);
    }

    _groesse() {
        const b = Math.max(this.feld.clientWidth, 2);
        const h = Math.max(this.feld.clientHeight, 2);
        this.renderer.setSize(b, h, false);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
        this.zeichnen();
    }

    _geaendert() {
        this.zeichnen();
        if (this._sperre) return;
        for (const a of this.gekoppelt) a._uebernehmen(this);
    }

    _uebernehmen(von) {
        this._sperre = true;
        this.kamera.position.copy(von.kamera.position);
        this.steuerung.target.copy(von.steuerung.target);
        this.steuerung.update();
        this.zeichnen();
        this._sperre = false;
    }

    zeichnen() {
        if (!this._imBild) {
            this._offen = true;
            return;
        }
        this._offen = false;
        this.renderer.render(this.szene, this.kamera);
    }

    _leeren() {
        for (const kind of [...this.inhalt.children]) {
            this.inhalt.remove(kind);
            Mesh3daigemeinsam.freigeben(kind);
        }
    }

    /**
     * @param {object|null} d `{beschreibung, teil, id, geist}` — Form siehe `Mesh3daibereiche`. `null` leert das Feld.
     * @param {string|null} leer der Text im leeren Feld (Vorgabe „noch keine Probe“)
     */
    zeigen(d, leer = null) {
        this._leeren();
        this.hinweis.hidden = !!d;
        this.hinweis.textContent = leer ?? 'noch keine Probe';
        // Echte Figur (Wolke und Fläche): Ursula1 trägt dunkelblaue Kleider und schwarzes Haar — auf dem dunklen Grund (1b1f27) kaum zu sehen (gesehen 15.10.2026). Darum ein hellerer Grund, und zwar in ALLEN
        // drei Feldern (Edgar, 15.10.2026: „das muss einheitlich sein in allen views“ — vorher war das Ergebnis dunkel).
        this.renderer.setClearColor(d?.echt ? Mesh3daiansicht.GRUND_WOLKE : Mesh3daiansicht.GRUND, 1);
        if (d) {
            this.zeichner.zeichnen(this.inhalt, this.art, d);
            Mesh3dairigzeichner.ueberlagern(this.inhalt, this.art, d);
        }
        this.zeichnen();
    }
}
