import { Genesis9felder } from '../gemeinsam/genesis9felder.js';
import { Genesis9gelenke } from '../gemeinsam/genesis9gelenke.js';

/**
 * Meshfigurgelenke — Daz' Gelenkkorrekturen (JCMs) in der Bewegung der Mesh-Bühne (14.10.2026).
 *
 * Edgar: „JCM (Gelenkkorrekturen) - warum wendest du die denn nicht an?? das mesh-3d sollte wie Charakter / Studio sein!" Szene und Studio rufen je Bild `Genesis9gelenke.takt` (Winkel der Knochen → Formelgraph → Felder auf der Haut,
 * dazu die Felder der getragenen Stücke); die Animationsleiste der Mesh-Bühne (`Engine2d3dKleideranimation`) tat es nie. Jetzt ruft sie diese Klasse nach jedem Bild:
 *
 *   * Körper, Augen, Mund: `Genesis9gelenke.takt(figur)` — derselbe Code wie im Studio.
 *   * Die Objekte aus dem Netz (Kleidung, Haar, Bestandteile) sind keine Stücke der Garderobe; ihr Feld kommt vom Server (`Meshfigurobjektfelder`: die Verschiebungen des Käfigs dort, wo das Objekt anliegt, ausgeblendet ab 2 bis 5 cm Abstand),
 *     wird einmal geholt, sobald die Figur ihre Ruhe verlässt, und mit denselben Werten wie die Haut auf das Netz des Objekts gelegt (`Genesis9felder.anwenden`). Anliegender Stoff bewegt sich so mit der korrigierten Haut;
 *     Stoff, der weit absteht, und starre Gegenstände (Stab, Bart, Haar am Kopf) bekommen kein Feld.
 *
 * Läuft nichts (Ruhe, keine Felder geladen), tut `takt` nichts.
 */
export class Meshfigurgelenke {

    constructor(buehne) {
        this.buehne = buehne;
        this._ziele = new WeakMap();        // Netz -> {adresse, felder: null (lädt) | {kanal: {n, d}}}
    }

    /** Ein Bild: Haut rechnen, die gleichen Werte auf die Objekte legen. */
    takt() {
        const werte = Genesis9gelenke.takt(this.buehne.modell);
        if (!werte) return null;
        for (const ziel of this.buehne.gelenkziele()) this._anwenden(ziel, werte);
        return werte;
    }

    _anwenden({ netz, adresse }, werte) {
        let e = this._ziele.get(netz);
        if (!e || e.adresse !== adresse) {
            e = { adresse, felder: null };
            this._ziele.set(netz, e);
            Genesis9felder.holenAdresse(adresse).then(felder => { if (this._ziele.get(netz) === e) e.felder = felder || {}; });
        }
        if (e.felder && Object.keys(e.felder).length) Genesis9felder.anwenden(netz, Genesis9gelenke.GRUPPE, e.felder, werte);
    }
}
