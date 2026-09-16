import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _populateTrackAddSubmenu } from './zeitleiste_spurmenue.js';
import { Spurerzeugung } from './spurerzeugung.js';
import { Mimikspur } from './mimikspur.js';
import { Mimikdialog } from './mimikdialog.js';
import { Scriptspur } from './scriptspur.js';

/**
 * Modellhinzufuegen — das zweigeteilte „Hinzufügen" einer Modellspur, für
 * BEIDE Rechtsklickmenüs: das der Zeitleistenfläche (`model-context-menu`)
 * und das des Spurkopfs (`track-context-menu`).
 *
 * Edgar, 15.09.2026: „Hinzufügen soll zweigeteilt sein, einmal Modell
 * hinzufügen, dann Animation. Animation mit normaler Animation, Mimik und
 * Script" — und, als es nur in der Fläche stand: „Rechtsklick bei Modell —
 * Hinzufügen ist nicht geändert!!!" Der Spurkopf links hat sein eigenes
 * Menü; beide füllen sich hier.
 *
 *   Modell hinzufügen ▸     die Figurarten (HumanBody, SMPL, MakeHuman, UMA,
 *                           UMA Python) mit ihren Katalogen — `Menuemodelle`
 *   Animation hinzufügen ▸  Animation ▸ (BVH-Bibliothek der verknüpften
 *                           Animationsspur), Mimik, Script
 */
export class Modellhinzufuegen {

    /**
     * Beide Untermenüs füllen.
     * @param ids  {modell, bvh} — die Kennungen der zwei Untermenü-Felder
     */
    static fuellen(spur, spurNr, menue, klickbild, ids) {
        _populateTrackAddSubmenu(spur, spurNr, menue, klickbild, ids.modell);
        Modellhinzufuegen._animationsBibliothek(spur, menue, klickbild, ids.bvh);
    }

    /** Die Einträge „Mimik" und „Script" des Menüs binden. */
    static binden(menue, spurNr, klickbild) {
        const befehle = {
            'ctx-mimik-track': () => {
                // Mimikspur (falls nötig) und gleich die Pose an der Klickstelle.
                const mimik = Mimikspur.anlegen(spurNr);
                Mimikdialog.oeffnen(mimik, klickbild, null);
            },
            'ctx-script-track': () => Scriptspur.hinzufuegen(spurNr, klickbild),
        };
        for (const [aktion, befehl] of Object.entries(befehle)) {
            const eintrag = menue.querySelector(`[data-action="${aktion}"]`);
            if (!eintrag) continue;
            eintrag.onclick = () => {
                menue.style.display = 'none';
                befehl();
            };
        }
    }

    /**
     * „Animation hinzufügen → Animation": die BVH-Bibliothek für die
     * verknüpfte Animationsspur des Modells. Hat das Modell noch keine,
     * bekommt es eine — auf Klick, nicht schon beim Öffnen des Menüs.
     */
    static _animationsBibliothek(spur, menue, klickbild, zielId) {
        const bewegung = state.project.getLinkedAnimation(spur);
        if (bewegung) {
            _populateTrackAddSubmenu(bewegung, state.project.indexOf(bewegung), menue,
                                     klickbild, zielId);
            return;
        }
        const ziel = document.getElementById(zielId);
        if (!ziel) return;
        ziel.innerHTML = '';
        const eintrag = document.createElement('div');
        eintrag.className = 'ctx-item';
        eintrag.innerHTML = '<i class="fas fa-plus ctx-symbol"></i> Animationsspur anlegen';
        eintrag.addEventListener('click', () => {
            menue.style.display = 'none';
            const neu = Spurerzeugung.animation();
            spur._linkedAnimIdx = state.project.indexOf(neu);
            fn.updateTrackHeaders();
            fn.renderTimeline();
        });
        ziel.appendChild(eintrag);
    }
}
