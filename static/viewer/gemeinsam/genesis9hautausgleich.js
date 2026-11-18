import { Genesis9texturen } from './genesis9texturen.js';
import { Protokoll } from './protokoll.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Genesis9hautausgleich — Gleichmäßigkeit, Symmetrie, Schatten aufhellen und Retusche auf der Albedo der Haut (18.11.2026).
 *
 * Edgar, 18.11.2026: „kannst du erstmal diese Regler im UI bauen? dann möchte ich die n1 Haut in der Bibliothek haben und mit den Reglern ausprobieren.
 * Zusätzlich Retusche". `inst.hautausgleich = {gleich, symmetrie, schatten, retusche}` in Prozent; gerechnet wird auf dem Server (`Genesis9/hautausgleich.py`,
 * Bänder nach Größe auf dem Körper, Muttermale und beidseitige Merkmale geschützt), der neue Bilder in die eigene Bibliothek legt. Hier werden sie als Albedo
 * der vier Hautgruppen eingesetzt — ohne Neubau des Körpers; alle Werte 0 legt die ursprüngliche Karte zurück. Nach jedem Körperbau neu (`Genesis9Modell`).
 *
 * Quelle ist die Albedo, die das Material beim Bau bekam (`userData.albedo`, `Genesis9netz`): ein Bibliothekspfad. Fotokacheln eines Modells (`/api/…`,
 * `Genesis9fototextur`) bleiben unberührt.
 */
export class Genesis9hautausgleich {

    static ADRESSE = '/api/character/genesis9-figur/hautausgleich/';
    static GRUPPEN = ['Head', 'Body', 'Arms', 'Legs'];
    static FELDER = [
        { name: 'gleich', label: 'Gleichmäßigkeit', hilfe: 'Glättet Flecken, Lichtränder und Farbsprünge mittlerer Größe (etwa 4 mm bis 3 cm) — '
            + 'z. B. Schattenflecken und Streifen aus dem Foto. Poren, Muttermale und Merkmale, die auf beiden Körperseiten gleich sind '
            + '(Augen, Brauen, Lippen, Brustwarzen), bleiben.' },
        { name: 'symmetrie', label: 'Symmetrie', hilfe: 'Vergleicht jede Stelle mit der gespiegelten auf der anderen Körperseite. Weicht eine Seite deutlich '
            + 'stärker ab (kaputte Stelle, Fotofehler, einseitiger Schatten), wird sie der anderen angeglichen — die bessere Seite bleibt, wie sie ist.' },
        { name: 'schatten', label: 'Schatten aufhellen', hilfe: 'Hellt Stellen auf, die dunkler sind als ihre Umgebung, ohne eine andere Farbe zu haben '
            + '(Schatten aus dem Foto, bis etwa 13 cm groß). Echte Farbunterschiede wie Lippen, Brustwarzen oder Bräune bleiben.' },
        { name: 'retusche', label: 'Retusche', hilfe: 'Gleicht kleine Flecken unter etwa 8 mm an ihre Umgebung an: Rötungen, Pickel, helle und dunkle '
            + 'Sprenkel. Braune Muttermale bleiben, soweit „Muttermale behalten" sie hält; beidseitige Merkmale bleiben immer.' },
        { name: 'behalten', label: 'Muttermale behalten', vorgabe: 100, hilfe: 'Wie stark Muttermale und alle kleinen Flecken unter etwa 8 mm von '
            + 'Gleichmäßigkeit, Symmetrie und Schatten verschont werden: 100 % = alle bleiben, wie sie sind; 0 % = sie werden mitgeglättet. '
            + 'Unter 100 % darf auch die Retusche Muttermale angleichen. Rechnet allein nichts.' },
    ];
    /** Nur diese lösen eine Rechnung aus; „Muttermale behalten" bestimmt, wie sie wirken. */
    static WIRKEN = ['gleich', 'symmetrie', 'schatten', 'retusche'];
    static WARTEN_MS = 250;

    static werte(inst) {
        return Object.fromEntries(Genesis9hautausgleich.FELDER.map(f => {
            const roh = inst.hautausgleich?.[f.name];
            const w = roh === undefined || roh === null || roh === '' ? (f.vorgabe || 0) : Number(roh) || 0;
            return [f.name, Math.max(0, Math.min(100, w))];
        }));
    }

    static vorgabe(name) {
        return Genesis9hautausgleich.FELDER.find(f => f.name === name)?.vorgabe || 0;
    }

    static aktiv(inst) {
        const werte = Genesis9hautausgleich.werte(inst);
        return Genesis9hautausgleich.WIRKEN.some(name => werte[name] > 0);
    }

    /** Die Materialien der vier Hautgruppen am Körper, deren Albedo ein Bibliothekspfad ist. */
    static materialien(inst) {
        const netz = inst.bodyMesh;
        if (!netz) return [];
        return (Array.isArray(netz.material) ? netz.material : [netz.material])
            .filter(m => Genesis9hautausgleich.GRUPPEN.includes(m?.userData?.gruppe) && m.userData.kachel && m.userData.albedo
                && !String(m.userData.albedo).startsWith('/'));
    }

    /** Einen Wert stellen (Prozent) und nach kurzer Ruhe anwenden. */
    static setzen(inst, name, prozent) {
        inst.hautausgleich = { ...(inst.hautausgleich || {}) };
        const wert = Math.max(0, Math.min(100, Math.round(Number(prozent) || 0)));
        if (wert !== Genesis9hautausgleich.vorgabe(name)) inst.hautausgleich[name] = wert; else delete inst.hautausgleich[name];
        clearTimeout(inst._hautausgleichWarten);
        inst._hautausgleichWarten = setTimeout(() => Genesis9hautausgleich.anwenden(inst), Genesis9hautausgleich.WARTEN_MS);
    }

    /** Die Bilder holen und einsetzen — oder bei allen Werten 0 die ursprünglichen zurücklegen. Ein späterer Aufruf überholt einen früheren. */
    static async anwenden(inst) {
        const lauf = (inst._hautausgleichLauf || 0) + 1;
        inst._hautausgleichLauf = lauf;
        const materialien = Genesis9hautausgleich.materialien(inst);
        if (!materialien.length) return;
        if (!Genesis9hautausgleich.aktiv(inst)) {
            for (const m of materialien) Genesis9hautausgleich._einsetzen(m, null);
            return;
        }
        const quellen = Object.fromEntries(materialien.map(m => [String(m.userData.kachel), m.userData.albedo]));
        const werte = Object.fromEntries(Object.entries(Genesis9hautausgleich.werte(inst)).map(([k, v]) => [k, v / 100]));
        let antwort;
        try {
            antwort = await Serverabruf.rechnen(Genesis9hautausgleich.ADRESSE, { quellen, werte });
        } catch (fehler) {
            Protokoll.warnung('Hautausgleich', `nicht gerechnet: ${fehler.message}`);
            return;
        }
        if (lauf !== inst._hautausgleichLauf) return;
        for (const m of materialien) {
            const pfad = antwort?.kacheln?.[String(m.userData.kachel)];
            if (!pfad) continue;
            Genesis9texturen.holen(pfad, true, m, textur => {
                if (lauf === inst._hautausgleichLauf) Genesis9hautausgleich._einsetzen(m, textur);
            });
        }
    }

    /** `textur` als Albedo — `null` legt die beim ersten Tausch gemerkte ursprüngliche Karte zurück. */
    static _einsetzen(material, textur) {
        if (textur && !material.userData.albedoUrsprung) material.userData.albedoUrsprung = material.map;
        const neu = textur || material.userData.albedoUrsprung;
        if (!neu || material.map === neu) return;
        material.map = neu;
        material.needsUpdate = true;
    }
}
