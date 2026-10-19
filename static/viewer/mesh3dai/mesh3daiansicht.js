/**
 * Mesh3daiansicht — EIN 3D-Feld der Seite „Mesh3D-AI“ (14.10.2026): zeigt je nach Art die Eingabe (Punktwolke der Außenfläche), die gewünschte Ausgabe (Genesis-Modell in der Pose) oder die Ausgabe des Netzes
 * (mit Fehlerpunkten und dem Soll als Geist). Was gezeichnet wird, bestimmt der Zeichner der Zeile (`Mesh3daibereiche`: ganzer Körper, Gesicht, Hände/Füße, Kleider); die Ansicht hält nur Leinwand, Licht und Kamera.
 * Seit 19.10.2026 ist die Leinwand eine 2D-Leinwand: gezeichnet wird mit EINEM Renderer für alle Felder (`Mesh3daizeichenflaeche` — jedes Bild nur einmal auf der Grafikkarte).
 *
 * Gezeichnet wird nur auf Anforderung (`zeigen`, Ziehen mit der Maus, Größenänderung), nie in einer Dauerschleife — zwölf Felder belasten die Grafikkarte sonst ohne Grund, und in einem verdeckten Tab
 * liefe `requestAnimationFrame` ohnehin nicht. Die drei Felder einer Zeile sind gekoppelt (`koppeln`): wer eines dreht, dreht alle, damit Eingabe, Soll und Ausgabe aus demselben Winkel zu vergleichen sind.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Mesh3daigemeinsam } from './mesh3daigemeinsam.js';
import { Mesh3dairigzeichner } from './mesh3dairigzeichner.js';
import { Mesh3daizeichenflaeche } from './mesh3daizeichenflaeche.js';

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
        this.grund = Mesh3daiansicht.GRUND;
        this.leinwand = feld.appendChild(document.createElement('canvas'));
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(35, 3 / 4, 0.02, 50);
        this.kamera.position.fromArray(kamera.position);
        this.steuerung = new OrbitControls(this.kamera, this.leinwand);
        this.steuerung.target.fromArray(kamera.ziel);
        this.steuerung.update();
        this.steuerung.addEventListener('change', () => this._geaendert());
        const himmel = new THREE.HemisphereLight(0xdfe8ff, 0x303642, 1.1);
        const licht = new THREE.DirectionalLight(0xffffff, 1.6);
        licht.position.set(2, 4, 3);
        // Die Lichter leuchten auch Ebene 1 (Genesis-Figur, `Mesh3daigenesisfigur`) — three.js prüft die Ebenen auch bei Lichtern.
        for (const l of [himmel, licht]) { l.layers.enableAll(); this.szene.add(l); }
        if (kamera.boden) this.szene.add(new THREE.GridHelper(3, 12, 0x4a5366, 0x2f3644));
        this.inhalt = new THREE.Group();
        this.szene.add(this.inhalt);
        this.hinweis = document.createElement('div');
        this.hinweis.className = 'mesh3dai-leer';
        this.hinweis.textContent = 'noch keine Probe';
        feld.appendChild(this.hinweis);
        // Nur zeichnen, was im Fenster steht (15.10.2026): damals hatte jedes Feld einen eigenen WebGL-Kontext, und „Textur“ lud die 10 Bilder (2048 px) in ALLE 15 Kontexte zugleich hoch —
        // gemessen 4,5 s Stillstand des Hauptfadens nach dem ersten Klick. Ein verdecktes Feld merkt sich den Auftrag und zeichnet, sobald es ins Bild kommt.
        // Seit 19.10.2026 wird auch der INHALT eines verdeckten Felds erst gebaut, wenn es ins Bild kommt (`_auftrag`): eine Genesis-Figur (`Mesh3daigenesisfigur`) baut sonst für alle 16 Felder zugleich.
        this._imBild = false;
        this._offen = false;
        this._auftrag = null;
        new IntersectionObserver(eintraege => {
            this._imBild = eintraege[eintraege.length - 1].isIntersecting;
            if (this._imBild && this._auftrag) this._fuellen();
            else if (this._imBild && this._offen) this.zeichnen();
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
        Mesh3daizeichenflaeche.zeichnen(this.leinwand, Math.max(this.feld.clientWidth, 2), Math.max(this.feld.clientHeight, 2), this.grund, r => this._malen(r));
    }

    /**
     * Genesis-Figur (Ebene 1, `Mesh3daigenesisfigur`): in „Textur“ mit ihren eigenen Materialien in einem Durchgang; in den einfarbigen Arten zuerst die Figur mit dem Ersatzmaterial
     * (`overrideMaterial`), dann alles andere ohne — die Materialien der Figur werden nie angefasst.
     */
    _malen(renderer) {
        const ersatz = this.inhalt.userData.genesisErsatz;
        if (!ersatz) {
            this.kamera.layers.enableAll();
            renderer.render(this.szene, this.kamera);
            return;
        }
        this.kamera.layers.set(1);
        this.szene.overrideMaterial = ersatz;
        renderer.render(this.szene, this.kamera);
        this.kamera.layers.set(0);
        this.szene.overrideMaterial = null;
        renderer.autoClear = false;
        renderer.render(this.szene, this.kamera);
        renderer.autoClear = true;
    }

    _leeren() {
        // Eine Genesis-Figur gehört nicht dem Feld (`mesh3daiFremd`): nur aushängen, nicht freigeben.
        this.inhalt.userData.genesisErsatz = undefined;
        this.inhalt.userData.hinweis = undefined;
        for (const kind of [...this.inhalt.children]) {
            this.inhalt.remove(kind);
            if (!kind.userData.mesh3daiFremd) Mesh3daigemeinsam.freigeben(kind);
        }
    }

    /**
     * @param {object|null} d `{beschreibung, teil, id, geist}` — Form siehe `Mesh3daibereiche`. `null` leert das Feld.
     * @param {string|null} leer der Text im leeren Feld (Vorgabe „noch keine Probe“)
     */
    zeigen(d, leer = null) {
        this._d = d;
        this._auftrag = { d, leer };
        if (this._imBild) this._fuellen();
    }

    /** Dasselbe noch einmal zeigen (eine Genesis-Figur ist fertig oder ihre feine Stufe ist da). Ein verdecktes Feld baut erst, wenn es ins Bild kommt. */
    neuZeigen() {
        if (this._d !== undefined) this.zeigen(this._d, this._auftrag?.leer ?? null);
    }

    _fuellen() {
        const { d, leer } = this._auftrag;
        this._auftrag = null;
        this._leeren();
        this.hinweis.hidden = !!d;
        this.hinweis.textContent = leer ?? 'noch keine Probe';
        // Echte Figur (Wolke und Fläche): Ursula1 trägt dunkelblaue Kleider und schwarzes Haar — auf dem dunklen Grund (1b1f27) kaum zu sehen (gesehen 15.10.2026). Darum ein hellerer Grund, und zwar in ALLEN
        // drei Feldern (Edgar, 15.10.2026: „das muss einheitlich sein in allen views“ — vorher war das Ergebnis dunkel).
        this.grund = d?.echt ? Mesh3daiansicht.GRUND_WOLKE : Mesh3daiansicht.GRUND;
        if (d) {
            this.zeichner.zeichnen(this.inhalt, this.art, d);
            Mesh3dairigzeichner.ueberlagern(this.inhalt, this.art, d);
            // Ein Zeichner kann einen Text ins Feld legen (Genesis-Figur wird gebaut, gescheitert).
            const text = this.inhalt.userData.hinweis;
            if (text) {
                this.hinweis.hidden = false;
                this.hinweis.textContent = text;
            }
        }
        this.zeichnen();
    }
}
