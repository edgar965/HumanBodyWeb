import { escapeHtml } from '../utils.js';
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { markDirty } from '../undo.js';
import { SmplFigur } from './smplfigur.js';

/**
 * Smplformregler — Größe und Fülle eines SMPL-Körpers.
 *
 * WARUM (Edgar, 06.09.2026: „der mann in Fall 2 soll schlank sein, finde den
 * Regler, dass du ihn schlank machst!"): Das Online-Tool hat diesen Regler
 * nicht. Im laufenden Tool gemessen: Mit Bust 70, Waist 55 und Hips 70 bleibt
 * sein 3D-Körper Punkt für Punkt derselbe — 142.500 Punkte, 172 cm, Taille
 * 30,4 cm breit, vor wie nach dem Drapieren. Die Maße wirken dort nur auf den
 * Schnitt.
 *
 * Geformt wird über die SMPL-Blendshapes, serverseitig
 * (`/api/character/smpl-figur/formen/`). Der Regler läuft -100..+100 mit 0 in
 * der Mitte, wie die gemeinsamen Regler. Ein voller Ausschlag sind rund 15 cm
 * Körpergröße bzw. 16-21 cm Taillenumfang — gemessen, nicht geschätzt
 * (`GarmentCode/smplform.py`).
 *
 * Losgelassen wird der Regler, nicht gezogen: Jeder Bau rechnet ein
 * SMPL-Netz mit 6.890 Punkten und legt es ab. Bei jedem Pixel neu zu bauen
 * hieße hunderte Läufe für eine Bewegung.
 */
export class Smplformregler {

    static REGLER = [
        { schluessel: 'groesse', name: 'Größe', links: 'klein', rechts: 'groß' },
        { schluessel: 'fuelle', name: 'Fülle', links: 'schlank', rechts: 'kräftig' },
    ];

    static fuellen(inst, behaelter) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        for (const angabe of Smplformregler.REGLER) {
            behaelter.appendChild(Smplformregler._zeile(inst, angabe));
        }
        behaelter.appendChild(Smplformregler._fuss(inst));
    }

    static _zeile(inst, angabe) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = Number(inst.form?.[angabe.schluessel]) || 0;
        zeile.innerHTML = `<label title="${escapeHtml(angabe.links)} … ${escapeHtml(angabe.rechts)}">`
            + `${escapeHtml(angabe.name)}</label>`;
        const schieber = document.createElement('input');
        schieber.type = 'range';
        schieber.min = '-100';
        schieber.max = '100';
        schieber.step = '1';
        schieber.value = String(wert);
        schieber.className = 'hb-dehnt-ohne-abstand';
        const anzeige = document.createElement('span');
        anzeige.className = 'slider-val';
        anzeige.textContent = String(wert);
        schieber.addEventListener('input', () => { anzeige.textContent = schieber.value; });
        schieber.addEventListener('change', () => {
            Smplformregler._bauen(inst, angabe.schluessel, Number(schieber.value));
        });
        zeile.appendChild(schieber);
        zeile.appendChild(anzeige);
        return zeile;
    }

    static _fuss(inst) {
        const fuss = document.createElement('div');
        fuss.className = 'hb-font-size-0-72rem';
        fuss.id = 'prop-smpl-formstand';
        const groesse = Number(inst.form?.groesse) || 0;
        const fuelle = Number(inst.form?.fuelle) || 0;
        fuss.textContent = (groesse || fuelle)
            ? `Geformt: ${inst.koerper}`
            : 'Durchschnittskörper des Tools (beide Regler in der Mitte).';
        return fuss;
    }

    /** Neuen Körper bauen und die Figur austauschen — Lage bleibt. */
    static async _bauen(inst, schluessel, wert) {
        const stand = document.getElementById('prop-smpl-formstand');
        if (stand) stand.textContent = 'Baue Körper …';
        const form = { ...inst.form, [schluessel]: wert };
        const neu = new SmplFigur(inst.id, {
            koerper: inst.koerper, geschlecht: inst.geschlecht, form,
        });
        try {
            await neu.load();
        } catch (fehler) {
            if (stand) stand.textContent = `Fehler: ${fehler.message}`;
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
        markDirty('SMPL-Form');
    }
}
