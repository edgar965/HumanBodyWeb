import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { base64ToFloat32, base64ToUint32 } from './kodierung.js';

/**
 * Genesis9felder — dünne Verschiebungsfelder je Regler auf den Browserpunkten
 * einer Genesis-9-Figur, je Bild mit Gewichten summiert ins `position`-Attribut.
 *
 * WOZU (18.09.2026 abends): Daz' Gelenkkorrekturen (JCMs) und die Visemes der
 * Lippensynchronisation ändern sich JE BILD — ein Neubau über den Server (0,4 s
 * je Zug) kommt dafür nicht in Frage. Der Server liefert einmal je Stufe die
 * Felder (`core/api/g9felder.py`: `koerper[kanal] = {n: Punktnummern, d:
 * xyz-Deltas in Metern}`, dasselbe je Anhang), hier werden sie gehalten und
 * summiert:
 *
 *     position[p] = ruhe[p] + Σ gewicht(kanal) · d(kanal, p)
 *
 * Geschrieben werden nur die Punkte, die jetzt oder beim letzten Mal bewegt
 * waren (`berührt`, wie `Mimikfelder.anwenden` für SMPL-X). Die Ruhelage ist
 * eine Kopie am Netz (`userData.felder`); die Häutung läuft danach auf der
 * GPU wie immer. Die Normalen bleiben die der Ruhelage — die Deltas liegen
 * im Millimeterbereich (JCM Oberschenkel bis 2 cm), ein voller
 * `computeVertexNormals` kostete auf 104.480 Punkten 40 ms je Bild.
 *
 * Ein Feldsatz gilt für ALLE Genesis-9-Figuren einer Stufe (die Unterteilung
 * ist linear; `Genesis9/reglerfelder.py`), darum je Gruppe und Stufe einmal
 * geladen. Zwei Gruppen dürfen dasselbe Netz beschreiben (JCMs und Visemes):
 * jede führt ihre eigene Berührt-Liste, und beide addieren auf die Ruhelage —
 * dafür summiert `anwenden` die Felder ALLER Gruppen, die am Netz gemerkt sind.
 */
export class Genesis9felder {

    static ADRESSE = '/api/character/genesis9-figur/felder/';
    static _lader = new Map();              // `${gruppe}/${stufen}` -> Promise

    /** Die Felder einer Gruppe (`gelenke`, `visemes`) auf einer Stufe — einmal geholt. */
    static holen(gruppe, stufen) {
        const schluessel = `${gruppe}/${stufen}`;
        let lader = Genesis9felder._lader.get(schluessel);
        if (!lader) {
            lader = Serverabruf.json(`${Genesis9felder.ADRESSE}${gruppe}/?stufen=${stufen}`)
                .then(daten => Genesis9felder.dekodieren(daten))
                .catch(fehler => {
                    Protokoll.warnung('Genesis 9', `Felder ${gruppe} nicht ladbar:`, fehler);
                    Genesis9felder._lader.delete(schluessel);
                    return null;
                });
            Genesis9felder._lader.set(schluessel, lader);
        }
        return lader;
    }

    /** Das Wörterbuch einer Antwort — base64 zu Typed Arrays. */
    static dekodieren(daten) {
        if (!daten || daten.fehler) return null;
        const feld = e => ({ n: base64ToUint32(e.n), d: base64ToFloat32(e.d) });
        const felder = daten.felder || {};
        const koerper = {};
        for (const [kanal, e] of Object.entries(felder.koerper || {})) koerper[kanal] = feld(e);
        const anhaenge = {};
        for (const [schluessel, kanaele] of Object.entries(felder.anhaenge || {})) {
            anhaenge[schluessel] = {};
            for (const [kanal, e] of Object.entries(kanaele)) anhaenge[schluessel][kanal] = feld(e);
        }
        return {
            stufen: daten.stufen, achsen: daten.achsen || {}, graph: daten.graph || null,
            visemes: daten.visemes || null, koerper, anhaenge, knochen: felder.knochen || {},
        };
    }

    // -------------------------------------------------------------- anwenden

    /**
     * Die Gewichte einer Gruppe am Netz merken und die Summe ALLER Gruppen
     * schreiben. `felder` = `{kanal: {n, d}}` dieser Gruppe auf diesem Netz.
     * Liefert true, wenn geschrieben wurde.
     */
    static anwenden(netz, gruppe, felder, gewichte) {
        const lage = netz?.geometry?.getAttribute('position');
        if (!lage) return false;
        const stand = Genesis9felder.stand(netz);
        const kennung = Genesis9felder.kennung(gewichte);
        const alt = stand.gruppen.get(gruppe);
        if (alt && alt.kennung === kennung) return false;
        stand.gruppen.set(gruppe, { felder, gewichte, kennung });
        Genesis9felder._schreiben(lage, stand);
        return true;
    }

    /** Eine Gruppe vom Netz nehmen (Figur verlässt die Bewegung) — schreibt die Ruhe zurück. */
    static entfernen(netz, gruppe) {
        const stand = netz?.geometry?.userData?.felder;
        if (!stand || !stand.gruppen.has(gruppe)) return;
        stand.gruppen.delete(gruppe);
        Genesis9felder._schreiben(netz.geometry.getAttribute('position'), stand);
    }

    static _schreiben(lage, stand) {
        const a = lage.array, ruhe = stand.ruhe, marke = stand.marke;
        // Zuerst alle zuletzt berührten Punkte zurück in die Ruhe.
        for (let j = 0; j < stand.anzahl; j++) {
            const p = stand.beruehrt[j] * 3;
            a[p] = ruhe[p]; a[p + 1] = ruhe[p + 1]; a[p + 2] = ruhe[p + 2];
            marke[stand.beruehrt[j]] = 0;
        }
        stand.anzahl = 0;
        for (const { felder, gewichte } of stand.gruppen.values()) {
            for (const [kanal, w] of Object.entries(gewichte)) {
                const f = felder[kanal];
                if (!f || !w) continue;
                const { n, d } = f;
                for (let i = 0; i < n.length; i++) {
                    const p = n[i];
                    if (!marke[p]) {
                        marke[p] = 1;
                        if (stand.anzahl < stand.beruehrt.length) stand.beruehrt[stand.anzahl++] = p;
                    }
                    const k = p * 3, m = i * 3;
                    a[k] += d[m] * w; a[k + 1] += d[m + 1] * w; a[k + 2] += d[m + 2] * w;
                }
            }
        }
        lage.needsUpdate = true;
    }

    /** Ruhelage, Marken und Berührt-Liste am Netz (einmal angelegt). */
    static stand(netz) {
        const daten = netz.geometry.userData;
        if (!daten.felder) {
            const lage = netz.geometry.getAttribute('position');
            daten.felder = {
                ruhe: Float32Array.from(lage.array),
                marke: new Uint8Array(lage.count),
                beruehrt: new Uint32Array(lage.count),
                anzahl: 0,
                gruppen: new Map(),
            };
        }
        return daten.felder;
    }

    static kennung(gewichte) {
        const teile = [];
        for (const [k, w] of Object.entries(gewichte || {})) {
            if (w) teile.push(`${k}:${w.toFixed(4)}`);
        }
        return teile.sort().join('|');
    }
}
