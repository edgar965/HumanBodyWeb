/**
 * Anatomiefenster — die Pixel der Karten der Haut lesen, die `Anatomiebild` braucht (12.10.2026, aus `Anatomiebild` und `Anatomieproben` herausgelöst).
 *
 * Die Karten der Haut sind 4096 × 4096; gebraucht wird ein Fenster darum (das Scham-Stück liegt auf einem Zehntel der Karte). Das Lesen geht über
 * einen Canvas und kennt damit das DOM — es bleibt auf dem Hauptfaden. Die Rechnung darauf (`Anatomiebild`, `Anatomieproben.lesen`) kennt es nicht
 * und läuft im Worker (`anatomiearbeiter.js`), die Fenster gehen als Pixel hinüber.
 *
 * Die Bilder der Figur kommen als `ImageBitmap` mit `flipY: false` und schon gewendet — Zeile = v · Höhe (`Anatomieton`); hat eine Karte `flipY`,
 * gilt Zeile = (1 − v) · Höhe.
 */
export class Anatomiefenster {

    /** Pixel Rand um das gelesene Fenster der Karten der Haut. */
    static RAND_PX = 16;

    /**
     * Die Fenster aller Gruppen der Haut: je Gruppe `{farbe, normal, rauh}` (je ein Fenster oder null) — oder null für die Gruppe, die kein Texel
     * des Stücks trägt, keine Farbkarte oder kein Bild hat.
     * @param zu        Ergebnis von `Anatomiezuordnung.rechnen`
     * @param ha        `{uv, ecken}` der Haut (nur die in Frage kommenden Dreiecke)
     * @param gruppe    `Uint8Array`: je Hautdreieck der Eintrag in `texturen`
     * @param texturen  `[{map, normalMap, roughnessMap}]` — die Karten je Gruppe der Haut
     */
    static lesen(zu, ha, gruppe, texturen) {
        const je = texturen.map(() => []);
        for (let k = 0; k < zu.anzahl; k++) je[gruppe[zu.btri[k]]].push(k);
        return texturen.map((textur, g) => {
            if (!je[g].length || !textur.map) return null;
            const f = Anatomiefenster._um(zu, ha, je[g], textur);
            return f.farbe ? f : null;
        });
    }

    /** Die Fenster der drei Karten um alle Stellen der Texel `liste`. */
    static _um(zu, ha, liste, textur) {
        let u0 = Infinity, v0 = Infinity, u1 = -Infinity, v1 = -Infinity;
        const uv = ha.uv, e = ha.ecken;
        for (const k of liste) {
            const t = zu.btri[k], l2 = zu.l2[k], l3 = zu.l3[k], l1 = 1 - l2 - l3;
            const u = l1 * uv[2 * e[3 * t]] + l2 * uv[2 * e[3 * t + 1]] + l3 * uv[2 * e[3 * t + 2]];
            const v = l1 * uv[2 * e[3 * t] + 1] + l2 * uv[2 * e[3 * t + 1] + 1] + l3 * uv[2 * e[3 * t + 2] + 1];
            u0 = Math.min(u0, u); u1 = Math.max(u1, u); v0 = Math.min(v0, v); v1 = Math.max(v1, v);
        }
        const lesen = (tex) => (tex ? Anatomiefenster.pixel(tex, u0, v0, u1, v1, Anatomiefenster.RAND_PX) : null);
        return { farbe: lesen(textur.map), normal: lesen(textur.normalMap), rauh: lesen(textur.roughnessMap) };
    }

    /**
     * Das Rechteck `[u0, u1] × [v0, v1]` der Karte, ringsum um `rand` Pixel größer, als Pixel — null ohne Bild.
     * Zeilen laufen von oben: bei einer Karte ohne `flipY` ist Zeile 0 gleich v = 0.
     */
    static pixel(textur, u0, v0, u1, v1, rand = 8) {
        const bild = textur?.image, breite = bild?.width, hoehe = bild?.height;
        if (!breite || !hoehe) return null;
        const flip = !!textur.flipY;
        const z0 = (flip ? 1 - v1 : v0) * hoehe, z1 = (flip ? 1 - v0 : v1) * hoehe;
        const x0 = Math.max(0, Math.floor(u0 * breite) - rand), x1 = Math.min(breite, Math.ceil(u1 * breite) + rand);
        const y0 = Math.max(0, Math.floor(z0) - rand), y1 = Math.min(hoehe, Math.ceil(z1) + rand);
        const b = x1 - x0, h = y1 - y0;
        if (b <= 0 || h <= 0) return null;
        const leinwand = typeof OffscreenCanvas === 'function' ? new OffscreenCanvas(b, h) : Object.assign(document.createElement('canvas'), { width: b, height: h });
        const ctx = leinwand.getContext('2d', { willReadFrequently: true });
        ctx.drawImage(bild, x0, y0, b, h, 0, 0, b, h);
        return { daten: ctx.getImageData(0, 0, b, h).data, x0, y0, b, h, breite, hoehe, flip };
    }
}
