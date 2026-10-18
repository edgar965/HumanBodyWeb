/**
 * Anatomielage — die Lage der Punkte, wie der Browser sie ZEIGT: `position` + `einzug` (18.10.2026, für `Anatomiebacken`, `Anatomiehaut`, `Genesis9hautebenenstueck`).
 *
 * Edgar, 18.10.2026 (DamiraAlt, Bild): „Genital hat ‚Nähte' und erfundene Textur, die nichts mit der Textur von DamiraAlt zu tun haben." Das `einzug`-Feld (xyz je
 * Punkt, im Vertex-Shader vor dem Skinning addiert, `hauteinzug.js`) rückt ein verschweißtes Stück auf die Haut, wie sie jetzt ist (`stuecknaht.js`), und die Haut am
 * Loch ein. Die Rechnung der Karten las nur `position`. Gemessen im Chrome an DamiraAlt („Daz Anatomie Frau" ohne Variante): `einzug` am Stück Median 34,8 mm, größte
 * 42,8 mm; die Randpunkte des Stücks liegen ohne ihn Median 7,7 mm (größte 12,7) neben dem nächsten Hautpunkt, mit ihm 0,00 (größte 3,8). Der Bake fand den Rand 7,8 mm
 * neben seiner Stelle (Kante im Bild), das Innere Median 12,5 mm, größte 37 mm daneben (Flächen Haut/Stück je Dreieck p10 0,16 bis p90 99: vergrößert, verschmiert).
 * Am angepassten Stück „cute girl DAZ" (12.10.2026, nahtlos) war der Einzug klein — dort fiel es nicht auf.
 *
 * Ohne Three.js und ohne DOM (Node-Tests).
 */
export class Anatomielage {

    /**
     * Stücknetz → Figur, eingetragen von `Anatomiehaut.anwenden`: `Hautloch.naehen` schreibt den Einzug oft erst NACH dem ersten Bake (die Maske kommt mit Ruhezeit und
     * im Worker) und zieht das Stück dann nach. Schwache Schlüssel: ein entferntes Netz hält keine Figur fest.
     */
    static figuren = new WeakMap();

    /** `position` + `einzug` je Punkt (`Float32Array`, xyz) — ohne `einzug` das Feld von `position` selbst; null ohne Punkte. */
    static lage(geo) {
        const p = geo?.attributes?.position, e = geo?.attributes?.einzug;
        if (!p?.array) return null;
        if (!e?.array || e.array.length !== p.array.length) return p.array;
        const aus = new Float32Array(p.array.length);
        for (let i = 0; i < aus.length; i++) aus[i] = p.array[i] + e.array[i];
        return aus;
    }

    /** Kasten `{lo, hi}` um die Punkte `pos` (xyz), ringsum um `rand` (m) größer. */
    static kasten(pos, rand) {
        const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
        for (let i = 0; i + 2 < pos.length; i += 3) {
            for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], pos[i + k]); hi[k] = Math.max(hi[k], pos[i + k]); }
        }
        return { lo: lo.map(w => w - rand), hi: hi.map(w => w + rand) };
    }

    /**
     * Kennung des Einzugs (Prüfsumme über den Inhalt, auf µm): `Hauteinzug.eintragen` schreibt bei jeder Maske neu, oft mit denselben Werten — die Kennung ändert sich
     * nur, wenn sich die Lage ändert. '-' ohne Einzug.
     */
    static kennung(geo) {
        const e = geo?.attributes?.einzug?.array;
        if (!e) return '-';
        let summe = 0;
        for (let i = 0; i < e.length; i++) summe = (summe + Math.round(e[i] * 1e6) * ((i % 7) + 1)) % 1000000007;
        return `${e.length}.${summe}`;
    }
}
