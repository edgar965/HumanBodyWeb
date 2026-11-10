/**
 * Fotogenesisanpassungsfigur — eine in ein Netz eingepasste Genesis-Figur als Zeichner eines Feldes der Jobseite (04.11.2026, dritte Zeile `Fotogenesisgenesiszeile`, Feld 1).
 *
 * Liest dasselbe Paket wie die erste Zeile der Mesh-Genesis-Testseite (`Meshgenesistestanpassung`) und baut die Figur mit deren Code: Geometrie
 * `Meshgenesismeshanpassung._geometrie`, Haut der Startfigur `_haut`, Ansichtsart `_objekt` (über den Prototyp gerufen, `this` trägt `figur`, `modus`, `hautMaterialien`, `_neu`).
 * Nur die Figur, ohne das Mesh und ohne das Anatomie-Stück; wie dort um den tiefsten Punkt des Meshs auf den Boden gestellt.
 */
import * as THREE from 'three';
import { Meshgenesismeshanpassung } from '../meshgenesis/meshgenesismeshanpassung.js';
import { Meshgenesislinienzeichner as LZ } from '../meshgenesis/meshgenesislinienzeichner.js';
import { Fotogenesisnetz } from './fotogenesisnetz.js';

export class Fotogenesisanpassungsfigur {
    /** @param {string} adresse Paket (`…/meshanpassung/` bzw. `…/genesiszeile/ipnet/`) @param {Function} neu ruft die Seite, wenn neu zu zeichnen ist (Textur nachgeladen) */
    constructor(adresse, neu) {
        this.adresse = adresse;
        this.neuRuf = neu;
        this.figur = null;
        this.figurHaut = null;
        this.hautMaterialien = null;
        this.modus = 'textur';
        this.fehler = '';
        this.bereit = this._laden();
    }

    async _laden() {
        try {
            // ohne das Netz (08.11.2026, Ladezeit): das Feld zeigt nur die Figur, vom Netz braucht es nur den tiefsten Punkt (`kopf.netz_boden`) — beim Zauberer 2 statt 11 MB
            const adresse = new URL(this.adresse, location.href);
            adresse.searchParams.set('netz', '0');
            const a = await fetch(adresse);
            if (!a.ok) throw new Error(a.status === 404 ? 'Noch nicht gerechnet.' : `HTTP ${a.status}`);
            const { kopf, daten } = LZ.paket(await a.arrayBuffer());
            const z = Meshgenesismeshanpassung.prototype;
            this.figur = Meshgenesismeshanpassung._geometrie(daten.figur, daten.figur_dreiecke);
            this.figurHaut = daten.uv && kopf.textur ? z._haut.call(this, daten, kopf.textur) : null;
            let boden = Number.isFinite(kopf.netz_boden) ? kopf.netz_boden : Infinity;
            if (!Number.isFinite(boden) && daten.netz_punkte) for (let i = 1; i < daten.netz_punkte.length; i += 3) boden = Math.min(boden, daten.netz_punkte[i]);
            for (const g of [this.figur, this.figurHaut]) g?.translate(0, -boden, 0);
        } catch (fehler) {
            this.fehler = fehler.message;
        }
        this._neu();
    }

    /** von `_haut` gerufen, wenn eine Textur da ist */
    _neu() {
        this.neuRuf?.();
    }

    /** Zeichner von `Meshgenesisansicht`; `d.modus` = Ansichtsart der Seite. */
    zeichnen(inhalt, _art, d) {
        if (!this.figur) {
            inhalt.userData.hinweis = this.fehler || 'wird geladen …';
            return;
        }
        this.modus = d?.modus ?? 'textur';
        if (this.modus === 'textur') {
            inhalt.add(this.figurHaut ? new THREE.Mesh(this.figurHaut, this.hautMaterialien)
                : Meshgenesismeshanpassung.prototype._objekt.call(this, this.figur, Meshgenesismeshanpassung.FIGURFARBE, 1));
            return;
        }
        // die anderen Ansichtsarten wie die Testfiguren der Zeile (`Fotogenesistestfigur`): Ersatzmaterial auf Ebene 1 (`Fotogenesisnetz.ersatz`) — mit dem eigenen Material auf Ebene 0
        // stand Feld 1 im Fotolicht flach und orange da (04.11.2026, Leiste der dritten Zeile, „Netz“ im Chrome)
        const netz = new THREE.Mesh(this.figur);
        netz.layers.set(1);
        netz.userData.meshgenesisFremd = true;          // die Geometrie gehört der Figur, nicht dem Feld (`Meshgenesisansicht._leeren`)
        inhalt.add(netz);
        inhalt.userData.genesisErsatz = Fotogenesisnetz.ersatz(this.modus);
    }
}
