/**
 * Stoffdeckung — wie viel eines Stoffs man NICHT durchschaut: Anteil seiner Dreiecke, deren UV-Mitte auf einer deckenden Stelle der Alphakarte liegt
 * (19.10.2026, für `Anatomieverdeckung`).
 *
 * Gemessen im Chrome (Damira0): Viele Daz-Stücke tragen eine Alphakarte samt `alphaTest` 0,02, die überall deckt — `g9_base_bikini` 100 % deckende
 * Texel. Die Spitze `mh_punkduck_strappy_lace_thong` deckt 0 %, `mh_punkduck_babydoll` 0 %, `mh_elvs_bow_bottom_panty` 0 %. Nach dem Material allein
 * (Alphakarte ja/nein) galt der Bikini als durchbrochen, und das Genital stach dort ungehindert durch. Die Karte zählt nur, wo der Stoff sie benutzt:
 * ein Atlas hat leere Flächen (`asian_female_unterw_sche_underwear`, 4096², 71 % deckende Texel über das ganze Bild).
 */
export class Stoffdeckung {

    /** Darunter gilt ein Stoff als durchbrochen (Anteil deckender Dreiecke). */
    static ANTEIL = 0.5;
    /** Kantenlänge (Texel) der verkleinerten Alphakarte. */
    static KANTE = 256;
    /** Höchstens so viele Dreiecke je Stück werden abgetastet (gleichmäßig verteilt). */
    static PROBEN = 4000;
    static _karten = new WeakMap();

    /** Sieht man durch das Netz hindurch? Durchsichtiges Material (`transparent`, Deckkraft < 1) immer; eine Alphakarte nur, wenn sie dort wenig deckt. */
    static durchbrochen(netz) {
        const materialien = [netz?.material].flat().filter(Boolean);
        if (materialien.some((m) => m.transparent === true || m.opacity < 1)) return true;
        const mitKarte = materialien.find((m) => m.alphaMap?.image);
        if (!mitKarte) return false;
        const geo = netz.geometry, uv = geo?.attributes?.uv?.array, index = geo?.userData?.indexVoll?.index || geo?.index?.array;
        if (!uv || !index) return true;
        const karte = Stoffdeckung._karte(mitKarte.alphaMap);
        return !karte || Stoffdeckung.anteil(uv, index, karte.alpha, Stoffdeckung.KANTE, mitKarte.alphaMap.flipY !== false) < Stoffdeckung.ANTEIL;
    }

    /**
     * Anteil der Dreiecke, deren UV-Mitte auf einem deckenden Texel liegt (Grün > 127, wie Threes `alphaMap` den Grünkanal liest). Ohne DOM (Node-Tests).
     * @param alpha  Grünwerte der Karte (Uint8, kante², Zeile 0 = oberste Bildzeile)
     * @param flipY  Threes `texture.flipY`: v = 0 ist dann die UNTERSTE Bildzeile
     */
    static anteil(uv, index, alpha, kante, flipY = true) {
        const dreiecke = Math.floor(index.length / 3), schritt = Math.max(1, Math.floor(dreiecke / Stoffdeckung.PROBEN));
        let deckt = 0, gezaehlt = 0;
        for (let t = 0; t < dreiecke; t += schritt) {
            let u = 0, v = 0;
            for (let e = 0; e < 3; e++) { u += uv[2 * index[3 * t + e]] / 3; v += uv[2 * index[3 * t + e] + 1] / 3; }
            u -= Math.floor(u); v -= Math.floor(v);
            const zeile = Math.min(kante - 1, Math.floor((flipY ? 1 - v : v) * kante)), spalte = Math.min(kante - 1, Math.floor(u * kante));
            deckt += alpha[zeile * kante + spalte] > 127 ? 1 : 0;
            gezaehlt++;
        }
        return gezaehlt ? deckt / gezaehlt : 1;
    }

    /** Die Alphakarte verkleinert auf KANTE² (Grünkanal), einmal je Textur. */
    static _karte(textur) {
        if (Stoffdeckung._karten.has(textur)) return Stoffdeckung._karten.get(textur);
        let karte = null;
        try {
            const k = Stoffdeckung.KANTE, leinwand = document.createElement('canvas');
            leinwand.width = k; leinwand.height = k;
            const ctx = leinwand.getContext('2d', { willReadFrequently: true });
            ctx.drawImage(textur.image, 0, 0, k, k);
            const d = ctx.getImageData(0, 0, k, k).data, alpha = new Uint8Array(k * k);
            for (let i = 0; i < alpha.length; i++) alpha[i] = d[4 * i + 1];
            karte = { alpha };
        } catch (fehler) {
            karte = null;                     // stumm gewollt: ohne lesbare Karte gilt der Stoff als durchbrochen (lieber kein Loch im Genital)
        }
        Stoffdeckung._karten.set(textur, karte);
        return karte;
    }
}
