import * as THREE from 'three';
import { EigenkleidGLSL } from './eigenkleidglsl.js';
import { EigenkleidschnittGLSL } from './eigenkleidschnitt.js';
import { Eigenkleidgeometrie } from './eigenkleidgeometrie.js';
import { Eigenkleidwerte } from './eigenkleidwerte.js';
import { Eigenkragen } from './eigenkragen.js';
import { Eigenrock } from './eigenrock.js';
import { Eigenkleidtreffer } from './eigenkleidtreffer.js';
import { Sanduhr } from './sanduhr.js';
import { Stoffshader } from './stoffshader.js';
import { Koerperkoordinatenpunkte } from './koerperkoordinatenpunkte.js';
import { Protokoll } from './protokoll.js';

/**
 * Eigenkleid — EIN eigenes Stück (Oberteil oder Hose) auf EINER Genesis-9-Figur (Stufe K2a, 25.10.2026).
 *
 * Ein zweites `SkinnedMesh` auf der Geometrie des Körpers (`Eigenkleidgeometrie`: dieselben Attributobjekte, voller Index, dazu Körperkoordinaten und Brücke je
 * Punkt — keine Kopie der Punkte) und an DEMSELBEN Skelett (`bind` mit dessen `bindMatrix`), mit eigenem Material (`EigenkleidGLSL`, `EigenkleidschnittGLSL`):
 * die Hautgruppen (`HAUT`), deren Kachel die Körperkoordinaten-Karte führt, bekommen das Stoffmaterial; alle anderen (Nägel, Mund …) ein unsichtbares — Three
 * zeichnet diese Gruppen gar nicht.
 *
 * NEU ANBINDEN: Jeder Bau des Körpers (Reglerzug, Stufenwechsel, Materialwechsel, Figurwechsel) ersetzt `inst.bodyMesh` und gibt die alte Geometrie frei
 * (`Genesis9Modell._altesWeg` → `Netzentsorgung.entfernen`). Das Stück hört auf das Ereignis `removed` des Körpers, versteckt sich sofort (sonst lüde Three die
 * freigegebene Geometrie beim nächsten Bild neu hoch) und bindet im nächsten Mikrotakt an den neuen Körper — der steht dann schon, `koerperAufbauen` baut ihn
 * synchron. Das `Skelettereignis` ruft zusätzlich `Eigenkleider.anwenden` (`eigenkleider.js`). Im Chrome belegt: Stufenwechsel, Materialwechsel, Reglerzug.
 *
 * Anklickbar seit 26.10.2026 (`Eigenkleidtreffer.schale`: Treffer auf der Haut, wo das Stück sie deckt; vorher `raycast` leer). Keine Schattenwürfe (der Schattendurchgang kennt den Sitz nicht und wäre der Körper).
 *
 * STOFF (25.10.2026 nachts): Bindung, Glanz, Glanzsaum wie am Daz-Stück — `Stoffshader.patchen` im SELBEN `onBeforeCompile` hinter dem eigenen Eingriff
 * (`Stoffshader.setzen` hinge einen zweiten an und überschriebe diesen), Werte über `Stoffshader.werte(stoffU, …)` mit dem Stoffmaß der Körper-UV (`uvMeter`).
 * KRAGEN (Oberteil): `Eigenkragen`, eigene Fläche am Ausschnitt, mit diesem Stück gebunden und nachgeführt.
 */
export class Eigenkleid {

    static HAUT = /^(Head|Body|Arms|Legs)$/;
    static WARTEN_MS = 250;
    static VERSUCHE = 40;

    constructor(inst, art, karte) {
        this.inst = inst;
        this.art = art;
        this.karte = karte;
        this.werte = Eigenkleidwerte.alle(inst, art);
        this.u = Eigenkleid.uniforms(karte, art);
        this.stoffU = Stoffshader.uniforms();
        this.uvMeter = 0;
        this.materialien = new Map();
        this.leer = new THREE.MeshBasicMaterial({ visible: false });
        this.netz = null;
        this.koerper = null;
        this.geo = null;
        this.bruecke = null;
        this.weg = false;
        this.kragen = art === 'oberteil' || art === 'kleid' ? new Eigenkragen(this) : null;
        this.rock = art === 'kleid' ? new Eigenrock(inst, art, karte) : null;          // Kleid = Oberteil + Rockteil (Stufe K3)
        this._entfernt = () => this._koerperWeg();
    }

    static uniforms(karte, art) {
        const v4 = () => ({ value: new THREE.Vector4() });
        return {
            uKkLaenge: { value: new THREE.Vector3(...karte.laengen) }, uKkArt: { value: Eigenkleidwerte.ARTEN[art].nummer },
            uKkSaum: v4(), uKkSitz: v4(), uKkAermelform: v4(), uKkHals: v4(), uKkKragen: v4(), uKkBand: v4(), uKkBruecke: v4(), uKkLage: { value: new THREE.Vector2() },
            uKkFalten: { value: 0 }, uKkFaltenAbstand: { value: EigenkleidschnittGLSL.FALTENABSTAND_M }, uKkFaltenTiefe: { value: EigenkleidschnittGLSL.FALTENTIEFE_M },
            uKkRelief: { value: 1 },
        };
    }

    /** An den jetzigen Körper der Figur binden; false, solange keiner (gebunden) da ist. */
    binden() {
        if (this.weg) return false;
        const koerper = this.inst?.bodyMesh;
        if (!koerper?.isSkinnedMesh || !koerper.skeleton || !koerper.parent) {
            if (this.netz) this.netz.visible = false;
            this._spaeter();
            return false;
        }
        this._versuche = 0;
        if (koerper !== this.koerper) {
            this.koerper?.removeEventListener('removed', this._entfernt);
            koerper.addEventListener('removed', this._entfernt);
            this.koerper = koerper;
        }
        const vorlagen = [koerper.material].flat();
        const liste = vorlagen.map(m => this._material(m));
        if (this.geo?.userData.quelle !== koerper.geometry) {
            Eigenkleidgeometrie.weg(this.geo);
            const neu = Eigenkleidgeometrie.bauen(koerper.geometry, vorlagen, this.karte);
            this.geo = neu.geo;
            this.bruecke = neu.bruecke;
            this.uvMeter = neu.uvMeter;
            this.u.uKkLaenge.value.set(...neu.laengen);
        }
        if (!this.netz) {
            this.netz = new THREE.SkinnedMesh(this.geo, liste);
            this.netz.name = `eigenkleid_${this.art}_${this.inst.id}`;
            this.netz.frustumCulled = false;
            this.netz.castShadow = false;
            this.netz.receiveShadow = true;
            Eigenkleidtreffer.schale(this.netz, this);                      // anklickbar: Treffer auf der Haut, wo das Stück sie deckt
            this.netz.userData.eigenkleid = this.art;
        } else {
            this.netz.geometry = this.geo;
            this.netz.material = liste;
        }
        this.netz.position.copy(koerper.position);
        this.netz.quaternion.copy(koerper.quaternion);
        this.netz.scale.copy(koerper.scale);
        this.netz.updateMatrix();
        this.netz.bindMode = koerper.bindMode;
        this.netz.bind(koerper.skeleton, koerper.bindMatrix);
        if (this.netz.parent !== koerper.parent) koerper.parent.add(this.netz);
        this.netz.visible = this.inst.kleiderSichtbar !== false;        // „Kleider aus“ gilt auch nach dem Neubau (`Kleidersichtbarkeit`)
        this.werteAnwenden();
        this.rock?.binden();
        return true;
    }

    _koerperWeg() {
        if (this.netz) this.netz.visible = false;
        this.kragen?.verbergen();
        this.rock?.verbergen();
        queueMicrotask(() => this.binden());
    }

    /** Noch kein gebundener Körper (Bau läuft): in `WARTEN_MS` noch einmal, höchstens `VERSUCHE`-mal, dann eine Warnung. */
    _spaeter() {
        if (this.weg || this._wartet) return;
        this._versuche = (this._versuche || 0) + 1;
        if (this._versuche > Eigenkleid.VERSUCHE) {
            Protokoll.warnung('Eigene Kleider', `${this.art}: kein gebundener Körper an ${this.inst?.id} — Stück bleibt verborgen`);
            return;
        }
        this._wartet = setTimeout(() => { this._wartet = null; this.binden(); }, Eigenkleid.WARTEN_MS);
    }

    /** Das Material für eine Körpergruppe: Stoff (EIN Material für alle Hautgruppen, deren Kachel die Karte führt) — oder unsichtbar. */
    _material(vorlage) {
        const gruppe = vorlage?.userData?.gruppe || '';
        const haut = (Eigenkleid.HAUT.test(gruppe) && this.karte.zeile.has(Number(vorlage.userData.kachel)))
            || (this.art === 'socke' && Koerperkoordinatenpunkte.NAEGEL.test(gruppe));            // Socken decken die Zehennägel mit

        if (!haut) return this.leer;
        let material = this.materialien.get('stoff');
        if (!material) {
            material = new THREE.MeshStandardMaterial({
                metalness: 0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
            });
            material.name = `eigenkleid_${this.art}`;
            material.userData.eigenkleid = this.art;
            material.onBeforeCompile = (shader) => {
                const fehlt = EigenkleidGLSL.patchen(shader, this.u);
                if (Stoffshader.patchen(shader, this.stoffU) < 4) fehlt.push('Stoff');
                if (fehlt.length) Protokoll.warnung('Eigene Kleider', `Shader ohne Stelle ${fehlt.join(', ')} — Sitz, Säume oder Stoff wirken nicht`);
            };
            material.customProgramCacheKey = () => `${EigenkleidGLSL.SCHLUESSEL}|${Stoffshader.SCHLUESSEL}${Stoffshader.FASSUNG}`;
            this.materialien.set('stoff', material);
        }
        return material;
    }

    /** Werte → Uniforms und Material (Farbe, Rauheit); ohne Neubau. `werte`: alle Felder (`Eigenkleidwerte.alle`). */
    werteAnwenden(werte = this.werte) {
        this.werte = { ...werte };
        const w = Eigenkleidwerte.shaderwerte(this.art, this.werte);
        for (const name of ['saum', 'sitz', 'aermelform', 'hals', 'kragen', 'band', 'bruecke']) this.u[`uKk${name[0].toUpperCase()}${name.slice(1)}`].value.set(...w[name]);
        this._brueckeNachfuehren(w);
        this.u.uKkFalten.value = w.falten;
        this.u.uKkRelief.value = w.relief;
        Stoffshader.werte(this.stoffU, w.stoff, this.uvMeter);
        for (const material of this.materialien.values()) {
            material.color.setHex(w.farbe);
            material.roughness = w.rauheit;
            material.metalness = w.metall;
        }
        this.kragen?.nachfuehren(w);
        this.rock?.werteAnwenden(this.werte);
    }

    /**
     * Fall unter Wölbungen und Saum: die Brücke dieser Schale (gemerkt je Fall und Saum; Hose und Socken tragen auf ganzer Höhe). Schon gerechnet → sofort; sonst erst
     * `BRUECKE_MS` nach dem letzten Zug, so lange mit Sanduhr (26.10.2026, Edgar: „Regler am T-Shirt … langsam. Mach eine Sanduhr“ — gemessen 134 ms je Zug am Saum,
     * 44 ms am Fall, weil jeder Schritt die Brücke neu rechnete).
     */
    static BRUECKE_MS = 150;

    _brueckeNachfuehren(w) {
        const fall = w.bruecke[3], saum = this.art === 'oberteil' || this.art === 'kleid' ? w.saum[0] : Infinity;
        if (!this.geo || Eigenkleidgeometrie.gerechnet(this.geo, fall, saum)) {
            Eigenkleidgeometrie.fallen(this.geo, fall, saum);
            return;
        }
        clearTimeout(this._brueckeZeit);
        if (!this._sanduhr) { this._sanduhr = true; Sanduhr.an('Drapierung rechnet …'); }
        this._brueckeZeit = setTimeout(() => {
            try {
                if (this.geo && !this.weg) Eigenkleidgeometrie.fallen(this.geo, fall, saum);
            } finally {
                this._sanduhr = false;
                Sanduhr.aus();
            }
        }, Eigenkleid.BRUECKE_MS);
    }

    /** Abnehmen: aus der Gruppe, Materialien frei — die Geometrie gehört dem Körper und bleibt. */
    entfernen() {
        this.weg = true;
        clearTimeout(this._wartet);
        if (this._sanduhr) { clearTimeout(this._brueckeZeit); this._sanduhr = false; Sanduhr.aus(); }
        this.kragen?.entfernen();
        this.rock?.entfernen();
        this.koerper?.removeEventListener('removed', this._entfernt);
        this.koerper = null;
        if (this.netz) {
            this.netz.parent?.remove(this.netz);
            this.netz = null;
        }
        Eigenkleidgeometrie.weg(this.geo);
        this.geo = null;
        for (const material of this.materialien.values()) material.dispose();
        this.materialien.clear();
        this.leer.dispose();
    }
}
