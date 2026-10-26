import { Dazschnittfelder } from './dazschnittfelder.js';

/**
 * Dazschnittwerte — die Eigen-Werte eines Daz-Stücks lesen, schreiben, in Uniforms umrechnen, und DIESELBE Schnittkante je Punkt wie der Shader (Stufe K2c,
 * 25.10.2026; Felder `Dazschnittfelder`, Shader `DazschnittGLSL`). Ohne Three.js, in Node prüfbar.
 *
 * ABLAGE: `inst.kleidung[kennung].regler['schnitt:<feld>']` — ein fehlender Eintrag heißt Vorgabe („wie geliefert“). `ohne(regler)` nimmt sie aus allem, was an
 * den Server geht (Anfrage des Stücks und Liste der getragenen in `Genesis9kleidung`, `Genesis9lagen`, `Dazkleidung`): Sie wirken nur im Browser, und im
 * Schlüssel der Antworten (`Genesis9antwortspeicher`, `G9antworten`) machten sie nach jedem Zug jede Stückantwort der Figur ungültig.
 *
 * KANTE (`kante`, Meter, > 0 = Stoff bleibt) — die Nullstelle einer stetigen Funktion der Körperkoordinaten (Kette, Anteil t, Rumpfhöhe h, Ruhe-x, vorn = cos
 * des Umfangswinkels), wie bei den eigenen Stücken (`EigenkleidschnittGLSL.kkKante`), aber jeder Schnitt einzeln an- und abschaltbar:
 *   Saum unten   (S − h)·L_Rumpf      nicht an Arm und Hand            Bund tiefer  (h − B)·L_Rumpf      nicht an Arm und Hand
 *   Ärmel        (Ä − t)·L_Arm        Arm und Rumpf (Schulter), Hand fällt ganz weg     Hosenbein  (B − t)·L_Bein   Bein, Fuß fällt ganz weg
 *   Ausschnitt   (h − Tiefe(x))·L_Rumpf   Rumpf, Hals, Kopf — Tiefe wie `kkHals`, außerhalb der Breite 0 (nur was über dem Halsansatz liegt)
 * Ein Punkt ohne Kette (nicht an Haut mit Körperkoordinaten gebunden) wird nie geschnitten.
 */
export class Dazschnittwerte {

    static PRAEFIX = Dazschnittfelder.PRAEFIX;
    /** Uniform-Wert „schneidet nicht“ (größer als jede Höhe/jeder Anteil). */
    static AUS = 99;
    static PRUEF = 50;
    /**
     * Rumpfpunkte tragen bis 15 cm um das Schultergelenk den Armanteil (`G9koerperkoordinaten.SCHULTER_M`) — in der A-Pose auch die Flanke UNTER der Achsel.
     * Ein kurzer Ärmel (12 %) schnitt dort ein Loch in die Seite (im Chrome gesehen, 25.10.2026, Basic Wear T Shirt, Seitenansicht). Unter der Rumpfhöhe
     * `ACHSEL_H` wächst die Kante deshalb um `ACHSEL_STEIGUNG` × Weg (in Rumpflänge) — stetig, der Schnitt läuft unter der Achsel aus. GESETZT (Augenmaß).
     */
    static ACHSEL_H = 0.18;
    static ACHSEL_STEIGUNG = 3;

    static schluessel(feld) {
        return `${Dazschnittwerte.PRAEFIX}${feld}`;
    }

    /** Die Regler des getragenen Stücks (Genesis 9: `inst.kleidung`). */
    static regler(inst, kennung) {
        return (inst?.kleidung || {})[kennung]?.regler || {};
    }

    static _begrenzen(f, w) {
        if (f.wahl) return Math.max(0, Math.min(f.wahl.length - 1, Math.round(w)));
        return Math.min(f.max, Math.max(f.min, w));
    }

    static wert(regler, feld) {
        const f = Dazschnittfelder.angaben(feld);
        if (!f) return null;
        const w = Number(regler?.[Dazschnittwerte.schluessel(feld)]);
        return Number.isFinite(w) ? Dazschnittwerte._begrenzen(f, w) : f.vorgabe;
    }

    /** Alle Felder `{feld: wert}` aus den Reglern eines Stücks. */
    static alle(regler) {
        return Object.fromEntries(Dazschnittfelder.FELDER.map(f => [f.feld, Dazschnittwerte.wert(regler, f.feld)]));
    }

    /** Einen Wert in die Regler des getragenen Stücks schreiben (begrenzt, auf den Schritt gerundet; die Vorgabe oder `null` löscht ihn); false ohne Stück. */
    static setzen(inst, kennung, feld, wert) {
        const getragen = (inst?.kleidung || {})[kennung];
        const f = Dazschnittfelder.angaben(feld);
        if (!getragen || !f) return false;
        getragen.regler = { ...(getragen.regler || {}) };
        const k = Dazschnittwerte.schluessel(feld), zahl = Number(wert);
        if (wert === null || wert === undefined || !Number.isFinite(zahl)) { delete getragen.regler[k]; return true; }
        const w = f.wahl ? Dazschnittwerte._begrenzen(f, zahl) : Number((Math.round(Dazschnittwerte._begrenzen(f, zahl) / f.schritt) * f.schritt).toFixed(4));
        if (Math.abs(w - f.vorgabe) < 1e-9) delete getragen.regler[k]; else getragen.regler[k] = w;
        return true;
    }

    /** Die Regler ohne die Eigen-Werte (für den Server). */
    static ohne(regler) {
        if (!regler || typeof regler !== 'object') return regler || {};
        const aus = {};
        for (const [k, v] of Object.entries(regler)) if (!k.startsWith(Dazschnittwerte.PRAEFIX)) aus[k] = v;
        return aus;
    }

    static _an(werte, feld) {
        const f = Dazschnittfelder.angaben(feld);
        return Math.abs(Number(werte[feld]) - f.aus) > 1e-9;
    }

    /** Schneidet irgendein Feld? */
    static schneidet(werte) {
        return ['ausschnitt_form', 'saum', 'aermel', 'bund', 'bein'].some(f => Dazschnittwerte._an(werte, f));
    }

    /** Braucht das Stück den Shader (ein Schnitt oder ein Abziehbild)? */
    static noetig(werte) {
        return Dazschnittwerte.schneidet(werte) || Number(werte.knoepfe) > 0 || (Number(werte.kragen) > 0 && Dazschnittwerte._an(werte, 'ausschnitt_form'));
    }

    /**
     * Werte → Uniforms (Längen in Metern; `AUS` = schneidet nicht):
     *   hals   (Form −1 aus | 0 rund, 1 V, 2 U, 3 Boot; Tiefe vorn; Tiefe hinten; Breite m)
     *   saum   (Saum unten S; Ärmel Ä; Bund B (−AUS aus); Hosenbein)
     *   band   (Saumbreite m; Saum hell −0,5…0,5; Kragenband m; Kragen hell)       leiste (Knöpfe; Länge Rumpf; Breite m; –)
     */
    static shaderwerte(werte) {
        const w = feld => Number(werte?.[feld] ?? Dazschnittfelder.angaben(feld).vorgabe);
        const an = feld => Dazschnittwerte._an(werte, feld);
        const A = Dazschnittwerte.AUS;
        return {
            hals: [an('ausschnitt_form') ? w('ausschnitt_form') - 1 : -1, w('ausschnitt'), w('ausschnitt_hinten'), w('ausschnitt_breite') / 1000],
            saum: [an('saum') ? w('saum') : A, an('aermel') ? w('aermel') : A, an('bund') ? w('bund') : -A, an('bein') ? w('bein') : A],
            band: [w('saumbreite') / 1000, w('saum_hell') / 100, w('kragen') / 1000, w('kragen_hell') / 100],
            leiste: [Math.round(w('knoepfe')), w('leiste'), w('leiste_breite') / 1000, 0],
        };
    }

    /** Ausschnittform wie `kkForm` (0 rund, 1 V, 2 U, 3 Boot). */
    static form(u, form) {
        const v = Math.min(Math.max(u, 0), 1);
        const s = form < 0.5 ? Math.sqrt(1 - v * v) : form < 1.5 ? 1 - v : form < 2.5 ? Math.sqrt(1 - v ** 4) : 1 - v ** 6;
        return u >= 1 ? 0 : s;
    }

    static _glatt(a, b, x) {
        const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
        return t * t * (3 - 2 * t);
    }

    /** Abstand zur Ausschnittkante (m, > 0 = Stoff) — `dkHals` im Shader. */
    static hals(h, x, vorn, s, laengen) {
        const u = Math.abs(x) / Math.max(0.5 * s.hals[3], 0.001);
        const g = Dazschnittwerte._glatt(-0.35, 0.35, vorn);
        const tiefe = s.hals[2] * Dazschnittwerte.form(u, 0) * (1 - g) + s.hals[1] * Dazschnittwerte.form(u, s.hals[0]) * g;
        return (h - tiefe) * laengen[0];
    }

    /**
     * Die Kante je Punkt (m, > 0 = bleibt) — `dkKante` im Shader. `kette` Nummer (`G9koerperkoordinaten.KETTEN`), `s` = `shaderwerte`, `laengen` [Rumpf, Arm,
     * Bein] m, `ansatz` die Rumpfhöhe des Halsansatzes unter dem Umfangswinkel des Punkts (`Koerperkoordinatenpunkte.ansatz`): ab dort misst der Ausschnitt.
     */
    static kante(kette, anteil, hoehe, x, vorn, s, laengen, ansatz = 0) {
        if (!(kette > 0)) return 1;
        const arm = kette === 2 || kette === 3, bein = kette === 4 || kette === 5, hand = kette === 8 || kette === 9, fuss = kette === 10 || kette === 11;
        const halszone = kette === 1 || kette === 6 || kette === 7;
        const [S, AE, B, BL] = s.saum, P = Dazschnittwerte.PRUEF;
        let f = 1;
        if (S < P && !arm && !hand) f = Math.min(f, (S - hoehe) * laengen[0]);
        if (AE < P && !bein && !fuss) {
            const achsel = halszone ? Math.max(0, hoehe - Dazschnittwerte.ACHSEL_H) * laengen[0] * Dazschnittwerte.ACHSEL_STEIGUNG : 0;
            f = Math.min(f, hand ? -1 : (AE - anteil) * laengen[1] + achsel);
        }
        if (B > -P && !arm && !hand) f = Math.min(f, (hoehe - B) * laengen[0]);
        if (BL < P && (bein || fuss)) f = Math.min(f, fuss ? -1 : (BL - anteil) * laengen[2]);
        if (s.hals[0] > -0.5 && halszone) f = Math.min(f, Dazschnittwerte.hals(hoehe - ansatz, x, vorn, s, laengen));
        return f;
    }

    /** Text neben dem Schieber; am Wert „aus“ steht „wie geliefert“. */
    static anzeige(f, wert) {
        const w = Number(wert);
        if (f.aus !== undefined && Math.abs(w - f.aus) < 1e-9) return 'wie geliefert';
        if (f.einheit === 'mm') return `${w.toFixed(1).replace('.', ',')} mm`;
        if (f.einheit === '%') return `${Math.round(w)} %`;
        if (f.einheit === 'Stück') return `${Math.round(w)} Stück`;
        return `${(w * 100).toFixed(1).replace('.', ',')} % ${f.einheit}`;
    }
}
