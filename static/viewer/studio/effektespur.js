/**
 * Effektespur — reine Rechnung fuer die Geschwindigkeitskurve der
 * Effekte-Spur: Anzeige-Zeit (Wanduhr, wie `state.playheadFrame`) zu
 * Inhalt-Zeit (Stelle im Quellmaterial der verknuepften Animationsspur).
 *
 * ANLASS (Edgar, 21.09.2026, „andersrum"): Das bisherige Standbild
 * (`clipbearbeitung.js standbildEinfuegen`) schneidet den BVH-Clip
 * tatsaechlich durch — genau das fand Edgar „unkontrolliert". Die Effekte-Spur
 * ersetzt das: „Speed"-Ereignisse (Taste G) auf einer EIGENEN Spur, ohne den
 * BVH-Clip anzufassen. Zwischen zwei Ereignissen wird die Geschwindigkeit
 * interpoliert; ein Standbild ist darin nur der Sonderfall Geschwindigkeit 0.
 *
 * DIE RICHTUNG DER ZEITEN
 * ========================
 * Ein Ereignis steht an einer ANZEIGE-Bildnummer (Wanduhr) — genau wie ein
 * Kamera- oder Licht-Schluessel (`kameraschluessel.js`), einfach
 * `startFrame = state.playheadFrame` beim Setzen, keine Umrechnung noetig.
 * Der „Balken" zwischen zwei Ereignissen ist ihr Anzeige-Abstand: wer die
 * Ereignisse weiter auseinanderzieht, macht den Balken (in Wanduhrzeit)
 * laenger — unabhaengig davon, wie viel Quellmaterial darin steckt.
 *
 * `inhalt()` integriert die Geschwindigkeit VORWAERTS ueber die Anzeige-Zeit
 * (Trapezregel, exakt bei stueckweise linearer Geschwindigkeit — keine
 * Numerik noetig) und liefert die Stelle im Quellmaterial. Bei
 * Geschwindigkeit 0 ueber einen ganzen Balken steht das Ergebnis am Ende
 * exakt da, wo es am Anfang stand — das Standbild.
 *
 * `anzeige()` ist die Umkehrung (Inhalt- zu Anzeige-Bild), gebraucht fuers
 * Zeichnen und den Maustreffer der BVH-Clips: deren `startFrame` bleibt
 * unangetastet im INHALT stehen (die Clips werden nie geschnitten), die
 * Zeitleiste zeigt sie aber an der ANZEIGE-Stelle, wo sie tatsaechlich
 * dran sind. Da `inhalt()` monoton ist (Geschwindigkeit wird auf 0 nach
 * unten geklemmt, nie negativ), geht das per Bisektion.
 *
 * Ohne Importe, damit die Rechnung in Node prüfbar ist (Projektkonvention,
 * vgl. `zeitkurve.js`).
 */
export class Effektespur {
    /** Geschwindigkeit ausserhalb jedes Balkens — normale Wiedergabe. */
    static VORGABE_SPEED = 1;

    /**
     * Tempo als Text — ohne Nachkommastellen, wenn es keine gibt (22.09.2026,
     * Edgar: „mach die Anzeige 1 oder 0, ohne Nachkommastellen wenn die 0
     * sind"). `1.00`/`0.00` -> `1`/`0`, `0.50` -> `0.5`, `1.25` -> `1.25`.
     * Rundet auf zwei Nachkommastellen (Fliesskomma-Reste wie 0,300000004).
     */
    static formatSpeed(wert) {
        return (Math.round((wert ?? 1) * 100) / 100).toString();
    }

    /** Schluessel eines `type==='speed_kf'`-Clips als {bild, speed}, sortiert. */
    static schluessel(clips) {
        return (clips || [])
            .filter(c => c.type === 'speed_kf')
            .map(c => ({ bild: c.startFrame, speed: Math.max(0, c.data?.speed ?? 1) }))
            .sort((a, b) => a.bild - b.bild);
    }

    /** Die Balken (Paare aufeinanderfolgender Schluessel) einer Liste. */
    static _balken(schluessel) {
        const balken = [];
        for (let i = 0; i < schluessel.length - 1; i++) {
            balken.push({ von: schluessel[i].bild, bis: schluessel[i + 1].bild,
                         v1: schluessel[i].speed, v2: schluessel[i + 1].speed });
        }
        return balken;
    }

    /** Geschwindigkeit bei Anzeige-Bild `bild` — 1 ausserhalb jedes Balkens. */
    static geschwindigkeit(schluessel, bild) {
        for (const b of Effektespur._balken(schluessel)) {
            if (bild < b.von || bild > b.bis) continue;
            const anteil = b.bis === b.von ? 0 : (bild - b.von) / (b.bis - b.von);
            return b.v1 + (b.v2 - b.v1) * anteil;
        }
        return Effektespur.VORGABE_SPEED;
    }

    /**
     * Anzeige-Bild (Wanduhr) -> Inhalt-Bild (Stelle im Quellmaterial).
     * Ohne Schluessel: unveraendert (Effekte-Spur leer oder nicht verknuepft).
     */
    static inhalt(schluessel, bildAnzeige) {
        if (!schluessel.length) return bildAnzeige;
        let inhalt = 0;
        let cursor = 0;
        for (const b of Effektespur._balken(schluessel)) {
            if (cursor >= bildAnzeige) break;
            // Luecke vor diesem Balken (nur vor dem allerersten moeglich,
            // Balken liegen sonst luecklos aneinander): Tempo 1 — und NICHT
            // weiter als `bildAnzeige`, sonst zaehlt ein Balken hinter dem
            // gesuchten Bild schon mit (Befund 21.09.2026, Rundreisetest).
            const vorLuecke = Math.min(b.von, bildAnzeige) - cursor;
            if (vorLuecke > 0) { inhalt += vorLuecke; cursor += vorLuecke; }
            if (cursor >= bildAnzeige) break;
            const bis = Math.min(bildAnzeige, b.bis);
            const dauer = bis - b.von;
            if (dauer > 0) {
                const vBis = b.v1 + (b.v2 - b.v1) * (dauer / (b.bis - b.von));
                inhalt += (b.v1 + vBis) / 2 * dauer;
                cursor = bis;
            }
        }
        if (bildAnzeige > cursor) inhalt += bildAnzeige - cursor;
        return inhalt;
    }

    /**
     * Inhalt-Bild -> Anzeige-Bild — Umkehrung von `inhalt()` per Bisektion.
     * Bei einem Standbild (Geschwindigkeit 0 im ganzen Balken) ist die
     * Umkehrung nicht eindeutig (ein ganzer Anzeige-Bereich liefert denselben
     * Inhalt); die Bisektion konvergiert auf den FRUEHESTEN Treffer — für
     * das Zeichnen des Clipanfangs genau richtig.
     */
    static anzeige(schluessel, bildInhalt) {
        if (!schluessel.length) return bildInhalt;
        const balken = Effektespur._balken(schluessel);
        const balkendauer = balken.reduce((summe, b) => summe + (b.bis - b.von), 0);
        let lo = 0;
        let hi = Math.max(bildInhalt, schluessel[schluessel.length - 1].bild) + balkendauer + 1;
        for (let i = 0; i < 40; i++) {
            const mitte = (lo + hi) / 2;
            if (Effektespur.inhalt(schluessel, mitte) < bildInhalt) lo = mitte; else hi = mitte;
        }
        return hi;
    }
}
