import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _sameSubMesh, getSelectableSubMeshes } from './teilnetz_auswahl.js';

/**
 * Getragenliste — die Liste „Objekte" im Eigenschaften-Reiter: jedes
 * Teilnetz der Figur (Kleidung, Haare, GarmentCode-Stücke) als Zeile, Klick
 * wählt es, das Kreuz entfernt es.
 *
 * Herausgelöst aus `properties.js` (12.09.2026, 304 Zeilen). Die Liste kennt
 * den Reiter nicht: Was nach der Wahl passiert (Regler nachziehen, Abschnitte
 * umschalten), holt sie über die Registrierung.
 */
export class Getragenliste {

    static LEER = '<li class="equipped-empty">Keine Objekte</li>';

    static fuellen(inst) {
        const list = document.getElementById('prop-equipped-list');
        if (!list) return;
        list.innerHTML = '';
        const targets = inst ? getSelectableSubMeshes(inst.id) : [];
        if (targets.length === 0) {
            list.innerHTML = Getragenliste.LEER;
            return;
        }
        for (const t of targets) list.appendChild(Getragenliste._zeile(inst, t));
    }

    static _zeile(inst, t) {
        const li = document.createElement('li');
        li.className = 'equipped-item';
        const nameSpan = document.createElement('span');
        nameSpan.className = 'equipped-item-name';
        if (_sameSubMesh(state._selectedSubMesh, t)) nameSpan.classList.add('selected');
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => Getragenliste._waehlen(inst, t));
        const rmBtn = document.createElement('button');
        rmBtn.className = 'equipped-item-remove';
        rmBtn.innerHTML = '&#10005;';
        rmBtn.title = 'Entfernen';
        rmBtn.addEventListener('click', (e) => { e.stopPropagation(); fn._removeSubMesh(t); });
        li.appendChild(nameSpan);
        li.appendChild(rmBtn);
        return li;
    }

    /** Das Teilnetz wird FRISCH gesucht — die Zeile könnte veraltet sein. */
    static _waehlen(inst, t) {
        if (state._selectedSubMesh) fn._setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        const fresh = getSelectableSubMeshes(inst.id).find(x => x.type === t.type && x.key === t.key);
        if (!fresh) return;
        state._selectedSubMesh = fresh;
        fn._setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
        fn._setBodyEmissive(inst, state._ZERO_EMISSIVE);
        fn._syncGarmentSliders();
        fn._updatePropContext();
        if (fresh.type === 'cloth') fn._syncPropGarmentControls();
        else if (fresh.type === 'hair') fn._syncPropHairControls();
        Getragenliste.fuellen(inst);
    }
}
