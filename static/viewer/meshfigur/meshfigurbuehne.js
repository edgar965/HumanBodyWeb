import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Meshfigurhaarwahl } from './meshfigurhaarwahl.js';
import { Meshfigurkleider } from './meshfigurkleider.js';
import { Meshfigurnetze } from './meshfigurnetze.js';
import { Meshfigurschalter } from './meshfigurschalter.js';

/**
 * Meshfigurbuehne — die angepasste Genesis-Figur und das Netz (bzw. Körper- und Kopfnetz) auf einer Bühne.
 *
 * Die Figur ist dieselbe Klasse wie in Szene und Studio (`Genesis9Modell`: Käfig sofort, feine
 * Stufe nach) mit den gestellten Reglern samt Eigenmorph und den gebackenen Kacheln als Albedo
 * (`fototextur`, derselbe Weg wie ein gespeichertes Modell in der Szene). Die Netze lädt
 * `Meshfigurnetze` in der Lage der Erkennung (Y oben, Blick +Z, Füße auf 0, ggf. auf die
 * Körpergröße gestreckt) — „Nebeneinander" rückt sie um `ABSTAND` nach rechts.
 *
 * Was davon zu sehen ist, schalten die Kästchen über der Ansicht einzeln (`Meshfigurschalter`):
 * Mesh · Haare · Kleider · Nebeneinander · 3DModell.
 */
export class Meshfigurbuehne {

    /** Seitlicher Versatz des Netzes bei „Nebeneinander" (Edgar: „um ca. 1,5 m verschoben"). */
    static ABSTAND = 1.5;

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('buehne');
        this.hinweis = document.getElementById('buehne-hinweis');
        this.modell = null;
        this._stand = null;
        this._baut = false;
        this._letzter = null;
        this._holt = false;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        this.netze = new Meshfigurnetze(seite, this.szene, text => this._melden(text));
        this.haar = new Meshfigurhaarwahl(seite, text => this._melden(text));
        this.kleider = new Meshfigurkleider(seite, text => this._melden(text));
        this.schalter = new Meshfigurschalter(() => this._sichtbarkeit());
    }

    _melden(text) { if (this.hinweis) { this.hinweis.textContent = text; this.hinweis.hidden = !text; } }

    _buehne() {
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'meshfigur-leinwand';
        this.feld.appendChild(this.canvas);
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        // Körper- und Kopfnetz werden am Hals geschnitten (`Meshfigurnetze`, Ebenen je Werkstoff).
        this.renderer.localClippingEnabled = true;
        this.szene = new THREE.Scene();
        this.kamera = new THREE.PerspectiveCamera(30, 1, 0.05, 50);
        this.kamera.position.set(0, 1.0, 4.4);
        this.steuerung = new OrbitControls(this.kamera, this.canvas);
        this.steuerung.target.set(0, 0.9, 0);
        this.steuerung.enableDamping = true;
        this.szene.add(new THREE.HemisphereLight(0xffffff, 0xc8c2ba, 1.3));
        const haupt = new THREE.DirectionalLight(0xffffff, 1.0);
        haupt.position.set(1, 1.5, 2);
        this.kamera.add(haupt);
        this.szene.add(this.kamera, new THREE.GridHelper(3, 12, 0x445566, 0x2a3340));
        // Der Behälter, nicht das Fenster: Er schrumpft, sobald die rechte Spalte gefüllt ist, ohne dass
        // ein `resize` kommt — gemessen stand die Leinwand dann 1045 × 866 px in 760 × 794 px und zog das
        // Bodengitter über das Formular (27.09.2026).
        new ResizeObserver(() => this._groesse()).observe(this.feld);
        const lauf = () => { this.steuerung.update(); this.renderer.render(this.szene, this.kamera); requestAnimationFrame(lauf); };
        requestAnimationFrame(lauf);
    }

    _groesse() {
        const b = this.feld.clientWidth || 640, h = this.feld.clientHeight || 640;
        this.renderer.setSize(b, h);
        this.kamera.aspect = b / h;
        this.kamera.updateProjectionMatrix();
    }

    /**
     * Die Knöpfe auf die Bühne übertragen. „Nebeneinander" ZEIGT das Netz (Edgar, 29.09.2026:
     * „nebeneinander soll das Mesh zeigen um ca. 1,5 m verschoben") — es schaltet „Mesh" also mit an,
     * statt gesperrt zu sein, solange man es nicht selbst eingeschaltet hat. Sichtbar am Knopf, nicht
     * heimlich: `setzen` lässt „Mesh" dabei aufleuchten.
     */
    _sichtbarkeit() {
        if (this.schalter.stand.nebeneinander) this.schalter.setzen('mesh', true);
        const an = this.schalter.stand;
        if (this.modell) this.modell.group.visible = an.modell;
        else if (an.modell && this._letzter && !this._baut && !this._holt) {
            // Nachgeholt, nicht verschachtelt: `zeigen` ruft selbst `_sichtbarkeit`, wenn es die Netze neu lädt.
            this._holt = true;
            queueMicrotask(() => { this._holt = false; this.zeigen(this._letzter); });
        }
        this.netze.sichtbar(an.mesh);
        this.netze.verschieben(an.nebeneinander ? Meshfigurbuehne.ABSTAND : 0);
        this.steuerung.target.x = an.nebeneinander ? Meshfigurbuehne.ABSTAND / 2 : 0;
        this._haarUndKleider();
    }

    /**
     * Haar und Kleider nachziehen — ihre Netze kommen nach dem Bau der Figur nach, also läuft das bei
     * JEDEM Stand der Seite mit. Fasst das Drehziel nicht an (`_sichtbarkeit` täte das, und alle 2 s
     * gerufen nähme es dem Nutzer jedes Verschieben der Ansicht wieder weg).
     */
    _haarUndKleider() {
        this.kleider.setzen(this.modell, this.haar.frisur?.kennung);
        const an = this.schalter.stand;
        this.haar.sichtbarkeit(an.haare);
        this.kleider.sichtbar(an.kleider);
    }

    // --------------------------------------------------------------- Stand

    async zeigen(z) {
        if (!this.renderer) return;
        const e = z.ergebnis || {};
        // Nur nach einem Neuladen: `_sichtbarkeit` setzt das Drehziel — alle 2 s gerufen, nähme es
        // dem Nutzer jedes Verschieben der Ansicht wieder weg.
        if (this.netze.zeigen(z)) this._sichtbarkeit();
        this.haar.zeigen(z, this.modell?.group || null);
        this.kleider.zeigen(z, this.modell?.group || null);
        this._haarUndKleider();
        const stellung = z.stellung || {};
        if (!Object.keys(stellung).length) { this._melden('Noch keine Figur — erst nach der Körperkette.'); return; }
        const kacheln = this.kacheln(e.fototextur);
        // Neue Textur („Textur" neu gebacken) oder eine neue Frisur (Schritt „frisur") baut die Figur
        // ebenso neu wie neue Regler.
        const kleidung = Meshfigurhaarwahl.kleidung(z);
        // Ist „3DModell" aus, wird die Figur gar nicht gebaut (01.10.2026): „2D3D Kleider" zeigt dann die fertige GLB des
        // letzten Stands, und der Bau im Browser hielt den Tab gemessen über 45 s fest. Schaltet man sie ein, holt
        // `_sichtbarkeit` den Bau nach.
        this._letzter = z;
        if (!this.schalter.stand.modell && !this.modell) return;
        const stand = JSON.stringify([stellung, kacheln, kleidung]);
        if (stand === this._stand || this._baut) return;
        this._stand = stand;
        await this._bauen(stellung, z, kacheln, kleidung);
    }

    /**
     * Die Kacheln als Adressen (`{1001: …}`), mit dem Stand des Backens — sie gehen VOR dem Bau als
     * Albedo in die Figur (`Genesis9fototextur`), in JEDE Stufe. Bis 27.09.2026 legte `Texturauflage`
     * sie nachträglich auf und fasste nur 30 s nach; kam die feine Stufe später (kalter Server), ersetzte
     * sie die Materialien, und die Figur stand mit Daz-Haut da (Befund Edgar, Bildschirmfoto).
     */
    kacheln(fototextur) {
        const f = fototextur || {}, marke = encodeURIComponent(f.stand || '');
        // Dazu das Augenbild (Daz-Iris in der Farbe des Netzes) — `Genesis9fototextur.anhang`.
        const bilder = { ...(f.kacheln || {}), ...(f.augen ? { augen: f.augen } : {}) };
        return Object.fromEntries(Object.entries(bilder)
            .map(([k, name]) => [k, `${this.seite.dateiAdresse('ergebnis', name)}?t=${marke}`]));
    }

    async _bauen(stellung, z, kacheln, kleidung) {
        this._baut = true;
        this._melden('Figur wird gebaut …');
        try {
            const neu = new Genesis9Modell('meshfigur', {
                figur: 'basis', regler: stellung, presetName: z.name, fototextur: kacheln, kleidung,
            });
            await neu.bauen();
            if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
            this.modell = neu;
            this.szene.add(neu.group);
            this.haar.anhaengen(neu);
            this.kleider.anhaengen(neu);
            const h = neu.hoehe || 1.7;
            this.steuerung.target.set(0, h * 0.52, 0);
            this.kamera.position.set(0, h * 0.55, h * 2.6);
            this._sichtbarkeit();
            this._melden('');
        } catch (fehler) {
            this._stand = null;
            this._melden(`Figur nicht gebaut: ${fehler.message}`);
        } finally {
            this._baut = false;
        }
    }
}
