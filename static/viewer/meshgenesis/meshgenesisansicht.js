/**
 * Meshgenesisansicht — EIN 3D-Feld der Seite „Mesh-Genesis“ (14.10.2026): zeigt je nach Art die Eingabe (Punktwolke der Außenfläche), die gewünschte Ausgabe (Genesis-Modell in der Pose) oder die Ausgabe des Netzes
 * (mit Fehlerpunkten und dem Soll als Geist). Was gezeichnet wird, bestimmt der Zeichner der Zeile (`Meshgenesisbereiche`: ganzer Körper, Gesicht, Hände/Füße, Kleider); die Ansicht hält nur Leinwand, Licht und Kamera.
 * Seit 19.10.2026 ist die Leinwand eine 2D-Leinwand: gezeichnet wird mit EINEM Renderer für alle Felder (`Meshgenesiszeichenflaeche` — jedes Bild nur einmal auf der Grafikkarte).
 *
 * Gezeichnet wird nur auf Anforderung (`zeigen`, Ziehen mit der Maus, Größenänderung), nie in einer Dauerschleife — zwölf Felder belasten die Grafikkarte sonst ohne Grund, und in einem verdeckten Tab
 * liefe `requestAnimationFrame` ohnehin nicht. Die drei Felder einer Zeile sind gekoppelt (`koppeln`): wer eines dreht, dreht alle, damit Eingabe, Soll und Ausgabe aus demselben Winkel zu vergleichen sind.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Meshgenesisgemeinsam } from './meshgenesisgemeinsam.js';
import { Meshgenesisrigzeichner } from './meshgenesisrigzeichner.js';
import { Meshgenesiszeichenflaeche } from './meshgenesiszeichenflaeche.js';
import { Studiolicht } from '../gemeinsam/studiolicht.js';

export class Meshgenesisansicht {
    static GRUND = 0x1b1f27;
    static GRUND_WOLKE = 0x5a6170;
    /**
     * Genesis-Figuren im Licht der Charakterseite (09.11.2026, Edgar zu damiraalt: „nimm die Pipeline der Scham wie bei Damira Model im Charakter Ansicht“ — das Stück war bitgleich,
     * Unterschied nur das Licht, `Studiolicht`). `Fotogenesisansicht` schaltet es aus: Dort gilt das an den Fotos gemessene Fotolicht (`FOTOLICHT`), die Abnahme misst das Rendering.
     */
    static STUDIO = true;

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
        this.grund = Meshgenesisansicht.GRUND;
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
        // three.js prüft die Ebenen auch bei Lichtern. Mit `STUDIO` leuchtet dieses Licht nur Ebene 0 (Netze, Wolken, Geist), die Genesis-Figur auf Ebene 1 (`Meshgenesisgenesisfigur`)
        // bekommt das Licht der Charakterseite (`Studiolicht`); ohne leuchtet es beide Ebenen wie bis 09.11.2026.
        const studio = this.constructor.STUDIO;
        for (const l of [himmel, licht]) { if (studio) l.layers.set(0); else l.layers.enableAll(); this.szene.add(l); }
        if (studio) for (const l of Studiolicht.lichter()) { l.layers.set(1); this.szene.add(l); }
        if (kamera.boden) this.szene.add(new THREE.GridHelper(3, 12, 0x4a5366, 0x2f3644));
        this.inhalt = new THREE.Group();
        this.szene.add(this.inhalt);
        this.hinweis = document.createElement('div');
        this.hinweis.className = 'meshgenesis-leer';
        this.hinweis.textContent = 'noch keine Probe';
        feld.appendChild(this.hinweis);
        // Nur zeichnen, was im Fenster steht (15.10.2026): damals hatte jedes Feld einen eigenen WebGL-Kontext, und „Textur“ lud die 10 Bilder (2048 px) in ALLE 15 Kontexte zugleich hoch —
        // gemessen 4,5 s Stillstand des Hauptfadens nach dem ersten Klick. Ein verdecktes Feld merkt sich den Auftrag und zeichnet, sobald es ins Bild kommt.
        // Seit 19.10.2026 wird auch der INHALT eines verdeckten Felds erst gebaut, wenn es ins Bild kommt (`_auftrag`): eine Genesis-Figur (`Meshgenesisgenesisfigur`) baut sonst für alle 16 Felder zugleich.
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

    /**
     * Neu zeichnen — gebündelt auf EIN Bild je Frame (08.11.2026, Edgar: „alle modelle sollen innerhalb von max. 5 s angezeigt werden“): Jedes Kamerastellen (`Fotogenesiskamera.feldStellen` →
     * `steuerung.update()` → `change`) zeichnete sofort und ließ alle gekoppelten Felder mitzeichnen (`_uebernehmen`); ein Durchgang über alle Felder kostete so rund N² volle Renderings,
     * und `kameras()` wiederholt sich bis zu 40-mal. Gemessen im Chrome (Zauberer Alle Textur): ein `setTimeout` von `Fotogenesissmplx.kameras` 7,5 s, ein `IntersectionObserver`-Ruf 10,8 s.
     * Im verdeckten Tab (kein `requestAnimationFrame`) sofort wie bisher; wer das Bild sofort braucht, ruft `zeichnenJetzt()`.
     */
    zeichnen() {
        if (!this._imBild) {
            this._offen = true;
            return;
        }
        this._offen = false;
        if (document.hidden) {
            this.zeichnenJetzt();
            return;
        }
        this._geplant ||= requestAnimationFrame(() => {
            this._geplant = 0;
            this.zeichnenJetzt();
        });
    }

    zeichnenJetzt() {
        if (this._geplant) {
            cancelAnimationFrame(this._geplant);
            this._geplant = 0;
        }
        Meshgenesiszeichenflaeche.zeichnen(this.leinwand, Math.max(this.feld.clientWidth, 2), Math.max(this.feld.clientHeight, 2), this.grund, r => {
            const zurueck = this.hauttausch?.();          // „Haut angleichen“: die Hautbilder nur für diesen Durchgang getauscht (`Fotogenesishautangleich._tauschen`)
            try {
                this._malen(r);
            } finally {
                zurueck?.();
            }
        });
    }

    /**
     * Genesis-Figur (Ebene 1, `Meshgenesisgenesisfigur`): in „Textur“ mit ihren eigenen Materialien in einem Durchgang; in den einfarbigen Arten zuerst die Figur mit dem Ersatzmaterial
     * (`overrideMaterial`), dann alles andere ohne — die Materialien der Figur werden nie angefasst.
     * Mit `STUDIO` immer zwei Durchgänge: die Figur mit Licht, Tone-Mapping und Belichtung der Charakterseite, danach Ebene 0 wie bisher (Fehlerfarben und Wolken ohne Tone-Mapping).
     */
    _malen(renderer) {
        const ersatz = this.inhalt.userData.genesisErsatz;
        if (this.constructor.STUDIO) {
            this.kamera.layers.set(1);
            this.szene.overrideMaterial = ersatz ?? null;
            Studiolicht.mitTonwerten(renderer, () => renderer.render(this.szene, this.kamera));
            this.kamera.layers.set(0);
            this.szene.overrideMaterial = null;
            renderer.autoClear = false;
            renderer.render(this.szene, this.kamera);
            renderer.autoClear = true;
            return;
        }
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
        // Eine Genesis-Figur gehört nicht dem Feld (`meshgenesisFremd`): nur aushängen, nicht freigeben.
        this.inhalt.userData.genesisErsatz = undefined;
        this.inhalt.userData.hinweis = undefined;
        for (const kind of [...this.inhalt.children]) {
            this.inhalt.remove(kind);
            if (!kind.userData.meshgenesisFremd) Meshgenesisgemeinsam.freigeben(kind);
        }
    }

    /**
     * @param {object|null} d `{beschreibung, teil, id, geist}` — Form siehe `Meshgenesisbereiche`. `null` leert das Feld.
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

    /** Einen aufgeschobenen Inhalt sofort bauen, auch im verdeckten Feld — für Aufnahmen aus der Figur (`Fotogenesisseite.seitenbilder`), die nicht aufs Scrollen warten können. */
    jetztFuellen() {
        if (this._auftrag) this._fuellen();
    }

    _fuellen() {
        const { d, leer } = this._auftrag;
        this._auftrag = null;
        this._leeren();
        this.hinweis.hidden = !!d;
        this.hinweis.textContent = leer ?? 'noch keine Probe';
        // Echte Figur (Wolke und Fläche): Ursula1 trägt dunkelblaue Kleider und schwarzes Haar — auf dem dunklen Grund (1b1f27) kaum zu sehen (gesehen 15.10.2026). Darum ein hellerer Grund, und zwar in ALLEN
        // drei Feldern (Edgar, 15.10.2026: „das muss einheitlich sein in allen views“ — vorher war das Ergebnis dunkel).
        this.grund = d?.echt ? Meshgenesisansicht.GRUND_WOLKE : Meshgenesisansicht.GRUND;
        if (d) {
            // Standardanimation (22.10.2026, `Meshgenesisfigurbewegung`): solange sie läuft oder steht, die bewegte Figur statt der stillen — ohne Rig (es zeigt die Haltung der KI, nicht die Bewegung).
            if (this.bewegung?.aktiv) {
                this.bewegung.einhaengen(this.inhalt, d);
            } else {
                this.zeichner.zeichnen(this.inhalt, this.art, d);
                Meshgenesisrigzeichner.ueberlagern(this.inhalt, this.art, d);
            }
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
