/**
 * Metawerte — Alter, Masse, Muskeltonus und Größe umrechnen.
 *
 * Der Regler zeigt seinen eigenen Bereich (z. B. 0…100), der Kern rechnet mit
 * der Auslenkung um die Mitte (−1…+1). Diese Umrechnung stand an VIER Stellen
 * Zeile für Zeile: `garment.buildBodyFitQueryString`, `smpl._fitSmplGarmentToBody`,
 * `presets.gatherModelState` und `presets.applyModelPreset` — dreimal in die eine,
 * einmal in die andere Richtung.
 *
 *     Anzeige -> Kern:  (wert − mitte) / halbeSpanne
 *     Kern -> Anzeige:  wert × halbeSpanne + mitte
 *
 * Die Spanne kommt aus `min`/`max` des Reglers, nicht aus einer Konstanten: Die
 * vier Regler haben in den Vorlagen unterschiedliche Bereiche.
 */
export class Metawerte {

    static NAMEN = ['age', 'mass', 'tone', 'height'];

    /** Der Regler eines Metawerts — `null`, wenn die Seite ihn nicht hat. */
    static regler(name) {
        return document.getElementById(`meta-${name}`);
    }

    /** Mitte und halbe Spanne eines Reglers. */
    static spanne(regler) {
        const klein = parseInt(regler.min);
        const gross = parseInt(regler.max);
        return { mitte: (klein + gross) / 2, halb: (gross - klein) / 2 };
    }

    /** Alle vorhandenen Metawerte als `{name: kernwert}`. */
    static auslesen() {
        const werte = {};
        for (const name of Metawerte.NAMEN) {
            const regler = Metawerte.regler(name);
            if (!regler) continue;
            const { mitte, halb } = Metawerte.spanne(regler);
            werte[name] = halb ? (parseInt(regler.value) - mitte) / halb : 0;
        }
        return werte;
    }

    /** Dieselben Werte als Anhang für eine Serverfrage (`&meta_age=…`). */
    static frage() {
        return Object.entries(Metawerte.auslesen())
            .map(([name, wert]) => `&meta_${name}=${wert}`).join('');
    }

    /**
     * Kernwerte auf die Regler legen; liefert die tatsächlich gesetzten Paare.
     *
     * Der Aufrufer entscheidet, was er damit tut — die Modellseite schickt sie
     * einzeln über den Datenkanal an den Server.
     */
    static setzen(werte) {
        const gesetzt = [];
        for (const name of Metawerte.NAMEN) {
            const regler = Metawerte.regler(name);
            if (!regler || werte?.[name] === undefined) continue;
            const { mitte, halb } = Metawerte.spanne(regler);
            const anzeigewert = Math.round(werte[name] * halb + mitte);
            regler.value = anzeigewert;
            const anzeige = document.getElementById(`meta-${name}-val`);
            if (anzeige) anzeige.textContent = anzeigewert;
            gesetzt.push([name, werte[name]]);
        }
        return gesetzt;
    }
}
