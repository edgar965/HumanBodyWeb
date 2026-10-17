import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Meshfighaltungspose } from './meshfighaltungspose.js';
import { Meshfighaut } from './meshfighaut.js';

/**
 * Meshfigurhaarobjekt — ein Haar als eigenes Objekt auf der Figur der Bühne: das Haar aus dem Netz
 * (`ergebnis/haar.glb`, 27.09.2026) oder die Haarkarten aus seiner Schale (`ergebnis/haarkarten.glb`,
 * Schritt „frisur", 29.09.2026). Beide liegen schon in der Ruhelage der Figur — sie hängen ohne eigene Lage
 * in deren Gruppe und wandern mit, wenn die Figur neu gebaut wird (`anhaengen`).
 *
 * `art`: `{name, datei: ergebnis => {datei, bytes, fehler}, karten}`. Karten tragen ein Deckkraftbild
 * (glTF `MASK`): `alphaToCoverage` statt harter Kante — genesis9-inhalte.md, Kin: „alphaTest 0.3 machte
 * krebskranke Haare".
 *
 * SICHTBAR JE NETZ, NICHT JE GRUPPE: Der Export (`Modellexportinhalt.objekte`) fragt `mesh.visible`; eine
 * ausgeblendete Gruppe mit sichtbaren Netzen darin ging mit in die GLB (bis 29.09.2026 beim Schalter „Haar").
 *
 * ANIMIERT (13.10.2026): Trägt der Steckbrief eine Hautdatei (`objekt.haut`), wird das Netz an das Skelett der Figur gebunden (`Meshfighaut`) — dann nimmt die Animation es mit. In der Haltung des Netzes
 * (`haltung`) bleibt es starr: die Figur ist dort fest gebacken, und die Animation schaltet die Haltung ohnehin aus.
 *
 * AN DIE HALTUNG GEBUNDEN (14.10.2026): In der Ruhe und in der Bewegung lädt das Objekt NICHT mehr die in die Ruhelage zurückgerechnete Fassung (Robe fächerförmig, Stab neben der Faust), sondern die Fassung der
 * Haltung — unverändert aus dem Netz — und bindet sie an das Skelett der Haltung (`Meshfighaltungspose`): der Stoff steht im Bild 0 des Netzes so, wie er im Netz steht, und die Bewegung verformt ihn von dort aus.
 * Voraussetzung: eine gültige Haltung mit Winkeln, die Haltungsfassung des Objekts und seine Hautdatei; sonst bleibt alles wie vorher. Bis die Haltung gerechnet ist (die Achsen kommen mit den Feldern der
 * Gelenkkorrekturen), bleibt das Netz unsichtbar — seine Punkte liegen in der Haltung, nicht in der Ruhe. Die Gelenkkorrekturen (`gelenkziel`) gelten für diese Fassung nicht: ihre Verschiebungen sind in der Ruhelage gerechnet.
 */
export class Meshfigurhaarobjekt {

    constructor(seite, melden, art) {
        this.seite = seite;
        this.melden = melden;
        this.art = art;
        this.objekt = null;
        this.gruppe = null;
        this.an = false;
        this.vorhanden = false;
        this._stand = null;
        this._haltung = false;
        this.skelett = null;        // das Skelett der gezeigten Figur (`anhaengen`)
        this.haut = null;           // die geladene Hautdatei zu `objekt` (`Meshfighaut.laden` + Namensliste)
        this._lauf = 0;             // zählt die Ladevorgänge: eine überholte Hautdatei wird verworfen
        this._gelenkAdresse = null; // wo die Gelenkkorrekturen dieses Objekts liegen (`gelenkadresse`)
        this.modell = null;         // die gezeigte Figur (`anhaengen`): die Haltung wird an ihrem Skelett gerechnet
        this._drehung = null;       // die Haltung des Netzes (`ergebnis.haltung.drehung`), wenn das Objekt an sie gebunden wird — sonst null
        this._wartet = false;       // an die Haltung gebunden, aber noch nicht gebunden: unsichtbar
        this._bindelauf = 0;        // zählt die Bindungen: eine überholte Haltung wird verworfen
        /** Ein gehaltener Gegenstand (Stab) bindet abgelöst, damit `Meshfigurstab` ihn um die Faust drehen kann (`Meshfighaut._an_die_haltung`). */
        this.beweglich = false;
        /** Wird gerufen, wenn das Netz (neu) an das Skelett gebunden ist — die Haut-Verdeckung und der Stab ziehen nach. */
        this.gebunden = null;
    }

    /**
     * Laden, wenn sich die Datei geändert hat; `gruppe` = die Gruppe der Figur (oder null).
     * `haltung`: die Figur steht in der Haltung des Netzes (`Meshfighaltung`) — dann gilt die Fassung des Objekts in dieser Haltung (`objekt.haltung`, unverändert aus dem Netz, im Raum der gebackenen Figur).
     * Hat es keine, ist es dort nicht zu sehen: die Fassung in Ruhe läge neben der Figur.
     */
    zeigen(z, gruppe, haltung = false) {
        const gesamt = this.art.datei(z.ergebnis || {}) || {};
        const hg = (z.ergebnis || {}).haltung || {};
        const anDieHaltung = !haltung && Boolean(gesamt.haltung?.datei && gesamt.haut && hg.gueltig && hg.drehung && Object.keys(hg.drehung).length);
        const o = (haltung || anDieHaltung) ? (gesamt.haltung || {}) : gesamt;
        this._drehung = anDieHaltung ? hg.drehung : null;
        const hautBeschreibung = ((haltung || anDieHaltung) ? (haltung ? o : gesamt) : o).haut || null;
        const wechsel = haltung !== this._haltung;
        this._haltung = haltung;
        this.vorhanden = Boolean(o.datei);
        if (gesamt.fehler) this.melden(`${this.art.name}: ${gesamt.fehler}`);
        if (!o.datei) {
            if (wechsel && this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt = null;
                this._stand = null;
            }
            return;
        }
        const stand = JSON.stringify([o.datei, o.bytes, o.flaechen, o.punkte, (hautBeschreibung || {}).bytes, anDieHaltung]);
        if (stand !== this._stand) {
            this._stand = stand;
            this._gelenkAdresse = Meshfigurhaarobjekt.gelenkadresse(this.seite.dateiAdresse('ergebnis', o.datei), anDieHaltung ? null : o.haut, encodeURIComponent(stand));
            this._laden(`${this.seite.dateiAdresse('ergebnis', o.datei)}?t=${encodeURIComponent(stand)}`, hautBeschreibung, encodeURIComponent(stand));
        }
        if (gruppe) this.anhaengen(gruppe);
    }

    /** Adresse der Gelenkfelder (JCM) zu einer Objektdatei — nur für Objekte mit Hautdatei, sonst null (Mesh-3D, `Meshfigurobjektfelder`; andere Seiten haben die Adresse nicht, dann gibt es keine Felder). */
    static gelenkadresse(dateiAdresse, haut, marke) {
        return haut && dateiAdresse.includes('/datei/ergebnis/') ? `${dateiAdresse.replace('/datei/ergebnis/', '/objektfelder/')}?t=${marke}` : null;
    }

    /** Für die Gelenkkorrekturen (`Meshfigurgelenke`): das an die Knochen gebundene Netz und die Adresse seiner Felder — null, solange es nicht gebunden ist, in der Haltung des Netzes steht oder die Seite keine Felder hat. */
    gelenkziel() {
        if (!this.objekt || !this.haut || !this._gelenkAdresse || this._haltung || this._drehung) return null;
        const netz = Meshfighaut.netze(this.objekt)[0];
        return netz?.isSkinnedMesh ? { netz, adresse: this._gelenkAdresse } : null;
    }

    /** In die Gruppe der Figur hängen; mit `skelett` (dem der gezeigten Figur) auch an ihre Knochen binden, wenn das Objekt eine Hautdatei hat. */
    anhaengen(gruppe, skelett = null, modell = null) {
        this.gruppe = gruppe;
        if (skelett) this.skelett = skelett;
        if (modell) this.modell = modell;
        if (this.objekt && this.objekt.parent !== gruppe) {
            this.objekt.parent?.remove(this.objekt);
            gruppe.add(this.objekt);
        }
        this._binden();
        this.sichtbar(this.an);
    }

    _binden() {
        if (!this.objekt || !this.haut || !this.skelett) return;
        if (this._drehung) { this._anDieHaltungBinden(); return; }
        Meshfighaut.binden(this.objekt, this.skelett, this.haut);
        this.gebunden?.(this);
    }

    /** An die Haltung binden (`Meshfighaltungspose`): die Haltung wird einmal je Skelett gerechnet; solange sie fehlt, bleibt das Netz unsichtbar (es liegt im Raum der Haltung). */
    _anDieHaltungBinden() {
        const { objekt, haut, skelett, modell, _drehung: drehung } = this;
        if (!modell) return;
        const lauf = ++this._bindelauf;
        const fertig = pose => {
            if (lauf !== this._bindelauf || objekt !== this.objekt) return;                  // überholt: ein neues Skelett oder Objekt
            if (!pose) { this.melden(`${this.art.name}: Haltung nicht gerechnet — das Objekt bleibt ausgeblendet`); return; }
            if (!Meshfighaut.binden(objekt, skelett, haut, { inverse: pose.inverse, boden: pose.boden, beweglich: this.beweglich })) return;
            this._wartet = false;
            this.sichtbar(this.an);
            this.gebunden?.(this);
        };
        const sofort = Meshfighaltungspose.gemerkt(modell, drehung);
        if (sofort) fertig(sofort);
        else Promise.resolve(Meshfighaltungspose.fuer(modell, drehung)).then(fertig);
    }

    _hautLaden(beschreibung, marke, lauf) {
        Meshfighaut.laden(`${this.seite.dateiAdresse('ergebnis', beschreibung.datei)}?t=${marke}`, beschreibung.punkte)
            .then(haut => {
                if (lauf !== this._lauf) return;                    // inzwischen kam ein anderes Objekt
                this.haut = { ...haut, knochen: beschreibung.knochen };
                this._binden();
            })
            .catch(fehler => this.melden(`${this.art.name}: Hautgewichte nicht geladen (${fehler.message || fehler}) — das Objekt bleibt starr`));
    }

    sichtbar(an) {
        this.an = an;
        this.objekt?.traverse(o => { if (o.isMesh) o.visible = an && !this._wartet; });
    }

    _laden(adresse, hautBeschreibung = null, marke = '') {
        const lauf = ++this._lauf;
        this.haut = null;
        new GLTFLoader().load(adresse, gltf => {
            if (lauf !== this._lauf) return;                        // überholt: ein neuerer Stand wird geladen
            const neu = gltf.scene;
            neu.name = this.art.name;
            neu.traverse(o => {
                for (const m of [].concat(o.material || [])) {
                    m.side = THREE.DoubleSide;
                    m.metalness = 0;
                    if (this.art.karten && m.map) m.alphaToCoverage = true;
                }
            });
            if (this.objekt) {
                this.objekt.parent?.remove(this.objekt);
                this.objekt.traverse(o => { o.geometry?.dispose?.(); });
            }
            this.objekt = neu;
            this._wartet = Boolean(this._drehung);                  // an die Haltung gebunden wird erst, wenn die Haltung gerechnet ist
            if (this.gruppe) this.anhaengen(this.gruppe);
            if (hautBeschreibung) this._hautLaden(hautBeschreibung, marke, lauf);
        }, undefined, fehler => this.melden(`${this.art.name} nicht geladen: ${fehler.message || fehler}`));
    }
}
