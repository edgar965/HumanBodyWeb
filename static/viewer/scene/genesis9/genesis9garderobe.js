import { escapeHtml } from '../utils.js';
import { Bildnachlader } from '../../gemeinsam/bildnachlader.js';
import { Bildauswahl } from '../../gemeinsam/bildauswahl.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Dazkleidung } from './dazkleidung.js';
import { Genesis9stueckregler } from './genesis9stueckregler.js';
import { Genesis9garderobekategorien } from './genesis9garderobekategorien.js';
import { Reiterzuordnung } from '../../gemeinsam/reiterzuordnung.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Stueckfarbe } from './stueckfarbe.js';
import { state } from '../state.js';

/**
 * Genesis9garderobe — Daz-Kleidung und -Haare einer Genesis-9-Figur (`Dazkleidung`: auch HumanBody).
 *
 * Die Liste ist der Ordner `People/Genesis 9/Clothing` und `…/Hair` der
 * Daz-Bibliothek (`Genesis9/garderobe.py`): jedes `wearable` eine Zeile mit
 * Häkchen, davor Daz' Vorschaubild (`<Name>.png` neben der `.duf`, nachgeladen
 * wie die MakeHuman-Stücke — Edgar 18.09.2026: „mach auch ein Icon in dem Tab"),
 * daneben die Farbvarianten des Produkts als Auswahl. Sie steht im Assets-Reiter
 * als eigener Bereich (Edgar, 17.09.2026: „machst Du einen extra Reiter dafür
 * bei Assets?", `Eigenschaftenbereiche.genesis9Garderobe`). Nur ein Stück, das nicht
 * zeigbar ist (dForce-Stranghaar ohne Flächen), steht ausgegraut da, mit Grund; der
 * Name trägt `stueckname` — als `<label>` in `.slider-row` las er sich sonst gesperrt.
 *
 * Anziehen holt alle Teile des Stücks auf der AKTUELLEN Reglerstellung (projiziert,
 * `G9folger`) und bindet sie an das Skelett der Figur; ein Reglerzug baut sie mit
 * (`Genesis9Modell.neuFormen`). Seit 18.09.2026 hat ein Stück neben der Farbvariante
 * bis zu drei Presets des Produkts, je Art eine Wahl: STIL (Morphe — Pixie: Jaunty,
 * Feathered …), POSE (dreht eigene Knochen — Eirgrids Zöpfe) und LÄNGE (skaliert sie).
 * REQUISITEN (`People/Genesis 9/Props`: Tubal-Waffen) hängen an einem Handknochen; ein
 * Stück mit Griffpose (`griff`) baut die Figur neu (Finger um den Griff, `anziehenMitGriff`).
 *
 * Die Gruppen sind seit 20.09.2026 Edgars Kategorien (`Genesis9garderobekategorien`:
 * Vorgabe aus Daz' Metadaten, Rechtsklick auf eine Zeile verschiebt). Ihr Kopf trägt
 * die Schrift von „Farbe / Material" (`aufklappkopf`, Edgar 21.09.2026: „die Schrift
 * der Kategorien soll so sein wie diese"); alle stehen ZU — bis auf die des Stücks,
 * das in der Szene gewählt ist (`state._selectedSubMesh`): die ist offen, seine Zeile
 * markiert, wie ein Klick über `Stueckmarkierung`.
 */
export class Genesis9garderobe {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    /** Die Preset-Arten eines Stücks (`Genesis9/garderobeeintrag.py`, `ARTEN`). */
    static STILARTEN = [['stil', 'Stil'], ['pose', 'Pose'], ['laenge', 'Länge']];
    /** Der Behälter im Assets-Reiter (`_genesis9_garderobe.html`). */
    static BEREICH = 'assets-genesis9-garderobe';

    /** Derselbe Katalog wie `Genesis9kleidung.anzeigename` (23.09.2026) — EIN
     *  Serverlauf statt zwei (Assets-Reiter UND Schwebeanzeige fragten ihn
     *  vorher unabhängig voneinander ab). */
    static liste() {
        return Genesis9kleidung.stuecke();
    }

    static async fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.dataset.figur = inst.id;      // wer zuletzt anfragt, gewinnt (Wettlauf beim Laden)
        behaelter.innerHTML = '<div class="gedaempft">Lade Garderobe …</div>';
        const [stuecke, stand] = await Promise.all([Genesis9garderobe.liste(),
                                                    Genesis9garderobekategorien.stand()]);
        if (behaelter.dataset.figur !== inst.id) return;
        behaelter.innerHTML = '';
        if (!stuecke.length) {
            behaelter.innerHTML = '<div class="gedaempft">Keine Daz-Kleidung gefunden.</div>';
            return;
        }
        const neuzeichnen = () => Genesis9garderobe.fuellen(inst, behaelter);
        const gewaehlt = Genesis9garderobe.gewaehltesStueck(inst);
        for (const [titel, eigene] of Genesis9garderobekategorien.gruppen(stuecke, stand)) {
            const kasten = document.createElement('details');
            kasten.className = 'g9-kategorie';
            kasten.open = Genesis9garderobekategorien.offen(titel, eigene.some(s => s.id === gewaehlt));
            kasten.innerHTML = `<summary class="aufklappkopf">${escapeHtml(titel)} `
                + `<span class="gedaempft">(${eigene.length})</span></summary>`;
            // Gemerkt wird nur Edgars Klick — `toggle` feuert auch, wenn `Stueckmarkierung`
            // die Kategorie des angeklickten Stücks öffnet, und die bliebe dann für immer offen.
            kasten.querySelector('summary').addEventListener('click',
                () => Genesis9garderobekategorien.merken(titel, !kasten.open));
            for (const stueck of eigene) {
                const zeile = Genesis9garderobe._zeile(inst, stueck, neuzeichnen);
                if (stueck.id === gewaehlt) zeile.classList.add('selected');
                kasten.appendChild(zeile);
                if (stueck.regler?.length && stueck.zeigbar) {
                    kasten.appendChild(Genesis9stueckregler.bauen(inst, stueck,
                        () => ({ ...(Dazkleidung.kleidung(inst)[stueck.id] || {}) })));
                }
            }
            behaelter.appendChild(kasten);
        }
    }

    /** Die Kennung des Daz-Stücks, das in der Szene auf DIESER Figur gewählt ist — sonst null
     *  (`Reiterzuordnung.stueckVon`: `angie_jeans/2` und `daz_angie_jeans/2` → `angie_jeans`). */
    static gewaehltesStueck(inst) {
        const ziel = state._selectedSubMesh;
        if (!ziel || ziel.charId !== inst.id) return null;
        const stueck = Reiterzuordnung.stueckVon(ziel.key);
        return stueck?.liste === 'daz' ? stueck.kennung : null;
    }

    /** `Genesis 8 Female` → `G8`, `Genesis` → `G1` — wie `G9fremdstueck.kurz`. */
    static kurz(herkunft) {
        const treffer = /Genesis(?: (\d))?/.exec(herkunft || '');
        return treffer ? `G${treffer[1] || '1'}` : '';
    }

    static _zeile(inst, stueck, neuzeichnen) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.inst = inst;
        Genesis9garderobekategorien.menue(zeile, stueck, neuzeichnen);
        const herkunft = stueck.herkunft || (stueck.basis ? 'Genesis 8' : '');
        zeile.title = stueck.zeigbar
            ? (stueck.knochen ? `${stueck.datei} — an ${stueck.knochen}` : stueck.datei)
                + (herkunft ? ` — ${herkunft}, per Auto-Fit auf Genesis 9` : '')
            : stueck.hinweis;
        const getragen = Boolean(Dazkleidung.kleidung(inst)[stueck.id]);
        const kennung = `g9-kleid-${stueck.id}`;
        zeile.innerHTML = `
            <input type="checkbox" id="${kennung}" ${getragen ? 'checked' : ''}
                   ${stueck.zeigbar ? '' : 'disabled'}>
            <label for="${kennung}" class="stueckname${stueck.zeigbar ? '' : ' gedaempft'}">${
                escapeHtml(stueck.name)}${
                herkunft ? ` <span class="gedaempft">${Genesis9garderobe.kurz(herkunft)}</span>` : ''}</label>`;
        const haken = zeile.querySelector('input');
        if (stueck.vorschau) {
            const bild = document.createElement('img');
            // `daz-vorschau`: heller Grund wie in Daz' Bibliothek — die LVA-Bilder
            // sind durchsichtig und auf der dunklen Seite fast schwarz (19.09.2026).
            bild.className = 'garment-thumb daz-vorschau';
            bild.alt = '';
            Bildnachlader.vormerken(bild,
                `${Genesis9garderobe.ADRESSE}${encodeURIComponent(stueck.id)}/vorschau/`);
            haken.after(bild);
        }
        const bisher = Dazkleidung.kleidung(inst)[stueck.id] || {};
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
        // Eigene Farbe (24.09.2026, „kann die Farbe der Haare auch angepasst werden?"):
        // getragen sofort, sonst gemerkt bis zum Anziehen (`werte`).
        felder.farbe = Stueckfarbe.feld({ inst, kennung: stueck.id, wert: bisher.farbe || '' });
        if (stueck.zeigbar) zeile.appendChild(felder.farbe);
        haken.addEventListener('change', () => {
            if (haken.checked) Genesis9garderobe._anziehen(inst, stueck.id, werte());
            else Genesis9garderobe._ausziehen(inst, stueck.id);
        });
        return zeile;
    }

    /** `{variante, stil, stile, regler, farbe, gruppenfarben, griff, knochen}` aus den Feldern der Zeile. */
    static werte(stueck, wahl, felder, inst) {
        const stile = {};
        for (const art of ['pose', 'laenge']) {
            if (felder[art]?.value) stile[art] = felder[art].value;
        }
        const bisher = Dazkleidung.kleidung(inst)[stueck.id] || {};
        return {
            variante: wahl?.value || '', stil: felder.stil?.value || '', stile,
            regler: { ...(bisher.regler || {}) },
            farbe: felder.farbe?.wert ?? (bisher.farbe || ''),
            gruppenfarben: { ...(bisher.gruppenfarben || {}) },
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
            () => Dazkleidung.anziehenAuf(inst, kennung, werte),
            () => fn.updateVertexCount?.());
    }

    static _ausziehen(inst, kennung) {
        Genesis9lauf.planen(inst,
            () => Dazkleidung.ausziehenAuf(inst, kennung),
            () => fn.updateVertexCount?.());
    }

    /**
     * Die Liste neu zeichnen, nachdem ein Stück auf einem ANDEREN Weg von der
     * Figur genommen wurde — Entf-Taste oder Kreuz in „Objekte" laufen über
     * `_removeSubMesh` (`teilnetz_auswahl.js`), nicht über das Häkchen hier.
     * Ohne diesen Aufruf blieb die Zeile angehakt, obwohl das Stück weg war
     * (Edgar, 25.09.2026: „erscheint es links bei den Assets noch angehakt").
     */
    static aktualisieren(inst) {
        return Genesis9garderobe.fuellen(inst, document.getElementById(Genesis9garderobe.BEREICH));
    }
}

fn.refreshGenesis9Garderobe = Genesis9garderobe.aktualisieren;
