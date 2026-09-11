import { types } from '@theatre/core';
import { Sequenzspuren } from '../laden/sequenzspuren.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Animationsspur — die geladene BVH-Animation als Spur in der Zeitleiste.
 *
 * ANLASS (Edgar, 11.09.2026): „auch die Animation erscheint nicht in der
 * timeline". Die Animation lief bis dahin an Theatre.js vorbei: ein
 * Three.js-Mixer, den die Bildschleife mit der Uhr weiterdrehte, und daneben
 * die Theatre-Sequenz für Kamera und Lichter — zwei Uhren, die der Abspieler
 * gleichzeitig startete und anhielt. In der Zeitleiste war davon nichts zu
 * sehen, und wer dort den Zeiger zog, bewegte die Figur nicht.
 *
 * JETZT FÜHRT THEATRE DIE ZEIT. Das Objekt „Animation" hat einen Wert `zeit`
 * (Sekunden im Clip) mit zwei Schlüsselbildern: 0 s → 0 und Clipende → Dauer,
 * geradlinig. Jede Änderung des Werts — beim Abspielen der Sequenz wie beim
 * Ziehen des Zeigers — stellt den Mixer auf diese Zeit. Damit gilt: Wer die
 * Schlüsselbilder verschiebt, dehnt oder staucht die Animation; wer sie
 * löscht, friert sie ein. Das ist Theatre-Semantik, keine Sonderregel.
 *
 * EIN OBJEKT, NICHT EINES JE CLIP: Der Schlüssel ist immer „Animation", der
 * Clipname steht als Beschriftung am Wert. Sonst bliebe je geladenem Clip
 * ein totes Objekt in der Zeitleiste zurück; `reconfigure` setzt den
 * Wertebereich für den neuen Clip.
 *
 * Fehlt die interne Schnittstelle (`Sequenzspuren`), bleibt es bei der Uhr:
 * `aktiv` ist dann false, und die Bildschleife dreht den Mixer wie zuvor.
 */
export class Animationsspur {

    static SCHLUESSEL = 'Animation';
    static MINDESTLAENGE_S = 0.01;

    constructor(blatt) {
        this.blatt = blatt;
        this.objekt = null;
        this.abmelden = null;
    }

    /** Ob Theatre gerade die Zeit der Animation führt. */
    get aktiv() {
        return Boolean(this.abmelden);
    }

    /**
     * Spur für einen Clip anlegen: `zeit` 0…dauer, Schlüsselbilder an beiden
     * Enden; `anwenden(zeit)` läuft bei jeder Änderung.
     * @returns das Theatre-Objekt (oder null ohne Blatt)
     */
    anlegen(name, dauer, anwenden) {
        this.loesen();
        if (!this.blatt) return null;
        const laenge = Math.max(Number(dauer) || 0, Animationsspur.MINDESTLAENGE_S);
        this.objekt = this.blatt.object(Animationsspur.SCHLUESSEL, {
            zeit: types.number(0, { range: [0, laenge], label: name }),
        }, { reconfigure: true });
        const gelungen = Sequenzspuren.setzen(this.objekt, [
            [['zeit'], 0, 0, Sequenzspuren.LINEAR],
            [['zeit'], laenge, laenge, Sequenzspuren.LINEAR],
        ]);
        if (gelungen) {
            this.abmelden = this.objekt.onValuesChange(({ zeit }) => anwenden(zeit));
            Protokoll.debug('animationsspur', `✓ Spur „${name}": 0–${laenge.toFixed(2)} s`);
        }
        return this.objekt;
    }

    /** Die Kopplung lösen — ein alter Mixer soll keine Zeiten mehr bekommen. */
    loesen() {
        if (this.abmelden) this.abmelden();
        this.abmelden = null;
    }
}
