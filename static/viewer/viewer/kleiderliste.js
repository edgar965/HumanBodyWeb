import { state } from './state.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';
import { Kleiderregler } from './kleiderregler.js';

/**
 * Kleiderliste — der Katalog der Modellseite als aufklappbare Liste.
 *
 * Herausgelöst aus `garment_liste.js` (229 Zeilen). Zwei Dinge:
 *
 * 1. **Vorschaubilder werden erst beim Aufklappen geladen** (`Bildnachlader`).
 *    Der Katalog hat mehrere hundert Einträge; alle Bilder sofort zu holen ist
 *    beim Seitenaufbau eine Anfragenlawine.
 * 2. **Ein Klick füllt die Regler** — aus dem gespeicherten Stand, wenn das
 *    Kleidungsstück schon angezogen ist, sonst aus den Katalogvorgaben. Beides
 *    steht in `Kleiderregler`, nicht hier.
 */
export class Kleiderliste {

    static BEHAELTER = 'garment-list';
    static KATEGORIEWAHL = 'garment-category';
    static MUSTERKNOPF = 'garment-edit-pattern';
    static MUSTERQUELLE = 'pattern-editor';

    constructor() {
        this.behaelter = document.getElementById(Kleiderliste.BEHAELTER);
    }

    static zeichnen() {
        return new Kleiderliste().zeichnen();
    }

    zeichnen() {
        if (!this.behaelter) return;
        const eintraege = this.gefiltert();
        if (eintraege.length === 0) {
            this.behaelter.innerHTML =
                '<div class="leer-hinweis">Keine Garments gefunden</div>';
            return;
        }
        this.behaelter.innerHTML = '';
        const nachKategorie = this.gruppiert(eintraege);
        for (const kategorie of Object.keys(nachKategorie).sort()) {
            this.behaelter.appendChild(
                this._kategorie(kategorie, nachKategorie[kategorie]));
        }
    }

    gefiltert() {
        const wahl = document.getElementById(Kleiderliste.KATEGORIEWAHL)?.value;
        if (!wahl) return state._garmentCatalog;
        return state._garmentCatalog.filter(eintrag => eintrag.category === wahl);
    }

    gruppiert(eintraege) {
        const nachKategorie = {};
        for (const eintrag of eintraege) {
            (nachKategorie[eintrag.category] ||= []).push(eintrag);
        }
        return nachKategorie;
    }

    _kategorie(name, eintraege) {
        const kasten = document.createElement('div');
        kasten.className = 'anim-category open';
        const kopf = document.createElement('div');
        kopf.className = 'anim-category-header';
        kopf.innerHTML = `<span class="cat-chevron">&#9654;</span> `
            + `${name.toUpperCase()} <span class="cat-count">${eintraege.length}</span>`;
        kopf.addEventListener('click', () => kasten.classList.toggle('open'));
        kasten.appendChild(kopf);
        const koerper = document.createElement('div');
        koerper.className = 'anim-category-body';
        for (const eintrag of eintraege) koerper.appendChild(this._zeile(eintrag));
        kasten.appendChild(koerper);
        return kasten;
    }

    _zeile(eintrag) {
        const zeile = document.createElement('div');
        zeile.className = 'anim-item garment-item';
        if (eintrag.id === state.selectedGarmentId) zeile.classList.add('active');
        if (eintrag.has_thumb) zeile.appendChild(this._bild(eintrag));
        const name = document.createElement('span');
        name.className = 'garment-name';
        name.textContent = eintrag.name;
        zeile.appendChild(name);
        zeile.dataset.garmentId = eintrag.id;
        zeile.addEventListener('click', () => this.waehlen(eintrag, zeile));
        return zeile;
    }

    _bild(eintrag) {
        const bild = document.createElement('img');
        bild.alt = eintrag.name;
        bild.className = 'garment-thumb';
        Bildnachlader.vormerken(bild,
                                `/api/character/garment/thumb/${eintrag.id}/`);
        return bild;
    }

    // ------------------------------------------------------------------ Auswahl

    waehlen(eintrag, zeile) {
        state.selectedGarmentId = eintrag.id;
        this.behaelter.querySelectorAll('.anim-item')
            .forEach(el => el.classList.remove('active'));
        zeile.classList.add('active');
        const zustand = state.garmentState[eintrag.id];
        if (zustand && state.garmentMeshes[eintrag.id]) {
            Kleiderregler.fuellen(zustand);
        } else {
            Kleiderregler.vorgaben(eintrag);
        }
        Kleiderliste.musterknopf(eintrag);
    }

    /** „Schnittmuster bearbeiten" gibt es nur für selbst gezeichnete Teile. */
    static musterknopf(eintrag) {
        const knopf = document.getElementById(Kleiderliste.MUSTERKNOPF);
        if (!knopf) return;
        knopf.style.display =
            eintrag.source === Kleiderliste.MUSTERQUELLE ? '' : 'none';
    }
}
