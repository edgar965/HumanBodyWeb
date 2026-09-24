/**
 * Zeitkurve — Geschwindigkeitskurve eines BVH-Clips.
 *
 * ANLASS (Edgar, 21.09.2026): Standbild an einer Stelle zeigen, dabei Kamera
 * und Licht frei weiterlaufen lassen (geht schon — eigene Spuren, siehe
 * `Standbild`/`Bvhspur`) UND die Geschwindigkeit VOR/NACH dem Standbild
 * weich ändern können (Ease-in/-out, Zeitlupe), nicht nur stufenweise über
 * mehrere gesplittete Clips mit je konstantem `speed`.
 *
 * WAS DIE KURVE BESCHREIBT
 * =========================
 * Punkte `{u, v, interpolation}`: bei Zeitanteil `u` (0 = Clipanfang, 1 =
 * Clipende) wird Quellanteil `v` (0 = `trimIn`, 1 = Clipende nach `trimOut`)
 * gezeigt. Die Endpunkte `(0,0)` und `(1,1)` sind FEST (nie gespeichert) —
 * Clipanfang und -ende zeigen immer, was `trimIn`/`trimOut` sagen, egal wie
 * die Kurve dazwischen verläuft.
 *
 * OHNE PUNKTE IST DIE KURVE DIE GERADE v=u
 * =========================================
 * Das ist exakt das bisherige Verhalten mit konstantem `speed` — siehe die
 * Herleitung in `bvhspur.js` (`Bvhspur._quellzeit`). Diese Klasse ist rein
 * additiv: kein Punkt, keine Änderung an einem bestehenden Projekt.
 *
 * EIN FLACHES STÜCK IST EIN WEICHER HALT
 * =======================================
 * Zwei Punkte mit gleichem `v` halten die Quelle über diese Zeitspanne an,
 * ohne dass es dafür einen eigenen Clip-Typ braucht (anders als `Standbild`,
 * der Sonderfall „ganz anhalten, fester Rahmen" bleibt trotzdem eigener Typ —
 * einfacher zu bedienen für den häufigen Fall).
 *
 * Ohne Import aus `state.js`/THREE — Node-testbar (`test_js_zeitkurve.py`).
 */
export class Zeitkurve {

    /** Gespeicherte Punkte plus die festen Anker (0,0) und (1,1), sortiert. */
    static mitAnkern(punkte) {
        const alle = [
            { u: 0, v: 0, interpolation: 'linear' },
            ...(punkte || []),
            { u: 1, v: 1, interpolation: 'linear' },
        ];
        return alle.slice().sort((a, b) => a.u - b.u);
    }

    /**
     * Quellanteil (0..1) bei Zeitanteil `u` (0..1, außerhalb wird geklemmt).
     *
     * Interpolationsart des VORHERIGEN Punkts entscheidet, wie zum nächsten
     * gemischt wird — dieselbe Wortwahl wie bei Licht-/Kamera-Keyframes
     * (`Schluesselpaar.gewichtung`): `smooth` (3t²−2t³), `step` (hart, bleibt
     * auf dem vorherigen Wert bis zum nächsten Punkt), sonst gerade.
     */
    static quellanteil(punkte, u) {
        const alle = Zeitkurve.mitAnkern(punkte);
        const x = Math.min(1, Math.max(0, u));
        let vorher = alle[0];
        let nachher = alle[alle.length - 1];
        for (const punkt of alle) {
            if (punkt.u <= x) vorher = punkt;
            if (punkt.u >= x) { nachher = punkt; break; }
        }
        if (vorher === nachher || nachher.u === vorher.u) return vorher.v;
        const anteil = (x - vorher.u) / (nachher.u - vorher.u);
        const art = vorher.interpolation || 'linear';
        const gewicht = art === 'smooth' ? anteil * anteil * (3 - 2 * anteil)
                       : art === 'step' ? 0
                       : anteil;
        return vorher.v + (nachher.v - vorher.v) * gewicht;
    }
}
