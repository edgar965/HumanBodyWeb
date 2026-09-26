/**
 * Hover-Hilfe für die GarmentCode-Regler.
 *
 * Edgar, 08.09.2026: „ich verstehe das UI nicht: mach mir hover wenn ich
 * darüber gehe über alle Einstellungen des UIs."
 *
 * EINE EIGENE KARTE, KEIN `title`-ATTRIBUT
 * =======================================
 * Der Browser-Tooltip erscheint erst nach rund einer Sekunde, bricht lange
 * Texte nach eigenem Gutdünken um und kann nichts hervorheben. Die Texte
 * hier sind zwei bis vier Zeilen lang und tragen einen Warnhinweis, wenn
 * der Regler unter einer Bedingung NICHTS tut — das muss man sehen können.
 *
 * DIE KARTE HÄNGT AM BODY, NICHT IN DER ZEILE. Das Bedienfeld scrollt und
 * hat `overflow`; eine Karte darin wäre am Rand abgeschnitten. Sie wird
 * deshalb absolut zum Fenster gesetzt und dreht nach links oder oben, wenn
 * sie sonst hinausragen würde.
 *
 * DIE TEXTE KOMMEN VOM SERVER, fertig zusammengesetzt
 * (`Assets/GarmentCode/reglerhilfe.py`) — sonst entscheidet die Oberfläche
 * noch einmal über Reihenfolge und Wortwahl und läuft mit der Quelle
 * auseinander.
 */

class GarmentcodeReglerhilfe {
    /** Abstand der Karte vom Zeiger, in Bildpunkten. */
    static VERSATZ = 14;
    /** Wie schnell sie kommt. Kurz, aber nicht sofort — sonst flackert sie
     *  beim Überfahren einer Liste von Reglern. */
    static VERZOEGERUNG_MS = 180;

    constructor() {
        this.karte = null;
        this.zeitgeber = null;
    }

    _karteBauen() {
        if (this.karte) return this.karte;
        const karte = document.createElement('div');
        karte.className = 'gc-hilfekarte';
        karte.hidden = true;
        document.body.appendChild(karte);
        this.karte = karte;
        return karte;
    }

    /**
     * Eine Zeile mit Hilfe versehen. `hilfe` ist das Feld des Servers:
     * {text, bedingung, original}.
     */
    anhaengen(element, titel, hilfe) {
        if (!element || !hilfe) return;
        const inhalt = this._inhalt(titel, hilfe);
        if (!inhalt) return;
        if (hilfe.bedingung) element.classList.add('gc-bedingt');
        element.addEventListener('mouseenter', (e) => this._zeigen(inhalt, e));
        element.addEventListener('mousemove', (e) => this._nachziehen(e));
        element.addEventListener('mouseleave', () => this._verbergen());
    }

    _inhalt(titel, hilfe) {
        const teile = [];
        teile.push(`<div class="gc-hilfe-titel">${this._sicher(titel)}</div>`);
        if (hilfe.text) {
            teile.push(`<div class="gc-hilfe-text">${this._sicher(hilfe.text)}</div>`);
        }
        if (hilfe.bedingung) {
            teile.push('<div class="gc-hilfe-warnung">'
                + `${this._sicher(hilfe.bedingung)}</div>`);
        }
        if (hilfe.original) {
            teile.push('<div class="gc-hilfe-original">'
                + `${this._sicher(hilfe.original)}</div>`);
        }
        // Nur der Titel wäre keine Hilfe — dann lieber gar keine Karte.
        return (hilfe.text || hilfe.bedingung) ? teile.join('') : '';
    }

    /** Fremder Text geht nie unbesehen ins HTML. */
    _sicher(text) {
        const kasten = document.createElement('div');
        kasten.textContent = String(text ?? '');
        return kasten.innerHTML;
    }

    _zeigen(inhalt, ereignis) {
        clearTimeout(this.zeitgeber);
        this.zeitgeber = setTimeout(() => {
            const karte = this._karteBauen();
            karte.innerHTML = inhalt;
            karte.hidden = false;
            this._setzen(ereignis);
        }, GarmentcodeReglerhilfe.VERZOEGERUNG_MS);
    }

    _nachziehen(ereignis) {
        if (this.karte && !this.karte.hidden) this._setzen(ereignis);
    }

    /**
     * Lage der Karte. Gemessen wird die Karte selbst (`offsetWidth`), nicht
     * geschätzt: Die Texte sind verschieden lang, und eine geschätzte
     * Breite schiebt kurze Karten unnötig weit nach links.
     */
    _setzen(ereignis) {
        const karte = this.karte;
        if (!karte) return;
        const versatz = GarmentcodeReglerhilfe.VERSATZ;
        const breite = karte.offsetWidth;
        const hoehe = karte.offsetHeight;
        let x = ereignis.clientX + versatz;
        let y = ereignis.clientY + versatz;
        if (x + breite > window.innerWidth - 8) {
            x = Math.max(8, ereignis.clientX - versatz - breite);
        }
        if (y + hoehe > window.innerHeight - 8) {
            y = Math.max(8, ereignis.clientY - versatz - hoehe);
        }
        karte.style.left = `${x}px`;
        karte.style.top = `${y}px`;
    }

    _verbergen() {
        clearTimeout(this.zeitgeber);
        if (this.karte) this.karte.hidden = true;
    }
}

export const garmentcodeReglerhilfe = new GarmentcodeReglerhilfe();
