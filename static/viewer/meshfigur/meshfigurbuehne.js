import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Skelettereignis } from '../gemeinsam/skelettereignis.js';
import { Meshfigurhaarwahl } from './meshfigurhaarwahl.js';
import { Meshfigurkleider } from './meshfigurkleider.js';
import { Meshfigurladezeit } from './meshfigurladezeit.js';
import { Meshfigurlicht } from './meshfigurlicht.js';
import { Meshfigurnetze } from './meshfigurnetze.js';
import { Meshfigurschalter } from './meshfigurschalter.js';
import { Meshfigurtakt } from './meshfigurtakt.js';
import { Meshfigurteile } from './meshfigurteile.js';
import { Meshfigurteileleiste } from './meshfigurteileleiste.js';

/**
 * Meshfigurbuehne — die angepasste Genesis-Figur und das Netz (bzw. Körper- und Kopfnetz) auf einer Bühne.
 *
 * Die Figur ist dieselbe Klasse wie in Szene und Studio (`Genesis9Modell`: Käfig sofort, feine
 * Stufe nach) mit den gestellten Reglern samt Eigenmorph und den gebackenen Kacheln als Albedo
 * (`fototextur`, derselbe Weg wie ein gespeichertes Modell in der Szene). Die Netze lädt
 * `Meshfigurnetze` in der Lage der Erkennung (Y oben, Blick +Z, Füße auf 0, ggf. auf die
 * Körpergröße gestreckt) und IMMER um `ABSTAND` nach links gerückt (die Grundfigur von „2D3D Kleider" steht rechts).
 *
 * Was davon zu sehen ist, schalten die Kästchen über der Ansicht einzeln (`Meshfigurschalter`):
 * Mesh · Haare · Kleider · Nebeneinander · 3DModell.
 */
export class Meshfigurbuehne {

    /** Seitlicher Versatz des Netzes, immer nach links (Edgar: „um ca. 1,5 m verschoben"). */
    static ABSTAND = 1.5;

    /** Obergrenze für die Pixel der Leinwand (Geräte-Pixel, nach Geräteverhältnis) — siehe `_groesse`. */
    static MAX_PIXEL = 3.0e6;

    constructor(seite) {
        this.seite = seite;
        this.feld = document.getElementById('buehne');
        this.hinweis = document.getElementById('buehne-hinweis');
        this.modell = null;
        this._stand = null;
        this._baut = false;
        this._letzter = null;
        this._holt = false;
        this._haltungGebaut = 'null';       // die Haltung der gebauten Figur (JSON), 'null' = Ruhe
        // Zeiten bis zum ersten gezeichneten Bild mit Figur → logs/client.log (Aktion `ladezeit`), siehe `Meshfigurladezeit`.
        this.zeit = new Meshfigurladezeit(() => seite.jobId);
        try { this._buehne(); } catch (fehler) { this._melden(`Keine 3D-Ansicht: ${fehler.message}`); return; }
        this.zeit.marke('buehne');
        this.netze = new Meshfigurnetze(seite, this.szene, text => this._melden(text));
        this.haar = new Meshfigurhaarwahl(seite, text => this._melden(text));
        this.kleider = new Meshfigurkleider(seite, text => this._melden(text));
        // Bestandteile des Netzes (Stab, Bart, Tasche …), von SAM 3 gefunden: eigene Objekte, geschaltet mit „Haare" bzw. „Kleider".
        this.teile = new Meshfigurteile(seite, text => this._melden(text));
        this.teileleiste = new Meshfigurteileleiste(document.getElementById('bestandteile-leiste'), this.teile);       // je Bestandteil ein Knopf (nur Mesh-3D)
        this.schalter = new Meshfigurschalter(() => this._sichtbarkeit());
        // Die Figur baut ihr Skelett bei jedem Umbau neu (Käfig, dann feine Stufe, jeder Reglerzug): die Objekte aus dem Netz (`Meshfighaut`) binden sich an das frische (13.10.2026).
        Skelettereignis.hoeren(({ inst }) => { if (inst && inst === this.modell) this._objekteBinden(inst); });
    }

    /** Haar, Kleidung und Bestandteile an Gruppe und Skelett der gezeigten Figur hängen. */
    _objekteBinden(modell) {
        this.haar.anhaengen(modell);
        this.kleider.anhaengen(modell);
        this.teile.anhaengen(modell);
    }

    /** Die an die Knochen gebundenen Netz-Objekte samt Adresse ihrer Gelenkfelder (JCM) — `[{netz, adresse}]`, siehe `Meshfigurgelenke`. */
    gelenkziele() {
        const objekte = [this.haar.netz, this.haar.karten, this.kleider.netz, ...[...this.teile.eintraege.values()].map(e => e.objekt)];
        return objekte.map(o => o.gelenkziel()).filter(Boolean);
    }

    _melden(text) { if (this.hinweis) { this.hinweis.textContent = text; this.hinweis.hidden = !text; } }

    /** Die volle Bildrate anfordern (Animationsklassen rufen es mit jedem Schritt der Bewegung) — siehe `Meshfigurtakt`. */
    wach(ms) { this.takt?.wach(ms); }

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
        // Wann gezeichnet wird (volle Rate nur bei Eingabe, Animation, Größenänderung; sonst 5 Bilder/s): `Meshfigurtakt`.
        this.takt = new Meshfigurtakt();
        this.steuerung.addEventListener('change', () => this.takt.wach());
        // Dasselbe Licht hat die Mesh-Ansicht von „Mesh-3D“ (`Mesh3dnetzbuehne`) — es steht in EINER Klasse.
        Meshfigurlicht.einrichten(this.szene, this.kamera);
        this.szene.add(new THREE.GridHelper(3, 12, 0x445566, 0x2a3340));
        // Der Behälter, nicht das Fenster: Er schrumpft, sobald die rechte Spalte gefüllt ist, ohne dass
        // ein `resize` kommt — gemessen stand die Leinwand dann 1045 × 866 px in 760 × 794 px und zog das
        // Bodengitter über das Formular (27.09.2026).
        new ResizeObserver(() => this._groesse()).observe(this.feld);
        // Gezeichnet wird nur, was jemand sieht (04.10.2026, Edgar: „Seite hängt — kann nicht Tab wechseln"): Die Schleife zeichnete vorher jedes
        // Bild weiter, auch wenn der Reiter mit der Bühne ausgeblendet war (`display: none`, keine Fläche) oder der Browser-Tab verdeckt — bei einem
        // Modell mit 57 Netzen und rund 600 000 Dreiecken in einer großen Leinwand die Hauptlast der Seite. Ob DAS den Hänger verursacht hat, ist
        // nicht belegt (im verdeckten Messtab nicht nachzustellen); die Last ist aber unnötig.
        const lauf = () => {
            if (!document.hidden && this.canvas.getClientRects().length && this.takt.faellig()) {
                this.steuerung.update();
                this.zeit.zeichnen(() => this.renderer.render(this.szene, this.kamera), this.renderer, !!this.modell);
            }
            requestAnimationFrame(lauf);
        };
        requestAnimationFrame(lauf);
    }

    /**
     * Leinwand an den Behälter anpassen — mit Grenzen für den Grafikspeicher (04.10.2026, Edgar: „Seite hängt, Tab Auftrag nicht anklickbar", offen ist nur
     * der Wechsel von „Iterationen" zurück auf „Auftrag", direkt aus dem Dashboard geöffnet geht es). Ursache nicht belegt; belegt ist, was die Bühne vorhielt: Die
     * Spalte der Bühne ist so hoch wie das Formular daneben (gemessen 1382 × 2142 px), mit Geräteverhältnis 1,575 und vierfacher Glättung waren das 7,3 Mio. Pixel
     * im Zeichenpuffer — auch bei ausgeblendetem Reiter —, und andere Aufträge (Pixal) füllen dieselbe Karte bis auf wenige MB (`engine2d3dkleider_render.GPU_FREI_MB`).
     * Deshalb: ausgeblendet (Behälter ohne Fläche) schrumpft der Puffer auf 1 × 1 und gibt den Speicher frei; sichtbar ist die Pixelzahl auf `MAX_PIXEL` begrenzt
     * (das Geräteverhältnis sinkt entsprechend, die Leinwand bleibt so groß wie der Behälter).
     */
    _groesse() {
        const b = this.feld.clientWidth, h = this.feld.clientHeight;
        this.takt.wach();
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
    }

    /**
     * Die Knöpfe auf die Bühne übertragen. „Nebeneinander" ZEIGT das Netz (Edgar, 29.09.2026:
     * „nebeneinander soll das Mesh zeigen um ca. 1,5 m verschoben") — es schaltet „Mesh" also mit an,
     * statt gesperrt zu sein, solange man es nicht selbst eingeschaltet hat. Sichtbar am Knopf, nicht
     * heimlich: `setzen` lässt „Mesh" dabei aufleuchten.
     */
    _sichtbarkeit() {
        this.wach();
        if (this.schalter.stand.nebeneinander) this.schalter.setzen('mesh', true);
        const an = this.schalter.stand;
        if (this.modell) this.modell.group.visible = an.modell;
        else if (an.modell && this._letzter && !this._baut && !this._holt) {
            // Nachgeholt, nicht verschachtelt: `zeigen` ruft selbst `_sichtbarkeit`, wenn es die Netze neu lädt.
            this._holt = true;
            queueMicrotask(() => { this._holt = false; this.zeigen(this._letzter); });
        }
        this.netze.sichtbar(an.mesh);
        // Das Netz steht IMMER `ABSTAND` links neben der Figur, nie in ihr (Edgar, 01.10.2026: „das hatten wir schon 10 Mal").
        this.netze.verschieben(-Meshfigurbuehne.ABSTAND);
        // „Haltung" umgeschaltet: die Figur wird in der anderen Haltung neu gebaut (der Server backt sie), die Objekte wechseln ihre Fassung.
        if (this.modell && this._letzter && !this._baut && !this._holt && JSON.stringify(this._haltungVon(this._letzter)) !== this._haltungGebaut) {
            this._holt = true;
            queueMicrotask(() => { this._holt = false; this.zeigen(this._letzter); });
        }
        this._haarUndKleider();
    }

    /**
     * „Haltung" ausschalten (von der Animationsleiste gerufen): eine Bewegung gehört auf die Figur in Ruhe (A-Pose) — in der gebackenen Haltung wäre ihre Bindung die falsche
     * (`mesh-3d-bestandteile.md`: ein Standbild, vor einer BVH-Bewegung die Pose auf „—"). Die Figur wird in Ruhe neu gebaut; erst danach lässt sich die Bewegung starten.
     */
    haltungAus() {
        if (!this.schalter.stand.haltung) return false;
        this.schalter.setzen('haltung', false);
        this._melden('Haltung aus — die Figur wird in Ruhe gebaut, danach läuft der Befehl der Animationsleiste.');
        this._sichtbarkeit();
        return true;
    }

    /** Haar, Kleidung und Bestandteile des Netzes laden und in die Gruppe der Figur hängen — `posiert`: die Figur steht in der Haltung des Netzes, die Objekte in ihrer Fassung dafür. */
    _objekteZeigen(z, gruppe, posiert) {
        this.haar.zeigen(z, gruppe, posiert);
        this.kleider.zeigen(z, gruppe, posiert);
        this.teile.zeigen(z, gruppe, posiert);
        this.teileleiste.zeigen();
    }

    /**
     * Die Haltung des Netzes (`ergebnis.haltung`, `Meshfighaltung`), in der die Figur gebaut wird — `{knochen: {'rotation/x': Grad}}` oder null (Ruhe).
     * Der Schalter „Haltung" wird nur angeboten, wenn der Lauf eine gültige hat; sonst bleibt alles wie vorher. Dann steht der Stoff unverändert am Körper, statt in die Ruhelage zurückgerechnet zu werden.
     */
    _haltungVon(z) {
        const h = (z.ergebnis || {}).haltung || {};
        const da = Boolean(h.gueltig && h.drehung && Object.keys(h.drehung).length);
        this.schalter.anbieten('haltung', da);
        return da && this.schalter.stand.haltung ? h.drehung : null;
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
        this.teile.sichtbar(an.haare, an.kleider);
    }

    // --------------------------------------------------------------- Stand

    async zeigen(z) {
        if (!this.renderer) return;
        const e = z.ergebnis || {};
        // Nur nach einem Neuladen: `_sichtbarkeit` setzt das Drehziel — alle 2 s gerufen, nähme es
        // dem Nutzer jedes Verschieben der Ansicht wieder weg.
        if (this.netze.zeigen(z)) this._sichtbarkeit();
        const haltung = this._haltungVon(z);
        // Die Objekte folgen der Figur, die GEZEIGT wird (nicht der gewünschten): bis die neue Haltung gebaut ist, stünde der Stoff sonst neben der alten.
        const posiert = this.modell ? this._haltungGebaut !== 'null' : Boolean(haltung);
        this._objekteZeigen(z, this.modell?.group || null, posiert);
        this._haarUndKleider();
        const stellung = z.stellung || {};
        if (!Object.keys(stellung).length) { this._melden('Noch keine Figur — erst nach der Körperkette.'); return; }
        this.zeit.marke('zustand');
        const kacheln = this.kacheln(e.fototextur);
        // Neue Textur („Textur" neu gebacken) oder eine neue Frisur (Schritt „frisur") baut die Figur
        // ebenso neu wie neue Regler.
        const kleidung = Meshfigurhaarwahl.kleidung(z);
        // Ist „3DModell" aus, wird die Figur gar nicht gebaut (01.10.2026): „2D3D Kleider" zeigt dann die fertige GLB des
        // letzten Stands, und der Bau im Browser hielt den Tab gemessen über 45 s fest. Schaltet man sie ein, holt
        // `_sichtbarkeit` den Bau nach.
        this._letzter = z;
        if (!this.schalter.stand.modell && !this.modell) return;
        const stand = JSON.stringify([stellung, kacheln, kleidung, haltung]);
        if (stand === this._stand || this._baut) return;
        this._stand = stand;
        await this._bauen(stellung, z, kacheln, kleidung, haltung);
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

    async _bauen(stellung, z, kacheln, kleidung, haltung) {
        this._baut = true;
        this._melden(haltung ? 'Figur wird in der Haltung des Netzes gebaut …' : 'Figur wird gebaut …');
        try {
            this.zeit.marke('bau');
            const neu = new Genesis9Modell('meshfigur', {
                figur: 'basis', regler: stellung, presetName: z.name, fototextur: kacheln, kleidung, drehung: haltung,
            });
            await neu.bauen();
            this.zeit.marke('figur');
            if (this.modell) { this.szene.remove(this.modell.group); this.modell.dispose?.(); }
            this.modell = neu;
            this._haltungGebaut = JSON.stringify(haltung);
            this.szene.add(neu.group);
            this._objekteZeigen(z, neu.group, Boolean(haltung));
            this._objekteBinden(neu);
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
