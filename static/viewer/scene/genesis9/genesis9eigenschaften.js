import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';
import { Genesis9garderobe } from './genesis9garderobe.js';
import { Genesis9posen } from './genesis9posen.js';

/**
 * Genesis9eigenschaften — der Eigenschaften-Reiter einer Genesis-9-Figur.
 *
 * Was diese Figur hat (18.09.2026): Daz' eigene Formregler in vier Bereichen
 * (Figur, Körper, Kopf, Mimik — `Genesis9/reglerplan.py`, 352 von 1.503+
 * Kanälen; der Rest sind Knochen-Posensteuerungen und Verstecktes), Hautsätze
 * und Augen der Starter Essentials und der Charakterordner, Brauenstil,
 * Wimpern, Nagellack und Schminke je Kategorie (`praesets`) sowie Daz-Posen
 * und -Ausdrücke (`genesis9posen.js`). Die Daz-Garderobe
 * (`genesis9garderobe.js`) füllt den Assets-Reiter.
 *
 * Der Reglerplan kommt EINMAL vom Server und wird hier gemerkt: Er hängt
 * nicht an der Figur, sondern an der Bibliothek.
 *
 * BEIM ZIEHEN WIRD GERECHNET, ABER ENTPRELLT (`genesis9lauf.js`): Ein
 * Reglerzug baut Körper, Anhänge UND Kleidung neu — 0,1 s Server plus
 * Übertragung (27.087 Punkte); während ein Lauf unterwegs ist, wird nur
 * der Wunsch gemerkt, sonst überholten sich die Antworten.
 */
export class Genesis9eigenschaften {

    static BEREICH = 'prop-genesis9-section';
    static ADRESSE = '/api/character/genesis9-figur/regler/';
    static _plan = null;

    static async fuellen(inst) {
        const bereich = document.getElementById(Genesis9eigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        Genesis9eigenschaften._kopf(inst);
        const plan = await Genesis9eigenschaften.plan();
        Genesis9eigenschaften._haut(inst, plan);
        await Genesis9posen.fuellen(inst);
        Genesis9eigenschaften._regler(inst, plan);
        // Die Garderobe steht im Assets-Reiter (`_genesis9_garderobe.html`,
        // Edgar 17.09.2026: „machst Du einen extra Reiter dafür bei Assets?").
        await Genesis9garderobe.fuellen(inst,
            document.getElementById(Genesis9garderobe.BEREICH));
    }

    /** HEISST `leeren`, WEIL `properties.js` SO RUFT (siehe `umapythoneigenschaften.js`). */
    static leeren() {
        document.getElementById(Genesis9eigenschaften.BEREICH)
            ?.classList.add('hb-versteckt');
    }

    static async plan() {
        if (!Genesis9eigenschaften._plan) {
            Genesis9eigenschaften._plan = await Serverabruf.json(
                Genesis9eigenschaften.ADRESSE);
        }
        return Genesis9eigenschaften._plan;
    }

    // ------------------------------------------------------------- Anzeige

    static _kopf(inst) {
        const feld = document.getElementById('prop-genesis9-kopf');
        if (!feld) return;
        const wirksam = Object.keys(inst.morphwerte || {}).length;
        feld.innerHTML = `<strong>${escapeHtml(inst.presetName)}</strong> · `
            + `${Number(inst.punktzahl || 0).toLocaleString()} Punkte · `
            + `SubD ${inst.stufen || 0} (${Number(inst.browserpunkte || 0).toLocaleString()}) · `
            + `${((inst.hoehe || 0) * 100).toFixed(1)} cm · ${wirksam} Morphs wirksam`;
    }

    // ---------------------------------------------------------------- Haut

    static _haut(inst, plan) {
        const behaelter = document.getElementById('prop-genesis9-haut');
        if (!behaelter) return;
        behaelter.innerHTML = '';
        behaelter.appendChild(Genesis9eigenschaften._wahl('Haut',
            [{ id: '', name: 'Wie im Katalog' },
             ...(plan.haut || []).map(h => ({ id: h.id, name: `${h.name} (${h.geschlecht})` }))],
            inst.haut || '',
            wert => Genesis9lauf.planen(inst, () => inst.hautSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst))));
        behaelter.appendChild(Genesis9eigenschaften._wahl('Augen',
            (plan.augen || []).map(a => ({ id: a.id, name: a.name })),
            inst.augen || '01',
            wert => Genesis9lauf.planen(inst, () => inst.augenSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst))));
        Genesis9eigenschaften._brauen(inst, plan, behaelter);
        // Wimpern, Nagellack und Schminke (18.09.2026): je Kategorie ein Preset
        // aus den Charakterordnern und dem Daz-Makeup-System (`Genesis9/schminke.py`).
        for (const kategorie of plan.praesets || []) {
            behaelter.appendChild(Genesis9eigenschaften._wahl(kategorie.name,
                [{ id: '', name: '—' }, ...kategorie.eintraege],
                inst.praesets?.[kategorie.kategorie] || '',
                wert => Genesis9lauf.planen(inst,
                    () => inst.praesetSetzen(kategorie.kategorie, wert),
                    () => Genesis9eigenschaften._kopf(inst))));
        }
    }

    /**
     * Brauen (18.09.2026): 12 Kartenstile, 9 Faserstile (`Genesis9/brauen.py`),
     * die Farbliste hängt an der Art — beim Wechsel der Art fällt eine Farbe,
     * die es dort nicht gibt, auf die Vorgabe zurück.
     */
    static _brauen(inst, plan, behaelter) {
        const stile = plan.brauenstile || [];
        if (!stile.length) return;
        const artVon = stil => (stile.find(s => s.id === stil) || stile[0]).art;
        const farben = art => (plan.brauenfarben || {})[art] || plan.brauen || [];
        const farbwahl = () => Genesis9eigenschaften._wahl('Brauenfarbe',
            [{ id: '', name: 'Vorgabe (Brown)' }, ...farben(artVon(inst.brauenstil))],
            inst.brauen || '',
            wert => Genesis9lauf.planen(inst, () => inst.brauenSetzen(wert),
                                        () => Genesis9eigenschaften._kopf(inst)));
        let farbzeile = farbwahl();
        behaelter.appendChild(Genesis9eigenschaften._wahl('Brauenstil',
            stile, inst.brauenstil || stile[0].id,
            wert => {
                const farbe = farben(artVon(wert)).some(f => f.id === inst.brauen) ? inst.brauen : '';
                inst.brauenstil = wert;
                inst.brauen = farbe;
                const neu = farbwahl();
                farbzeile.replaceWith(neu);
                farbzeile = neu;
                Genesis9lauf.planen(inst, () => inst.brauenstilSetzen(wert, farbe),
                                    () => Genesis9eigenschaften._kopf(inst));
            }));
        behaelter.appendChild(farbzeile);
    }

    static _wahl(titel, eintraege, wert, beimAendern) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label>${escapeHtml(titel)}</label>`;
        const feld = document.createElement('select');
        feld.className = 'hb-dehnt';
        for (const e of eintraege) {
            const option = document.createElement('option');
            option.value = e.id;
            option.textContent = e.name;
            option.selected = e.id === wert;
            feld.appendChild(option);
        }
        feld.addEventListener('change', () => { beimAendern(feld.value); markDirty(); });
        zeile.appendChild(feld);
        return zeile;
    }

    // -------------------------------------------------------------- Regler

    static _regler(inst, plan) {
        const behaelter = document.getElementById('prop-genesis9-regler');
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const bereiche = plan.bereiche || [];
        if (!bereiche.length) {
            behaelter.innerHTML = `<div class="gedaempft">${
                escapeHtml(plan.fehler || 'Keine Regler gefunden.')}</div>`;
            return;
        }
        for (const bereich of bereiche) {
            const kasten = document.createElement('details');
            kasten.className = 'uma-gruppe';
            kasten.open = bereich.schluessel === 'figur';
            kasten.innerHTML = `<summary>${escapeHtml(bereich.name)} `
                + `<span class="gedaempft">(${bereich.regler.length})</span></summary>`;
            for (const r of bereich.regler) {
                kasten.appendChild(Genesis9eigenschaften._zeile(inst, r));
            }
            behaelter.appendChild(kasten);
        }
    }

    static _zeile(inst, regler) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = inst.regler?.[regler.name] ?? regler.vorgabe ?? 0;
        const kennung = `g9-${regler.name}`;
        zeile.innerHTML = `
            <label for="${kennung}" title="${escapeHtml(regler.name)}">${
                escapeHtml(regler.anzeige)}</label>
            <input type="range" id="${kennung}" min="${regler.min}" max="${regler.max}"
                   step="0.01" value="${wert}" data-regler="${escapeHtml(regler.name)}">
            <span class="slider-value">${Genesis9eigenschaften.text(wert)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value);
            anzeige.textContent = Genesis9eigenschaften.text(neu);
            Genesis9lauf.planen(inst, () => inst.reglerSetzen(regler.name, neu),
                                () => Genesis9eigenschaften._kopf(inst));
        });
        return zeile;
    }

    /** Daz zeigt die Kanäle als Prozent — hier auch. */
    static text(wert) {
        return `${Math.round(wert * 100)} %`;
    }
}
