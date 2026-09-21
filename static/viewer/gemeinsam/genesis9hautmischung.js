import { Genesis9haut } from './genesis9haut.js';
import { Genesis9texturen } from './genesis9texturen.js';
import { Protokoll } from './protokoll.js';
import { Serverabruf } from './serverabruf.js';

/**
 * Genesis9hautmischung — weitere Hautsätze mit Gewicht über der gewählten Haut.
 *
 * Edgar (21.09.2026): „kann ich denn eine HD Textur von einem Modell (z.B.
 * Ursula) auf Kin übertragen? … mach eine Kategorie und Einstellung ganz unten
 * bei den Modell Eigenschaften, «Textur» mit allen Texturen die du hast, und
 * Regler dazu in %". Die Auswahl «Haut» tauscht den Satz; hier wird GEMISCHT:
 * `inst.hautmischung = {hautsatz: prozent}`, jede Schicht mit Prozent > 0 legt
 * Albedo, Normalen und Rauheit ihres Satzes im Shader über die Grundhaut
 * (`Genesis9haut.mischung`, Reihenfolge = Reihenfolge im Objekt).
 *
 * OHNE NEUBAU DES KÖRPERS: ein Reglerzug ist ein Uniform-Update
 * (`gewichte`), erst eine neue Schicht holt ihre Bildpfade vom Server
 * (`/haut/<satz>/bilder/`, einmal je Satz) und die Bilder aus dem Vorrat
 * (`Genesis9texturen` — ein zweiter Satz teilt nichts mit dem ersten, 4K je
 * Kachel, ~64 MB auf der GPU je Kachel und Schicht; deshalb `HOECHSTENS` 3).
 * Nach jedem Körperbau (`koerperAufbauen`) hängt das Modell die Mischung neu
 * ein — die Materialien sind dann frisch.
 *
 * Gruppen: die Materialien tragen `userData.gruppe` (Head, Body, Arms, Legs,
 * Fingernails …); eine Schicht wirkt auf jede Gruppe, für die ihr Satz ein
 * Albedo hat — auch Mund und Augen eines „All MAT"-Satzes auf den Anhängen.
 */
export class Genesis9hautmischung {

    static ADRESSE = '/api/character/genesis9-figur/haut/';
    /** Mehr Schichten kosten je Kachel weitere 4K-Bilder auf der GPU. */
    static HOECHSTENS = 3;
    /** Hautsatz -> Promise<{gruppe: {albedo, normalen, rauheit}}> */
    static _bilder = new Map();

    /** Die wirksamen Schichten: `[{id, gewicht}]`, Prozent > 0, höchstens `HOECHSTENS`. */
    static schichten(inst) {
        return Object.entries(inst.hautmischung || {})
            .filter(([, prozent]) => Number(prozent) > 0)
            .slice(0, Genesis9hautmischung.HOECHSTENS)
            .map(([id, prozent]) => ({ id, gewicht: Math.min(100, Number(prozent)) / 100 }));
    }

    /** Alle Materialien der Figur mit Gruppe (Körper und Anhänge). */
    static materialien(inst) {
        const netze = [inst.bodyMesh, ...Object.values(inst.anhangNetze || {})].filter(Boolean);
        const aus = [];
        for (const netz of netze) {
            for (const m of (Array.isArray(netz.material) ? netz.material : [netz.material])) {
                if (m?.userData?.gruppe) aus.push(m);
            }
        }
        return aus;
    }

    /** Die Bildpfade eines Satzes je Gruppe — einmal geholt; {} bei Fehler. */
    static bilder(id) {
        if (!Genesis9hautmischung._bilder.has(id)) {
            const adresse = Genesis9hautmischung.ADRESSE + encodeURIComponent(id) + '/bilder/';
            Genesis9hautmischung._bilder.set(id, Serverabruf.json(adresse)
                .then(antwort => antwort.gruppen || {})
                .catch(fehler => {
                    Protokoll.warnung('Hautmischung', `Bilder von „${id}" nicht ladbar: ${fehler.message}`);
                    Genesis9hautmischung._bilder.delete(id);
                    return {};
                }));
        }
        return Genesis9hautmischung._bilder.get(id);
    }

    /**
     * Die Mischung auf die Materialien der Figur legen: Programm mit der Zahl
     * der Schichten, Bilder je Gruppe einhängen, Gewichte setzen.
     */
    static async anwenden(inst) {
        const schichten = Genesis9hautmischung.schichten(inst);
        const lauf = inst._mischungslauf = (inst._mischungslauf || 0) + 1;
        const bilder = await Promise.all(schichten.map(s => Genesis9hautmischung.bilder(s.id)));
        if (lauf !== inst._mischungslauf) return;           // überholt
        inst._mischungsschichten = schichten.map(s => s.id);
        for (const material of Genesis9hautmischung.materialien(inst)) {
            const gruppe = material.userData.gruppe;
            // Nur Schichten, die diese Gruppe bedienen — sonst stünde ein
            // schwarzer Platzhalter mit Gewicht auf dem Mund.
            const eigene = schichten.map((s, i) => ({ ...s, bilder: bilder[i][gruppe] }))
                .filter(s => s.bilder?.albedo);
            Genesis9haut.mischung(material, eigene.length);
            material.userData.genesis9.mischungIds = eigene.map(s => s.id);
            eigene.forEach((s, i) => {
                Genesis9haut.mischungGewicht(material, i, s.gewicht);
                Genesis9hautmischung._laden(material, i, s.bilder);
            });
        }
    }

    static _laden(material, i, bilder) {
        const holen = (pfad, art, srgb) => Genesis9texturen.holen(pfad, srgb, material,
            bild => Genesis9haut.mischungBild(material, i, art, bild));
        holen(bilder.albedo, 'farbe', true);
        if (bilder.normalen) holen(bilder.normalen, 'normalen', false);
        if (bilder.rauheit) holen(bilder.rauheit, 'rauheit', false);
    }

    /**
     * Nur die Gewichte nachziehen (Reglerzug) — wenn sich die MENGE der
     * Schichten ändert (0 → 30 %, 30 → 0 %), muss `anwenden` ran.
     * Liefert true, wenn das reichte.
     */
    static gewichte(inst) {
        const schichten = Genesis9hautmischung.schichten(inst);
        const materialien = Genesis9hautmischung.materialien(inst);
        if (!materialien.length) return true;
        const bekannt = inst._mischungsschichten || [];
        if (bekannt.length !== schichten.length || bekannt.some((id, i) => id !== schichten[i].id)) {
            return false;
        }
        for (const material of materialien) {
            // Je Material sind nur die Schichten da, die seine Gruppe bedienen —
            // in der Reihenfolge der Gesamtliste (`mischungIds` aus `anwenden`).
            const eigene = material.userData.genesis9?.mischungIds || [];
            eigene.forEach((id, i) => {
                const s = schichten.find(x => x.id === id);
                if (s) Genesis9haut.mischungGewicht(material, i, s.gewicht);
            });
        }
        return true;
    }
}
