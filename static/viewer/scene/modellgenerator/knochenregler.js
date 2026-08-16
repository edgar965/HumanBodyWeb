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
            const regler = document.getElementById(id);
            if (!regler) continue;
            const anzeige = document.getElementById(id + '-val');
            regler.addEventListener('input', () => {
                const v = parseFloat(regler.value);
                if (anzeige) anzeige.textContent = v.toFixed(stellen);
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                teil[eigenschaft] = v;
                if (imBaum) baumAuffrischen(Modellbauzustand.gewaehlterKnochen);
                neuAufbauen();
            });
        }
    }

    static _schalterBinden(neuAufbauen) {
        for (const [id, eigenschaft] of SCHALTER) {
            const feld = document.getElementById(id);
            if (!feld) continue;
            feld.addEventListener('change', () => {
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                teil[eigenschaft] = feld.checked;
                neuAufbauen();
            });
        }
    }

    static _vektorenBinden(neuAufbauen) {
        for (const [praefix, eigenschaft, stellen] of VEKTOREN) {
            for (const achse of ['x', 'y', 'z']) {
                const regler = document.getElementById(praefix + achse);
                if (!regler) continue;
                const anzeige = document.getElementById(praefix + achse + '-val');
                regler.addEventListener('input', () => {
                    const v = parseFloat(regler.value);
                    if (anzeige) {
                        anzeige.textContent = stellen ? v.toFixed(stellen) : String(v);
                    }
                    const teil = Modellbauzustand.teil();
                    if (!teil) return;
                    if (!teil[eigenschaft]) teil[eigenschaft] = { x: 0, y: 0, z: 0 };
                    teil[eigenschaft][achse] = v;
                    neuAufbauen();
                });
            }
        }
    }

    static _farbeBinden(neuAufbauen, baumAuffrischen) {
        const feld = document.getElementById('mg-bone-color');
        if (!feld) return;
        feld.addEventListener('input', () => {
            const teil = Modellbauzustand.teil();
            if (!teil) return;
            teil.color = feld.value;
            baumAuffrischen(Modellbauzustand.gewaehlterKnochen);
            neuAufbauen();
        });
    }

    static _formBinden(formGewechselt) {
        const form = document.getElementById('mg-bone-shape');
        if (form) {
            form.addEventListener('change', () => {
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                teil.shape = form.value;
                formGewechselt(form.value);
            });
        }
        const kleidung = document.getElementById('mg-bone-garment');
        if (kleidung) {
            kleidung.addEventListener('change', () => {
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                teil.is_garment = kleidung.checked;
                fn.markDirty?.(kleidung.checked ? 'Kleidungsstueck an'
                                                : 'Kleidungsstueck aus');
            });
        }
    }

    static _texturBinden(neuAufbauen) {
        const datei = document.getElementById('mg-bone-texture-file');
        const loeschen = document.getElementById('mg-bone-texture-clear');
        if (datei) {
            datei.addEventListener('change', () => {
                const f = datei.files && datei.files[0];
                const teil = Modellbauzustand.teil();
                if (!f || !teil) return;
                const leser = new FileReader();
                leser.onload = () => {
                    teil.texture = leser.result;
                    Knochenregler._texturZeigen(leser.result);
                    neuAufbauen();
                    fn.markDirty?.('Textur gesetzt');
                };
                leser.readAsDataURL(f);
            });
        }
        if (loeschen) {
            loeschen.addEventListener('click', () => {
                const teil = Modellbauzustand.teil();
                if (!teil) return;
                delete teil.texture;
                Knochenregler._texturZeigen(null);
                if (datei) datei.value = '';
                neuAufbauen();
                fn.markDirty?.('Textur entfernt');
            });
        }
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
