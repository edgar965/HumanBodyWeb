import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Meshfigurhaarobjekt } from './meshfigurhaarobjekt.js';
import { Meshfigurnetze } from './meshfigurnetze.js';

/**
 * Meshfigurbuehne — die angepasste Genesis-Figur und das Netz (bzw. Körper- und Kopfnetz) auf einer Bühne.
 *
 * Die Figur ist dieselbe Klasse wie in Szene und Studio (`Genesis9Modell`: Käfig sofort, feine
 * Stufe nach) mit den gestellten Reglern samt Eigenmorph und den gebackenen Kacheln als Albedo
 * (`fototextur`, derselbe Weg wie ein gespeichertes Modell in der Szene). Die Netze lädt
 * `Meshfigurnetze` in der Lage der Erkennung (Y oben, Blick +Z, Füße auf 0, ggf. auf die
 * Körpergröße gestreckt) — „Nebeneinander" rückt sie um `ABSTAND` nach rechts.
 */
export class Meshfigurbuehne {

    static ABSTAND = 0.75;

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('buehne');
        this.hinweis = document.getElementById('buehne-hinweis');
        this.was = 'figur';
        this.modell = null;
        this._stand = null;
        this._baut = false;
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        this.netze = new Meshfigurnetze(seite, this.szene, text => this._melden(text));
        this.haar = new Meshfigurhaarobjekt(seite, text => this._melden(text));
        for (const r of document.querySelectorAll('input[name="meshfigur-was"]')) {
            r.addEventListener('change', () => { if (r.checked) { this.was = r.value; this._sichtbarkeit(); } });
        }
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

    _sichtbarkeit() {
        if (this.modell) this.modell.group.visible = this.was !== 'netz';
        this.netze.sichtbar(this.was !== 'figur');
        this.netze.verschieben(this.was === 'beide' ? Meshfigurbuehne.ABSTAND : 0);
        const mitte = this.was === 'beide' ? Meshfigurbuehne.ABSTAND / 2 : 0;
        this.steuerung.target.x = mitte;
    }

    // --------------------------------------------------------------- Stand

    async zeigen(z) {
        if (!this.renderer) return;
        const e = z.ergebnis || {};
        // Nur nach einem Neuladen: `_sichtbarkeit` setzt das Drehziel — alle 2 s gerufen, nähme es
        // dem Nutzer jedes Verschieben der Ansicht wieder weg.
        if (this.netze.zeigen(z)) this._sichtbarkeit();
        this.haar.zeigen(z, this.modell?.group || null);
        const stellung = z.stellung || {};
        if (!Object.keys(stellung).length) { this._melden('Noch keine Figur — erst nach der Körperkette.'); return; }
        const kacheln = this.kacheln(e.fototextur);
        // Neue Textur („Textur" neu gebacken) baut die Figur ebenso neu wie neue Regler.
        const stand = JSON.stringify([stellung, kacheln]);
        if (stand === this._stand || this._baut) return;
        this._stand = stand;
        await this._bauen(stellung, z, kacheln);
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

    async _bauen(stellung, z, kacheln) {
        this._baut = true;
        this._melden('Figur wird gebaut …');
        try {
            const neu = new Genesis9Modell('meshfigur', {
                figur: 'basis', regler: stellung, presetName: z.name, fototextur: kacheln,
            });
            await neu.bauen();
            if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
            this.modell = neu;
            this.szene.add(neu.group);
            this.haar.anhaengen(neu.group);
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
