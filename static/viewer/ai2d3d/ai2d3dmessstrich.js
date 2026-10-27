/**
 * Ai2d3dmessstrich — Zeichenhilfen der Testzeilen (`Ai2d3dmesspunkte`): Strich, Nummer und die Umrisse der Eigenregler (26.10.2026, Edgar: „eine weitere Zeile … mit den
 * Eigen-Umrissen, Zahlen auf Vorlage, Ergebnis und dann Vorlage auf Ergebnis“ — `Reglerumrisse`). Strich und Nummer standen bis dahin in `Ai2d3dmesspunkte`.
 *
 * Ein Umriss ist eine Kette von Bildpunkten je Seite (Vorlage = Rand im Foto, Ergebnis = Rand im Rendering); `null` = an dieser Stelle nicht gemessen, dort bleibt die Linie offen.
 */
export class Ai2d3dmessstrich {
    static strich(c, a, b) {
        c.beginPath();
        c.moveTo(a[0], a[1]);
        c.lineTo(b[0], b[1]);
        c.stroke();
    }

    /** Pfeil a → b in der Strichfarbe, Spitze in `fillStyle` — Feld 3 der Gesichtspunkte: Ergebnis − Eingabe (26.10.2026). Kürzer als die Spitze: nur der Strich. */
    static pfeil(c, a, b) {
        Ai2d3dmessstrich.strich(c, a, b);
        const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy), s = 6;
        if (l < s) return;
        const ux = dx / l, uy = dy / l;
        c.beginPath();
        c.moveTo(b[0], b[1]);
        c.lineTo(b[0] - s * ux - 0.5 * s * uy, b[1] - s * uy + 0.5 * s * ux);
        c.lineTo(b[0] - s * ux + 0.5 * s * uy, b[1] - s * uy - 0.5 * s * ux);
        c.closePath();
        c.fill();
    }

    static nummer(c, text, x, y, farbe, gross) {
        c.font = `${gross ? 'bold 14px' : '10px'} system-ui, sans-serif`;
        c.lineWidth = 3;
        c.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        c.strokeText(text, x, y);
        c.fillStyle = farbe;
        c.fillText(text, x, y);
        c.lineWidth = 1;
    }

    /** Alle Umrisse auf die Fläche; `seiten` ['vorlage'] / ['ergebnis'] / beide, `hervor` = Nummern der berührten Tabellenzeile (die übrigen Umrisse blass).
     *  Mit beiden Seiten (Feld 3) darunter je Stelle die Linie Vorlage → Ergebnis, rot ab `grenzePx` (Pixel des Fotos) — Edgar 26.10.2026: „mach linien zwischen den Punkten der
     *  Vorlage und des Ergebnisses sodass man schnell die Abweichung sehen kann“. Beide Ketten zählen dieselben Stellen (`Reglerumrisse`, gleich lang). */
    static umrisse(c, auf, umrisse, seiten, farben, hervor, grenzePx = Infinity) {
        for (const u of umrisse) {
            const an = !hervor || u.nummern.some(n => hervor.has(n));
            c.globalAlpha = an ? 1 : 0.3;
            if (seiten.length > 1) Ai2d3dmessstrich._verbinden(c, auf, u.vorlage, u.ergebnis, farben.verbindung ?? '#e03131');
            c.lineWidth = 2;
            for (const seite of seiten) {
                c.strokeStyle = farben[`${seite}_linie`] ?? farben[seite];      // Linie des Ergebnisses schwarz (27.10.2026)
                Ai2d3dmessstrich._kette(c, auf, u[seite], u.geschlossen);
            }
        }
        c.globalAlpha = 1;
        c.lineWidth = 1;
    }

    /** Linien durch zusammengehörige Gesichtspunkte (27.10.2026, Edgar: „zwischen den Punkten am Kopf … eine Linie zwischen denen, die zusammengehören“): je Zeile mit `ketten`
     *  ({nummern, geschlossen}) die Punkte der Reihe nach verbunden, blau im Foto, orange im Rendering; `hervor` wie bei den Umrissen. */
    static ketten(c, auf, zeilen, punkte, seiten, farben, hervor) {
        const nach = new Map(punkte.map(p => [p.nr, p]));
        c.lineWidth = 1.5;
        for (const z of zeilen) {
            for (const k of z.ketten ?? []) {
                c.globalAlpha = !hervor || k.nummern.some(n => hervor.has(n)) ? 1 : 0.3;
                for (const seite of seiten) {
                    c.strokeStyle = farben[`${seite}_linie`] ?? farben[seite];      // Linie des Ergebnisses schwarz (27.10.2026)
                    Ai2d3dmessstrich._kette(c, auf, k.nummern.map(n => nach.get(n)?.[seite] ?? null), k.geschlossen);
                }
            }
        }
        c.globalAlpha = 1;
        c.lineWidth = 1;
    }

    /** Je Stelle die dünne graue Linie Vorlage → Ergebnis (27.10.2026, Edgar: „graue dünne linien zwischen orange und blau“; bis dahin schwarz bzw. rot über der Grenze). */
    static _verbinden(c, auf, vorlage, ergebnis, grau) {
        c.lineWidth = 1;
        c.strokeStyle = grau;
        for (let i = 0; i < Math.min(vorlage.length, ergebnis.length); i++) {
            const a = vorlage[i], b = ergebnis[i];
            if (a && b) Ai2d3dmessstrich.strich(c, auf(a), auf(b));
        }
    }

    static _kette(c, auf, punkte, geschlossen) {
        const n = punkte.length, folge = geschlossen ? n : n - 1;
        c.beginPath();
        for (let i = 0; i < folge; i++) {
            const a = punkte[i], b = punkte[(i + 1) % n];
            if (!a || !b) continue;
            const [ax, ay] = auf(a), [bx, by] = auf(b);
            c.moveTo(ax, ay);
            c.lineTo(bx, by);
        }
        c.stroke();
    }
}
