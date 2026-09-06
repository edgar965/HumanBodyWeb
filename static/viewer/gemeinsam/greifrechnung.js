/**
 * Greifrechnung — was eine Mausbewegung beim Greifen bedeutet.
 *
 * WARUM EIGENES MODUL (06.09.2026, Edgar: „ich verstehe nicht G zum Translate,
 * bei Klick auf G und dann Maus tut sich nichts"): Das Greifen selbst hängt an
 * Three.js und am Browser. Die Entscheidungen darin — welche Achse eine Taste
 * meint, wie aus zwei Bildschirmpunkten ein Winkel oder ein Faktor wird, was
 * ein unbrauchbarer Wert ist — hängen an nichts davon und stehen deshalb hier,
 * wo sie sich prüfen lassen.
 *
 * Alle Funktionen rechnen im Bildschirmraum (Pixel, y zeigt nach unten).
 */
export class Greifrechnung {

    /** Kleiner Radius um die Objektmitte: dort ist der Winkel Zufall. */
    static MINDESTABSTAND = 8;

    /** Ein Faktor darunter oder darüber ist keine Absicht mehr. */
    static KLEINSTER = 0.01;
    static GROESSTER = 100;

    /**
     * Welche Achse eine Taste während des Greifens meint.
     * @returns 'x' | 'y' | 'z' | null   (null heißt: frei in der Bildebene)
     */
    static achse(taste) {
        const t = String(taste || '').toLowerCase();
        return (t === 'x' || t === 'y' || t === 'z') ? t : null;
    }

    /**
     * Eine Verschiebung auf eine Achse beschränken.
     * @param delta  {x, y, z} in Weltkoordinaten
     * @param achse  'x' | 'y' | 'z' | null
     */
    static maskieren(delta, achse) {
        const d = { x: Number(delta?.x) || 0, y: Number(delta?.y) || 0, z: Number(delta?.z) || 0 };
        if (!achse) return d;
        return { x: achse === 'x' ? d.x : 0,
                 y: achse === 'y' ? d.y : 0,
                 z: achse === 'z' ? d.z : 0 };
    }

    /**
     * Drehwinkel im Bogenmaß: der Winkel, um den der Zeiger um die Objektmitte
     * gewandert ist. Im Bildschirmraum zeigt y nach unten, deshalb das
     * Vorzeichen — gegen den Uhrzeigersinn ist positiv wie in Three.js.
     *
     * Liegt einer der Punkte praktisch auf der Mitte, ist der Winkel Zufall
     * und wird zu 0: sonst springt die Figur beim ersten Pixel um 180 Grad.
     */
    static winkel(mitte, von, nach) {
        const a = Greifrechnung._abstand(mitte, von);
        const b = Greifrechnung._abstand(mitte, nach);
        if (!isFinite(a) || !isFinite(b)) return 0;
        if (a < Greifrechnung.MINDESTABSTAND || b < Greifrechnung.MINDESTABSTAND) return 0;
        const w1 = Math.atan2(-(von.y - mitte.y), von.x - mitte.x);
        const w2 = Math.atan2(-(nach.y - mitte.y), nach.x - mitte.x);
        let d = w2 - w1;
        while (d > Math.PI) d -= 2 * Math.PI;
        while (d < -Math.PI) d += 2 * Math.PI;
        return d;
    }

    /**
     * Skalierfaktor: wie viel weiter der Zeiger jetzt von der Mitte weg ist.
     * 1 heißt „unverändert" — auch dann, wenn nichts Brauchbares herauskommt.
     */
    static faktor(mitte, von, nach) {
        const a = Greifrechnung._abstand(mitte, von);
        const b = Greifrechnung._abstand(mitte, nach);
        if (!isFinite(a) || !isFinite(b)) return 1;
        if (a < Greifrechnung.MINDESTABSTAND) return 1;
        const f = b / a;
        if (!isFinite(f) || f < Greifrechnung.KLEINSTER || f > Greifrechnung.GROESSTER) return 1;
        return f;
    }

    /** Die Zeile, die während des Greifens im Bild steht. */
    static anzeige(modus, wert, achse) {
        const wo = achse ? ' ' + achse.toUpperCase() : '';
        if (modus === 'rotate') {
            return `Drehen${wo}: ${(wert * 180 / Math.PI).toFixed(1)}°`;
        }
        if (modus === 'scale') return `Größe${wo}: ×${wert.toFixed(3)}`;
        const d = wert || { x: 0, y: 0, z: 0 };
        return `Verschieben${wo}: ${d.x.toFixed(2)} / ${d.y.toFixed(2)} / ${d.z.toFixed(2)} m`;
    }

    static _abstand(a, b) {
        const dx = Number(b?.x) - Number(a?.x), dy = Number(b?.y) - Number(a?.y);
        return Math.sqrt(dx * dx + dy * dy);
    }
}
