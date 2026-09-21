/**
 * Freistellervorschau — die Regler des Freistellers sofort im Browser rechnen (21.09.2026).
 *
 * Edgar: „die slider sollen sofort wirken, mach websocket dafür oder sowas!" Ein Reglerzug
 * kostete einen Server-Umlauf (0,3–1 s). Jetzt kommt EINMAL die Grundlage in Vorschaugröße
 * (`freisteller/<datei>/grundlage/`: Bild, weiche Maske nach Modell/Matting/Punkten/GrabCut,
 * bei der Positivliste die ΔE-Abstandskarte), und diese Klasse rechnet je Reglerzug in
 * Millisekunden auf einer Leinwand — dieselbe Reihenfolge und dieselben Formeln wie
 * `Bildmodellfreisteller.alpha` auf dem Server (der beim Speichern in voller Größe rechnet):
 *
 *     Positivliste: Abstand ≤ Positivschwelle → 1, Schließen/Öffnen (Streupixel), nur Flecken,
 *       die am Kern hängen (`verbunden`), dann max(Kern, Haut) — der Kern (erodiertes Innere
 *       der Maske + Marken) bleibt ganz (Edgar: „die Positivliste soll NUR außerhalb der Figur
 *       gelten … markiere die Figur, den Kopf, merke dir die Pixel")
 *     Rand (Dilatation/Erosion, Bildpixel × f) → Schwelle (Band um t, Kern ≥ SICHER bleibt 1)
 *     → Weich (Gauß ≈ 3 × Kastenfilter, σ = weich·f·0,5) → Striche (drin 1 / draußen 0) → Hintergrund
 *
 * Morphologie als Chebyshev-Quadrat (Server: Ellipse) — an der Kante um ein Pixel anders,
 * dafür ohne Umlauf. Wer es exakt sehen will: Speichern rechnet den Server.
 */
export class Freistellervorschau {

    static HINTERGRUND = { weiss: [255, 255, 255], schwarz: [0, 0, 0], grau: [128, 128, 128], gruen: [0, 177, 64] };

    constructor(leinwand) {
        this.leinwand = leinwand;
        this.grundlage = null;      // {breite, hoehe, f, sicher, rgb: Uint8ClampedArray, maske: Float32Array, abstand: Float32Array|null}
    }

    /** Die Serverantwort (Data-URLs) in Pixel dekodieren. */
    async setzen(antwort) {
        const [bild, maske, abstand, kern] = await Promise.all([
            Freistellervorschau._pixel(antwort.bild, antwort.breite, antwort.hoehe),
            Freistellervorschau._pixel(antwort.maske, antwort.breite, antwort.hoehe),
            antwort.abstand ? Freistellervorschau._pixel(antwort.abstand, antwort.breite, antwort.hoehe) : null,
            antwort.kern ? Freistellervorschau._pixel(antwort.kern, antwort.breite, antwort.hoehe) : null,
        ]);
        const n = antwort.breite * antwort.hoehe;
        const m = new Float32Array(n), a = abstand ? new Float32Array(n) : null, k = kern ? new Float32Array(n) : null;
        for (let i = 0; i < n; i++) {
            m[i] = maske[i * 4] / 255;
            if (a) a[i] = abstand[i * 4] / (antwort.abstand_mal || 4);
            if (k) k[i] = kern[i * 4] > 127 ? 1 : 0;
        }
        this.grundlage = { breite: antwort.breite, hoehe: antwort.hoehe, f: antwort.f, sicher: antwort.sicher ?? 0.95,
                           rgb: bild, maske: m, abstand: a, kern: k };
        this.leinwand.width = antwort.breite;
        this.leinwand.height = antwort.hoehe;
        return this.grundlage;
    }

    static _pixel(datenUrl, breite, hoehe) {
        return new Promise((ok, nein) => {
            const bild = new Image();
            bild.onload = () => {
                const c = document.createElement('canvas');
                c.width = breite; c.height = hoehe;
                const ctx = c.getContext('2d', { willReadFrequently: true });
                ctx.drawImage(bild, 0, 0, breite, hoehe);
                ok(ctx.getImageData(0, 0, breite, hoehe).data);
            };
            bild.onerror = () => nein(new Error('Grundlage nicht lesbar'));
            bild.src = datenUrl;
        });
    }

    /** Die Vorschau zu `regler` zeichnen — nur mit Grundlage; liefert das Alpha (Float32Array). */
    zeichnen(regler) {
        const g = this.grundlage;
        if (!g) return null;
        const { breite: w, hoehe: h, f } = g;
        let a;
        if (g.abstand && g.kern && regler.positiv) {
            // Kern (erodiertes Innere + Marken) bleibt ganz; außerhalb nur Haut, die an ihm hängt.
            let haut = new Float32Array(w * h);
            const t = Number(regler.toleranz ?? 20);
            for (let i = 0; i < haut.length; i++) haut[i] = g.abstand[i] <= t ? 1 : 0;
            haut = Freistellervorschau.morph(Freistellervorschau.morph(haut, w, h, 1, true), w, h, 1, false);   // schließen
            haut = Freistellervorschau.morph(Freistellervorschau.morph(haut, w, h, 1, false), w, h, 1, true);   // öffnen
            a = Freistellervorschau.verbunden(haut, w, h, g.kern);
            for (let i = 0; i < a.length; i++) if (g.kern[i] > a[i]) a[i] = g.kern[i];
        } else {
            a = Float32Array.from(g.maske);
        }
        const rand = Math.round(Number(regler.rand || 0) * f);
        if (rand) a = Freistellervorschau.morph(a, w, h, Math.abs(rand), rand > 0);
        // Schwelle wie auf dem Server: Band ±0,15 um t·SICHER, unten nie unter 0, Kern ≥ SICHER bleibt 1.
        const t = (Number(regler.schwelle ?? 50) / 100) * g.sicher;
        const band = Math.min(0.15, t, g.sicher - t);
        const unten = Math.max(0, t - band), oben = Math.max(t + band, t - band + 1e-3);
        for (let i = 0; i < a.length; i++) a[i] = Math.min(1, Math.max(0, (a[i] - unten) / (oben - unten)));
        const weich = Number(regler.weich || 0) * f;
        if (weich > 0) a = Freistellervorschau.weich(a, w, h, weich * 0.5);
        Freistellervorschau.striche(a, w, h, regler.striche || []);
        const farbe = Freistellervorschau.HINTERGRUND[regler.hintergrund] || Freistellervorschau.HINTERGRUND.weiss;
        const aus = new ImageData(w, h), d = aus.data, rgb = g.rgb;
        for (let i = 0, p = 0; i < a.length; i++, p += 4) {
            const al = a[i], bl = 1 - al;
            d[p] = rgb[p] * al + farbe[0] * bl;
            d[p + 1] = rgb[p + 1] * al + farbe[1] * bl;
            d[p + 2] = rgb[p + 2] * al + farbe[2] * bl;
            d[p + 3] = 255;
        }
        this.leinwand.getContext('2d').putImageData(aus, 0, 0);
        return a;
    }

    // ------------------------------------------------------------ Filter

    /** Dilatation (`max` true) oder Erosion um `r` Pixel, getrennt nach Zeilen und Spalten. */
    static morph(a, w, h, r, max) {
        const wahl = max ? Math.max : Math.min;
        const z = new Float32Array(a.length), aus = new Float32Array(a.length);
        for (let y = 0; y < h; y++) {
            const o = y * w;
            for (let x = 0; x < w; x++) {
                let v = a[o + x];
                for (let k = Math.max(0, x - r); k <= Math.min(w - 1, x + r); k++) v = wahl(v, a[o + k]);
                z[o + x] = v;
            }
        }
        for (let x = 0; x < w; x++) {
            for (let y = 0; y < h; y++) {
                let v = z[y * w + x];
                for (let k = Math.max(0, y - r); k <= Math.min(h - 1, y + r); k++) v = wahl(v, z[k * w + x]);
                aus[y * w + x] = v;
            }
        }
        return aus;
    }

    /**
     * Bereichswachstum: von jedem Pixel, das in `a` (0/1) UND in der Figur (`figur` > 0,5) liegt,
     * über 8 Nachbarn durch `a` laufen — was nicht erreicht wird, hängt nicht an der Figur (ein
     * hautfarbener Fleck weit weg ist Wand, kein Arm). Wie `Bildmodellhauttonmaske.verbunden`.
     */
    static verbunden(a, w, h, figur) {
        const aus = new Float32Array(a.length);
        const stapel = new Int32Array(a.length);
        let n = 0;
        for (let i = 0; i < a.length; i++) if (a[i] > 0 && figur[i] > 0.5) { aus[i] = 1; stapel[n++] = i; }
        while (n > 0) {
            const i = stapel[--n], x = i % w, y = (i - x) / w;
            for (let dy = -1; dy <= 1; dy++) {
                const yy = y + dy;
                if (yy < 0 || yy >= h) continue;
                for (let dx = -1; dx <= 1; dx++) {
                    const xx = x + dx;
                    if (xx < 0 || xx >= w) continue;
                    const j = yy * w + xx;
                    if (a[j] > 0 && !aus[j]) { aus[j] = 1; stapel[n++] = j; }
                }
            }
        }
        return aus;
    }

    /** Gauß-Näherung: dreimal Kastenfilter, Breite aus σ (Wells 1986). */
    static weich(a, w, h, sigma) {
        const r = Math.max(1, Math.round(Math.sqrt(12 * sigma * sigma / 3 + 1) / 2));
        let z = a;
        for (let n = 0; n < 3; n++) z = Freistellervorschau._kasten(Freistellervorschau._kasten(z, w, h, r, true), w, h, r, false);
        return z;
    }

    static _kasten(a, w, h, r, zeilen) {
        const aus = new Float32Array(a.length);
        const laenge = zeilen ? w : h, anzahl = zeilen ? h : w;
        const idx = zeilen ? (i, j) => i * w + j : (i, j) => j * w + i;
        for (let i = 0; i < anzahl; i++) {
            let summe = 0, n = 0;
            for (let j = 0; j <= Math.min(r, laenge - 1); j++) { summe += a[idx(i, j)]; n++; }
            for (let j = 0; j < laenge; j++) {
                aus[idx(i, j)] = summe / n;
                const raus = j - r, rein = j + r + 1;
                if (raus >= 0) { summe -= a[idx(i, raus)]; n--; }
                if (rein < laenge) { summe += a[idx(i, rein)]; n++; }
            }
        }
        return aus;
    }

    /** Striche wie `Bildmodellfreistellerkorrektur.striche`: drin → 1, draußen → 0 (drin zuerst, draußen gewinnt). */
    static striche(a, w, h, striche) {
        if (!striche.length) return;
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        const ctx = c.getContext('2d', { willReadFrequently: true });
        for (const art of ['drin', 'draussen']) {
            ctx.clearRect(0, 0, w, h);
            ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = '#fff'; ctx.fillStyle = '#fff';
            let da = false;
            for (const s of striche) {
                if (s.art !== art || !s.punkte?.length) continue;
                da = true;
                const dicke = Math.max(1, Math.round(s.breite * w));
                if (s.punkte.length === 1) {
                    ctx.beginPath(); ctx.arc(s.punkte[0][0] * (w - 1), s.punkte[0][1] * (h - 1), Math.max(0.5, dicke / 2), 0, 2 * Math.PI); ctx.fill();
                    continue;
                }
                ctx.lineWidth = dicke;
                ctx.beginPath();
                s.punkte.forEach(([x, y], i) => { if (i) ctx.lineTo(x * (w - 1), y * (h - 1)); else ctx.moveTo(x * (w - 1), y * (h - 1)); });
                ctx.stroke();
            }
            if (!da) continue;
            const d = ctx.getImageData(0, 0, w, h).data;
            const wert = art === 'drin' ? 1 : 0;
            for (let i = 0, p = 3; i < a.length; i++, p += 4) if (d[p] > 127) a[i] = wert;
        }
    }
}
