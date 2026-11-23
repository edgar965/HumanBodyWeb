import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _sameSubMesh, getSelectableSubMeshes } from './teilnetz_auswahl.js';
import { Genesis9kleidung } from '../gemeinsam/genesis9kleidung.js';

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
        const targets = inst ? getSelectableSubMeshes(inst.id).filter(t => !Getragenliste._genital(inst, t)) : [];
        if (targets.length === 0) {
            list.innerHTML = Getragenliste.LEER;
            return;
        }
        for (const t of targets) list.appendChild(Getragenliste._zeile(inst, t));
    }

    /**
     * Ein Genital-Stück einer Genesis-Figur („Daz Anatomie Frau|Mann“, MakeHuman, eigene Scham) steht schon im Bereich „Genitalien“ (`Genesis9genitalien`,
     * Stücke mit `anatomie` aus der Garderobe) — hier nicht noch einmal (23.11.2026, Edgar: „mach diesen eintrag weg, den gibt es doppelt“). Bei einer
     * HumanBody-Figur gibt es diesen Bereich nicht, dort bleibt die Zeile. Ohne Katalog zählt die Kennung `daz_anatomie_*`; der Katalog kommt nach und
     * füllt die Liste neu.
     */
    static _genital(inst, t) {
        if (t.type !== 'cloth' || inst.quelle !== 'genesis9') return false;
        const kennung = String(t.key).split('/')[0];
        const katalog = Genesis9kleidung._stuecke;
        if (!katalog) {
            Genesis9kleidung.stuecke().then(liste => { if (liste.length && state.characters.get(inst.id) === inst) Getragenliste.fuellen(inst); });
            return kennung.startsWith('daz_anatomie_');
        }
        return Boolean(katalog.find(s => s.id === kennung)?.anatomie);
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
