import { Mesh3daifigurbewegung } from '../mesh3dai/mesh3daifigurbewegung.js';
import { Ai2d3dzeile1form } from './ai2d3dzeile1form.js';

/**
 * Ai2d3dzeile1bewegung — die Abspielleiste der Zeile 1 (Genesis-Figur der Mesh-Methode): dieselbe Bewegung wie Zeile 2 (`Mesh3daifigurbewegung`, Regler, Haut und Stücke aus den
 * Fotos), dazu die Form der Zeile 1 auf Körper, Anhängen und Stücken (`Ai2d3dzeile1form`, 31.10.2026 nachts). Genesis 9 baut in zwei Zügen mit neuen Netzen
 * (`Mesh3daifigurbewegung._pruefen`) — jedes neue Netz bekommt die Form, bevor es gezeichnet wird.
 */
export class Ai2d3dzeile1bewegung extends Mesh3daifigurbewegung {

    async _figurBauen(q) {
        const gebaut = await super._figurBauen(q);
        this._form = gebaut && q.zeile1 ? new Ai2d3dzeile1form(q.zeile1, this._abbildung) : null;
        if (gebaut && !q.zeile1) console.warn('Ai2d3dzeile1bewegung: keine Form der Zeile 1 (zeile1_form) — die Figur bewegt sich mit den Reglern allein');
        return gebaut;
    }

    _pruefen() {
        super._pruefen();
        this._formLegen();
    }

    _bild() {
        this._formLegen();
        super._bild();
    }

    _formLegen() {
        const m = this.modell;
        if (!this._form || !m?.bodyMesh) return;
        for (const netz of [m.bodyMesh, ...Object.values(m.anhangNetze || {}), ...this.kleider.map(k => k.mesh)]) this._form.anwenden(netz?.geometry);
    }
}
