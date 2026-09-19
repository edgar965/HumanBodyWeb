import { escapeHtml } from '../utils.js';
import { Bildnachlader } from '../../gemeinsam/bildnachlader.js';
import { Bildauswahl } from '../../gemeinsam/bildauswahl.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9stueckregler } from './genesis9stueckregler.js';

/**
 * Genesis9garderobe — die Daz-Kleidung und -Haare einer Genesis-9-Figur.
 *
 * Die Liste ist der Ordner `People/Genesis 9/Clothing` und `…/Hair` der
 * Daz-Bibliothek (`Genesis9/garderobe.py`): jedes `wearable` eine Zeile mit
 * Häkchen, davor Daz' Vorschaubild (`<Name>.png` neben der `.duf`, nachgeladen
 * wie die MakeHuman-Stücke — Edgar 18.09.2026: „mach auch ein Icon in dem Tab"),
 * daneben die Farbvarianten des Produkts als Auswahl. Sie steht im Assets-Reiter
 * als eigener Bereich (Edgar, 17.09.2026: „machst Du einen extra Reiter dafür
 * bei Assets?"), sichtbar nur bei einer Genesis-9-Figur
 * (`Eigenschaftenbereiche.genesis9Garderobe`). Nur ein Stück, das nicht zeigbar
 * ist (dForce-Stranghaar ohne Flächen), steht ausgegraut da, mit Grund; der Name
 * trägt `stueckname` — als `<label>` in `.slider-row` las er sich sonst gesperrt.
 *
 * Anziehen holt alle Teile des Stücks auf der AKTUELLEN Reglerstellung
 * (projiziert, `G9folger`) und bindet sie an das Skelett der Figur; ein
 * Reglerzug baut sie mit (`Genesis9Modell.neuFormen`). Seit 18.09.2026 hat
 * ein Stück neben der Farbvariante bis zu drei Presets des Produkts, je Art
 * eine Wahl: STIL (Morphe — Pixie: Jaunty, Feathered …), POSE (dreht eigene
 * Knochen — Eirgrids Zöpfe nach hinten, gespreizt) und LÄNGE (skaliert sie).
 * REQUISITEN (`People/Genesis 9/Props`: Tubal-Waffen) hängen an einem
 * Handknochen; ein Stück mit Griffpose (`griff`) baut die Figur neu, damit
 * sich die Finger um den Griff schließen (`anziehenMitGriff`).
 */
export class Genesis9garderobe {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    static ARTEN = [['kleidung', 'Kleidung'], ['haar', 'Haare'], ['requisit', 'Requisiten']];
    /** Die Preset-Arten eines Stücks (`Genesis9/garderobeeintrag.py`, `ARTEN`). */
    static STILARTEN = [['stil', 'Stil'], ['pose', 'Pose'], ['laenge', 'Länge']];
    /** Der Behälter im Assets-Reiter (`_genesis9_garderobe.html`). */
    static BEREICH = 'assets-genesis9-garderobe';
    static _liste = null;

    static async liste() {
        if (!Genesis9garderobe._liste) {
            const daten = await Serverabruf.json(Genesis9garderobe.ADRESSE);
            Genesis9garderobe._liste = daten.stuecke || [];
        }
        return Genesis9garderobe._liste;
    }

    static async fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '<div class="gedaempft">Lade Garderobe …</div>';
        const stuecke = await Genesis9garderobe.liste();
        behaelter.innerHTML = '';
        if (!stuecke.length) {
            behaelter.innerHTML = '<div class="gedaempft">Keine Daz-Kleidung gefunden.</div>';
            return;
        }
        for (const [art, titel] of Genesis9garderobe.ARTEN) {
            const eigene = stuecke.filter(s => s.art === art);
            if (!eigene.length) continue;
            const kasten = document.createElement('details');
            kasten.className = 'uma-gruppe';
            kasten.open = art === 'kleidung';
            kasten.innerHTML = `<summary>${titel} `
                + `<span class="gedaempft">(${eigene.length})</span></summary>`;
            for (const stueck of eigene) {
                kasten.appendChild(Genesis9garderobe._zeile(inst, stueck));
                if (stueck.regler?.length && stueck.zeigbar) {
                    kasten.appendChild(Genesis9stueckregler.bauen(inst, stueck,
                        () => ({ ...(inst.kleidung?.[stueck.id] || {}) })));
                }
            }
            behaelter.appendChild(kasten);
        }
    }

    static _zeile(inst, stueck) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.inst = inst;
        zeile.title = stueck.zeigbar
            ? (stueck.knochen ? `${stueck.datei} — an ${stueck.knochen}` : stueck.datei)
                + (stueck.basis ? ' — Genesis 8, per Auto-Fit auf Genesis 9' : '')
            : stueck.hinweis;
        const getragen = Boolean(inst.kleidung?.[stueck.id]);
        const kennung = `g9-kleid-${stueck.id}`;
        zeile.innerHTML = `
            <input type="checkbox" id="${kennung}" ${getragen ? 'checked' : ''}
                   ${stueck.zeigbar ? '' : 'disabled'}>
            <label for="${kennung}" class="stueckname${stueck.zeigbar ? '' : ' gedaempft'}">${
                escapeHtml(stueck.name)}${
                stueck.basis ? ' <span class="gedaempft">G8</span>' : ''}</label>`;
        const haken = zeile.querySelector('input');
        if (stueck.vorschau) {
            const bild = document.createElement('img');
            bild.className = 'garment-thumb';
            bild.alt = '';
            Bildnachlader.vormerken(bild,
                `${Genesis9garderobe.ADRESSE}${encodeURIComponent(stueck.id)}/vorschau/`);
            haken.after(bild);
        }
        const bisher = inst.kleidung?.[stueck.id] || {};
        const werte = () => Genesis9garderobe.werte(stueck, wahl, felder, inst);
        // Die Farbvarianten mit Daz' Vorschaubild je Eintrag (`Bildauswahl`,
        // 18.09.2026 nachts: „in der Combo box die Farben / icons").
        const wahl = Genesis9garderobe._auswahl(zeile, stueck, stueck.varianten, 'Standard',
            bisher.variante || '', haken, () => werte(),
            v => (v.id === '' ? stueck.vorschau : v.vorschau)
                ? `${Genesis9garderobe.ADRESSE}${encodeURIComponent(stueck.id)}/vorschau/`
                  + (v.id ? `?variante=${encodeURIComponent(v.id)}` : '')
                : null);
        const felder = {};
        for (const [art, titel] of Genesis9garderobe.STILARTEN) {
            const eintraege = (stueck.stile || []).filter(s => (s.art || 'stil') === art);
            const vorgabe = art === 'stil' ? (bisher.stil || '') : (bisher.stile?.[art] || '');
            felder[art] = Genesis9garderobe._auswahl(zeile, stueck, eintraege, titel, vorgabe,
                                                    haken, () => werte());
        }
        haken.addEventListener('change', () => {
            if (haken.checked) Genesis9garderobe._anziehen(inst, stueck.id, werte());
            else Genesis9garderobe._ausziehen(inst, stueck.id);
        });
        return zeile;
    }

    /** `{variante, stil, stile: {pose, laenge}, regler, griff, knochen}` aus den Feldern der Zeile. */
    static werte(stueck, wahl, felder, inst) {
        const stile = {};
        for (const art of ['pose', 'laenge']) {
            if (felder[art]?.value) stile[art] = felder[art].value;
        }
        return {
            variante: wahl?.value || '', stil: felder.stil?.value || '', stile,
            regler: { ...(inst.kleidung?.[stueck.id]?.regler || {}) },
            griff: Boolean(stueck.griff),
            // Eigene Knochen (Eirgrid: 14 Zöpfe) — das Stück hängt im Browser-Skelett.
            knochen: Boolean(stueck.eigene_knochen),
        };
    }

    /**
     * Eine Auswahl (Variante oder Stil) in die Zeile — oder null, wenn es nichts
     * zu wählen gibt. Mit `bild` (Adresse je Eintrag) eine `Bildauswahl`, sonst
     * ein `<select>`; beide antworten auf `.value` und `change`.
     */
    static _auswahl(zeile, stueck, eintraege, leerText, vorgabe, haken, werte, bild = null) {
        if (!eintraege?.length) return null;
        const alle = [{ id: '', name: leerText }, ...eintraege];
        let feld;
        if (bild) {
            feld = Bildauswahl.bauen(alle, vorgabe, bild);
        } else {
            feld = document.createElement('select');
            for (const v of alle) {
                const option = document.createElement('option');
                option.value = v.id;
                option.textContent = v.name;
                option.selected = v.id === vorgabe;
                feld.appendChild(option);
            }
        }
        feld.classList.add('hb-dehnt');
        feld.disabled = !stueck.zeigbar;
        feld.addEventListener('change', () => {
            if (haken.checked) Genesis9garderobe._anziehen(zeile.inst, stueck.id, werte());
        });
        zeile.appendChild(feld);
        return feld;
    }

    static _anziehen(inst, kennung, werte) {
        Genesis9lauf.planen(inst,
            () => inst.anziehenMitGriff(kennung, werte),
            () => fn.updateVertexCount?.());
    }

    static _ausziehen(inst, kennung) {
        Genesis9lauf.planen(inst,
            () => inst.ausziehen(kennung),
            () => fn.updateVertexCount?.());
    }
}
