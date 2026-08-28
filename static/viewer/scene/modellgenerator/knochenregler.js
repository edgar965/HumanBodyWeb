/**
 * Knochenregler — die Bedienelemente eines einzelnen Knochens, die unabhaengig
 * von der Form sind: Radius, Farbe, Ueberlappung, Versatz, Drehung, Textur.
 *
 * Aus modellgenerator_ui.js herausgeloest (Umbau 16.08.2026). Wie bei
 * Formregler gilt: eine Tabelle, aus der sowohl das Anbinden als auch das
 * Nachziehen laeuft — vorher standen beide Richtungen getrennt im Code.
 */
import { fn } from '../../gemeinsam/registrierung.js';
import { Modellbauzustand } from './zustand.js';
import { Teilbindung } from './teilbindung.js';

/** [Kennung, Eigenschaft, Vorgabe, Stellen, Baumeintrag auffrischen] */
const SCHIEBER = [
    ['mg-bone-radius', 'radius', 0.03, 3, true],
    ['mg-bone-overlap', 'overlap', 0.5, 2, false],
    ['mg-axial-scale', 'axialScale', 1.0, 2, false],
];

/** [Kennung, Eigenschaft, Vorgabe] — Ankreuzfelder. */
const SCHALTER = [
    ['mg-plane-doublesided', 'planeDoubleSided', true],
    ['mg-spiral-skirt', 'spiralSkirt', false],
    ['mg-helix-skirt', 'spiralSkirt', false],
];

/** [Kennungspraefix, Eigenschaft, Stellen] — je drei Achsen. */
const VEKTOREN = [
    ['mg-head-off-', 'headOffset', 3],
    ['mg-tail-off-', 'tailOffset', 3],
    ['mg-shape-rot-', 'shapeRotation', 0],
];

export class Knochenregler {
    static binden(neuAufbauen, formGewechselt, baumAuffrischen) {
        Knochenregler._schieberBinden(neuAufbauen, baumAuffrischen);
        Knochenregler._schalterBinden(neuAufbauen);
        Knochenregler._vektorenBinden(neuAufbauen);
        Knochenregler._farbeBinden(neuAufbauen, baumAuffrischen);
        Knochenregler._formBinden(formGewechselt);
        Knochenregler._texturBinden(neuAufbauen);
    }

    static _schieberBinden(neuAufbauen, baumAuffrischen) {
        for (const [id, eigenschaft, , stellen, imBaum] of SCHIEBER) {
            Teilbindung.regler(id, (v) => v.toFixed(stellen), (teil, v) => {
                teil[eigenschaft] = v;
                if (imBaum) baumAuffrischen(Modellbauzustand.gewaehlterKnochen);
                neuAufbauen();
            });
        }
    }

    static _schalterBinden(neuAufbauen) {
        for (const [id, eigenschaft] of SCHALTER) {
            Teilbindung.an(id, 'change', (teil, feld) => {
                teil[eigenschaft] = feld.checked;
                neuAufbauen();
            });
        }
    }

    static _vektorenBinden(neuAufbauen) {
        for (const [praefix, eigenschaft, stellen] of VEKTOREN) {
            for (const achse of ['x', 'y', 'z']) {
                // `String(v)` bei null Stellen, nicht `toFixed(0)`: Die
                // Drehung zeigt so „7.5“ statt „8“ (Stand vor dem Umbau).
                Teilbindung.regler(
                    praefix + achse,
                    (v) => (stellen ? v.toFixed(stellen) : String(v)),
                    (teil, v) => {
                        if (!teil[eigenschaft]) {
                            teil[eigenschaft] = { x: 0, y: 0, z: 0 };
                        }
                        teil[eigenschaft][achse] = v;
                        neuAufbauen();
                    });
            }
        }
    }

    static _farbeBinden(neuAufbauen, baumAuffrischen) {
        Teilbindung.an('mg-bone-color', 'input', (teil, feld) => {
            teil.color = feld.value;
            baumAuffrischen(Modellbauzustand.gewaehlterKnochen);
            neuAufbauen();
        });
    }

    static _formBinden(formGewechselt) {
        Teilbindung.an('mg-bone-shape', 'change', (teil, form) => {
            teil.shape = form.value;
            formGewechselt(form.value);
        });
        Teilbindung.an('mg-bone-garment', 'change', (teil, kleidung) => {
            teil.is_garment = kleidung.checked;
            fn.markDirty?.(kleidung.checked ? 'Kleidungsstueck an'
                                            : 'Kleidungsstueck aus');
        });
    }

    static _texturBinden(neuAufbauen) {
        const datei = Teilbindung.an(
            'mg-bone-texture-file', 'change', (teil, feld) => {
                const f = feld.files && feld.files[0];
                if (!f) return;
                const leser = new FileReader();
                leser.onload = () => {
                    teil.texture = leser.result;
                    Knochenregler._texturZeigen(leser.result);
                    neuAufbauen();
                    fn.markDirty?.('Textur gesetzt');
                };
                leser.readAsDataURL(f);
            });
        Teilbindung.an('mg-bone-texture-clear', 'click', (teil) => {
            delete teil.texture;
            Knochenregler._texturZeigen(null);
            if (datei) datei.value = '';
            neuAufbauen();
            fn.markDirty?.('Textur entfernt');
        });
    }

    static _texturZeigen(datenUrl) {
        const bild = document.getElementById('mg-bone-texture-thumb');
        const rahmen = document.getElementById('mg-bone-texture-preview');
        if (bild) bild.src = datenUrl || '';
        if (rahmen) rahmen.style.display = datenUrl ? '' : 'none';
    }

    /** Alle Bedienelemente auf ein Knochenteil nachziehen. */
    static nachziehen(teil) {
        for (const [id, eigenschaft, vorgabe, stellen] of SCHIEBER) {
            const regler = document.getElementById(id);
            const anzeige = document.getElementById(id + '-val');
            const v = teil[eigenschaft] ?? vorgabe;
            if (regler) regler.value = v;
            if (anzeige) anzeige.textContent = v.toFixed(stellen);
        }
        for (const [id, eigenschaft, vorgabe] of SCHALTER) {
            const feld = document.getElementById(id);
            if (feld) feld.checked = teil[eigenschaft] ?? vorgabe;
        }
        for (const [praefix, eigenschaft, stellen] of VEKTOREN) {
            const v = teil[eigenschaft] || { x: 0, y: 0, z: 0 };
            for (const achse of ['x', 'y', 'z']) {
                const regler = document.getElementById(praefix + achse);
                const anzeige = document.getElementById(praefix + achse + '-val');
                if (regler) regler.value = v[achse] || 0;
                if (anzeige) {
                    anzeige.textContent = stellen ? (v[achse] || 0).toFixed(stellen)
                                                  : String(v[achse] || 0);
                }
            }
        }
        const form = document.getElementById('mg-bone-shape');
        if (form) form.value = teil.shape || 'cylinder';
        const kleidung = document.getElementById('mg-bone-garment');
        if (kleidung) {
            // Ohne ausdrueckliche Angabe gilt: Rock und Tutu sind Kleidung.
            const stoff = ['skirt', 'tutu', 'spiral_tutu', 'helix_ribbon']
                .includes(teil.shape);
            kleidung.checked = teil.is_garment !== undefined ? !!teil.is_garment : stoff;
        }
        const farbe = document.getElementById('mg-bone-color');
        if (farbe) farbe.value = teil.color || Modellbauzustand.konfig.default_color;
        Knochenregler._texturZeigen(teil.texture || null);
        const datei = document.getElementById('mg-bone-texture-file');
        if (datei) datei.value = '';
    }
}
