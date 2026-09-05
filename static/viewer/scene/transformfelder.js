import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Transformfelder — die neun Zahlenfelder (Pos, Rot, Scale × x, y, z) im
 * Eigenschaften-Reiter, für HumanBody- und UMA-Figuren gleich.
 *
 * Herausgelöst aus `properties.js` (05.09.2026, Befund `dateigroesse`).
 */
export class Transformfelder {

    static ZEILEN = [
        { label: 'Pos', prop: 'position', step: 0.01 },
        { label: 'Rot', prop: 'rotation', step: 1, isDeg: true },
        { label: 'Scale', prop: 'scale', step: 0.01 },
    ];
    static ACHSEN = ['x', 'y', 'z'];

    /** Die Felder für eine Figur aufbauen; Eingaben schreiben direkt in die Gruppe. */
    static fuellen(inst) {
        const grid = document.getElementById('prop-transform');
        grid.innerHTML = '';
        for (const row of Transformfelder.ZEILEN) {
            const lbl = document.createElement('label'); lbl.textContent = row.label; grid.appendChild(lbl);
            for (const axis of Transformfelder.ACHSEN) {
                const input = document.createElement('input');
                input.type = 'number';
                input.step = row.step;
                input.dataset.prop = row.prop;
                input.dataset.axis = axis;
                input.className = 'prop-transform-input';
                input.value = parseFloat(Transformfelder._wert(inst, row.prop, axis).toFixed(3));
                input.addEventListener('input', () => {
                    const num = parseFloat(input.value); if (isNaN(num)) return;
                    if (row.isDeg) inst.group.rotation[axis] = THREE.MathUtils.degToRad(num);
                    else inst.group[row.prop][axis] = num;
                    fn.updateCharacterListUI();
                });
                grid.appendChild(input);
            }
        }
    }

    /** Die Felder an die Gruppe angleichen — nach dem Ziehen mit dem Griff. */
    static angleichen() {
        const inst = state.characters.get(state.currentPropsCharId);
        if (!inst) return;
        document.querySelectorAll('.prop-transform-input').forEach(input => {
            const prop = input.dataset.prop, axis = input.dataset.axis;
            if (!prop || !axis || document.activeElement === input) return;
            input.value = parseFloat(Transformfelder._wert(inst, prop, axis).toFixed(3));
        });
    }

    static _wert(inst, prop, axis) {
        return prop === 'rotation'
            ? THREE.MathUtils.radToDeg(inst.group.rotation[axis]) : inst.group[prop][axis];
    }
}
