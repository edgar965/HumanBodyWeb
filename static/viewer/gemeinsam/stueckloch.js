/**
 * Stueckloch — das Loch, das ein VERSCHWEISSTES Ersatzstück (Scham aus einer .blend) in die Haut schneidet (09.10.2026).
 *
 * WARUM (Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit
 * der Nase und dem Mund macht, und mach es genau so"): Bei Genesis ist ein Rand eine KANTE, keine Überlappung — Lippen und
 * Mundhöhle sind ein Netz, und Daz' Geograft „Anatomical Elements" verschweißt seine Randpunkte mit den Punkten eines Lochs im
 * Körper. Bis dahin rechnete der Browser jedes Mal neu, welche Haut unter dem Stück wegfällt (Strahlen entlang der Normalen,
 * Splitter, Lücken — `hautverdeckung.js`); das Loch war der Rest einer Rechnung, sein Rand ein Stern aus ganzen Dreiecken, das
 * Stück endete irgendwo daneben (gesehen im Chrome: dunkle Keile bis zum Hintergrund, helle Zipfel).
 *
 * HIER: Der Bau legt das Loch fest (`Blendimportschamloch`: Dreiecke der Haut der Stufe 1, ein Kantenring) und legt den Rand des
 * Stücks genau auf diesen Ring (`Blendimportschamnaht`). Das Stück bringt die Dreiecknummern mit (`userData.hautLoch`,
 * `{von, dreiecke}`); der Browser lässt genau diese Dreiecke weg — keine Rechnung, keine Strahlen, keine Absenkung, keine
 * weiche Kante. Gilt nur, wenn die Haut dieselbe Zahl Dreiecke hat wie beim Bau (`von`, Stufe 1: 201.248); ein anderes Netz
 * (grobe Stufe, andere Figur) kennt die Nummern nicht — dann rechnet `hautverdeckung.js` wie vorher.
 *
 * Ohne Three.js und ohne DOM (Node-Test `test_js_stueckloch.py`).
 */
import { Protokoll } from './protokoll.js';

export class Stueckloch {

    /** Schlüssel schon gemeldeter Abweichungen (je Stück einmal, sonst stünde sie bei jeder Maske im Protokoll). */
    static _gemeldet = new Set();

    /**
     * Das Loch des Stücks — `Uint32Array` der Dreiecknummern der Haut —, wenn es zu einer Haut mit `anzahl` Dreiecken passt;
     * sonst null (kein Loch angegeben, oder die Haut ist eine andere Stufe).
     * @param netz    Three.js-Netz des Stücks (`userData.hautLoch`)
     * @param anzahl  Zahl der Dreiecke der Haut (volle Folge, ohne ausgeblendete)
     */
    static von(netz, anzahl) {
        const loch = netz?.userData?.hautLoch;
        if (!loch?.dreiecke?.length) return null;
        if (loch.von !== anzahl) {
            const schluessel = `${netz.name}|${loch.von}|${anzahl}`;
            if (!Stueckloch._gemeldet.has(schluessel)) {
                Stueckloch._gemeldet.add(schluessel);
                Protokoll.debug('Stueckloch', `${netz.name || 'Stück'}: Loch für ${loch.von} Hautdreiecke, die Haut hat ${anzahl} — `
                    + 'die Haut rechnet das Loch selbst');
            }
            return null;
        }
        return Uint32Array.from(loch.dreiecke);
    }

    /**
     * Die verschweißten Stücke einer Figur und ihr gemeinsames Loch: `{schluessel, weg}` — `weg[t] = 1`, wenn das Dreieck `t` der
     * Haut entfällt —, oder null, wenn kein sichtbares Stück ein passendes Loch trägt.
     * @param stuecke  `[schluessel, netz]`-Paare der Stücke, die zählen (sichtbar, Art Kleidung)
     * @param anzahl   Zahl der Dreiecke der Haut
     */
    static maske(stuecke, anzahl) {
        let weg = null;
        const schluessel = [], punkte = [], d = [], ringe = [];
        for (const [name, netz] of stuecke) {
            const nummern = Stueckloch.von(netz, anzahl);
            if (!nummern) continue;
            weg = weg || new Uint8Array(anzahl);
            for (let i = 0; i < nummern.length; i++) weg[nummern[i]] = 1;
            schluessel.push(name);
            const v = netz.userData.hautLoch.verschiebung;
            if (v?.punkte?.length) { punkte.push(...v.punkte); for (const z of v.d) d.push(z[0], z[1], z[2]); }
            const r = netz.userData.hautLoch.ring;
            if (r?.punkte?.length) {
                ringe.push({ netz, ring: { lage: Float32Array.from(r.lage.flat()), punkte: Uint32Array.from(r.punkte),
                                           d: Float32Array.from(r.d.flat()) } });
            }
        }
        if (!weg) return null;
        return { schluessel, weg, ringe, verschiebung: punkte.length ? { punkte: Uint32Array.from(punkte), d: Float32Array.from(d) } : null };
    }

    /**
     * Die Ringpunkte der Haut um ihre Verschiebung rücken (`verschiebung` aus `maske`): der Ring des Lochs wird eine glatte Linie
     * (`Blendimportschamring`), und das Stück liegt auf dieser Linie. Geschrieben wird in das `einzug`-Feld (xyz je Punkt, im
     * Vertex-Shader vor dem Skinning addiert, `hauteinzug.js`) — die Punkte drehen mit jedem Knochen mit. Addiert, nie ersetzt:
     * ein Saumband unter anderem Stoff behält seinen Einzug.
     * @param werte  `Float32Array` (3 je Punkt) des `einzug`-Attributs
     * @returns Zahl der verschobenen Punkte
     */
    static verschieben(werte, verschiebung) {
        if (!verschiebung) return 0;
        const { punkte, d } = verschiebung;
        let n = 0;
        for (let k = 0; k < punkte.length; k++) {
            const i = punkte[k];
            if (3 * i + 2 >= werte.length) continue;
            werte[3 * i] += d[3 * k]; werte[3 * i + 1] += d[3 * k + 1]; werte[3 * i + 2] += d[3 * k + 2];
            n++;
        }
        return n;
    }

    /** Zwei Dreiecksmasken vereinigen (`null` zählt als leer); die erste bleibt unverändert, wenn sie gegeben ist und die zweite fehlt. */
    static vereinen(a, b) {
        if (!b) return a;
        if (!a) return b;
        const aus = Uint8Array.from(a);
        for (let i = 0; i < aus.length; i++) if (b[i]) aus[i] = 1;
        return aus;
    }
}
