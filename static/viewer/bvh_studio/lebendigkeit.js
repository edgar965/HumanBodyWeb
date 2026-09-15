/**
 * Lebendigkeit — kleine Automatiken über der gesetzten Mimik.
 *
 * Edgar, 13.09.2026: „Lebendigkeit, Blinzeln, Mimikveränderungen um die
 * aktuelle Mimik … an bei neuer Spur, aber konfigurierbar." Alles ist eine
 * Funktion der Zeit `t` (Sekunden) und einer festen Saat — dieselbe Spur
 * ergibt beim Abspielen und beim Einrechnen dieselben Bilder.
 *
 * Bausteine (je `an`, `staerke` 0…1, dazu Abstand oder Tempo):
 * - blinzeln:  alle abstand[0..1] s ein Lidschlag von 150 ms (schließen 60,
 *              öffnen 90); setzt aus, wenn die Pose die Augen schon schließt.
 * - blick:     alle abstand s ein kleiner Augensprung, dann langsames Zurück.
 * - atmen:     Nasenflügel im Takt `periode` s.
 * - variation: die Gewichte der aktuellen Pose schwanken langsam um ±staerke.
 * - zucken:    alle abstand s ein Mikroausdruck (Mundwinkel / Braue), 300 ms.
 * - schlucken: alle abstand s ein Schlucken, 600 ms.
 * Ohne Importe — der Test rechnet in Node (`test_js_lebendigkeit`).
 */
export class Lebendigkeit {

    static VORGABE = Object.freeze({
        an: true, saat: 7,
        blinzeln: { an: true, staerke: 1, abstand: [2, 6] },
        blick: { an: true, staerke: 1, abstand: [1, 3] },
        atmen: { an: false, staerke: 0.5, periode: 4 },
        variation: { an: false, staerke: 0.15, tempo: 0.3 },
        zucken: { an: false, staerke: 0.5, abstand: [5, 15] },
        schlucken: { an: false, staerke: 1, abstand: [20, 60] },
    });

    static BLINZELN_S = 0.15;
    static BLINZELN_ZU_S = 0.06;
    static ZUCKEN_S = 0.3;
    static SCHLUCKEN_S = 0.6;
    static BLICK_SPRUNG_S = 0.08;
    static BLICK_WEITE = 0.35;
    static ZUCKER = ['mouthSmileL', 'mouthSmileR', 'browOutVertL', 'browOutVertR'];

    /** Tiefe Kopie der Vorgabe (für eine neue Spur). */
    static vorgabe() {
        return JSON.parse(JSON.stringify(Lebendigkeit.VORGABE));
    }

    /** Deterministischer Zufall 0…1 aus Saat, Ereignis- und Feldnummer. */
    static zufall(saat, k, j = 0) {
        let x = (saat * 374761393 + k * 668265263 + j * 2246822519) | 0;
        x = Math.imul(x ^ (x >>> 13), 1274126177);
        x ^= x >>> 16;
        return (x >>> 0) / 4294967296;
    }

    /**
     * Das Ereignis einer Folge zufälliger Abstände, in dem `t` liegt:
     * `{k, seit}` (seit = Sekunden seit dem Beginn) oder null.
     */
    static ereignis(saat, reihe, abstand, dauer, t) {
        let beginn = 0;
        for (let k = 0; k < 10000; k++) {
            beginn += abstand[0] + (abstand[1] - abstand[0]) * Lebendigkeit.zufall(saat, k, reihe);
            if (beginn > t) return null;
            if (t < beginn + dauer) return { k, seit: t - beginn };
        }
        return null;
    }

    /** Zuschlag auf die Gewichte an der Zeit `t`; `pose` sind die aktuellen Gewichte. */
    static zuschlag(einstellung, t, pose = {}) {
        const e = einstellung || {};
        const aus = {};
        if (!e.an) return aus;
        const dazu = (einheit, wert) => { if (wert) aus[einheit] = (aus[einheit] || 0) + wert; };
        const saat = e.saat ?? 7;

        const b = e.blinzeln;
        if (b?.an && (pose.eyeClosedL || 0) < 0.8) {
            const ev = Lebendigkeit.ereignis(saat, 1, b.abstand, Lebendigkeit.BLINZELN_S, t);
            if (ev) {
                const zu = Lebendigkeit.BLINZELN_ZU_S;
                const profil = ev.seit < zu ? ev.seit / zu
                    : 1 - (ev.seit - zu) / (Lebendigkeit.BLINZELN_S - zu);
                dazu('eyeClosedL', profil * b.staerke);
                dazu('eyeClosedR', profil * b.staerke);
            }
        }
        const bl = e.blick;
        if (bl?.an) {
            const [h, v] = Lebendigkeit._blick(saat, bl, t);
            dazu('eyesHoriz', h);
            dazu('eyesVert', v);
        }
        const a = e.atmen;
        if (a?.an && a.periode > 0) {
            dazu('nostrilsExpansion', a.staerke * 0.5 * (1 + Math.sin(2 * Math.PI * t / a.periode)));
        }
        const va = e.variation;
        if (va?.an) {
            let n = 0;
            for (const [einheit, g] of Object.entries(pose)) {
                const ph = Lebendigkeit.zufall(saat, n++, 4) * 6.283;
                const rausch = 0.6 * Math.sin(2 * Math.PI * va.tempo * 0.7 * t + ph)
                             + 0.4 * Math.sin(2 * Math.PI * va.tempo * 1.3 * t + ph * 2);
                dazu(einheit, g * va.staerke * rausch);
            }
        }
        const z = e.zucken;
        if (z?.an) {
            const ev = Lebendigkeit.ereignis(saat, 5, z.abstand, Lebendigkeit.ZUCKEN_S, t);
            if (ev) {
                const einheit = Lebendigkeit.ZUCKER[Math.floor(
                    Lebendigkeit.zufall(saat, ev.k, 6) * Lebendigkeit.ZUCKER.length)];
                dazu(einheit, z.staerke * Math.sin(Math.PI * ev.seit / Lebendigkeit.ZUCKEN_S));
            }
        }
        const s = e.schlucken;
        if (s?.an) {
            const ev = Lebendigkeit.ereignis(saat, 7, s.abstand, Lebendigkeit.SCHLUCKEN_S, t);
            if (ev) dazu('deglutition', (s.staerke ?? 1) * Math.sin(Math.PI * ev.seit / Lebendigkeit.SCHLUCKEN_S));
        }
        return aus;
    }

    /** Blickrichtung [horizontal, vertikal]: Sprung zum Ziel, dann langsames Zurückdriften. */
    static _blick(saat, bl, t) {
        let beginn = 0, ziel = [0, 0], vorher = [0, 0], seit = t;
        for (let k = 0; k < 10000; k++) {
            const naechster = beginn + bl.abstand[0] + (bl.abstand[1] - bl.abstand[0]) * Lebendigkeit.zufall(saat, k, 2);
            if (naechster > t) { seit = t - beginn; break; }
            beginn = naechster;
            vorher = ziel;
            ziel = [(Lebendigkeit.zufall(saat, k, 3) - 0.5) * 2 * Lebendigkeit.BLICK_WEITE,
                    (Lebendigkeit.zufall(saat, k, 8) - 0.5) * Lebendigkeit.BLICK_WEITE];
        }
        const sprung = Math.min(1, seit / Lebendigkeit.BLICK_SPRUNG_S);
        const drift = Math.exp(-seit / 2);
        return [0, 1].map(i => (vorher[i] + (ziel[i] - vorher[i]) * sprung) * drift * bl.staerke);
    }
}
