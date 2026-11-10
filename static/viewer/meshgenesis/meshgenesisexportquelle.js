import { Exportleistefigur } from '../exportleiste/exportleistefigur.js';
import { Meshgenesisbewegungsfigur } from './meshgenesisbewegungsfigur.js';

/**
 * Meshgenesisexportquelle — die Figur der Testseite von Mesh-Genesis für die Exportleiste (31.10.2026, `Exportleiste`, Server `Meshgenesistestexportquelle`).
 *
 * Exportiert wird die Ausgabe als Genesis-Figur mit den Stücken der KI — dieselbe, die die Standardanimation bewegt (`Meshgenesisfigurbewegung`: Regler der Figur, Haut, Anatomie-Stück,
 * Kleider nach der Wahl der Karte „Kleider und Bestandteile“). Sie entsteht erst beim ersten Abspielen; hier wird sie bei Bedarf gebaut und ganz abgewartet (feine Stufe), danach
 * noch einmal `vorbereiten`, damit die Stücke am Skelett der feinen Stufe hängen (Genesis 9 baut dort neue Knochen). Der BVH-Vorschlag ist die Standardanimation der Leiste.
 */
export class Meshgenesisexportquelle {

    /** @param bewegung `() => Meshgenesisfigurbewegung | null` (die Seite legt sie im Konstruktor an) */
    constructor(bewegung) {
        this.bewegung = bewegung;
    }

    bvh() {
        return this.bewegung()?.wahl || null;
    }

    /** @param angaben `{bvh}`: Vorgabe des Bereichs (`zustand.bvh_vorgabe`) — für eine Figur ohne eigene Leiste (`Fotogenesisexportfigur`) */
    async modell(angaben = {}) {
        const b = this.bewegung();
        if (!b) throw new Error('Diese Seite hat keine Genesis-Figur in der Ausgabe');
        if (!b.wahl && angaben.bvh) b.wahlSetzen(angaben.bvh);
        if (!b.wahl) throw new Error('Die Standardanimation wird noch gelesen — gleich noch einmal');
        await b.vorbereiten();
        if (!b.modell) throw new Error(b.text || 'Für diesen Test gibt es keine Genesis-Figur');
        await Exportleistefigur.vollBauen(b.modell);
        await b.vorbereiten();
        const m = b.modell;
        return { inst: m, figur: m.figur, regler: m.regler || {}, hoehe_m: Meshgenesisbewegungsfigur.hoehe(m) };
    }
}
