import { Bedienleiste } from './bedienleiste.js';

/**
 * Kamerabahn — Kamera-Keyframes setzen und löschen.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 94 Zeilen in drei
 * Menue-Zuhoerern, die sich Zeile fuer Zeile wiederholten —
 *
 *   * dreimal `e.stopPropagation()` plus das Schliessen aller Menuepunkte,
 *   * zweimal das Suchen des Theatre-Zustands im localStorage ueber
 *     `Object.keys(localStorage).find(k => k.includes('theatre') || …)`,
 *   * zweimal der Weg zu den Kameraspuren
 *     `state?.sheetsById?.Main?.sequence?.tracksByObject?.Camera?.trackData`.
 *
 * Warum ueberhaupt localStorage: Theatre.js bietet keine Schnittstelle zum
 * Loeschen einzelner Keyframes. Der Zustand liegt im Browser, wird dort
 * geaendert, und danach muss die Seite neu geladen werden — das ist kein
 * schoener Weg, aber der einzige, und er steht jetzt an EINER Stelle
 * beschrieben statt in zwei Kopien.
 */
export class Kamerabahn {

    /** Zeitfenster, in dem ein Keyframe als "an dieser Stelle" gilt. */
    static TOLERANZ_S = 0.05;

    /**
     * @param {Object} sequenz  sheet.sequence
     * @param {Object} kameraObjekt  das Theatre-Objekt der Kamera
     * @param {THREE.Camera} kamera
     * @param {Object} studio  das Theatre-Studio (fuer transaction)
     */
    constructor(sequenz, kameraObjekt, kamera, studio) {
        this.sequenz = sequenz;
        this.kameraObjekt = kameraObjekt;
        this.kamera = kamera;
        this.studio = studio;
    }

    verdrahten() {
        this._menue('menu-cam-set', () => this.setzen(this.sequenz.position));
        this._menue('menu-cam-delete-at', () => this.loeschenBei(this.sequenz.position));
        this._menue('menu-cam-clear', () => this.alleLoeschen());
        return this;
    }

    /**
     * Menuepunkt verdrahten: Klick nicht weitergeben und alle Menues zuklappen.
     * Diese drei Zeilen standen in jedem der drei Zuhoerer — das Zuklappen
     * selbst insgesamt fuenfmal in der Datei, deshalb kommt es aus Bedienleiste.
     */
    _menue(id, tun) {
        document.getElementById(id)?.addEventListener('click', (ereignis) => {
            ereignis.stopPropagation();
            Bedienleiste.menuesZuklappen();
            tun();
        });
    }

    /** Position und Bildwinkel der Kamera als Keyframe festhalten. */
    setzen(zeit) {
        this.sequenz.position = zeit;
        const { position, fov } = this.kameraObjekt.props;
        this.studio.transaction(({ set }) => {
            set(position.x, this.kamera.position.x);
            set(position.y, this.kamera.position.y);
            set(position.z, this.kamera.position.z);
            set(fov, this.kamera.fov);
        });
        const p = this.kamera.position;
        console.debug(`✓ Kamera-Keyframe bei ${zeit.toFixed(2)}s:`,
            `pos(${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)})`,
            `fov=${this.kamera.fov.toFixed(1)}`);
    }

    /** Keyframes in der Naehe dieser Zeit entfernen. */
    loeschenBei(zeit, toleranz = Kamerabahn.TOLERANZ_S) {
        this._spurenAendern(spuren => {
            let entfernt = 0;
            for (const spur of Object.values(spuren)) {
                if (!spur.keyframes) continue;
                const vorher = spur.keyframes.length;
                spur.keyframes = spur.keyframes.filter(
                    kf => Math.abs(kf.position - zeit) > toleranz);
                entfernt += vorher - spur.keyframes.length;
            }
            if (!entfernt) {
                console.debug(`Keine Kamera-Keyframes bei ${zeit.toFixed(2)}s`);
                return false;
            }
            console.debug(`✓ ${entfernt} Kamera-Keyframe(s) bei ${zeit.toFixed(2)}s `
                        + 'gelöscht — Seite wird neu geladen');
            return true;
        });
    }

    /** Alle Kamera-Keyframes entfernen. */
    alleLoeschen() {
        this._spurenAendern(spuren => {
            for (const spur of Object.values(spuren)) {
                if (spur.keyframes) spur.keyframes = [];
            }
            console.debug('✓ Alle Kamera-Keyframes gelöscht — Seite wird neu geladen');
            return true;
        });
    }

    // ------------------------------------------------------------------ intern

    /**
     * Kameraspuren aus dem Theatre-Zustand holen, aendern, zurueckschreiben.
     * Gibt der Rueckruf true zurueck, wird gespeichert und neu geladen.
     */
    _spurenAendern(aendern) {
        const schluessel = Object.keys(localStorage).find(
            k => k.toLowerCase().includes('theatre'));
        if (!schluessel) {
            console.warn('Kein Theatre-Zustand im localStorage');
            return;
        }
        try {
            const zustand = JSON.parse(localStorage.getItem(schluessel));
            const spuren = zustand?.sheetsById?.Main?.sequence
                ?.tracksByObject?.Camera?.trackData;
            if (!spuren) {
                console.warn('Keine Kameraspuren gefunden');
                return;
            }
            if (aendern(spuren)) {
                localStorage.setItem(schluessel, JSON.stringify(zustand));
                window.location.reload();
            }
        } catch (fehler) {
            console.error('Kameraspuren nicht änderbar:', fehler);
        }
    }
}
