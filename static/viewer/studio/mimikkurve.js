/**
 * Mimikkurve — die Gewichte der Mimikspur an einem Bild, zwischen den
 * Schlüsselbildern interpoliert.
 *
 * Edgar, 13.09.2026: „in der Animationsleiste für Gesicht setze ich eine Pose
 * zu einem Zeitpunkt, eine andere für einen anderen, und die interpolierst
 * zwischen den 2 Posen? … die letzte Mimik bleibt am Modell."
 *
 * Ein Schlüsselbild: `{ frame, gewichte: {einheit: −1…+1}, staerke: 0…1,
 * uebergang: 'weich' | 'linear', halten: Sekunden }`. Vor dem ersten ist das
 * Gesicht neutral, nach dem letzten bleibt die letzte Pose. Zwischen zweien:
 * die erste hält `halten` Sekunden, dann läuft der Übergang bis zum zweiten —
 * seine Art (`uebergang`) steht am Ziel. Interpoliert werden die Gewichte auf
 * den Einheiten, nicht die Knochen: so mischen sich zwei Posen wie in MB-Lab.
 * Ohne Importe — der Test rechnet in Node (`test_js_mimikkurve`).
 */
export class Mimikkurve {

    /** Gewichte (Pose · Stärke) eines Schlüsselbilds. */
    static pose(schluessel) {
        const staerke = schluessel.staerke ?? 1;
        /** @type {Object<string, number>} */
        const aus = {};
        for (const [einheit, g] of Object.entries(schluessel.gewichte || {})) {
            if (g) aus[einheit] = g * staerke;
        }
        return aus;
    }

    /** Anteil 0…1 des Übergangs — weich (Smoothstep) oder linear. */
    static anteil(u, uebergang) {
        const x = Math.min(1, Math.max(0, u));
        return uebergang === 'linear' ? x : x * x * (3 - 2 * x);
    }

    /** Zwei Gewichtssätze mischen: (1 − a) · A + a · B über alle Einheiten. */
    static mischen(a, b, anteil) {
        /** @type {Object<string, number>} */
        const aus = {};
        for (const einheit of new Set([...Object.keys(a), ...Object.keys(b)])) {
            const wert = (a[einheit] || 0) * (1 - anteil) + (b[einheit] || 0) * anteil;
            if (wert) aus[einheit] = wert;
        }
        return aus;
    }

    /**
     * Die Gewichte am Bild `frame`.
     * @param {Array} schluessel Schlüsselbilder (Reihenfolge beliebig)
     * @param {number} frame Bild der Zeitleiste
     * @param {number} fps Bilder je Sekunde der Zeitleiste
     */
    static gewichte(schluessel, frame, fps) {
        const reihe = [...schluessel].sort((a, b) => a.frame - b.frame);
        if (!reihe.length || frame < reihe[0].frame) return {};
        let i = 0;
        while (i + 1 < reihe.length && reihe[i + 1].frame <= frame) i++;
        const von = reihe[i];
        const a = Mimikkurve.pose(von);
        if (i + 1 >= reihe.length) return a;                 // die letzte bleibt
        const zu = reihe[i + 1];
        const start = von.frame + (von.halten || 0) * fps;
        const laenge = zu.frame - start;
        if (frame <= start || laenge <= 0) return a;
        const u = Mimikkurve.anteil((frame - start) / laenge, zu.uebergang);
        return Mimikkurve.mischen(a, Mimikkurve.pose(zu), u);
    }
}
