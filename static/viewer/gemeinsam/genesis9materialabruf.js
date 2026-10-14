import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Genesis9antwortspeicher } from './genesis9antwortspeicher.js';

/**
 * Genesis9materialabruf — die Netzantwort des Körpers: aus dem Speicher, mit neuen Materialien, oder vom Server (12.10.2026).
 *
 * Zwei Dinge in einer Frage (`holen`), beide aus Edgars Aufträgen vom 12.10.2026:
 *
 * 1. „Bei einem reinen Hautwechsel das Netz nicht neu holen und nur die Texturen tauschen." Gemessen im Chrome (cute girl Daz, vier Häute): jeder Wechsel holte die ganze
 *    Netzantwort noch einmal — 10 MB, der Server rechnete 0,9–1,4 s (Antwort-Kopfzeit), obwohl sich an Punkten, Skelett und Hautgewichten nichts ändert. Haut, Augenbild,
 *    Brauenfarbe und Presets stehen nur in den `gruppen` des Körpers und der Anhänge; der Server liefert sie allein (`POST …/material/`, `G9materialnetz`), und hier werden
 *    sie in die gehaltene Antwort eingesetzt (`verbinden`).
 * 2. „Jede Figur soll auch ihre zweite Fassung (fein) und ultrafein im RAM halten." Die Antworten liegen je Stufe im `Genesis9antwortspeicher`; ein Stufenwechsel auf eine
 *    Stufe, die schon dagewesen war, braucht keine Anfrage. Die Materialien werden dabei nachgezogen: Jeder Eintrag trägt, mit welcher Haut/welchen Augen/Brauen/Presets
 *    er zuletzt gebaut wurde (`material`); weicht die Wahl ab, kommt die leichte Anfrage für DIESE Stufe.
 *
 * WANN GEHALTENES GILT: Die Stellung gleicht der des Eintrags in allem außer Haut, Augen, Brauenfarbe und Presets (`stellung`): dieselbe Adresse ohne Stufe, dieselben Regler,
 * Pose, Ausdruck, Griffe, Kleidung UND derselbe Brauenstil (er wählt die Anhänge). Wer eines davon ändert, bekommt von selbst die volle Antwort. Dazu müssen die Gruppen der
 * leichten Antwort zum Netz passen (`passt`: gleiche Namen und Indexbereiche, gleiche Stufe). Scheitert die leichte Anfrage (alter Server, Netzfehler), wird das Netz geholt —
 * der Wechsel geht nie verloren.
 */
export class Genesis9materialabruf {

    /** Rumpffelder, die nur Materialien bestimmen. Der Brauenstil gehört NICHT dazu: Er wählt, welche Anhänge es gibt. */
    static MATERIAL = ['haut', 'augen', 'brauen', 'praesets'];

    /** Der Rumpf der Netzanfrage: alles, was Gestalt, Skelett und Materialien der Figur bestimmt. */
    static nutzlast(inst) {
        return {
            regler: inst.regler || {}, haut: inst.haut, augen: inst.augen, brauen: inst.brauen, brauenstil: inst.brauenstil,
            praesets: inst.praesets, pose: inst.pose, ausdruck: inst.ausdruck, griffe: inst.griffe(), kleidung: inst.kleidungsliste(),
            ...(inst.drehung ? { drehung: inst.drehung } : {}),
        };
    }

    /** Die Stellung: Adresse ohne Stufe und Rumpf ohne die Materialfelder — alles, was die Geometrie bestimmt. */
    static stellung(adresse, nutzlast) {
        const rest = { ...nutzlast };
        for (const feld of Genesis9materialabruf.MATERIAL) delete rest[feld];
        return JSON.stringify([Genesis9antwortspeicher.ohneStufen(adresse), rest]);
    }

    /** Was die Materialien bestimmt — der Eintrag im Speicher trägt es mit. */
    static material(nutzlast) {
        return JSON.stringify(Genesis9materialabruf.MATERIAL.map(feld => nutzlast[feld] ?? null));
    }

    /** Die Adresse der leichten Anfrage zur Netzadresse (`…/netz/[?stufen=N]`); der Name der Figur darf selbst „netz" heißen. */
    static adresse(netzAdresse) {
        return netzAdresse.replace(/\/netz\/(\?|$)/, '/material/$1');
    }

    /**
     * Die Antwort für den Bau: aus dem Speicher, dort mit den Materialien der Wahl, sonst vom Server.
     * @returns {Promise<{daten: object, stellung: string, stufe: string, material: string, neu: boolean}>}  `neu`: noch abzulegen (`merken`)
     */
    static async holen(inst, adresse, nutzlast) {
        const stellung = Genesis9materialabruf.stellung(adresse, nutzlast);
        const stufe = Genesis9antwortspeicher.stufe(adresse);
        const material = Genesis9materialabruf.material(nutzlast);
        const treffer = Genesis9antwortspeicher.suchen(inst, 'koerper', stellung, stufe);
        if (treffer?.material === material) {
            return { daten: Genesis9antwortspeicher.kopie(treffer.daten), stellung, stufe, material, neu: false };
        }
        const daten = treffer ? await Genesis9materialabruf._leicht(adresse, nutzlast, Genesis9antwortspeicher.kopie(treffer.daten)) : null;
        return { daten: daten || await Serverabruf.netzSenden(adresse, nutzlast), stellung, stufe, material, neu: true };
    }

    /** Eine Antwort, die gebaut wird, im Speicher ablegen (nicht die einer überholten Anfrage; nicht, was schon so darin liegt). */
    static merken(inst, antwort) {
        if (antwort.neu) Genesis9antwortspeicher.ablegen(inst, 'koerper', antwort.stellung, antwort.stufe, antwort.daten, antwort.material);
    }

    /** Die leichte Anfrage — oder null (Fehler, passt nicht): dann kommt die volle. */
    static async _leicht(adresse, nutzlast, stand) {
        try {
            const material = await Serverabruf.netzSenden(Genesis9materialabruf.adresse(adresse), nutzlast);
            const daten = Genesis9materialabruf.verbinden(stand, material);
            if (!daten) Protokoll.info('Genesis9materialabruf', 'Die Materialien passen nicht zum Netz — das Netz wird neu geholt');
            return daten;
        } catch (fehler) {
            Protokoll.warnung('Genesis9materialabruf', `Materialien nicht geholt (${fehler.message}) — das Netz wird neu geholt`);
            return null;
        }
    }

    /**
     * Die Antwort des letzten Baus mit den Materialien der leichten — oder null, wenn diese nicht zu ihr passen. Rein: verändert keinen der beiden.
     * @param stand     die volle Antwort (eine Kopie aus dem Speicher)
     * @param material  `{stufen, gruppen, anhaenge: [{schluessel, gruppen}]}`
     */
    static verbinden(stand, material) {
        if (!stand || !Array.isArray(material?.gruppen) || !Array.isArray(material.anhaenge)) return null;
        if (material.stufen !== stand.stufen || !Genesis9materialabruf.passt(stand.gruppen, material.gruppen)) return null;
        const alte = stand.anhaenge || [];
        if (alte.length !== material.anhaenge.length) return null;
        const anhaenge = [];
        for (const anhang of alte) {
            const neu = material.anhaenge.find(m => m.schluessel === anhang.schluessel);
            if (!neu || !Genesis9materialabruf.passt(anhang.gruppen, neu.gruppen)) return null;
            anhaenge.push({ ...anhang, gruppen: neu.gruppen });
        }
        return { ...stand, gruppen: material.gruppen, anhaenge };
    }

    /** Gleiche Gruppen in gleicher Reihenfolge: Name, Kachel und Indexbereich (der Bereich gehört zum Netz, das schon steht). */
    static passt(alt, neu) {
        if (!Array.isArray(alt) || !Array.isArray(neu) || alt.length !== neu.length) return false;
        return alt.every((g, i) => g.name === neu[i].name && g.kachel === neu[i].kachel
            && g.index_ab === neu[i].index_ab && g.index_anzahl === neu[i].index_anzahl);
    }
}
