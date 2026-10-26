import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Dazkleidung } from './dazkleidung.js';
import { Genesis9stueckregler } from './genesis9stueckregler.js';
import { Stueckfarbe } from './stueckfarbe.js';
import { Stueckstoff } from './stueckstoff.js';
import { Dazschnittfelder } from '../../gemeinsam/dazschnittfelder.js';
import { Dazschnittwerte } from '../../gemeinsam/dazschnittwerte.js';
import { Dazschnitt } from '../../gemeinsam/dazschnitt.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Dazeigenblock — der Knopf „Eigen …“ an jedem Genesis-Kleidungsstück (Daz) und der Block, den er öffnet (Stufe K2c, 25.10.2026, Edgar: „bei allen
 * Eigenschaften eines Genesis-Kleidungsstückes einen Regler, der diese ‚Eigen‘-Regler aufmacht?“ — „Mach weiter, alle Aufgaben“).
 *
 * DERSELBE AUFBAU wie beim eigenen Stück (`Genesis9eigenkleidkasten`, Blöcke Säume · Kragen · Sitz · Brücke · Stoff · Textur), soweit er an einem fertigen Stück
 * Sinn ergibt:
 *   Ausschnitt, Säume     NEU — nur Wegschneiden (`Dazschnitt`; Felder `Dazschnittfelder`, je Kategorie nur die passenden); Zug = Uniforms, Loslassen = Index und
 *                         Hautverdeckung
 *   Kragen und Knopfleiste NEU — nur Abziehbild (Shader), keine Geometrie
 *   Sitz                  die vorhandenen Regler `passform:*` und die Drapierung über dem Geograft (`drapierung:*`) — eingebunden, nicht neu gebaut
 *   Brücke über Mulden    `drapierung:bruecke_*` (Server, `G9muldendrapierung`) — eingebunden über `Genesis9stueckregler._zeile` (ein Zug zieht das Stück neu an)
 *   Stoff                 `Stueckstoff.felder` und die Faltenkarte `bild.falten_*` — eingebunden
 *   Textur                Farbe des Stücks (`Stueckfarbe`)
 * Der Block entsteht erst beim ersten Öffnen. Nur an Genesis-9-Figuren (die Körperkoordinaten gibt es nur dort).
 */
export class Dazeigenblock {

    /** Bekommt dieses Stück den Knopf? Echte Kleidungsstücke, keine Sammeleinträge, keine Anatomie. */
    static passt(inst, stueck) {
        return inst?.quelle === 'genesis9' && stueck?.art === 'kleidung' && !stueck.anatomie && !stueck.mischbar
            && !/^(haar_generisch|kleidung_generisch)/.test(stueck.id || '');
    }

    /** Knopf und (verborgener) Block als ein Element. `werteLesen` wie bei `Genesis9stueckregler` (Werte des getragenen Stücks als Kopie). */
    static knopf(inst, stueck, werteLesen) {
        const huelle = document.createElement('div');
        huelle.className = 'daz-eigen';
        huelle.dataset.dazEigen = stueck.id;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'einstellung-knopf daz-eigen-knopf';
        knopf.setAttribute('aria-expanded', 'false');
        knopf.textContent = 'Eigen …';
        knopf.title = 'Ausschnitt und Säume (nur wegschneiden), Kragen als Abziehbild, Brücke über Mulden, Sitz und Stoff';
        const block = document.createElement('div');
        block.className = 'genesis9-stueckregler daz-eigen-block';
        block.hidden = true;
        knopf.addEventListener('click', () => {
            block.hidden = !block.hidden;
            knopf.classList.toggle('offen', !block.hidden);
            knopf.setAttribute('aria-expanded', String(!block.hidden));
            if (!block.hidden && !block.childElementCount) Dazeigenblock._bloecke(block, inst, stueck, werteLesen);
        });
        huelle.append(knopf, block);
        return huelle;
    }

    static _titel(block, text) {
        block.insertAdjacentHTML('beforeend', `<div class="gedaempft g9-eigenregler-unter">${escapeHtml(text)}</div>`);
    }

    static _bloecke(block, inst, stueck, werteLesen) {
        const meldung = document.createElement('div');
        meldung.className = 'gedaempft daz-eigen-meldung';
        meldung.textContent = Dazkleidung.kleidung(inst)[stueck.id] ? 'Schneidet nur weg — angebaut wird nichts.' : 'Erst anziehen: die Werte gelten dem getragenen Stück.';
        block.appendChild(meldung);
        const felder = Dazschnittfelder.fuer(stueck.kategorie);
        for (const [schluessel, titel] of Dazschnittfelder.BLOECKE) {
            const eigene = felder.filter(f => f.block === schluessel);
            if (!eigene.length) continue;
            Dazeigenblock._titel(block, titel);
            for (const f of eigene) block.appendChild(f.wahl ? Dazeigenblock._wahl(inst, stueck.id, f, meldung) : Dazeigenblock._schieber(inst, stueck.id, f, meldung));
        }
        const regler = stueck.regler || [];
        const zeilen = (titel, liste, zusatz = []) => {
            if (!liste.length && !zusatz.length) return;
            Dazeigenblock._titel(block, titel);
            for (const z of zusatz) block.appendChild(z);
            for (const r of liste) block.appendChild(Genesis9stueckregler._zeile(inst, stueck, r, werteLesen));
        };
        const name = r => String(r.name || '');
        zeilen('Sitz', regler.filter(r => name(r).startsWith('passform:') || (name(r).startsWith('drapierung:') && !name(r).startsWith('drapierung:bruecke_'))));
        zeilen('Brücke über Mulden', regler.filter(r => name(r).startsWith('drapierung:bruecke_')));
        zeilen('Stoff', regler.filter(r => /(^|\.)bild\.falten_/.test(name(r))), [Stueckstoff.felder(inst, stueck.id)]);
        const werte = Dazkleidung.kleidung(inst)[stueck.id] || {};
        const farbe = document.createElement('div');
        farbe.className = 'slider-row';
        farbe.innerHTML = '<label class="stueckname">Farbe des Stücks</label>';
        farbe.appendChild(Stueckfarbe.feld({ inst, kennung: stueck.id, wert: werte.farbe || '', titel: 'Farbe des Stücks' }));
        zeilen('Textur', [], [farbe]);
    }

    static _zeile(f, feld) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row daz-eigen-zeile';
        zeile.innerHTML = `<label title="${escapeHtml(f.hilfe || '')}">${escapeHtml(f.titel)}</label>`;
        feld.dataset.dazSchnitt = f.feld;
        feld.title = `${f.hilfe || f.titel} · Doppelklick: Vorgabe`;
        zeile.appendChild(feld);
        return zeile;
    }

    /** Die Werte des Stücks mit `feld` = `wert` (für die Vorschau im Zug). */
    static _mit(inst, kennung, feld, wert) {
        return { ...Dazschnittwerte.alle(Dazschnittwerte.regler(inst, kennung)), [feld]: wert };
    }

    static _vorschau(inst, kennung, feld, wert) {
        const werte = Dazeigenblock._mit(inst, kennung, feld, wert);
        if (!Dazschnitt.vorschau(inst, kennung, werte)) Dazschnitt.anwenden(inst, kennung, { werte, masken: false }).catch(f => Protokoll.warnung('Daz-Schnitt', f.message));
    }

    /** Loslassen: Wert in die Regler, Schnitt mit Index und Hautverdeckung; das Ergebnis steht in der Meldung. */
    static async _setzen(inst, kennung, f, wert, meldung) {
        if (!Dazschnittwerte.setzen(inst, kennung, f.feld, wert)) {
            meldung.textContent = 'Erst anziehen: die Werte gelten dem getragenen Stück.';
            return;
        }
        markDirty();
        try {
            const stand = await Dazschnitt.anwenden(inst, kennung);
            meldung.textContent = stand ? `${stand.entfernt} Dreiecke weggeschnitten · Haut darunter wird neu gerechnet` : 'Nur an Genesis-9-Figuren.';
        } catch (fehler) {
            meldung.textContent = fehler.message;
            Protokoll.fehler('Daz-Schnitt', `${kennung}: ${f.feld}`, fehler);
        }
    }

    static _schieber(inst, kennung, f, meldung) {
        const schieber = document.createElement('input');
        Object.assign(schieber, { type: 'range', min: f.min, max: f.max, step: f.schritt });
        schieber.value = Dazschnittwerte.wert(Dazschnittwerte.regler(inst, kennung), f.feld);
        const zeile = Dazeigenblock._zeile(f, schieber);
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-value';
        anzeige.textContent = Dazschnittwerte.anzeige(f, schieber.value);
        zeile.appendChild(anzeige);
        schieber.addEventListener('input', () => {
            anzeige.textContent = Dazschnittwerte.anzeige(f, schieber.value);
            Dazeigenblock._vorschau(inst, kennung, f.feld, Number(schieber.value));
        });
        schieber.addEventListener('change', () => Dazeigenblock._setzen(inst, kennung, f, Number(schieber.value), meldung));
        schieber.addEventListener('dblclick', () => {
            schieber.value = f.vorgabe;
            anzeige.textContent = Dazschnittwerte.anzeige(f, f.vorgabe);
            Dazeigenblock._setzen(inst, kennung, f, null, meldung);
        });
        return zeile;
    }

    static _wahl(inst, kennung, f, meldung) {
        const feld = document.createElement('select');
        feld.className = 'viewer-select hb-dehnt';
        f.wahl.forEach((name, i) => feld.add(new Option(name, String(i))));
        feld.value = String(Dazschnittwerte.wert(Dazschnittwerte.regler(inst, kennung), f.feld));
        const zeile = Dazeigenblock._zeile(f, feld);
        feld.addEventListener('change', () => Dazeigenblock._setzen(inst, kennung, f, Number(feld.value), meldung));
        return zeile;
    }
}
