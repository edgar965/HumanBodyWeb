import { state } from './state.js';
import { setSlider, bindSlider } from './utils.js';
import { Bildnachlader } from '../gemeinsam/bildnachlader.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Smplkleidernetz } from './smpl_kleidernetz.js';

/**
 * Smplkleiderliste — der SMPL-Kleiderkatalog samt Bedienfeld.
 *
 * Herausgelöst aus `smpl.js` (393 Zeilen). Die Zeilen tragen dieselben Klassen
 * wie der Katalog der Modellseite (`garment-item`, `garment-thumb`,
 * `garment-name` in `css/animationsbaum.css`) — vorher standen dort dieselben
 * Stilangaben ein zweites Mal als `style.cssText` im JavaScript.
 *
 * Ein Häkchen markiert die Stücke, die gerade in der Szene liegen; deshalb wird
 * die Liste nach jedem Laden und Entfernen neu gezeichnet.
 */
export class Smplkleiderliste {

    static BEHAELTER = 'smpl-garment-list';
    static KATEGORIEWAHL = 'smpl-garment-category';
    static FARBE = 'smpl-garment-color';
    static RAUHEIT = 'smpl-garment-roughness';

    constructor() {
        this.behaelter = document.getElementById(Smplkleiderliste.BEHAELTER);
    }

    static zeichnen() {
        return new Smplkleiderliste().zeichnen();
    }

    // ------------------------------------------------------------- Bedienfeld

    /** Regler und Knöpfe binden, Katalog holen, Liste zeichnen. */
    static async aufbauen() {
        if (!document.getElementById('garment-smpl-panel')) return;
        bindSlider(Smplkleiderliste.RAUHEIT, `${Smplkleiderliste.RAUHEIT}-val`,
                   wert => (wert / 100).toFixed(2));
        Smplkleiderliste._werkstoffBinden();
        Smplkleiderliste._knoepfeBinden();
        document.getElementById(Smplkleiderliste.KATEGORIEWAHL)
            ?.addEventListener('change', () => Smplkleiderliste.zeichnen());
        await Smplkleiderliste.katalogLaden();
    }

    /** Farbe und Rauheit wirken sofort auf das gewählte Netz. */
    static _werkstoffBinden() {
        const gewaehltes = () => state.smplGarmentMeshes[state._smplSelectedId];
        const farbe = document.getElementById(Smplkleiderliste.FARBE);
        farbe?.addEventListener('input', () => {
            gewaehltes()?.material.color.set(farbe.value);
        });
        const rauheit = document.getElementById(Smplkleiderliste.RAUHEIT);
        rauheit?.addEventListener('input', () => {
            const netz = gewaehltes();
            if (netz) netz.material.roughness = rauheit.value / 100;
        });
    }

    static _knoepfeBinden() {
        document.getElementById('smpl-garment-load')?.addEventListener(
            'click', () => Smplkleiderliste.laden(state._smplSelectedId));
        document.getElementById('smpl-garment-remove')?.addEventListener(
            'click', () => Smplkleiderliste.entfernen(state._smplSelectedId));
        document.getElementById('smpl-garment-remove-all')?.addEventListener(
            'click', () => Smplkleiderliste.alleEntfernen());
    }

    static async katalogLaden() {
        try {
            const daten = await Serverabruf.json('/api/smpl/garment/library/');
            state._smplCatalog = [];
            Smplkleiderliste._kategorien(daten.categories);
            for (const kategorie of Object.keys(daten.garments || {})) {
                state._smplCatalog.push(...daten.garments[kategorie]);
            }
        } catch (fehler) {
            Protokoll.fehler('smpl', 'Katalog nicht ladbar', fehler);
            return;
        }
        Smplkleiderliste.zeichnen();
    }

    static _kategorien(namen) {
        const wahl = document.getElementById(Smplkleiderliste.KATEGORIEWAHL);
        if (!wahl || !namen) return;
        for (const name of namen) {
            const eintrag = document.createElement('option');
            eintrag.value = name;
            eintrag.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            wahl.appendChild(eintrag);
        }
    }

    // ----------------------------------------------------------------- Aktionen

    static async laden(kennung) {
        if (!kennung) return;
        const knopf = document.getElementById('smpl-garment-load');
        if (knopf) {
            knopf.disabled = true;
            knopf.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Laden...';
        }
        try {
            if (await Smplkleidernetz.laden(kennung)) Smplkleiderliste.zeichnen();
        } finally {
            if (knopf) {
                knopf.disabled = false;
                knopf.innerHTML = '<i class="fas fa-plus"></i> Laden';
            }
        }
    }

    static entfernen(kennung) {
        if (!kennung || !state.smplGarmentMeshes[kennung]) return;
        Smplkleidernetz.entfernen(kennung);
        Smplkleiderliste.zeichnen();
    }

    static alleEntfernen() {
        for (const kennung of Object.keys(state.smplGarmentMeshes)) {
            Smplkleidernetz.entfernen(kennung);
        }
        Smplkleiderliste.zeichnen();
    }

    // -------------------------------------------------------------------- Liste

    zeichnen() {
        if (!this.behaelter) return;
        const wahl = document.getElementById(Smplkleiderliste.KATEGORIEWAHL)?.value;
        const eintraege = wahl
            ? state._smplCatalog.filter(eintrag => eintrag.category === wahl)
            : state._smplCatalog;
        if (eintraege.length === 0) {
            this.behaelter.innerHTML =
                '<div class="leer-hinweis">Keine SMPL-Garments gefunden</div>';
            return;
        }
        const nachKategorie = {};
        for (const eintrag of eintraege) {
            (nachKategorie[eintrag.category] ||= []).push(eintrag);
        }
        this.behaelter.innerHTML = '';
        for (const name of Object.keys(nachKategorie).sort()) {
            this.behaelter.appendChild(
                this._kategorie(name, nachKategorie[name]));
        }
    }

    _kategorie(name, eintraege) {
        const kasten = document.createElement('div');
        kasten.className = 'anim-category';
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
        if (eintrag.id === state._smplSelectedId) zeile.classList.add('active');
        if (eintrag.has_thumb) {
            const bild = document.createElement('img');
            bild.alt = eintrag.name;
            bild.className = 'garment-thumb';
            // Erst laden, wenn die Zeile sichtbar wird.
            Bildnachlader.vormerken(bild, `/api/smpl/garment/thumb/${eintrag.id}/`);
            zeile.appendChild(bild);
        }
        const name = document.createElement('span');
        name.className = 'garment-name';
        name.textContent = eintrag.name;
        zeile.appendChild(name);
        if (state.smplGarmentMeshes[eintrag.id]) {
            const haken = document.createElement('span');
            haken.className = 'garment-haken';
            haken.textContent = '✓';
            zeile.appendChild(haken);
        }
        zeile.addEventListener('click', () => this._waehlen(eintrag, zeile));
        zeile.addEventListener('dblclick', () => {
            state._smplSelectedId = eintrag.id;
            Smplkleiderliste.laden(eintrag.id);
        });
        return zeile;
    }

    /** Auswählen — und bei geladenen Stücken die Regler auf ihr Material. */
    _waehlen(eintrag, zeile) {
        state._smplSelectedId = eintrag.id;
        this.behaelter.querySelectorAll('.anim-item')
            .forEach(el => el.classList.remove('active'));
        zeile.classList.add('active');
        const netz = state.smplGarmentMeshes[eintrag.id];
        if (!netz) return;
        const farbe = document.getElementById(Smplkleiderliste.FARBE);
        if (farbe) farbe.value = '#' + netz.material.color.getHexString();
        setSlider(Smplkleiderliste.RAUHEIT,
                  Math.round(netz.material.roughness * 100),
                  wert => (wert / 100).toFixed(2));
    }
}
