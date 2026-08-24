import * as THREE from 'three';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Zeigerwahl — was ein Klick in die Bühne auswählt.
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Die Reihenfolge der Prüfungen ist
 * die Bedienlogik und darf nicht getauscht werden:
 *
 *     1. Licht-Symbole   — sie sind klein und liegen vor der Figur
 *     2. Kleidungsstücke — sie liegen AUF der Figur
 *     3. die Figur selbst
 *     4. nichts davon    — Auswahl aufheben
 *
 * Ein `SkinnedMesh` ohne gebundenes Skelett wirft beim Schneiden; das ist kein
 * Fehler, sondern heißt „dieser Strahl trifft es nicht" — deshalb der stille
 * Ausstieg.
 */
export class Zeigerwahl {

    /**
     * @param {Object} teile { canvas, camera, lightIcons, figuren, auswahl,
     *                         lichtpanel, kleiderpanel, figurpanel }
     */
    constructor(teile) {
        Object.assign(this, teile);
        this.strahl = new THREE.Raycaster();
        this.zeiger = new THREE.Vector2();
    }

    verdrahten() {
        this.canvas.addEventListener('click', ereignis => this._klick(ereignis));
        return this;
    }

    _klick(ereignis) {
        const rahmen = this.canvas.getBoundingClientRect();
        this.zeiger.x = ((ereignis.clientX - rahmen.left) / rahmen.width) * 2 - 1;
        this.zeiger.y = -((ereignis.clientY - rahmen.top) / rahmen.height) * 2 + 1;
        this.strahl.setFromCamera(this.zeiger, this.camera);
        if (this._licht()) return;
        if (this._figurOderKleidung()) return;
        this.auswahl.leeren();
        this.lichtpanel.verbergen();
    }

    _licht() {
        const symbole = [this.lightIcons.spotLeftIcon,
                         this.lightIcons.spotRightIcon,
                         this.lightIcons.backLightIcon];
        const treffer = this.strahl.intersectObjects(symbole, true);
        if (!treffer.length) return false;
        const symbol = Zeigerwahl._hoch(treffer[0].object,
                                        teil => teil.userData.light);
        if (!symbol) return false;
        this.auswahl.lichtWaehlen(symbol);
        Protokoll.debug('main', '✓ Licht ausgewählt:', symbol.userData.light);
        this.lichtpanel.zeigen(symbol.userData.light, symbol);
        return true;
    }

    _figurOderKleidung() {
        let treffer;
        try {
            treffer = this.strahl.intersectObjects(this.figuren, true);
        } catch (fehler) {
            return true;   // SkinnedMesh ohne Skelett — Klick ist erledigt
        }
        if (!treffer.length) return false;
        const netz = treffer[0].object;
        if (netz.userData.isGarment) {
            this.auswahl.kleidungWaehlen(netz);
            Protokoll.debug('main', '✓ Garment ausgewählt:', netz.name);
            this.kleiderpanel.zeigen(netz);
            return true;
        }
        const figur = Zeigerwahl._hoch(netz, teil => teil.userData.isCharacter);
        if (!figur) return false;
        this.auswahl.figurWaehlen(figur);
        Protokoll.debug('main', '✓ Character ausgewählt:',
                        figur.userData.presetName);
        this.figurpanel.zeigen(figur);
        return true;
    }

    /** Von einem Treffer aufwärts, bis `passt` zutrifft — sonst `null`. */
    static _hoch(teil, passt) {
        let aktuell = teil;
        while (aktuell.parent && !passt(aktuell)) aktuell = aktuell.parent;
        return passt(aktuell) ? aktuell : null;
    }
}
