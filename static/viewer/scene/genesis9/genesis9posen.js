import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Genesis9lauf } from './genesis9lauf.js';

/**
 * Genesis9posen — Daz-Posen und -Ausdrücke einer Genesis-9-Figur (18.09.2026).
 *
 * Die Liste kommt von `/api/character/genesis9-figur/posen/` (`Genesis9/posen.py`):
 * 150 Posen der Starter Essentials und der Space-Valkyrie-Sammlung, gruppiert
 * nach Ordner, dazu Ausdrücke (FACS-Regler: Ursula, Space Valkyrie).
 *
 * EIN STANDBILD, KEINE ANIMATION: Der Server backt die Pose in das Netz und
 * stellt das Skelett dazu — wer danach eine BVH-Bewegung abspielt, stellt die
 * Pose auf „—", sonst rechnet der Retarget gegen eine verdrehte Ruhelage.
 *
 * FORMPRESETS (18.09.2026 nachts): Daz' `preset_shape` (Ursula Body, Head,
 * HD Body, Breasts Push Up, Long Lashes, Navel, Oval Nails; Kin Fullbody,
 * Head, Body) stellen Regler — hier Kästchen: an setzt die Regler des
 * Presets, aus setzt sie auf 0 (Daz' `REM`-Fassung). Sie landen in
 * `inst.regler` und werden mit der Figur gespeichert.
 */
export class Genesis9posen {

    static ADRESSE = '/api/character/genesis9-figur/posen/';
    static BEHAELTER = 'prop-genesis9-pose';
    static _liste = null;

    static async liste() {
        if (!Genesis9posen._liste) {
            Genesis9posen._liste = await Serverabruf.json(Genesis9posen.ADRESSE);
        }
        return Genesis9posen._liste;
    }

    static async fuellen(inst) {
        const behaelter = document.getElementById(Genesis9posen.BEHAELTER);
        if (!behaelter) return;
        const daten = await Genesis9posen.liste();
        behaelter.innerHTML = '';
        if (daten.fehler) {
            behaelter.innerHTML = `<div class="gedaempft">${escapeHtml(daten.fehler)}</div>`;
            return;
        }
        behaelter.appendChild(Genesis9posen._wahl(inst, 'Pose', 'pose', daten.posen || []));
        behaelter.appendChild(Genesis9posen._wahl(inst, 'Ausdruck', 'ausdruck', daten.ausdruecke || []));
        for (const gruppe of daten.formen || []) behaelter.appendChild(Genesis9posen._formen(inst, gruppe));
        const hinweis = document.createElement('div');
        hinweis.className = 'gedaempft hb-font-size-0-72rem';
        hinweis.textContent = 'Standbild: vor einer BVH-Bewegung die Pose auf „—" stellen.';
        behaelter.appendChild(hinweis);
    }

    /** Ob alle Regler eines Formpresets in der Figur auf ihrem Wert stehen. */
    static aktiv(inst, regler) {
        const eintraege = Object.entries(regler || {});
        return eintraege.length > 0
            && eintraege.every(([k, w]) => Math.abs((inst.regler?.[k] || 0) - w) < 1e-6);
    }

    /** Eine Gruppe Formpresets (ein Charakter) als Kästchen. */
    static _formen(inst, gruppe) {
        const block = document.createElement('details');
        block.className = 'hb-formpresets';
        block.innerHTML = `<summary>Form · ${escapeHtml(gruppe.gruppe)} <span class="gedaempft">(${
            gruppe.eintraege.length})</span></summary>`;
        for (const e of gruppe.eintraege) {
            const zeile = document.createElement('label');
            zeile.className = 'hb-formpreset';
            const haken = document.createElement('input');
            haken.type = 'checkbox';
            haken.checked = Genesis9posen.aktiv(inst, e.regler);
            haken.addEventListener('change', () => {
                inst.regler = inst.regler || {};
                for (const [k, w] of Object.entries(e.regler || {})) {
                    if (haken.checked) inst.regler[k] = w; else delete inst.regler[k];
                }
                Genesis9lauf.planen(inst, () => inst.neuFormen(), () => {});
                markDirty();
            });
            zeile.append(haken, document.createTextNode(` ${e.name}`));
            block.appendChild(zeile);
        }
        return block;
    }

    static _wahl(inst, titel, feld, gruppen) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label>${escapeHtml(titel)}</label>`;
        const wahl = document.createElement('select');
        wahl.className = 'hb-dehnt';
        const leer = document.createElement('option');
        leer.value = ''; leer.textContent = '—';
        wahl.appendChild(leer);
        for (const gruppe of gruppen) {
            const block = document.createElement('optgroup');
            block.label = gruppe.gruppe;
            for (const e of gruppe.eintraege) {
                const option = document.createElement('option');
                option.value = e.id;
                option.textContent = e.name;
                option.selected = e.id === inst[feld];
                block.appendChild(option);
            }
            wahl.appendChild(block);
        }
        wahl.addEventListener('change', () => {
            Genesis9lauf.planen(inst, () => inst.poseSetzen(feld, wahl.value), () => {});
            markDirty();
        });
        zeile.appendChild(wahl);
        return zeile;
    }
}
