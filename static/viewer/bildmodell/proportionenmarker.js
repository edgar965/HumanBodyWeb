/**
 * Proportionenmarker — Marker setzen, löschen, alle setzen, alle Vorgaben löschen.
 *
 * Herausgelöst aus `Proportionendialog` (20.09.2026, die Datei stand bei 276
 * Zeilen, als die Modellsicht oben auf der Seite als zweite Sicht dazukam).
 * Alles hier arbeitet auf dem Zustand des Dialogs (`quellen`, `lagen`,
 * `start`, `entfernt`, `eingaben`) und nennt das Bild über seine Quelle
 * (`id`), nicht über einen Reiter — so gilt es für das Popup und die Sicht
 * oben gleichermaßen. Nach jeder Änderung: `dialog.nachzeichnen()` (alle
 * Sichten) und `dialog.aenderung()` (Tabelle, 3D).
 *
 * Edgar (20.09.2026): „einzelne Marker LÖSCHEN … ALLE Maße rechts, auf die
 * Figur ziehen … Mach einen Button zum Hinzufügen aller Maße."
 */
import { Proportionenvorschlag } from './proportionenvorschlag.js';

export class Proportionenmarker {

    /** Länge einer neu gesetzten Linie ohne Wert (cm). */
    static NEU_CM = 20;

    static _kopie(o) { return JSON.parse(JSON.stringify(o)); }

    /** Den Marker eines Maßes aus dem Bild `id` nehmen — gemerkt je Foto (`entfernt`). */
    static loeschen(d, k, id) {
        if (!id || !d.quellen[id]) return;
        delete (d.lagen[id] || {})[k];
        delete (d.start[id] || {})[k];
        (d.entfernt[id] = d.entfernt[id] || new Set()).add(k);
        for (const s of d.sichten) if (s.bild.quelle?.id === id && s.bild.aktiv === k) s.bild.aktiv = null;
        d.nachzeichnen();
        d.aenderung();
    }

    /** Ein Maß ins Bild `id`: waagerecht um `punkt` (sonst Bildmitte), Länge = Wert in cm. */
    static setzen(d, k, punkt, id, zeichnen = true) {
        const q = id ? d.quellen[id] : null;
        if (!q || (d.lagen[id] || {})[k]) return;
        const cm = Number(d.wert(id, k)) || Proportionenmarker.NEU_CM;
        const l = q.px_je_m ? cm / 100 * q.px_je_m : q.breite * 0.2;
        const [cx, cy] = punkt || [q.breite / 2, q.hoehe / 2];
        const linie = [[Math.round((cx - l / 2) * 10) / 10, cy], [Math.round((cx + l / 2) * 10) / 10, cy]];
        (d.lagen[id] = d.lagen[id] || {})[k] = linie;
        (d.start[id] = d.start[id] || {})[k] = Proportionenmarker._kopie(linie);
        if (d.entfernt[id]) d.entfernt[id].delete(k);
        for (const s of d.sichten) if (s.bild.quelle?.id === id) s.bild.aktiv = k;
        if (!zeichnen) return;
        d.nachzeichnen();
        d.aenderung();
    }

    /** Alle fehlenden Maße der Ansicht ins Bild `id` — Lage aus der Ziel-Ansicht (`Proportionenvorschlag`). */
    static alle(d, id) {
        const q = id ? d.quellen[id] : null;
        if (!q) return;
        const reihe = (d.daten().ansichten || {})[q.ansicht];
        for (const m of d.katalog.proportionen || []) {
            if ((d.lagen[id] || {})[m.schluessel]) continue;
            const punkt = Proportionenvorschlag.lage(m.schluessel, q, reihe, d.lagen[id] || {});
            if (punkt) Proportionenmarker.setzen(d, m.schluessel, punkt, id, false);
        }
        d.nachzeichnen();
        d.aenderung();
    }

    /** Alle Vorgaben weg, entfernte Marker wieder da, Linien wie vom Server. */
    static alleLoeschen(d) {
        for (const k of Object.keys(d.eingaben)) d.eingaben[k] = null;
        d.entfernt = {};
        d._quellstand = null;
        d.quellenAufbauen();
        d.lagen = Proportionenmarker._kopie(d.start);
        if (d.tabelle) for (const i of d.tabelle.querySelectorAll('input')) i.value = '';
        d.nachzeichnen();
        d.aenderung();
    }
}
