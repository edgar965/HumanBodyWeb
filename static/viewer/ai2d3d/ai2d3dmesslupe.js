/**
 * Ai2d3dmesslupe — die Lupe in Feld 3 der Testzeile „Messpunkte“ der Seite „2d-3d-AI“ (25.10.2026; Edgar: „Was bedeutet zum Beispiel 5 oder 4, ab wo bis wo ist diese Zahl?? es muss
 * doch für jede Zahl eine Linie kommen, die sehe ich nicht“). Die Linien waren da, aber bei rund 0,14 Bildpunkten je Fotopixel sind 5 mm Abweichung zwei Bildpunkte lang.
 *
 * Beim Berühren einer Tabellenzeile zeigt die Lupe die Stelle in voller Fotoauflösung, Foto und Rendering übereinander, und schreibt jede Zahl der Zeile an ihre Linie:
 *  Randpunkt  blaue Linie Knochenachse → Rand im Foto (= Vorlage), orange Linie Knochenachse → Rand im Rendering (= Ergebnis), dazwischen die Abweichung
 *  Punkt      Linie vom blauen Punkt (Foto) zum orangen (Rendering) = Abweichung
 * Die Lupe steht in der Ecke gegenüber der Stelle, damit sie sie nicht verdeckt.
 */
export class Ai2d3dmesslupe {
    static ANTEIL = 0.6;
    static RAND_PX = 70;
    static _grenzen = [0, 0];

    /** @param {CanvasRenderingContext2D} c Feld 3 @param {{b: number, h: number, k: number[], s: number}} a Ausschnitt der Fläche @param {HTMLImageElement} foto
     *  @param {HTMLImageElement} seite @param {number} q Pixel des Renderings je Fotopixel @param {object} zeile Tabellenzeile @param {object[]} punkte @param {object} F Farben */
    static zeichnen(c, a, foto, seite, q, zeile, punkte, F) {
        // eine Zeile kann eine Gruppe sein (Messpunkte des Kopfes, 25.10.2026: Kinnlinie mit 17 Punkten) — dann jede Linie der Gruppe, beschriftet mit dem Mittel
        const gruppe = punkte.filter(x => zeile.nummern.includes(x.nr)), p = gruppe[0];
        const orte = gruppe.flatMap(x => [x.achse, x.vorlage, x.ergebnis]).filter(Boolean);
        if (!orte.length) return;
        const r = Ai2d3dmesslupe.RAND_PX, xs = orte.map(o => o[0]), ys = orte.map(o => o[1]);
        const seitenlaenge = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) + 2 * r;
        const x0 = (Math.min(...xs) + Math.max(...xs) - seitenlaenge) / 2, y0 = (Math.min(...ys) + Math.max(...ys) - seitenlaenge) / 2;
        // so breit wie Feld 3 (auf schmalen Bildschirmen ist das Feld nur ~200 px breit), oben oder unten — gegenüber der Stelle
        const g = Math.round(Math.min(a.b - 8, a.h * Ai2d3dmesslupe.ANTEIL)), s = g / seitenlaenge;
        const ox = Math.round((a.b - g) / 2), oy = (ys[0] - a.k[1]) * a.s > a.h / 2 ? 4 : a.h - g - 4;
        Ai2d3dmesslupe._grenzen = [ox, ox + g];
        c.save();
        c.fillStyle = '#ffffff';
        c.fillRect(ox - 3, oy - 3, g + 6, g + 6);
        c.beginPath();
        c.rect(ox, oy, g, g);
        c.clip();
        c.drawImage(foto, x0, y0, seitenlaenge, seitenlaenge, ox, oy, g, g);
        c.globalAlpha = 0.5;
        c.drawImage(seite, x0 * q, y0 * q, seitenlaenge * q, seitenlaenge * q, ox, oy, g, g);
        c.globalAlpha = 1;
        const auf = o => [ox + (o[0] - x0) * s, oy + (o[1] - y0) * s];
        const zahl = v => `${new Intl.NumberFormat('de-DE', { maximumFractionDigits: 1 }).format(v)} mm`;
        const ueber = zeile.ueber ? F.ueber : '#222222';
        if (p.achse) {
            Ai2d3dmesslupe._linie(c, auf(p.achse), p.vorlage && auf(p.vorlage), F.vorlage, 3, zeile.vorlage !== null && `Foto ${zahl(zeile.vorlage)}`, -1);
            Ai2d3dmesslupe._linie(c, auf(p.achse), p.ergebnis && auf(p.ergebnis), F.ergebnis, 3, zeile.ergebnis !== null && `Rendering ${zahl(zeile.ergebnis)}`, 1);
            if (p.vorlage && p.ergebnis && zeile.abweichung_mm !== null) {
                Ai2d3dmesslupe._linie(c, auf(p.vorlage), auf(p.ergebnis), ueber, 2, `Abweichung ${zahl(zeile.abweichung_mm)}`, 3);
            }
        } else {
            const mit = gruppe.filter(x => x.vorlage && x.ergebnis);
            const text = zeile.abweichung_mm !== null && `${mit.length > 1 ? 'Mittel ' : 'Abweichung '}${zahl(zeile.abweichung_mm)}`;
            mit.forEach((x, i) => Ai2d3dmesslupe._linie(c, auf(x.vorlage), auf(x.ergebnis), ueber, mit.length > 1 ? 2 : 3, i === 0 && text, 1));
        }
        for (const x of gruppe) {
            for (const [seite_, farbe] of [['vorlage', F.vorlage], ['ergebnis', F.ergebnis]]) {
                if (!x[seite_]) continue;
                const [px, py] = auf(x[seite_]);
                c.fillStyle = farbe;
                c.beginPath();
                c.arc(px, py, gruppe.length > 1 ? 3 : 5, 0, 2 * Math.PI);
                c.fill();
            }
        }
        c.restore();
        c.strokeStyle = '#333333';
        c.lineWidth = 1;
        c.strokeRect(ox, oy, g, g);
    }

    /** Linie a → b mit Beschriftung an der Mitte, `seite` verschiebt die Schrift quer zur Linie (Vielfache von 12 px), damit sich zwei Beschriftungen nicht überdecken. */
    static _linie(c, a, b, farbe, breite, text, seite) {
        if (!a || !b) return;
        c.strokeStyle = farbe;
        c.lineWidth = breite;
        c.beginPath();
        c.moveTo(a[0], a[1]);
        c.lineTo(b[0], b[1]);
        c.stroke();
        if (!text) return;
        const l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, n = [-(b[1] - a[1]) / l, (b[0] - a[0]) / l];
        c.font = 'bold 13px system-ui, sans-serif';
        // die Schrift bleibt in der Lupe (sonst schnitt der Rand „Abweichung −35,1 mm“ ab, Chrome 25.10.2026)
        const halb = c.measureText(text).width / 2 + 3, [links, rechts] = Ai2d3dmesslupe._grenzen;
        const x = Math.min(Math.max((a[0] + b[0]) / 2 + n[0] * 12 * seite, links + halb), rechts - halb), y = (a[1] + b[1]) / 2 + n[1] * 12 * seite;
        c.textAlign = 'center';
        c.lineWidth = 4;
        c.strokeStyle = 'rgba(255, 255, 255, 0.95)';
        c.strokeText(text, x, y + 4);
        c.fillStyle = farbe;
        c.fillText(text, x, y + 4);
        c.textAlign = 'start';
    }
}
