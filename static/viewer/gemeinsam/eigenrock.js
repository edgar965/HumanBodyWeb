import * as THREE from 'three';
import { Eigenkleidgeometrie } from './eigenkleidgeometrie.js';
import { Eigenkleidtreffer } from './eigenkleidtreffer.js';
import { Eigenkleidwerte } from './eigenkleidwerte.js';
import { Eigenrockdrapieren } from './eigenrockdrapieren.js';
import { Eigenrockgeometrie } from './eigenrockgeometrie.js';
import { Protokoll } from './protokoll.js';
import { Stoffshader } from './stoffshader.js';

/**
 * Eigenrock — ein eigener Rock, oder der Rockteil eines eigenen Kleids, als eigene Fläche (Stufe K3, 25.10.2026 nachts; Auftrag Edgar „Mach weiter, alle Aufgaben“,
 * Konzept `Docu/konzepte/2026-10-25_eigene-kleider-konzept.md`: „Rock/Kleid (Hülle zwischen den Beinen) + Knopf ‚Drapieren‘ mit Reglern (Falten, Steifigkeit, Gewicht,
 * örtlich weiter)“).
 *
 * Ein `SkinnedMesh` am Skelett des Körpers, gebunden wie die Schale und der Kragen. Das Netz baut `Eigenrockgeometrie` aus der Haut (Körperkoordinaten aus
 * `Eigenkleidgeometrie`, je Körpergeometrie einmal) — neu nur, wenn sich Bund, Länge, Sitz, Weite oder Falten ändern oder der Körper. Stoff, Farbe und Rauheit sind
 * Material und Uniforms (kein Neubau). Steht `drapiert` auf 1, fällt der Stoff nach jedem Neubau von selbst (`Eigenrockdrapieren`, zusammengefasst über `WARTEN_MS`,
 * ein älterer Lauf schreibt nicht über einen neueren). Im Kleid (`art` = 'kleid') hängt der Rock an `Eigenkleid` und setzt `UEBERLAPPUNG` über dessen Saum an.
 */
export class Eigenrock {

    static UEBERLAPPUNG = 0.02;
    static WARTEN_MS = 250;
    static VERSUCHE = 40;
    static _schalen = new WeakMap();

    constructor(inst, art, karte) {
        this.inst = inst;
        this.art = art;
        this.karte = karte;
        this.werte = Eigenkleidwerte.alle(inst, art);
        this.stoffU = Stoffshader.uniforms();
        this.material = new THREE.MeshStandardMaterial({ metalness: 0, side: THREE.DoubleSide });
        this.material.name = `eigenrock_${art}`;
        this.material.onBeforeCompile = (shader) => Stoffshader.patchen(shader, this.stoffU);
        this.material.customProgramCacheKey = () => `${Stoffshader.SCHLUESSEL}${Stoffshader.FASSUNG}`;
        this.netz = null;
        this.bau = null;
        this.koerper = null;
        this.weg = false;
        this.stand = null;
        this.laeuft = null;
        this._stand = '';
        this._lauf = 0;
    }

    /** Werte → Maße der Geometrie (m, Anteile). */
    static masse(art, werte) {
        const w = feld => Number(werte?.[feld] ?? Eigenkleidwerte.angaben(art, feld)?.vorgabe ?? 0);
        return { bund: art === 'kleid' ? w('saum') - Eigenrock.UEBERLAPPUNG : w('bund'), laenge: w('laenge'), sitz: Math.max(1, w('sitz_rock')) / 1000,
                 weite: [w('weite_vorn') / 100, w('weite_hinten') / 100, w('weite_seite') / 100], falten: [w('falten_zahl'), w('falten_tiefe') / 1000] };
    }

    /** An den jetzigen Körper der Figur binden; false, solange keiner (gebunden) da ist. */
    binden() {
        if (this.weg) return false;
        const koerper = this.inst?.bodyMesh;
        if (!koerper?.isSkinnedMesh || !koerper.skeleton || !koerper.parent) {
            if (this.netz) this.netz.visible = false;
            if ((this._versuche = (this._versuche || 0) + 1) <= Eigenrock.VERSUCHE) {
                clearTimeout(this._wartet);
                this._wartet = setTimeout(() => this.binden(), Eigenrock.WARTEN_MS);
            }
            return false;
        }
        this._versuche = 0;
        this.koerper = koerper;
        this.werteAnwenden(this.werte, true);
        return true;
    }

    /** Werte → Material und Stoff; Geometrie neu nur bei geänderten Maßen; Drapieren nach Neubau oder bei Änderung von Drapiert/Steifigkeit/Gewicht. */
    werteAnwenden(werte = this.werte, neu = false) {
        const vorher = this.werte;
        this.werte = { ...werte };
        const w = Eigenkleidwerte.shaderwerte(this.art, this.werte);
        this.material.color.setHex(w.farbe);
        this.material.roughness = w.rauheit;
        this.material.metalness = w.metall;
        Stoffshader.werte(this.stoffU, w.stoff, 1);
        if (!this.koerper || this.weg) return;
        const masse = Eigenrock.masse(this.art, this.werte), drapiert = Number(this.werte.drapiert) >= 0.5;
        const stand = JSON.stringify([this.koerper.geometry.id, masse]);
        if (neu || stand !== this._stand) {
            this._stand = stand;
            this._bauen(masse);
            if (drapiert) this.drapieren();
        } else if (drapiert && (Number(vorher?.drapiert) < 0.5 || vorher?.steif !== this.werte.steif || vorher?.gewicht !== this.werte.gewicht)) {
            this.drapieren();
        } else if (!drapiert && Number(vorher?.drapiert) >= 0.5) {
            this.grundform();
        }
    }

    _schale(koerper) {
        let schale = Eigenrock._schalen.get(koerper.geometry);
        if (!schale) {
            schale = Eigenkleidgeometrie.bauen(koerper.geometry, [koerper.material].flat(), this.karte).geo;
            Eigenrock._schalen.set(koerper.geometry, schale);
        }
        return schale;
    }

    _bauen(masse) {
        this._lauf++;
        const bau = Eigenrockgeometrie.bauen(this._schale(this.koerper), masse);
        this.bau?.geo.dispose();
        this.bau = bau;
        if (!bau) {
            this.stand = null;
            if (this.netz) this.netz.visible = false;
            Protokoll.warnung('Eigene Kleider', `${this.art}: Bund oder Saum nicht gefunden (Bund ${masse.bund}, Länge ${masse.laenge}) — Rock bleibt verborgen`);
            return;
        }
        bau.grund = Float32Array.from(bau.geo.attributes.position.array);
        this.stand = { ms: Math.round(bau.ms), punkte: bau.geo.attributes.position.count, drapiert: null };
        this._binden();
    }

    _binden() {
        const k = this.koerper;
        if (!this.netz) {
            this.netz = new THREE.SkinnedMesh(this.bau.geo, this.material);
            this.netz.name = `eigenrock_${this.art}_${this.inst.id}`;
            this.netz.frustumCulled = false;
            this.netz.castShadow = false;
            this.netz.receiveShadow = true;
            Eigenkleidtreffer.rock(this.netz);                              // anklickbar (Klick öffnet den Reiter des Stücks)
            this.netz.userData.eigenkleid = this.art === 'kleid' ? 'kleid_rock' : 'rock';
        } else {
            this.netz.geometry = this.bau.geo;
        }
        this.netz.position.copy(k.position);
        this.netz.quaternion.copy(k.quaternion);
        this.netz.scale.copy(k.scale);
        this.netz.updateMatrix();
        this.netz.bindMode = k.bindMode;
        this.netz.bind(k.skeleton, k.bindMatrix);
        if (this.netz.parent !== k.parent) k.parent.add(this.netz);
        this.netz.visible = this.inst.kleiderSichtbar !== false;        // „Kleider aus“ (`Kleidersichtbarkeit`)
    }

    /** Stoff fallen lassen (Knopf „Drapieren“) — → Promise mit `{ms, schritte, saum_mm, weite_mm}` oder null (überholt, kein Netz, Fehler). */
    drapieren() {
        clearTimeout(this._drapWarten);
        this._offen?.(null);              // der zusammengefasste ältere Aufruf: überholt, aber aufgelöst (sonst hing der Kasten bei „fällt …“)
        const nr = ++this._lauf;
        this.laeuft = new Promise((fertig) => {
            this._offen = fertig;
            this._drapWarten = setTimeout(async () => {
                const bau = this.bau;
                if (nr !== this._lauf || !bau || this.weg) { fertig(null); return; }
                try {
                    bau.geo.attributes.position.array.set(bau.grund);
                    const b = await Eigenrockdrapieren.rechnen(bau, Number(this.werte.steif) / 100, Number(this.werte.gewicht) / 100);
                    if (nr !== this._lauf || bau !== this.bau) { fertig(null); return; }
                    Eigenrockgeometrie.normalen(bau.geo, bau.zeilen, bau.spalten);
                    bau.geo.computeBoundingSphere();
                    this.stand = { ...this.stand, drapiert: b };
                    fertig(b);
                } catch (fehler) {
                    Protokoll.fehler('Eigene Kleider', `${this.art}: Drapieren fehlgeschlagen`, fehler);
                    fertig(null);
                }
            }, Eigenrock.WARTEN_MS);
        });
        return this.laeuft;
    }

    /** Zurück auf die Startform (A-Linie, eingelegte Falten), ohne Neubau. */
    grundform() {
        this._lauf++;
        if (!this.bau) return;
        this.bau.geo.attributes.position.array.set(this.bau.grund);
        this.bau.geo.attributes.position.needsUpdate = true;
        Eigenrockgeometrie.normalen(this.bau.geo, this.bau.zeilen, this.bau.spalten);
        if (this.stand) this.stand.drapiert = null;
    }

    verbergen() {
        if (this.netz) this.netz.visible = false;
    }

    entfernen() {
        this.weg = true;
        this._lauf++;
        clearTimeout(this._wartet);
        clearTimeout(this._drapWarten);
        this._offen?.(null);
        this.netz?.parent?.remove(this.netz);
        this.netz = null;
        this.bau?.geo.dispose();
        this.bau = null;
        this.material.dispose();
    }
}
