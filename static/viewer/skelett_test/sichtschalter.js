import { Testzustand } from './testzustand.js';
import { Klappbereiche } from '../gemeinsam/klappbereiche.js';

/**
 * Die Sichtbarkeitsschalter der Vergleichsseite.
 *
 * Aus aufbau.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`). Dort
 * standen sieben wortgleiche Blöcke untereinander — je Skelett einer.
 */
export class Sichtschalter {
    /** Kästchen-ID -> Schlüssel in `Testzustand.skeletons`. */
    static SKELETTE = {
        'toggle-def': 'def',
        'toggle-cmu': 'cmu',
        'toggle-mixamo': 'mixamo',
        'toggle-mocapnet': 'mocapnet',
        'toggle-bandai': 'bandai',
        'toggle-smpl': 'smpl',
        'toggle-openpose': 'openpose',
    };

    /** Hängt alle Schalter ein — Beschriftungen, Skelette, Klappabschnitte. */
    static binden() {
        Sichtschalter._beschriftungen();
        for (const [id, schluessel] of Object.entries(Sichtschalter.SKELETTE)) {
            Sichtschalter._skelett(id, schluessel);
        }
        Sichtschalter._klappabschnitte();
    }

    static _beschriftungen() {
        const kaestchen = document.getElementById('toggle-labels');
        if (!kaestchen) return;
        kaestchen.addEventListener('change', (e) => {
            const sichtbar = e.target.checked;
            for (const skelett of Object.values(Testzustand.skeletons)) {
                skelett.labels.forEach(lbl => { lbl.visible = sichtbar; });
            }
        });
    }

    static _skelett(id, schluessel) {
        const kaestchen = document.getElementById(id);
        if (!kaestchen) return;
        kaestchen.addEventListener('change', (e) => {
            const skelett = Testzustand.skeletons[schluessel];
            if (skelett?.group) skelett.group.visible = e.target.checked;
        });
    }

    /** Abschnitte auf- und zuklappbar machen — siehe `Klappbereiche`. */
    static _klappabschnitte() {
        Klappbereiche.verdrahten();
    }
}
