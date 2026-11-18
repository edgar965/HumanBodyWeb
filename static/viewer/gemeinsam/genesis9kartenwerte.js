import * as THREE from 'three';

/**
 * Genesis9kartenwerte — was Daz an den Karten eines Materials außer dem Bild selbst stellt (17.11.2026, Edgar: „die Default-Textur ist falsch“,
 * „das See-through-Kleid ist gar nicht durchsichtig“).
 *
 * WIEDERHOLUNG: Iray Uber kachelt alle Karten mit `Horizontal/Vertical Tiles` (`bilder.wiederholung` = [wu, wv, vu, vv]); ein Bild kann darüber
 * eigene Werte tragen (`bilder.bildwiederholung[art]`). Wirksam ist das Produkt der Wiederholungen und die Summe der Verschiebungen
 * (`Genesis9/materialgrund.py`). Die Alienontrack-Kleider legen so ihr kachelbares Stoffbild `Seamless/Cloth_base.png` 4- bis 8-fach, die
 * Normalenkarte des Schnitts aber einmal (0,25 × 4) — ohne Wiederholung lag das Stoffbild einmal, viermal zu grob, über dem ganzen Kleid.
 * Die Textur im Vorrat (`Genesis9texturen`) teilen alle Stücke; eine eigene Wiederholung bekommt einen Klon (gleiche Bildquelle, eigene Matrix).
 *
 * WERTE OHNE KARTE: Metallgewicht ohne Metallkarte; Durchsicht (`Cutout Opacity`) auch über einer Deckkraftkarte — Daz rechnet Karte × Wert.
 */
export class Genesis9kartenwerte {

    static NEUTRAL = [1, 1, 0, 0];

    /** Wirksame Wiederholung einer Karte → [wu, wv, vu, vv] — oder null, wenn sie einmal liegt. */
    static wiederholung(bilder, art) {
        const m = Array.isArray(bilder?.wiederholung) ? bilder.wiederholung : Genesis9kartenwerte.NEUTRAL;
        const b = Array.isArray(bilder?.bildwiederholung?.[art]) ? bilder.bildwiederholung[art] : Genesis9kartenwerte.NEUTRAL;
        const w = [m[0] * b[0], m[1] * b[1], m[2] + b[2], m[3] + b[3]];
        return w.some((x, i) => Math.abs(x - Genesis9kartenwerte.NEUTRAL[i]) > 1e-6) ? w : null;
    }

    /** Die Textur, wie sie auf dieser Karte liegt: mit eigener Wiederholung ein Klon, sonst dieselbe. */
    static bild(textur, bilder, art) {
        const w = Genesis9kartenwerte.wiederholung(bilder, art);
        if (!w || !textur) return textur;
        const klon = textur.clone();
        klon.wrapS = THREE.RepeatWrapping;
        klon.wrapT = THREE.RepeatWrapping;
        klon.repeat.set(w[0], w[1]);
        klon.offset.set(w[2], w[3]);
        klon.needsUpdate = true;
        return klon;
    }

    /**
     * Zahlen, die ohne (oder über) einer Karte gelten. Durchsicht als Zahl (`.mhmat` opacity, 25.09.2026; Daz `Cutout Opacity`), mit Karte als
     * Faktor darüber. Halbdurchsichtiger Stoff schreibt KEINE Tiefe (17.11.2026): sonst verdeckte die Vorderseite des See-through-Kleids die Cami
     * darunter ganz — Three zeichnet durchsichtige Netze nach den deckenden, das Kleid kam vor der Cami, und die Cami fiel durch die Tiefenprobe
     * (gemessen: Cami 3–73 mm über der Haut, Wicklung nach außen, trotzdem unsichtbar).
     */
    static werte(material, bilder) {
        if (!bilder.metall && Number.isFinite(bilder.metallgewicht)) material.metalness = bilder.metallgewicht;
        if (!Number.isFinite(bilder.alphawert) || bilder.alphawert >= 0.999) return;
        material.opacity = bilder.alphawert;
        // Mit Deckkraftkarte (Haarkarten: Alpha-to-Coverage, `Genesis9netz.material`) nur der Faktor — Mischung und Tiefe bleiben, wie sie sind.
        if (bilder.alpha) return;
        material.transparent = true;
        material.depthWrite = false;
    }
}
