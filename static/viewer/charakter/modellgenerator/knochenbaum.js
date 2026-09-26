/**
 * Knochenbaum — die Liste der Knochen links im Modell-Reiter.
 *
 * Aus modellgenerator_ui.js herausgeloest (Umbau 16.08.2026).
 */
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Knochengruppen } from '../state.js';
import { Modellbauzustand } from './zustand.js';

export class Knochenbaum {
    /**
     * Baum neu aufbauen.
     *
     * `waehlen` und `neuAufbauen` kommen von aussen, damit dieses Modul weder
     * die Knochenauswahl noch die Modellerzeugung importieren muss — beide
     * wuerden zurueck auf den Baum zeigen.
     */
    static aufbauen(waehlen, neuAufbauen) {
        const behaelter = document.getElementById('mg-bone-tree');
        if (!behaelter || !Modellbauzustand.konfig) return;
        behaelter.innerHTML = '';
        for (const gruppe of Knochenbaum._gruppen()) {
            if (gruppe.bones.length === 0) continue;
            behaelter.appendChild(
                Knochenbaum._gruppe(gruppe, waehlen, neuAufbauen));
        }
    }

    static _gruppen() {
        if (Modellbauzustand.skelettart === 'rig' && Modellbauzustand.rigKnochen) {
            const e = Knochengruppen.einteilenRig(Modellbauzustand.rigKnochen);
            return [
                { label: 'DEF', bones: e.def, zu: false },
                { label: 'MCH', bones: e.mch, zu: true },
                { label: 'ORG', bones: e.org, zu: true },
                { label: 'Control', bones: e.control, zu: true },
            ];
        }
        const e = Knochengruppen.einteilen(state.rigifySkeletonData);
        return [
            { label: 'Körper', bones: e.body, zu: false },
            { label: 'Finger', bones: e.finger, zu: true },
            { label: 'Gesicht', bones: e.face, zu: true },
        ];
    }

    static _gruppe(gruppe, waehlen, neuAufbauen) {
        const kasten = document.createElement('div');
        kasten.className = 'mg-category';

        const kopf = document.createElement('div');
        kopf.className = 'mg-category-header' + (gruppe.zu ? ' collapsed' : '');
        kopf.innerHTML = `<span class="mg-chevron">&#9660;</span> `
                       + `${gruppe.label} (${gruppe.bones.length})`;
        kasten.appendChild(kopf);

        const rumpf = document.createElement('div');
        rumpf.className = 'mg-category-body' + (gruppe.zu ? ' hidden' : '');
        for (const name of gruppe.bones) {
            const teil = Modellbauzustand.konfig.bone_parts[name];
            if (!teil) continue;
            rumpf.appendChild(Knochenbaum._eintrag(name, teil, waehlen, neuAufbauen));
        }
        kasten.appendChild(rumpf);

        kopf.addEventListener('click', () => {
            kopf.classList.toggle('collapsed');
            rumpf.classList.toggle('hidden');
        });
        return kasten;
    }

    static _eintrag(name, teil, waehlen, neuAufbauen) {
        const zeile = document.createElement('div');
        zeile.className = 'mg-bone-item';
        zeile.dataset.bone = name;

        const haken = document.createElement('input');
        haken.type = 'checkbox';
        haken.checked = teil.visible;
        haken.addEventListener('change', (e) => {
            e.stopPropagation();
            teil.visible = haken.checked;
            neuAufbauen();
            fn.markDirty?.(haken.checked ? 'Knochen anzeigen' : 'Knochen ausblenden');
        });

        const beschriftung = document.createElement('span');
        beschriftung.className = 'mg-bone-label';
        beschriftung.textContent = name.replace(/^(DEF|MCH|ORG)-/, '');
        beschriftung.title = name;

        const farbfleck = document.createElement('span');
        farbfleck.className = 'mg-bone-swatch';
        farbfleck.style.backgroundColor =
            teil.color || Modellbauzustand.konfig.default_color;

        zeile.append(haken, beschriftung, farbfleck);
        zeile.addEventListener('click', (e) => {
            if (e.target === haken) return;   // das Ankreuzfeld regelt sich selbst
            waehlen(name);
        });
        return zeile;
    }

    /** Nur den Farbfleck eines Eintrags auffrischen. */
    static eintragAuffrischen(name) {
        const zeile = document.querySelector(`.mg-bone-item[data-bone="${name}"]`);
        const teil = Modellbauzustand.konfig?.bone_parts[name];
        if (!zeile || !teil) return;
        const fleck = zeile.querySelector('.mg-bone-swatch');
        if (fleck) fleck.style.backgroundColor = teil.color;
    }

    /** Auswahl im Baum hervorheben. */
    static hervorheben(name) {
        document.querySelectorAll('.mg-bone-item').forEach(el => {
            el.classList.toggle('selected', el.dataset.bone === name);
        });
    }

    /** Einen Eintrag sichtbar machen — Gruppe aufklappen, hinscrollen. */
    static insBildRuecken(name) {
        const zeile = document.querySelector(`.mg-bone-item[data-bone="${name}"]`);
        if (!zeile) return;
        const rumpf = zeile.closest('.mg-category-body');
        if (rumpf?.classList.contains('hidden')) {
            rumpf.classList.remove('hidden');
            rumpf.previousElementSibling?.classList.remove('collapsed');
        }
        zeile.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
