import { Eigenkleidfelder } from './eigenkleidfelder.js';
import { Eigenkleidstoff } from './eigenkleidstoff.js';

/**
 * Eigenkleidwerte — Werte der eigenen Stücke lesen, schreiben und in Shader-Uniforms umrechnen (Stufe K2a, 25.10.2026; Konzept
 * `Docu/konzepte/2026-10-25_eigene-kleider-konzept.md`, Abschnitt 3). Die Felder selbst: `Eigenkleidfelder`. Ohne Three.js, in Node prüfbar.
 *
 * WERTE stehen in den Reglern der Figur (`inst.regler`) unter `kleid:<art>:<feld>` — so reisen sie mit „Modell speichern“. Der Server übergeht Namen, die er nicht kennt
 * (`G9formung.aus_abfrage`: kein Kanal, kein Eigen-, Familien-, Alters- oder Anhangregler → `continue`). Ein fehlender Eintrag heißt Vorgabe; `kleid:<art>:an` = 1 heißt
 * „angelegt“. Ablegen nimmt nur `an` heraus — die übrigen Werte bleiben, ein erneutes Anlegen bringt dasselbe Stück zurück.
 */
export class Eigenkleidwerte {

    static PRAEFIX = 'kleid:';
    static ARTEN = Eigenkleidfelder.ARTEN;
    static BLOECKE = Eigenkleidfelder.BLOECKE;
    static FELDER = Eigenkleidfelder.FELDER;
    static MINDEST_MM = 1;

    static schluessel(art, feld) {
        return `${Eigenkleidwerte.PRAEFIX}${art}:${feld}`;
    }

    static angaben(art, feld) {
        return (Eigenkleidwerte.FELDER[art] || []).find(f => f.feld === feld) || null;
    }

    /** Wirkt das Feld bei diesen Werten (`Eigenkleidfelder.AKTIV`; ohne Regel immer)? */
    static aktiv(art, feld, werte) {
        const regel = Eigenkleidfelder.AKTIV[feld];
        if (!regel || !werte) return true;
        const w = new Proxy(werte, { get: (z, k) => Number(z[k] ?? Eigenkleidwerte.angaben(art, k)?.vorgabe ?? 0) });
        return Boolean(regel(w, art));
    }

    static an(inst, art) {
        return Number(inst?.regler?.[Eigenkleidwerte.schluessel(art, 'an')]) >= 0.5;
    }

    /** Die angelegten Arten der Figur. */
    static getragen(inst) {
        return Object.keys(Eigenkleidwerte.ARTEN).filter(art => Eigenkleidwerte.an(inst, art));
    }

    static _begrenzen(f, w) {
        if (f.farbe) return f.leer && w < 0 ? -1 : Math.round(w) & 0xffffff;
        if (f.wahl) return Math.max(0, Math.min(f.wahl.length - 1, Math.round(w)));
        return Math.min(f.max, Math.max(f.min, w));
    }

    /** Ein Wert aus den Reglern, auf den Bereich des Felds begrenzt — ohne Eintrag die Vorgabe. */
    static wert(inst, art, feld) {
        const f = Eigenkleidwerte.angaben(art, feld);
        if (!f) return null;
        const w = Number(inst?.regler?.[Eigenkleidwerte.schluessel(art, feld)]);
        return Number.isFinite(w) ? Eigenkleidwerte._begrenzen(f, w) : f.vorgabe;
    }

    static alle(inst, art) {
        return Object.fromEntries((Eigenkleidwerte.FELDER[art] || []).map(f => [f.feld, Eigenkleidwerte.wert(inst, art, f.feld)]));
    }

    /** Einen Wert in die Regler schreiben (begrenzt, auf den Schritt gerundet); `null` = zurück auf die Vorgabe. Löst keinen Neubau aus. */
    static setzen(inst, art, feld, wert) {
        const f = Eigenkleidwerte.angaben(art, feld);
        inst.regler = inst.regler || {};
        const k = Eigenkleidwerte.schluessel(art, feld);
        const zahl = Number(wert);
        if (!f || wert === null || wert === undefined || !Number.isFinite(zahl)) { delete inst.regler[k]; return; }
        const w = Eigenkleidwerte._begrenzen(f, zahl);
        inst.regler[k] = f.farbe || f.wahl ? w : Number((Math.round(w / f.schritt) * f.schritt).toFixed(4));
    }

    static anlegen(inst, art) {
        inst.regler = inst.regler || {};
        inst.regler[Eigenkleidwerte.schluessel(art, 'an')] = 1;
    }

    static ablegen(inst, art) {
        if (inst?.regler) delete inst.regler[Eigenkleidwerte.schluessel(art, 'an')];
    }

    /** Text neben dem Schieber: „30,0 % Arm“, „6,0 mm“, „35 %“, „4 Stück“. */
    static anzeige(f, wert) {
        const w = Number(wert);
        if (f.einheit === 'mm' || f.einheit === 'cm') return `${w.toFixed(1).replace('.', ',')} ${f.einheit}`;
        if (f.einheit === '%') return `${Math.round(w)} %`;
        if (f.einheit === 'Stück') return `${Math.round(w)} Stück`;
        if (f.einheit === 'je cm') return `${w.toFixed(1).replace('.', ',')} je cm`;
        return `${(w * 100).toFixed(1).replace('.', ',')} % ${f.einheit}`;
    }

    static hex(zahl) {
        return `#${(Math.round(Number(zahl)) & 0xffffff).toString(16).padStart(6, '0')}`;
    }

    static ausHex(text) {
        const zahl = parseInt(String(text || '').replace('#', ''), 16);
        return Number.isFinite(zahl) ? zahl : null;
    }

    /**
     * Werte → Uniforms (Belegung in `EigenkleidGLSL`/`EigenkleidschnittGLSL`; Längen in Metern):
     *   saum    Oberteil (Saum unten, Ärmel, –, –) bzw. Hose (Bund, Beinlänge, –, –) als Anteile
     *   sitz    Oberteil (oben, Mitte, unten, Ärmel) bzw. Hose (Bund, Gesäß, Bein, –), m, je mindestens `MINDEST_MM`
     *   hals    (Form, Tiefe vorn, Tiefe hinten, Breite m)          kragen  (Stehkragenhöhe m, Leiste Länge (Anteil), Knöpfe, Leistenbreite m)
     *   band    (Saumbreite m, Helligkeit −0,5…0,5, –, –)           bruecke (Abstand m, Ausbreitung m, Glättung 0…1, Fall m je m)
     *   falten, rauheit 0…1, farbe 0xRRGGBB
     *   Socken: saum (Bündchen als Beinanteil, –, –, –), sitz (Fuß, Schaft, –, –)
     * Seit 25.10.2026 nachts zusätzlich (nur neue Schlüssel, die alten unverändert): `stoff` (Form `Stoffarten.werte`, für `Stoffshader.werte`), `metall` 0…1,
     * `relief` (Faktor auf Wulst, Knöpfe, Falten) und `gestalt` (Kragen: Form, Höhe m, Spitze m, Abstand m).
     */
    static shaderwerte(art, werte) {
        const w = feld => Number(werte?.[feld] ?? Eigenkleidwerte.angaben(art, feld)?.vorgabe ?? 0);
        const m = feld => Math.max(Eigenkleidwerte.MINDEST_MM, w(feld)) / 1000;
        const stoff = Eigenkleidstoff.stoff(Object.fromEntries((Eigenkleidwerte.FELDER[art] || []).map(f => [f.feld, w(f.feld)])));
        const aus = {
            band: [w('saumbreite') / 1000, w('saum_hell') / 100, 0, 0],
            bruecke: [w('abstand') / 1000, w('ausbreitung') / 100, w('glaettung') / 100, w('fall') / 100],
            falten: Math.max(0, w('falten')) / 100, rauheit: Math.min(1, Math.max(0, w('rauheit') / 100)), farbe: Math.round(w('farbe')) & 0xffffff,
            stoff, metall: stoff.metall, relief: Math.max(0, stoff.relief), gestalt: [0, 0, 0, 0], aermelform: [0, 0, 0, 0],
        };
        if (art === 'hose') {
            return { ...aus, saum: [w('bund'), w('bein'), 0, 0], sitz: [m('sitz_bund'), m('sitz_gesaess'), m('sitz_bein'), 0], hals: [0, 0, 0, 0], kragen: [0, 0, 0, 0] };
        }
        if (art === 'socke') {
            return { ...aus, saum: [w('buendchen'), 0, 0, 0], sitz: [m('sitz_fuss'), m('sitz_bein'), 0, 0], hals: [0, 0, 0, 0], kragen: [0, 0, 0, 0] };
        }
        return {
            ...aus, saum: [w('saum'), w('aermel'), 0, 0], sitz: [m('sitz_oben'), m('sitz_mitte'), m('sitz_unten'), m('sitz_aermel')],
            hals: [w('ausschnitt_form'), w('ausschnitt'), w('ausschnitt_hinten'), w('ausschnitt_breite') / 1000],
            kragen: [w('kragen') / 1000, w('leiste'), Math.round(w('knoepfe')), w('leiste_breite') / 1000],
            gestalt: [Math.round(w('kragen_form')), w('kragen_hoehe') / 1000, w('kragen_spitze') / 1000, w('kragen_abstand') / 1000],
            aermelform: [w('aermel_weite') / 1000, Math.round(w('aermel_falten')), w('aermel_faltentiefe') / 1000, art === 'kleid' ? 1 : 0],   // w: Taillennaht
        };
    }
}
