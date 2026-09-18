/**
 * Lipsyncformen — Rhubarbs Mundformen A–H/X als Reglerstellungen je Figurart.
 *
 * Rhubarb Lip Sync (`core/dienste/lippensync.py`) liefert den Preston-Blair-
 * Satz: A geschlossen (M, B, P) · B leicht offen, Zähne zusammen (K, S, T,
 * EE) · C offen (EH, AE) · D weit offen (AA) · E leicht gerundet (AO, ER) ·
 * F gespitzt (UW, OW, W) · G Zähne auf der Unterlippe (F, V) · H Zunge oben
 * (L) · X Ruhe. Was das an der Figur heißt, steht hier — einmal für Genesis 9
 * (die 17 Viseme-Regler `facs_ctrl_v…`, Daz' eigene Mundformen; Werte 0…1)
 * und einmal als MB-Lab-Einheiten für die DEF-Figur und SMPL-X (dieselben
 * Einheiten wie die Mimikspur; `Mimikbasis`/`Mimiksmplx` legen sie an).
 *
 * Die Gewichte sind Augenmaß am Rhubarb-Handbuch, keine Messung: „B: Zähne
 * geschlossen, leicht offen" wird bei Daz zur Hälfte `Vis EE`, zur Hälfte
 * `Vis S`. Ohne Importe — `test_js_lipsynckurve` rechnet in Node.
 */
export class Lipsyncformen {

    /** Genesis 9: Form -> `{Viseme-Regler: Gewicht}`. */
    static GENESIS9 = {
        A: { facs_ctrl_vM: 1.0 },
        B: { facs_ctrl_vEE: 0.5, facs_ctrl_vS: 0.5 },
        C: { facs_ctrl_vEH: 0.9 },
        D: { facs_ctrl_vAA: 1.0 },
        E: { facs_ctrl_vER: 0.7, facs_ctrl_vOW: 0.3 },
        F: { facs_ctrl_vUW: 0.7, facs_ctrl_vW: 0.5 },
        G: { facs_ctrl_vF: 1.0 },
        H: { facs_ctrl_vL: 1.0 },
        X: {},
    };

    /** MB-Lab-Einheiten (DEF-Figur, SMPL-X): Form -> `{Einheit: Gewicht}`. */
    static MBLAB = {
        A: { mouthClosed: 0.4 },
        B: { mouthOpenTeethClosed: 0.5 },
        C: { mouthOpenHalf: 0.7 },
        D: { mouthOpen: 0.7, mouthOpenLarge: 0.3 },
        E: { mouthOpenO: 0.5 },
        F: { mouthOpenO: 0.9 },
        G: { mouthBite: 0.5 },
        H: { mouthOpenHalf: 0.4, tongueTipUp: 0.6 },
        X: {},
    };

    /** Die Tabelle einer Figurart (`genesis9` → Daz-Visemes, sonst MB-Lab). */
    static tabelle(quelle) {
        return quelle === 'genesis9' ? Lipsyncformen.GENESIS9 : Lipsyncformen.MBLAB;
    }
}
