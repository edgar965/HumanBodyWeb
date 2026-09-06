import { UmaFigur } from './umafigur.js';
import { Umaanimation } from './umaanimation.js';
import { state } from '../state.js';

/**
 * Umamasse — Größe und Gewicht einer UMA-Figur als zwei Regler ganz oben.
 *
 * WARUM (06.09.2026, Edgar: „Wo ist der Größen-, Gewichtregler??"): UMA hat
 * beides, aber verstreut — `height` unter 18 bis 22 Körperreglern, das
 * Gewicht auf `upperWeight`, `lowerWeight`, `belly` und `waist` verteilt.
 * Hier stehen sie vorn: Größe zeigt Zentimeter (aus der sichtbaren Höhe der
 * Figur gerechnet), Gewicht stellt die vier Regler gemeinsam.
 */
export class Umamasse {

    static GEWICHT = ['upperWeight', 'lowerWeight', 'belly', 'waist'];
    // Muskeln (06.09.2026, Edgar: „hast du kein Muskeltonus?") — UMA führt sie
    // als zwei Regler unter 22 Körperreglern; hier gemeinsam, wie das Gewicht.
    static MUSKELN = ['upperMuscle', 'lowerMuscle'];

    /** `beimAendern()` rechnet die Regler auf die Knochen und gleicht die Einzelregler an. */
    static fuellen(inst, behaelter, beimAendern) {
        behaelter.innerHTML = '';
        behaelter._zeilen = null;
        if (!inst.regler || !('height' in inst.dna)) return;
        // Nur in der Ruhelage messen: Läuft eine Animation, ist die Figur
        // gebeugt und die Gelenkspanne kürzer — die Anzeige sagte dann 101 cm
        // statt 168 (06.09.2026). Die alte Basis gilt dann weiter.
        if (!inst._masseBasis || state._animatedCharId !== inst.id) {
            inst._masseBasis = {
                cm: UmaFigur.hoehe(inst.netze) * 100,
                gelenke: Umaanimation.hoehe(inst),
            };
        }
        const groesse = Umamasse._zeile('Größe', Math.round(inst.dna.height * 100), `${Umamasse.cm(inst)} cm`);
        groesse.input.addEventListener('input', () => {
            inst.dna.height = parseInt(groesse.input.value, 10) / 100;
            beimAendern();
            groesse.wert.textContent = `${Umamasse.cm(inst)} cm`;
        });
        const gewicht = Umamasse._sammelzeile(inst, 'Gewicht', Umamasse.GEWICHT, beimAendern);
        const muskeln = Umamasse._sammelzeile(inst, 'Muskeln', Umamasse.MUSKELN, beimAendern);
        behaelter.append(groesse.zeile, gewicht.zeile, muskeln.zeile);
        behaelter._zeilen = { groesse, gewicht, muskeln };
    }

    /** Ein Regler, der mehrere DNA-Werte gemeinsam stellt (Gewicht, Muskeln). */
    static _sammelzeile(inst, beschriftung, namen, beimAendern) {
        const wert = Umamasse.mittel(inst, namen);
        const zeile = Umamasse._zeile(beschriftung, wert, wert);
        zeile.input.addEventListener('input', () => {
            const neu = parseInt(zeile.input.value, 10) / 100;
            for (const name of namen) if (name in inst.dna) inst.dna[name] = neu;
            beimAendern();
            zeile.wert.textContent = zeile.input.value;
        });
        return zeile;
    }

    /**
     * Zentimeter aus der Gelenkspanne: beim Füllen wird einmal die sichtbare
     * Höhe (alle Punkte durch ihre Knochen) gemessen, danach genügt das billige
     * Verhältnis der Gelenkspannen — die Regler ziehen sich sonst zäh.
     */
    static cm(inst) {
        const basis = inst._masseBasis;
        if (!basis || !basis.gelenke) return '?';
        if (state._animatedCharId === inst.id) return Math.round(basis.cm);   // gebeugt misst falsch
        inst.group.updateMatrixWorld(true);
        return Math.round(basis.cm * Umaanimation.hoehe(inst) / basis.gelenke);
    }

    /** Mittel der genannten DNA-Werte in 0–100; 50, wenn die Rasse keinen davon kennt. */
    static mittel(inst, namen) {
        const werte = namen.filter(n => n in inst.dna).map(n => inst.dna[n]);
        return werte.length ? Math.round(werte.reduce((a, b) => a + b, 0) / werte.length * 100) : 50;
    }

    static gewicht(inst) {
        return Umamasse.mittel(inst, Umamasse.GEWICHT);
    }

    /** Nach einer Änderung an den Einzelreglern die drei Zeilen nachziehen. */
    static angleichen(inst, behaelter) {
        const zeilen = behaelter._zeilen;
        if (!zeilen) return;
        zeilen.groesse.input.value = Math.round((inst.dna.height ?? 0.5) * 100);
        zeilen.groesse.wert.textContent = `${Umamasse.cm(inst)} cm`;
        for (const [name, namen] of [['gewicht', Umamasse.GEWICHT], ['muskeln', Umamasse.MUSKELN]]) {
            const wert = Umamasse.mittel(inst, namen);
            zeilen[name].input.value = wert;
            zeilen[name].wert.textContent = wert;
        }
    }

    static _zeile(beschriftung, wert, anzeige) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        zeile.innerHTML = `<label>${beschriftung}</label>`
            + `<input type="range" min="0" max="100" step="1" value="${wert}">`
            + `<span class="slider-val">${anzeige}</span>`;
        return { zeile, input: zeile.querySelector('input'), wert: zeile.querySelector('.slider-val') };
    }
}
