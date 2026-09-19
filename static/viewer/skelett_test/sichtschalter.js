import { Testzustand } from './testzustand.js';
import { Klappbereiche } from '../gemeinsam/klappbereiche.js';
import { Reihenfolge } from './reihenfolge.js';

/**
 * Die Sichtbarkeitsschalter der Vergleichsseite.
 *
 * Aus aufbau.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`). Dort
 * standen sieben wortgleiche Blöcke untereinander — je Skelett einer.
 *
 * Seit 19.09.2026 auch die Platznummern (`Reihenfolge`): eine Zahl je
 * Skelett; ändert sich eine, rücken die anderen nach hinten, die Zeilen und
 * die Schilder über der Leinwand sortieren sich mit. DEF bleibt 1.
 */
export class Sichtschalter {
    /** Kästchen-ID -> Schlüssel in `Testzustand.skeletons`. */
    static SKELETTE = {
        'toggle-uma': 'uma',
        'toggle-genesis9': 'genesis9',
        'toggle-def': 'def',
        'toggle-cmu': 'cmu',
        'toggle-mixamo': 'mixamo',
        'toggle-mocapnet': 'mocapnet',
        'toggle-bandai': 'bandai',
        'toggle-smpl': 'smpl',
        'toggle-openpose': 'openpose',
    };

    /** Hängt alle Schalter ein — Beschriftungen, Skelette, Plätze, Klappabschnitte. */
    static binden() {
        Sichtschalter._beschriftungen();
        for (const [id, schluessel] of Object.entries(Sichtschalter.SKELETTE)) {
            Sichtschalter._skelett(id, schluessel);
        }
        Sichtschalter._reihenfolge();
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

    /** Die Platznummern: lesen, anwenden, bei Änderung neu verteilen und merken. */
    static _reihenfolge() {
        const felder = [...document.querySelectorAll('input.platznummer[data-skelett]')];
        if (!felder.length) return;
        let folge = Reihenfolge.ausText(Sichtschalter._gemerkt());
        Sichtschalter._plaetze(folge, felder);
        for (const feld of felder) {
            feld.addEventListener('change', () => {
                folge = Reihenfolge.verschoben(folge, feld.dataset.skelett, Number(feld.value));
                Sichtschalter._plaetze(folge, felder);
                try {
                    localStorage.setItem(Reihenfolge.SCHLUESSEL, JSON.stringify(folge));
                } catch (_fehler) { /* stumm gewollt: privates Fenster */ }
            });
        }
    }

    static _gemerkt() {
        try {
            return localStorage.getItem(Reihenfolge.SCHLUESSEL);
        } catch (_fehler) {
            return null;
        }
    }

    /** Skelette an ihre Plätze, Nummern in die Felder, Zeilen und Schilder sortieren. */
    static _plaetze(folge, felder) {
        const plaetze = Reihenfolge.plaetze(folge);
        const zeilen = felder[0].closest('.panel-body');
        const schilder = document.querySelector('.skeleton-labels');
        for (const schluessel of folge) {
            const platz = plaetze[schluessel];
            const skelett = Testzustand.skeletons[schluessel];
            if (skelett) {
                skelett.xOffset = platz.x;
                skelett.zOffset = platz.z;
                if (skelett.group) skelett.group.position.set(platz.x, 0, platz.z);
            }
            const feld = felder.find(f => f.dataset.skelett === schluessel);
            if (feld) {
                feld.value = String(platz.nummer);
                const zeile = feld.closest('.toggle-row');
                if (zeilen && zeile) zeilen.appendChild(zeile);
            }
            const schild = schilder?.querySelector('.skeleton-label.' + schluessel);
            if (schild) schilder.appendChild(schild);
        }
    }

    /** Abschnitte auf- und zuklappbar machen — siehe `Klappbereiche`. */
    static _klappabschnitte() {
        Klappbereiche.verdrahten();
    }
}
