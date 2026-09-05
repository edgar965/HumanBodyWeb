import { UmaFigur } from './umafigur.js';
import { Umaanimation } from './umaanimation.js';

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

    /** `beimAendern()` rechnet die Regler auf die Knochen und gleicht die Einzelregler an. */
    static fuellen(inst, behaelter, beimAendern) {
        behaelter.innerHTML = '';
        behaelter._zeilen = null;
        if (!inst.regler || !('height' in inst.dna)) return;
        inst._masseBasis = {
            cm: UmaFigur.hoehe(inst.netze) * 100,
            gelenke: Umaanimation.hoehe(inst),
        };
        const groesse = Umamasse._zeile('Größe', Math.round(inst.dna.height * 100), `${Umamasse.cm(inst)} cm`);
        groesse.input.addEventListener('input', () => {
            inst.dna.height = parseInt(groesse.input.value, 10) / 100;
            beimAendern();
            groesse.wert.textContent = `${Umamasse.cm(inst)} cm`;
        });
        const g = Umamasse.gewicht(inst);
        const gewicht = Umamasse._zeile('Gewicht', g, g);
        gewicht.input.addEventListener('input', () => {
            const wert = parseInt(gewicht.input.value, 10) / 100;
            for (const name of Umamasse.GEWICHT) if (name in inst.dna) inst.dna[name] = wert;
            beimAendern();
            gewicht.wert.textContent = gewicht.input.value;
        });
        behaelter.append(groesse.zeile, gewicht.zeile);
        behaelter._zeilen = { groesse, gewicht };
    }

    /**
     * Zentimeter aus der Gelenkspanne: beim Füllen wird einmal die sichtbare
     * Höhe (alle Punkte durch ihre Knochen) gemessen, danach genügt das billige
     * Verhältnis der Gelenkspannen — die Regler ziehen sich sonst zäh.
     */
    static cm(inst) {
        const basis = inst._masseBasis;
        if (!basis || !basis.gelenke) return '?';
        inst.group.updateMatrixWorld(true);
        return Math.round(basis.cm * Umaanimation.hoehe(inst) / basis.gelenke);
    }

    static gewicht(inst) {
        const werte = Umamasse.GEWICHT.filter(n => n in inst.dna).map(n => inst.dna[n]);
        return werte.length ? Math.round(werte.reduce((a, b) => a + b, 0) / werte.length * 100) : 50;
    }

    /** Nach einer Änderung an den Einzelreglern die beiden Zeilen nachziehen. */
    static angleichen(inst, behaelter) {
        const zeilen = behaelter._zeilen;
        if (!zeilen) return;
        zeilen.groesse.input.value = Math.round((inst.dna.height ?? 0.5) * 100);
        zeilen.groesse.wert.textContent = `${Umamasse.cm(inst)} cm`;
        const g = Umamasse.gewicht(inst);
        zeilen.gewicht.input.value = g;
        zeilen.gewicht.wert.textContent = g;
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
