import { escapeHtml } from '../utils.js';
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { markDirty } from '../undo.js';
import { SmplFigur } from './smplfigur.js';
import { Smplkatalog } from './smplkatalog.js';
import { Smplformregler } from './smplformregler.js';

/**
 * Smpleigenschaften — der Eigenschaften-Reiter für einen GarmentCode-Körper.
 *
 * Was ein solcher Körper hat: einen Namen aus der Liste des Tools und die
 * von GarmentCode VORGEGEBENEN Maße. Was er nicht hat: Morphs, Regler,
 * Skelett. Die Maße stehen hier zum Nachlesen — sie sind es, aus denen der
 * GarmentCode-Reiter den Schnitt baut, genau wie das Online-Tool. Hier wird
 * nichts gemessen und nichts geraten.
 */
export class Smpleigenschaften {

    static BEREICH = 'prop-smpl-section';

    static fuellen(inst) {
        const bereich = document.getElementById(Smpleigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        const kopf = document.getElementById('prop-smpl-kopf');
        if (kopf) {
            const punkte = inst.bodyMesh?.geometry?.attributes?.position?.count || 0;
            kopf.textContent = `${inst.koerper} · ${punkte} Punkte · `
                + `${inst.hoehe ? (inst.hoehe * 100).toFixed(0) : '?'} cm`;
        }
        Smpleigenschaften._koerper(inst, document.getElementById('prop-smpl-geschlecht'));
        // Die zwei Regler, die das Online-Tool nicht hat (smplformregler.js).
        Smplformregler.fuellen(inst, document.getElementById('prop-smpl-form'));
        Smpleigenschaften._masse(inst, document.getElementById('prop-smpl-masse'));
    }

    static leeren() {
        const bereich = document.getElementById(Smpleigenschaften.BEREICH);
        if (bereich) bereich.classList.add('hb-versteckt');
    }

    /** Ein anderer Körper aus der Liste des Tools — die Figur wird getauscht. */
    static async _koerper(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        let liste = [];
        try {
            liste = await Smplkatalog.liste();
        } catch (fehler) {
            behaelter.innerHTML = `<div class="hb-hinweis">Liste nicht abrufbar: ${escapeHtml(fehler.message)}</div>`;
            return;
        }
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = '<label>Körper</label>';
        const auswahl = document.createElement('select');
        auswahl.className = 'viewer-select hb-dehnt-ohne-abstand';
        // Eine über die Regler geformte Figur trägt einen Namen, der in
        // dieser Liste NICHT steht (`smpl_m_…`). Ohne eigenen Eintrag fiele
        // die Auswahl stumm auf den ersten zurück und behauptete `mean_all`
        // — für einen Körper, der gerade 192 cm misst.
        const geformt = !liste.some(e => e.name === inst.koerper);
        if (geformt) {
            const eigen = document.createElement('option');
            eigen.value = inst.koerper;
            eigen.textContent = `Geformt (${inst.geschlecht === 'male' ? 'männlich' : 'weiblich'})`;
            eigen.selected = true;
            auswahl.appendChild(eigen);
        }
        for (const eintrag of liste) {
            const option = document.createElement('option');
            option.value = eintrag.name;
            option.textContent = eintrag.anzeige || eintrag.name;
            option.selected = !geformt && eintrag.name === inst.koerper;
            auswahl.appendChild(option);
        }
        auswahl.addEventListener('change', () => Smpleigenschaften._tauschen(inst, auswahl.value));
        zeile.appendChild(auswahl);
        behaelter.appendChild(zeile);
    }

    static async _tauschen(inst, koerper) {
        if (koerper === inst.koerper) return;
        const neu = new SmplFigur(inst.id, { koerper });
        try {
            await neu.load();
        } catch (fehler) {
            alert(`Körper nicht ladbar: ${fehler.message}`);
            return;
        }
        neu.group.position.copy(inst.group.position);
        neu.group.rotation.copy(inst.group.rotation);
        neu.group.scale.copy(inst.group.scale);
        state.scene.remove(inst.group);
        inst.dispose();
        state.characters.set(inst.id, neu);
        state.scene.add(neu.group);
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(inst.id);
        markDirty('GarmentCode-Körper');
    }

    /** Die vorgegebenen Maße — Zentimeter und Grad, wie in der YAML. */
    static _masse(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const namen = Object.keys(inst.masse || {}).sort();
        if (!namen.length) {
            behaelter.innerHTML = '<div class="hb-hinweis">Keine Maße vorhanden.</div>';
            return;
        }
        for (const name of namen) {
            const wert = inst.masse[name];
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            zeile.innerHTML = `<label>${escapeHtml(name)}</label>`
                + `<span class="slider-val">${escapeHtml(typeof wert === 'number' ? String(+wert.toFixed(2)) : String(wert))}</span>`;
            behaelter.appendChild(zeile);
        }
    }
}
