import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Mimikfelder } from './mimikfelder.js';

/**
 * Mimiksmplx — die Mimik auf einer SMPL-X-Figur: Netzpunkte statt Knochen.
 *
 * Edgar, 16.09.2026: „Mimik auch auf SMPL-X." Die Figur trägt Kiefer und
 * Augen als Gelenke, Lippen, Lider, Brauen aber nicht — dort ist ein
 * Gesichtsausdruck eine Verschiebung der Hautpunkte. `smplx_basis.json`
 * bringt je MB-Lab-Einheit das Feld auf dem SMPL-X-Kopf mit
 * (`SMPL/xmimik.py`: von HumanBody übertragen); hier wird es je Bild in das
 * `position`-Attribut des Netzes geschrieben — die Ruhelage bleibt als
 * Kopie am Netz, das Skinning läuft danach wie immer auf dem Attribut.
 *
 * Geschrieben wird nur, wenn sich die Gewichte geändert haben
 * (`Mimikfelder.kennung`), und nur die Punkte, die bewegt sind oder waren;
 * die Normalen werden dann für die Dreiecke des Kopfes neu gerechnet
 * (`_normalen`; gemessen 16.09.2026: Summe und Schreiben 1 ms je Wechsel).
 * Ein Netz anderer Topologie (GarmentCodes `mean_all`, 23.752 Punkte)
 * bekommt nichts — `passt` sagt es.
 */
export class Mimiksmplx {
    static BASIS = '/static/mimik/smplx_basis.json';
    static PUNKTE = 10475;

    static basis = null;
    static _lader = null;

    static laden() {
        if (!Mimiksmplx._lader) {
            Mimiksmplx._lader = Serverabruf.json(Mimiksmplx.BASIS)
                .then(basis => {
                    Mimiksmplx.basis = basis;
                    fn.applyPlayhead?.();           // das erste Bild nachholen
                    return basis;
                })
                .catch(fehler => {
                    console.warn('[BVH Studio] SMPL-X-Mimik nicht ladbar:', fehler);
                    return null;
                });
        }
        return Mimiksmplx._lader;
    }

    static get bereit() { return !!Mimiksmplx.basis; }

    /** Trägt diese Figur (`{mesh, quelle}`) ihre Mimik als Netzverschiebung? */
    static passt(figur) {
        const netz = figur?.mesh;
        return figur?.quelle === 'smpl' && !!netz?.geometry
            && netz.geometry.getAttribute('position')?.count === Mimiksmplx.PUNKTE;
    }

    /** Gewichte auf das Netz legen; lädt die Basis beim ersten Mal nach. */
    static setzen(netz, gewichte) {
        if (!Mimiksmplx.bereit) { Mimiksmplx.laden(); return; }
        const kennung = Mimikfelder.kennung(gewichte);
        const stand = Mimiksmplx._stand(netz);
        if (stand.kennung === kennung) return;
        const lage = netz.geometry.getAttribute('position');
        const summe = Mimikfelder.summe(Mimiksmplx.basis, gewichte);
        stand.bewegt = Mimikfelder.anwenden(lage.array, stand.ruhe, summe, stand.bewegt);
        stand.kennung = kennung;
        lage.needsUpdate = true;
        Mimiksmplx._normalen(netz.geometry, stand);
    }

    /**
     * Normalen nur dort neu rechnen, wo die Mimik hinreicht. Ein voller
     * `computeVertexNormals` kostete 4,4 ms je Bild (10.475 Punkte, 20.908
     * Dreiecke); die Felder berühren ~4.800 Kopfpunkte. Beim ersten Mal werden
     * die Dreiecke gesammelt, die einen Feldpunkt enthalten — danach werden je
     * Bild nur ihre Punkte genullt, aufsummiert und normiert.
     */
    static _normalen(geometrie, stand) {
        const lage = geometrie.getAttribute('position').array;
        const normale = geometrie.getAttribute('normal');
        if (!normale) { geometrie.computeVertexNormals(); return; }
        const n = normale.array;
        if (!stand.dreiecke) Mimiksmplx._dreiecke(geometrie, stand);
        const feld = stand.imFeld, punkte = stand.punkte, d = stand.dreiecke;
        for (let j = 0; j < punkte.length; j++) {
            const i = punkte[j] * 3;
            n[i] = 0; n[i + 1] = 0; n[i + 2] = 0;
        }
        // Nur Feldpunkte bekommen die Summe — ihre Dreiecke sind alle dabei.
        // Ein Randpunkt außerhalb des Feldes behält seine Normale: von ihm
        // fehlten hier die Dreiecke jenseits des Feldes.
        for (let k = 0; k < d.length; k += 3) {
            const pa = d[k], pb = d[k + 1], pc = d[k + 2];
            const a = pa * 3, b = pb * 3, c = pc * 3;
            const abx = lage[b] - lage[a], aby = lage[b + 1] - lage[a + 1], abz = lage[b + 2] - lage[a + 2];
            const acx = lage[c] - lage[a], acy = lage[c + 1] - lage[a + 1], acz = lage[c + 2] - lage[a + 2];
            const nx = aby * acz - abz * acy, ny = abz * acx - abx * acz, nz = abx * acy - aby * acx;
            if (feld[pa]) { n[a] += nx; n[a + 1] += ny; n[a + 2] += nz; }
            if (feld[pb]) { n[b] += nx; n[b + 1] += ny; n[b + 2] += nz; }
            if (feld[pc]) { n[c] += nx; n[c + 1] += ny; n[c + 2] += nz; }
        }
        for (let j = 0; j < punkte.length; j++) {
            const i = punkte[j] * 3, l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1;
            n[i] /= l; n[i + 1] /= l; n[i + 2] /= l;
        }
        normale.needsUpdate = true;
    }

    /** Die Feldpunkte (alle Einheiten) und die Dreiecke, die einen davon enthalten. */
    static _dreiecke(geometrie, stand) {
        const imFeld = new Uint8Array(geometrie.getAttribute('position').count);
        for (const einheit of Object.values(Mimiksmplx.basis)) {
            for (const richtung of Object.values(einheit)) {
                for (const i of richtung.i || []) imFeld[i] = 1;
            }
        }
        const index = geometrie.getIndex().array;
        const dreiecke = [];
        for (let k = 0; k < index.length; k += 3) {
            const a = index[k], b = index[k + 1], c = index[k + 2];
            if (imFeld[a] || imFeld[b] || imFeld[c]) dreiecke.push(a, b, c);
        }
        const punkte = [];
        imFeld.forEach((drin, i) => { if (drin) punkte.push(i); });
        stand.imFeld = imFeld;
        stand.dreiecke = Uint32Array.from(dreiecke);
        stand.punkte = Uint32Array.from(punkte);
    }

    /** Ruhelage und zuletzt bewegte Punkte, am Netz gemerkt. */
    static _stand(netz) {
        const daten = netz.geometry.userData;
        if (!daten.mimik) {
            daten.mimik = {
                ruhe: Float32Array.from(netz.geometry.getAttribute('position').array),
                bewegt: new Set(),
                kennung: '',
            };
        }
        return daten.mimik;
    }
}
