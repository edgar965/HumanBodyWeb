/**
 * Ai2d3dmesszeiger — Punkte der Felder 1 und 2 einer Messzeile nur unter dem Zeiger (27.10.2026, Edgar: „mache die Punkte weg auf diesen Zeichnungen und zeige sie nur an bei hover oder
 * klick auf die Linie (dann nächsten Punkt anzeigen)“).
 *
 * Nach jedem Zeichnen merkt sich `Ai2d3dmesspunkte` je Fläche die gezeichneten Linien und Punkte in Bildschirmpixeln (`merken`). Steht der Zeiger höchstens LINIE_PX neben einer Linie
 * oder PUNKT_PX neben einem Punkt, gilt der nächste Punkt als gewählt — in allen Feldern der Zeile derselbe (gleiche Nummer). Ein Klick hält ihn fest, ein Klick ins Leere löst ihn.
 * Seit 27.10.2026 alle vier Felder (Edgar: „mach den Hover wenn ich über die blauen / schwarzen linien gehe für alle 4 Bilder, also auch für Geometrie und für das Ergebnis bild“):
 * Feld 3 meldet `Ai2d3dtrainingbild` mit `anmelden` an, in Feld 3 und 4 zählen die Linien beider Seiten.
 */
export class Ai2d3dmesszeiger {
    static LINIE_PX = 6;
    static PUNKT_PX = 12;

    /** @param {HTMLCanvasElement[]} flaechen Felder der Zeile @param {() => void} neu neu zeichnen */
    constructor(flaechen, neu) {
        this.nr = null;
        this.fest = null;
        this.neu = neu;
        this.ziele = new Map();
        for (const fl of flaechen) this.anmelden(fl);
    }

    /** Eine Fläche dazunehmen (Feld 3 der Zeile, `Ai2d3dtrainingbild`). */
    anmelden(fl) {
        if (fl.dataset.zeiger) return;
        fl.dataset.zeiger = '1';
        fl.addEventListener('mousemove', e => this._setzen(this._naechster(fl, e) ?? this.fest));
        fl.addEventListener('mouseleave', () => this._setzen(this.fest));
        fl.addEventListener('click', e => {
            this.fest = this._naechster(fl, e);
            this._setzen(this.fest);
        });
    }

    /** Linien und Punkte der Fläche (Bildschirmpixel) nach dem Zeichnen: Umrisse, Ketten, Achslinien und die Punkte mit Nummer der Seite `ansicht` ('beide': Foto und Rendering). */
    merken(flaeche, auf, f, ansicht) {
        const linien = [], punkte = [], kette = (liste, zu) => {
            const p = liste.map(q => (q ? auf(q) : null));
            for (let i = 0; i < p.length - 1 + (zu ? 1 : 0); i++) if (p[i] && p[(i + 1) % p.length]) linien.push([p[i], p[(i + 1) % p.length]]);
        };
        for (const seite of ansicht === 'beide' ? ['vorlage', 'ergebnis'] : [ansicht]) {
            for (const u of f.umrisse ?? []) kette(u[seite], u.geschlossen);
            const nach = new Map(f.punkte.map(p => [p.nr, p[seite]]));
            for (const z of f.zeilen) for (const k of z.ketten ?? []) kette(k.nummern.map(n => nach.get(n) ?? null), k.geschlossen);
            for (const p of f.punkte) if (p.achse && p[seite]) linien.push([auf(p.achse), auf(p[seite])]);
            punkte.push(...f.punkte.filter(p => p[seite]).map(p => ({ nr: p.nr, ort: auf(p[seite]) })));
        }
        this.ziele.set(flaeche, { linien, punkte });
    }

    /** Wird Punkt `nr` gezeigt? (Die Ausnahme „Punkte ohne Linie immer“ für die ViTPose-Ohrpunkte entfiel mit den Ohrumrissen, 27.10.2026.) */
    zeigt(nr) {
        return this.nr === nr;
    }

    _setzen(nr) {
        if (nr === this.nr) return;
        this.nr = nr;
        this.neu();
    }

    _naechster(fl, e) {
        const z = this.ziele.get(fl);
        if (!z || !z.punkte.length) return null;
        const r = fl.getBoundingClientRect(), m = [e.clientX - r.left, e.clientY - r.top];
        let best = null, bd = Infinity;
        for (const p of z.punkte) {
            const d = Math.hypot(p.ort[0] - m[0], p.ort[1] - m[1]);
            if (d < bd) [best, bd] = [p.nr, d];
        }
        const anLinie = z.linien.some(([a, b]) => Ai2d3dmesszeiger._abstand(m, a, b) <= Ai2d3dmesszeiger.LINIE_PX);
        return anLinie || bd <= Ai2d3dmesszeiger.PUNKT_PX ? best : null;
    }

    /** Abstand von Punkt m zur Strecke a–b. */
    static _abstand(m, a, b) {
        const dx = b[0] - a[0], dy = b[1] - a[1], l = dx * dx + dy * dy;
        const t = l ? Math.max(0, Math.min(1, ((m[0] - a[0]) * dx + (m[1] - a[1]) * dy) / l)) : 0;
        return Math.hypot(a[0] + t * dx - m[0], a[1] + t * dy - m[1]);
    }
}
