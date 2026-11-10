/**
 * Meshgenesisohneglieder — Knopf „Ohne fehlende Glieder“ der Testseite (31.10.2026, Edgar zu mann_gold: „bei dem Modell sind die Beine und Arme nicht vorhanden im Mesh. Kannst du eine Option machen,
 * so dass die beim Ergebnis nicht angezeigt werden?“). Welche Knochen der Eingang nicht hat, rechnet der Schritt „Kleider“ (`meshgenesis_kostuem_ohneeingang.py`, über die Kleiderliste als
 * `ohne_eingang.knochen`); hier fällt die Haut weg, deren stärkster Knochen dazugehört — im Stand am Anzeigenetz, im Tanz an der gebauten Genesis-Figur (`Figurhaut.indexSetzen`, `punkteWeg`).
 */
import { Figurhaut } from '../gemeinsam/figurhaut.js';

export class Meshgenesisohneglieder {
    /** Die gebaute Genesis-Figur des Tanzes (`Meshgenesisfigurbewegung`): die Haut der Knochen `ohne` fällt aus jedem Index, auch aus dem, den die Hautverdeckung danach setzt. */
    static figurAnwenden(modell, ohne) {
        const weg = Meshgenesisohneglieder.punkte(modell?.bodyMesh, ohne);
        if (!weg) return;
        const geo = modell.bodyMesh.geometry;
        geo.userData.punkteWeg = weg;
        const voll = Figurhaut.merken(geo);
        Figurhaut.indexSetzen(geo, voll.index, voll.gruppen);
    }

    /** Uint8Array je Dreieck des Anzeigenetzes (1 = fällt weg) oder null. `namen`: Knochennamen in der Reihenfolge der Kinematik (Indizes von `netz.knochen`). */
    static dreiecke(netz, namen, ohne) {
        if (!ohne?.length || !netz?.knochen) return null;
        const weg = Meshgenesisohneglieder._staerkste(netz.knochen, netz.gewicht, netz.kopf.haut, namen.map(n => ohne.includes(n)));
        const aus = new Uint8Array(netz.material.length);
        for (let t = 0; t < aus.length; t++) aus[t] = weg[netz.dreiecke[t * 3]] | weg[netz.dreiecke[t * 3 + 1]] | weg[netz.dreiecke[t * 3 + 2]];
        return aus;
    }

    /** Uint8Array je Punkt der gehäuteten Genesis-Figur (`skinIndex`/`skinWeight`, Knochen des Skeletts) oder null. */
    static punkte(mesh, ohne) {
        const geo = mesh?.geometry;
        const si = geo?.getAttribute('skinIndex'), sw = geo?.getAttribute('skinWeight');
        if (!ohne?.length || !si || !sw || !mesh.skeleton) return null;
        return Meshgenesisohneglieder._staerkste(si.array, sw.array, si.itemSize, mesh.skeleton.bones.map(b => ohne.includes(b.name)));
    }

    /** Je Punkt 1, wenn sein stärkster Knochen markiert ist. */
    static _staerkste(knochen, gewicht, k, markiert) {
        const n = knochen.length / k;
        const aus = new Uint8Array(n);
        for (let i = 0; i < n; i++) {
            let best = -1, wert = -1;
            for (let h = 0; h < k; h++) if (gewicht[i * k + h] > wert) { wert = gewicht[i * k + h]; best = knochen[i * k + h]; }
            aus[i] = markiert[best] ? 1 : 0;
        }
        return aus;
    }
}
