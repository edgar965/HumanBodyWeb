import { Protokoll } from './protokoll.js';
import { Kleiderknochen } from './kleiderknochen.js';

/**
 * Kleidervorschau — die Kleidung folgt einem neuen Körper SOFORT, noch bevor der Server ihre genaue Lage liefert.
 *
 * WARUM (Edgar, 16.10.2026: „Der Regler soll viel schneller die Figur ändern können. Warum dauert das so lange?"): Ein Reglerzug holt Körper UND jedes
 * getragene Stück neu. Gemessen an Mann1 (Server im Leerlauf, `ProjektTemp/_wegwerf/mann_regler/zeit_je_stueck.py`): Körper 0,3 s, T-Shirt 3,5 s, Boxershorts
 * 1,3 s, Haar 1,9 s, Stiefel 0,3 s — zusammen 7,4 s, weil jedes Stück die Körperfläche, die Lagen darunter und die Bindung an die Körperdreiecke neu rechnet
 * (T-Shirt: Bindung 2,5 von 4,2 s). Die Haut unter einem Kleidungsstück ist ausgeblendet (`Hautverdeckung`), sichtbar wird eine Änderung also erst mit dem
 * letzten Stück: im Log 8 bis 20 s nach dem Zug.
 *
 * Die Bindung jedes anliegenden Stückes (`bindung`, `bary`, `mischung`: Körperdreieck, Baryzentrik, Gewicht — vom Server mitgeliefert, `Oberflaechenbindung`) sagt, an
 * welchem Körperpunkt ein Stoffpunkt hängt. Sobald der neue Körper da ist (0,8 s), wandert jeder gebundene Stoffpunkt um die Verschiebung SEINES Körperpunkts mal
 * `mischung` — wie Blenders Surface Deform. Das ist eine Näherung: freie Stoffteile (weiter als 8 cm vom Körper) und der Abstand entlang der Normalen bleiben stehen.
 * Die genaue Lage vom Server ersetzt sie wenig später wie bisher.
 *
 * Ein Stück, das in DIESEM Lauf schon vom Server kam, ist genau (`geometry.userData.lauf`) und wird nicht noch einmal verschoben.
 *
 * WAS KEINE BINDUNG HAT, FOLGT DEN KNOCHEN (17.10.2026, Daz-Posen): Haar, Requisiten und der ungebundene Anteil freier Stoffpunkte
 * (`1 − mischung`) wandern mit der Bewegung ihrer Knochen von der alten zur neuen Stellung (`Kleiderknochen`) — bis dahin blieb das Haar
 * bei „03 Laying Back" an der alten Kopfstelle stehen, bis seine eigene Antwort kam.
 */
export class Kleidervorschau {

    /** Unter dieser Verschiebung (Meter) gilt der Körper als unverändert (Material-, Stufen- oder Presetwechsel). */
    static SCHWELLE = 1e-6;

    /** Die Körperpunkte VOR dem Neuaufbau — oder null, wenn es noch keinen Körper gibt. */
    static merken(inst) {
        const position = inst?.bodyMesh?.geometry?.attributes?.position;
        if (!position) return null;
        // `exakt`: die Daz-Wege der Posenvorschau, wenn der Zug genau ihre Stellung bringt (`inst._posenwege.gilt`).
        const exakt = inst._posenwege?.gilt?.(inst) ? inst._posenwege.wege : null;
        return { punkte: Float32Array.from(position.array), stufen: inst.stufen || 0, knochen: Kleiderknochen.lagen(inst), exakt };
    }

    /**
     * Den Zug eines Körpers begleiten: sobald er gebaut ist, folgt die Kleidung. Gilt nur, wenn dieser Zug nicht inzwischen überholt wurde (`inst._lauf`) —
     * sonst käme dieselbe Verschiebung zweimal (der neuere Zug rechnet von dem Körper, der bei seinem Start stand).
     * `koerper`: das Versprechen von `koerperAufbauen`; sein Fehler gehört dem Aufrufer (`Promise.all`), nicht hierher.
     */
    static begleiten(inst, vorher, koerper) {
        const lauf = inst._lauf;
        koerper.then(() => {
            if (inst._lauf !== lauf) return;
            try {
                Kleidervorschau.folgen(inst, vorher);
            } catch (fehler) {
                Protokoll.warnung('Kleidervorschau', `Stücke nicht mitgenommen: ${fehler.message}`);
            }
        }, () => {});
    }

    /**
     * Die gebundenen Stücke um die Verschiebung des Körpers mitnehmen. Nach dem Aufbau des neuen Körpers aufrufen (`inst.stufen` ist dann schon gesetzt).
     * @returns Zahl der verschobenen Stücke
     */
    static folgen(inst, vorher) {
        const neu = inst?.bodyMesh?.geometry?.attributes?.position?.array;
        if (!vorher || !neu || neu.length !== vorher.punkte.length || (inst.stufen || 0) !== vorher.stufen) return 0;
        const beginn = performance.now();
        const verschiebung = Kleidervorschau._verschiebung(vorher.punkte, neu);
        if (!verschiebung) return 0;
        // null ohne gemerkte Knochen: nur die Oberflächenbindung
        const wege = Kleiderknochen.ausServer(vorher.exakt, inst) || Kleiderknochen.wege(vorher.knochen, inst);
        let stuecke = 0, punkte = 0;
        for (const netz of Object.values(inst.clothMeshes || {})) {
            const n = Kleidervorschau._mitnehmen(inst, netz, verschiebung, vorher.stufen, neu.length / 3, wege);
            if (n) { stuecke++; punkte += n; }
        }
        Protokoll.debug('Kleidervorschau', `${stuecke} Stücke, ${punkte} Punkte in ${(performance.now() - beginn).toFixed(0)} ms mitgenommen`);
        return stuecke;
    }

    /** `neu − alt` je Koordinate — oder null, wenn sich nichts bewegt hat. */
    static _verschiebung(alt, neu) {
        const d = new Float32Array(neu.length);
        let groesste = 0;
        for (let i = 0; i < neu.length; i++) {
            d[i] = neu[i] - alt[i];
            const a = Math.abs(d[i]);
            if (a > groesste) groesste = a;
        }
        return groesste > Kleidervorschau.SCHWELLE ? d : null;
    }

    /**
     * Ein Netz: seine gebundenen Punkte um die Körperverschiebung verschieben, den Rest mit den Knochen (`wege`, darf null sein).
     * Die Knochenbewegung zuerst: Sie rechnet von der alten Lage, die Oberflächenverschiebung hängt nicht von ihr ab.
     * @returns Zahl der verschobenen Punkte
     */
    static _mitnehmen(inst, netz, verschiebung, stufen, koerperPunkte, wege = null) {
        const geo = netz?.geometry;
        if (!geo || netz.userData?.stoff || geo.userData?.lauf === inst._lauf) return 0;
        const bindung = Kleidervorschau._bindung(geo, stufen, koerperPunkte);
        const knochen = wege ? Kleiderknochen.haeuten(netz, wege, bindung ? (i) => Kleidervorschau._frei(bindung, i) : null) : 0;
        if (!bindung) return knochen;
        const { dreieck, bary, mischung, position } = bindung;
        const p = position.array;
        let bewegt = 0;
        for (let i = 0; i < mischung.length; i++) {
            const m = mischung[i], a = dreieck[3 * i] * 3;
            if (!(m > 0) || a < 0) continue;
            const b = dreieck[3 * i + 1] * 3, c = dreieck[3 * i + 2] * 3;
            const u = bary[3 * i] * m, v = bary[3 * i + 1] * m, w = bary[3 * i + 2] * m;
            p[3 * i] += u * verschiebung[a] + v * verschiebung[b] + w * verschiebung[c];
            p[3 * i + 1] += u * verschiebung[a + 1] + v * verschiebung[b + 1] + w * verschiebung[c + 1];
            p[3 * i + 2] += u * verschiebung[a + 2] + v * verschiebung[b + 2] + w * verschiebung[c + 2];
            bewegt++;
        }
        if (bewegt) {
            position.needsUpdate = true;
            geo.boundingSphere = null;       // Hülle und Kugel stammen aus der alten Lage
            geo.boundingBox = null;
        }
        return Math.max(bewegt, knochen);
    }

    /** Die Oberflächenbindung eines Netzes, wenn sie zu diesem Körper passt — sonst null. */
    static _bindung(geo, stufen, koerperPunkte) {
        const bindung = geo.userData?.bindung;
        if (!bindung || bindung.stufen !== stufen || (bindung.punkte !== undefined && bindung.punkte !== koerperPunkte)) return null;
        const dreieck = geo.attributes.bindung?.array, bary = geo.attributes.bary?.array, mischung = geo.attributes.mischung?.array;
        const position = geo.attributes.position;
        if (!dreieck || !bary || !mischung || position.count !== mischung.length) return null;
        return { dreieck, bary, mischung, position };
    }

    /** Der Anteil von Punkt i, den die Oberfläche NICHT trägt: `1 − mischung`, ganz ohne Körperdreieck 1. */
    static _frei({ dreieck, mischung }, i) {
        const m = mischung[i];
        return m > 0 && dreieck[3 * i] >= 0 ? 1 - m : 1;
    }
}
