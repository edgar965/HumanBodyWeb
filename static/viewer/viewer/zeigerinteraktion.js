import { state } from './state.js';
import { isVeActive, isVeBoxSelecting, getVeTargetMesh,
         veHandleKeydown } from './vertex_editor.js';
import { veHandleClick, veBoxSelectStart, veBoxSelectMove,
         veBoxSelectEnd } from './vertex_auswahl.js';

/**
 * Zeigerinteraktion — Zeigen, Auswählen und Entfernen von Kleidung, Haaren und
 * Zubehör in der 3D-Ansicht der Viewer-Seite.
 *
 * Aus viewer/interaction.js herausgeloest (Umbau 16.08.2026):
 * `initInteraction()` hatte 107 Zeilen mit zwei inneren Funktionen. Die
 * Umrechnung der Mausposition in Strahlkoordinaten stand ZWEIMAL darin — einmal
 * für den Vertex-Editor, einmal für das normale Zeigen. Jetzt `_strahlSetzen()`.
 *
 * Ist der Vertex-Editor aktiv, gehören ihm alle Mausereignisse; das ist der
 * Grund für die vielen `isVeActive()`-Abfragen.
 */
export class Zeigerinteraktion {

    /** Bis zu dieser Bewegung gilt ein Druck noch als Klick, nicht als Ziehen. */
    static KLICK_TOLERANZ = 3;
    /** Versatz des Hinweisfelds zum Zeiger. */
    static HINWEIS_VERSATZ = [14, -10];

    /**
     * @param wahl.ziele     () => Liste auswählbarer Objekte
     * @param wahl.finden    (objekt, ziele) => Eintrag oder null
     * @param wahl.gleich    (a, b) => boolean
     * @param wahl.leuchten  (eintrag, farbe) => void
     * @param wahl.entfernen () => gewähltes Objekt entfernen
     * @param wahl.gewechselt (eintrag) => Auswahl hat sich geändert
     */
    constructor(wahl) {
        Object.assign(this, wahl);
        this.leinwand = state.renderer.domElement;
        this.hinweis = document.getElementById('garment-tooltip');
        this.entfernenKnopf = document.getElementById('selection-remove-btn');
        this._schwebtAn = false;
        this._letzteMaus = null;
    }

    verdrahten() {
        this.leinwand.addEventListener('mousemove', e => this._bewegen(e));
        this.leinwand.addEventListener('mouseleave', () => this._verlassen());
        this.leinwand.addEventListener('mousedown', e => this._druecken(e));
        this.leinwand.addEventListener('mouseup', e => this._loslassen(e));
        window.addEventListener('keydown', e => this._taste(e));
        this.entfernenKnopf?.addEventListener('click', () => this.entfernen());
        return this;
    }

    // ------------------------------------------------------------------- Maus

    /**
     * Bewegung wird auf ein Bild pro Takt gedrosselt — sonst rechnet der
     * Strahlwerfer bei jedem Pixel durch alle Netze.
     */
    _bewegen(ereignis) {
        if (isVeActive() && isVeBoxSelecting()) {
            veBoxSelectMove(ereignis);
            return;
        }
        this._letzteMaus = ereignis;
        if (this._schwebtAn) return;
        this._schwebtAn = true;
        requestAnimationFrame(() => {
            this._schwebtAn = false;
            if (!this._letzteMaus) return;
            if (isVeActive()) this._veZeiger(this._letzteMaus);
            else this._schweben(this._letzteMaus);
        });
    }

    _verlassen() {
        const schwebend = state._hoveredItem;
        if (schwebend && !this.gleich(schwebend, state._selectedItem)) {
            this.leuchten(schwebend, state._ZERO_EMISSIVE);
        }
        state._hoveredItem = null;
        this._hinweisAus();
    }

    _druecken(ereignis) {
        if (ereignis.button !== 0) return;
        state._mouseDownPos = { x: ereignis.clientX, y: ereignis.clientY };
        // Alt+Ziehen zieht im Vertex-Editor einen Auswahlrahmen.
        if (isVeActive() && ereignis.altKey) veBoxSelectStart(ereignis);
    }

    _loslassen(ereignis) {
        if (isVeActive() && isVeBoxSelecting()) {
            veBoxSelectEnd(ereignis);
            state._mouseDownPos = null;
            return;
        }
        if (ereignis.button !== 0 || !state._mouseDownPos) return;
        const dx = ereignis.clientX - state._mouseDownPos.x;
        const dy = ereignis.clientY - state._mouseDownPos.y;
        state._mouseDownPos = null;
        // Nach dem Drehen der Kamera soll sich die Auswahl nicht ändern.
        if (Math.hypot(dx, dy) > Zeigerinteraktion.KLICK_TOLERANZ) return;
        if (isVeActive()) veHandleClick(ereignis);
        else this._klick();
    }

    _taste(ereignis) {
        if (ereignis.target.closest('input, select, textarea')) return;
        if (ereignis.key === 'Delete' && state._selectedItem) {
            this.entfernen();
            return;
        }
        if (isVeActive()) veHandleKeydown(ereignis);
    }

    // ----------------------------------------------------------------- Strahl

    /** Mausposition in Strahlkoordinaten — stand vorher zweimal ausgeschrieben. */
    _strahlSetzen(ereignis) {
        const kasten = this.leinwand.getBoundingClientRect();
        state._mouseNDC.x = ((ereignis.clientX - kasten.left) / kasten.width) * 2 - 1;
        state._mouseNDC.y = -((ereignis.clientY - kasten.top) / kasten.height) * 2 + 1;
        state._raycaster.setFromCamera(state._mouseNDC, state.camera);
        return kasten;
    }

    /** Im Vertex-Editor zeigt der Zeiger nur, ob er das Netz trifft. */
    _veZeiger(ereignis) {
        this._strahlSetzen(ereignis);
        const treffer = state._raycaster.intersectObject(getVeTargetMesh());
        this.leinwand.style.cursor = treffer.length > 0 ? 'pointer' : '';
    }

    _schweben(ereignis) {
        const kasten = this._strahlSetzen(ereignis);
        const ziele = this.ziele();
        const treffer = state._raycaster.intersectObjects(
            ziele.map(ziel => ziel.root), true);
        const gefunden = treffer.length
            ? this.finden(treffer[0].object, ziele) : null;

        if (gefunden) this._hinweisAn(gefunden.label, ereignis, kasten);
        else this._hinweisAus();

        if (this.gleich(state._hoveredItem, gefunden)) return;
        const vorher = state._hoveredItem;
        if (vorher && !this.gleich(vorher, state._selectedItem)) {
            this.leuchten(vorher, state._ZERO_EMISSIVE);
        }
        state._hoveredItem = gefunden;
        if (gefunden && !this.gleich(gefunden, state._selectedItem)) {
            this.leuchten(gefunden, state._HOVER_EMISSIVE);
        }
    }

    _hinweisAn(text, ereignis, kasten) {
        this.leinwand.style.cursor = 'pointer';
        if (!this.hinweis) return;
        const [dx, dy] = Zeigerinteraktion.HINWEIS_VERSATZ;
        this.hinweis.textContent = text;
        this.hinweis.style.left = (ereignis.clientX - kasten.left + dx) + 'px';
        this.hinweis.style.top = (ereignis.clientY - kasten.top + dy) + 'px';
        this.hinweis.style.display = 'block';
    }

    _hinweisAus() {
        this.leinwand.style.cursor = '';
        if (this.hinweis) this.hinweis.style.display = 'none';
    }

    // ---------------------------------------------------------------- Auswahl

    /** Klick auf das schwebende Objekt wählt es, ein zweiter Klick hebt auf. */
    _klick() {
        const vorher = state._selectedItem;
        const schwebend = state._hoveredItem;
        if (state._selectedItem) {
            this.leuchten(state._selectedItem, state._ZERO_EMISSIVE);
        }
        const neu = (schwebend && !this.gleich(vorher, schwebend))
            ? schwebend : null;
        state._selectedItem = neu;
        if (neu) this.leuchten(neu, state._SELECT_EMISSIVE);
        if (this.entfernenKnopf) {
            this.entfernenKnopf.style.display = neu ? '' : 'none';
        }
        if (!this.gleich(vorher, neu)) this.gewechselt(neu);
    }
}
