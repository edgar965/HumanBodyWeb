import { Eigenhaut } from './eigenhaut.js';
import { Knochenkette } from './knochenkette.js';
import { Serverabruf } from './serverabruf.js';
import { base64ToFloat32 } from './kodierung.js';
import { Smpldetails } from './smpldetails.js';
import { Smplnetz } from './smplnetz.js';

/**
 * Smplformzug — ein Reglerzug an einer stehenden SMPL-X-Figur (25.11.2026, Edgar: „alle regler unter 0,2 s“).
 *
 * Der Server schickt nur Punkte und Skelett (`nur: 'form'`); Dreiecke, UV, Gewichte, Material, Texturen und Hautdetails bleiben stehen. Bis dahin baute jeder Zug eine neue Figur, und der
 * Server maß sie vorher aus und legte sie ab — gemessen 13,5 bis 18 s. Die Maße kommen danach (`Smplmassanzeige`).
 *
 * EIN Zug zur Zeit, der letzte Wert gewinnt: Zwei gleichzeitige könnten sich überholen, dann bliebe die ältere Form stehen.
 */
export class Smplformzug {

    /** Figur → true, solange ein Zug läuft; 'nochmal', wenn inzwischen weitergezogen wurde. */
    static _laeuft = new WeakMap();

    /** Trägt die Figur Stücke (gebunden an ihr Skelett), baut der Aufrufer sie neu wie bisher. */
    static moeglich(inst) {
        return Boolean(inst.bodyMesh?.isSkinnedMesh && inst.skelett && inst._uvUrsprung && !Object.keys(inst.clothMeshes || {}).length);
    }

    /** Die Form der Figur (`inst.form`) zeigen. @returns true, wenn dieser Aufruf den Zug gefahren hat; false, wenn einer lief, der sie mitnimmt */
    static async ziehen(inst) {
        if (Smplformzug._laeuft.has(inst)) {
            Smplformzug._laeuft.set(inst, 'nochmal');
            return false;
        }
        try {
            do {
                Smplformzug._laeuft.set(inst, true);
                await Smplformzug._einmal(inst);
            } while (Smplformzug._laeuft.get(inst) === 'nochmal');
        } finally {
            Smplformzug._laeuft.delete(inst);
        }
        return true;
    }

    static async _einmal(inst) {
        const daten = await Serverabruf.netzSenden('/api/character/smpl-figur/formen/', { geschlecht: inst.geschlecht || 'female', ...inst.form, nur: 'form' });
        if (daten.fehler) throw new Error(daten.fehler);
        Smplformzug.anwenden(inst, daten);
    }

    /** Die Antwort auf die stehende Figur legen. */
    static anwenden(inst, daten) {
        const namen = inst.skelett.bones.map(k => k.name), neue = Knochenkette.bauplan(daten.skelett?.knochen).map(k => k.name);
        if (namen.length !== neue.length || !namen.every((n, i) => n === neue[i])) throw new Error('Das Skelett der Form passt nicht zur Figur');   // die stehenden Gewichte gälten nicht
        const flach = base64ToFloat32(daten.punkte);
        const punkte = Array.from({ length: daten.punktzahl }, (_, i) => flach.subarray(3 * i, 3 * i + 3));
        inst.skelettBauen(daten.skelett);
        inst.bodyMesh = Smplnetz.umformen(inst.group, inst.bodyMesh, flach, inst._uvUrsprung);
        inst.bodyMesh.name = `garmentcode_koerper_${daten.name}`;
        Eigenhaut.einhaengen(inst.group, inst.bodyMesh, inst.skelett);
        Smpldetails.umformen(inst, punkte);
        inst.koerper = daten.name;
        inst.betas = daten.betas || inst.betas;
        inst.masse = daten.masse || {};
        inst.hoehe = daten.hoehe || 0;
    }
}
