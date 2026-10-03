import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';

/**
 * Engine2d3dKleidernetzansicht — ein Auftrag OHNE Figur zeigt beim Öffnen sein Netz.
 *
 * Edgar, 03.10.2026: „speichere für jeden Job die beste Figur, so dass ich die beim Laden schnell sehen kann … Meldung:
 * Die Figur wird erst aufgebaut" (Auftrag `2026.10.02.22.20.52`). Die Vergleichsläufe (TRELLIS, Pixal3D) haben nur den Schritt „Netz"
 * gerechnet: Es gibt weder eine Stellung (Schritt „Körper") noch ein Modell des Stands (`Engine2d3dKleiderstandmodell` braucht die
 * Stellung). Die Bühne meldete „Noch keine Figur — erst nach der Körperkette." und blieb leer — während das Netz (`netz/mesh.glb`,
 * das Beste, was der Auftrag hat) längst geladen war, nur mit dem Schalter „Mesh" aus.
 *
 * Jetzt: Hat der Auftrag nichts als das Netz, schaltet diese Klasse „Mesh" EINMAL von selbst ein und richtet die Kamera auf das Netz
 * (es steht wie immer `Meshfigurbuehne.ABSTAND` links der Mitte). Wer „Mesh" danach ausschaltet, bleibt dabei; sobald der Auftrag
 * eine Figur bekommt, ist hier nichts mehr zu tun (Netz links, Modell in der Mitte — die Anordnung der Bühne).
 */
export class Engine2d3dKleidernetzansicht {

    static MELDUNG = 'Nur das Netz aus den Fotos (Schritt „Netz“) — die Figur entsteht erst mit dem Schritt „Körper“.';
    /** Der Text der Bühne, den diese Klasse ersetzt (`Meshfigurbuehne.zeigen`). */
    static LEER = 'Noch keine Figur';
    /** Höhe der Mitte und Kamerahöhe über dem Boden — das Netz ist auf die Körpergröße (1,7 m) skaliert und steht auf 0. */
    static MITTE_Y = 0.85;
    static KAMERA = { y: 0.95, z: 4.4 };

    constructor(seite, buehne) {
        this.seite = seite;
        this.buehne = buehne;
        this._gezeigt = false;
    }

    /** Hat der Auftrag außer dem Netz nichts zu zeigen — weder eine Stellung noch ein Modell noch eine Runde? */
    static nurNetz(z) {
        const e = z.ergebnis || {};
        return !!e.netz && !!(z.eingang || {}).datei && !Object.keys(z.stellung || {}).length && !z.standmodell
            && !(e.iterationen || []).length;
    }

    /** Bei jedem Stand der Seite. Die Bühne setzt ihre Meldung davor (`Engine2d3dKleiderseite.zeigen`), hier wird sie ersetzt. */
    zeigen(z) {
        if (!Engine2d3dKleidernetzansicht.nurNetz(z)) return;
        const hinweis = this.buehne.hinweis;
        if (hinweis && hinweis.textContent.startsWith(Engine2d3dKleidernetzansicht.LEER)) {
            this.buehne._melden(Engine2d3dKleidernetzansicht.MELDUNG);
        }
        if (this._gezeigt || !this.buehne.netze?.gruppe) return;
        this._gezeigt = true;
        this.buehne.schalter?.setzen('mesh', true);
        this.buehne._sichtbarkeit();
        this._ausrichten();
    }

    /** Die Kamera auf das Netz (links der Mitte) statt auf die Mitte, in der keine Figur steht. */
    _ausrichten() {
        const x = -Meshfigurbuehne.ABSTAND, k = Engine2d3dKleidernetzansicht;
        this.buehne.steuerung.target.set(x, k.MITTE_Y, 0);
        this.buehne.kamera.position.set(x, k.KAMERA.y, k.KAMERA.z);
    }
}
