import { Gcnachformung } from './gcnachformung.js';
import { Humanbodybindung } from './humanbodybindung.js';
import { float32ToBase64 } from './kodierung.js';
import { Protokoll } from './protokoll.js';

/**
 * Gcreglerfolge — GarmentCode-Stücke auf Genesis 9 folgen den Reglern
 * (24.09.2026, Edgar: „fixe auch dies").
 *
 * Genesis 9 baut nach jedem Reglerzug Körper UND Skelett neu und meldet das
 * `Skelettereignis`; `GarmentcodeNachbindung` baut daraufhin jedes `gc_`-Stück
 * aus seinen Rig-Daten (`userData.gcRig`) neu. Hier stehen die Rig-Daten davor
 * auf dem neuen Körper: Je Figur bleibt der zuletzt gesehene Körper gemerkt
 * (die Punkte selbst — `Netzentsorgung` räumt das alte Netz ab), und hat der
 * neue dieselbe Punktzahl, setzt `Gcnachformung` Punkte und Normalen um.
 * Andere Punktzahl (Käfig → feine Stufe): nichts umsetzen, nur neu merken.
 *
 * Die umgesetzten Punkte gehen auch in die Daz-Lagen (`punkte64` am Rig,
 * `Genesis9lagen.gcGetragen`) — der Server kennt sonst nur die Rig-Datei vom
 * Bau, und ein Hemd läge nach dem Zug über der alten Hose.
 *
 * GRENZE: Gespeichert wird die Rig-ADRESSE. Nach einem Neuladen steht das Stück
 * wieder in der Form vom Bau; erst ein neuer Bau passt es dem Körper von dann an.
 */
export class Gcreglerfolge {

    /** Figur → `{geo, punkte}` des zuletzt gesehenen Körpers. */
    static _koerper = new WeakMap();

    /** Vor `nachbinden` rufen; gibt die Zahl der umgesetzten Stücke. */
    static anwenden(inst) {
        const geo = inst?.bodyMesh?.geometry;
        if (inst?.quelle !== 'genesis9' || !geo?.attributes?.position) return 0;
        const vorher = Gcreglerfolge._koerper.get(inst);
        const jetzt = { geo, punkte: geo.attributes.position.array };
        Gcreglerfolge._koerper.set(inst, jetzt);
        if (!vorher || vorher.geo === geo || vorher.punkte.length !== jetzt.punkte.length) return 0;
        const index = Humanbodybindung.vollerIndex(vorher.geo) || Humanbodybindung.vollerIndex(geo);
        let anzahl = 0;
        for (const [schluessel, netz] of Object.entries(inst.clothMeshes || {})) {
            const rig = netz?.userData?.gcRig;
            if (!schluessel.startsWith('gc_') || !rig?.punkte?.length) continue;
            try {
                netz.userData.gcRig = Gcreglerfolge.umgesetzt(rig, vorher.punkte, jetzt.punkte, index);
                anzahl += 1;
            } catch (fehler) {
                Protokoll.warnung('GarmentCode', `${schluessel}: nicht nachgeformt — ${fehler.message}`);
            }
        }
        return anzahl;
    }

    /** Das Rig mit umgesetzten Punkten und Normalen (Projektlage: x, −z, y der Szene). */
    static umgesetzt(rig, alt, neu, index) {
        const stoff = Gcreglerfolge._three(rig.punkte);
        const normalen = rig.normalen?.length === rig.punkte.length ? Gcreglerfolge._three(rig.normalen) : null;
        const ergebnis = Gcnachformung.umsetzen(alt, neu, index, stoff, normalen);
        if (!ergebnis) throw new Error('Körper ohne gleiche Topologie');
        return {
            ...rig,
            punkte: Gcreglerfolge._projekt(ergebnis.punkte),
            ...(normalen ? { normalen: Gcreglerfolge._projekt(ergebnis.normalen) } : {}),
            punkte64: float32ToBase64(ergebnis.punkte),
            nachgeformt: (rig.nachgeformt || 0) + 1,
        };
    }

    /** Projekt `[[x, y, z]]` (Z oben) → Three Float32Array (x, z, −y) — wie `GarmentcodeGeometrie.aus`. */
    static _three(liste) {
        const aus = new Float32Array(liste.length * 3);
        liste.forEach((p, i) => { aus[3 * i] = p[0]; aus[3 * i + 1] = p[2]; aus[3 * i + 2] = -p[1]; });
        return aus;
    }

    static _projekt(feld) {
        const aus = new Array(feld.length / 3);
        for (let i = 0; i < aus.length; i++) aus[i] = [feld[3 * i], -feld[3 * i + 2], feld[3 * i + 1]];
        return aus;
    }
}
