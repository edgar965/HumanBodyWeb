/**
 * Hautverdeckung — die Haut unter der Kleidung wird nicht gezeichnet.
 *
 * Die Rechnung steht in `gemeinsam/hautmaske.js` (ohne Three.js, dort
 * auch der Befund vom 11.09.2026: Splitter Haut an Bund, Schritt und Knie
 * einer 2-mm-Leggings in Dance1, mit keinem Gewichtssatz zu beheben). Hier
 * nur die Three.js-Seite: den Index des Körpers gegen einen ohne die
 * verdeckten Dreiecke tauschen — und zurück, wenn das letzte Stück geht.
 *
 * DER VOLLE INDEX BLEIBT AM NETZ (`geometry.userData.indexVoll`): Die
 * Stoffgrenze des Weichgewebes rechnet die Körpernormalen aus den
 * Dreiecken, und die verdeckten Punkte sind genau die, an denen der Stoff
 * hängt — mit dem gekürzten Index hätten sie keine Normale mehr
 * (`weichgewebeaufbau.js` liest `indexVoll`). Auch jede spätere Maske
 * rechnet vom vollen Index aus, nie vom schon gekürzten.
 *
 * DIE RANDDREIECKE (eine oder zwei Ecken verdeckt) bleiben im Index, sonst
 * stünde jenseits jeder Stoffkante ein Loch von einer Dreieckslänge; ihre
 * verdeckten Ecken zieht `Hauteinzug` im Shader unter den Stoff.
 *
 * WANN: bei jedem `Stueckereignis` (GarmentCode-Stück kommt oder geht,
 * auch beim Nachbinden nach dem Skelettbau — der Körper ist dann ein
 * neues Netz mit geklonter Geometrie, `userData` teilt es sich mit dem
 * alten, der volle Index ist also da). Alle Stücke der Figur zählen, nicht
 * nur das gemeldete: Die Maske ist die Vereinigung.
 */
import { THREE } from './state.js';
import { Hautmaske } from '../gemeinsam/hautmaske.js';
import { Stueckereignis } from './garmentcode_stueckereignis.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Hauteinzug } from '../gemeinsam/hauteinzug.js';

export class Hautverdeckung {

    /** Den Körper der Figur gegen alle ihre Stücke maskieren. */
    static anwenden(inst) {
        const geo = inst?.bodyMesh?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Hautverdeckung.merken(geo);
        const stoffe = Hautverdeckung.stoffe(inst);
        if (!stoffe.length) return Hautverdeckung.aufheben(inst);
        const voll = geo.userData.indexVoll;
        const t0 = performance.now();
        const maske = Hautmaske.verdeckt(geo.attributes.position.array, voll.index, stoffe);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, maske);
        Hautverdeckung.indexSetzen(geo, neu.index, neu.gruppen);
        geo.userData.hautVerdeckt = maske;
        // Die Randdreiecke (eine oder zwei Ecken verdeckt) bleiben gezeichnet;
        // ihre verdeckten Ecken tauchen im Shader unter den Stoff.
        Hauteinzug.setzen(inst.bodyMesh, maske, voll.index);
        let verdeckt = 0;
        for (let i = 0; i < maske.length; i++) verdeckt += maske[i];
        const stand = { verdeckt, dreiecke: neu.entfernt, stuecke: stoffe.length,
                        ms: Math.round(performance.now() - t0) };
        Protokoll.debug('Hautverdeckung', `${verdeckt} Körperpunkte unter ${stoffe.length} `
            + `Stücken, ${neu.entfernt} Dreiecke ausgeblendet, ${stand.ms} ms`);
        return stand;
    }

    /** Den vollen Index wiederherstellen (kein Stück mehr). */
    static aufheben(inst) {
        const geo = inst?.bodyMesh?.geometry;
        const voll = geo?.userData?.indexVoll;
        if (!voll) return null;
        Hautverdeckung.indexSetzen(geo, voll.index, voll.gruppen);
        delete geo.userData.hautVerdeckt;
        Hauteinzug.setzen(inst.bodyMesh, null, null);
        return { verdeckt: 0, dreiecke: 0, stuecke: 0, ms: 0 };
    }

    /** Der volle Index — einmal gemerkt, bevor je gekürzt wurde. */
    static merken(geo) {
        if (geo.userData.indexVoll) return geo.userData.indexVoll;
        geo.userData.indexVoll = {
            index: geo.index.array.slice(),
            gruppen: geo.groups.map((g) => ({ start: g.start, count: g.count,
                                              materialIndex: g.materialIndex })),
        };
        return geo.userData.indexVoll;
    }

    /** Der volle Index eines Körpers, gekürzt oder nicht. */
    static vollerIndex(geo) {
        return geo?.userData?.indexVoll?.index || geo?.index?.array || null;
    }

    /** Die Stücke der Figur, jedes in der Lage des Körpers (Ruhelage). */
    static stoffe(inst) {
        const aus = [];
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const g = netz?.geometry;
            if (!g?.attributes?.position || !g.index) continue;
            aus.push({ schluessel, punkte: g.attributes.position.array,
                       dreiecke: Hautverdeckung.vollerIndex(g) });
        }
        return aus;
    }

    static indexSetzen(geo, index, gruppen) {
        geo.setIndex(new THREE.BufferAttribute(index, 1));
        geo.clearGroups();
        for (const g of gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
    }

    /** Figuren, deren Maske aussteht — ein Lauf je Umlauf, nicht je Ereignis. */
    static _ausstehend = new Set();

    /**
     * Auf jedes Stück reagieren — die Vereinigung aller Stücke zählt.
     *
     * GEBÜNDELT: `GarmentcodeAnziehen.einhaengen` meldet erst das Entfernen
     * des alten Stücks, dann das neue, und beim Laden einer Szene kommen
     * mehrere Stücke nacheinander. Jede Meldung sofort zu rechnen hieße
     * dieselbe Maske mehrmals je Umlauf.
     */
    static einhaengen() {
        Stueckereignis.hoeren(({ inst }) => {
            if (!inst || Hautverdeckung._ausstehend.has(inst)) return;
            Hautverdeckung._ausstehend.add(inst);
            setTimeout(() => {
                Hautverdeckung._ausstehend.delete(inst);
                try { Hautverdeckung.anwenden(inst); }
                catch (fehler) { Protokoll.warnung('Hautverdeckung', fehler.message); }
            }, 0);
        });
    }
}

Hautverdeckung.einhaengen();
// Für Messungen aus der Konsole — die Szene lädt als ein Bündel.
window.__hautverdeckung = Hautverdeckung;
window.__hautmaske = Hautmaske;
