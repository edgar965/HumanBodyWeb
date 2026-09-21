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
 * verdeckten Ecken zieht `Hauteinzug` im Shader unter den Stoff. Seit dem
 * 13.09.2026 bleibt dahinter ein Band versenkter Haut (`Saumband`) — wer in
 * eine Ärmelöffnung sieht, sieht den Arm, nicht die andere Ärmelwand.
 *
 * WANN: bei jedem `Stueckereignis` (GarmentCode-Stück kommt oder geht,
 * auch beim Nachbinden nach dem Skelettbau — der Körper ist dann ein
 * neues Netz mit geklonter Geometrie, `userData` teilt es sich mit dem
 * alten, der volle Index ist also da). Alle Stücke der Figur zählen, nicht
 * nur das gemeldete: Die Maske ist die Vereinigung.
 *
 * Die Three.js-Handgriffe (`merken`, `indexSetzen`, `vollerIndex`) erbt sie
 * von `gemeinsam/figurhaut.js` — sie standen hier ein zweites Mal (Befund
 * `doppelcode`, 17.09.2026). Eigen bleibt, WO Körper und Stücke liegen
 * (`inst.bodyMesh`, `inst.clothMeshes`) und das Ereignis, das sie anstößt.
 */
import { Hautmaske } from './hautmaske.js';
import { Figurhaut } from './figurhaut.js';
import { Stueckereignis } from './stueckereignis.js';
import { Skelettereignis } from './skelettereignis.js';
import { Protokoll } from './protokoll.js';
import { Hauteinzug } from './hauteinzug.js';
import { Saumschnitt } from './saumschnitt.js';

export class Hautverdeckung extends Figurhaut {

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
        geo.userData.hautVerdeckt = maske;
        // Verdeckte Haut neben der gezeichneten bleibt versenkt gezeichnet
        // (`Saumband`); die Randecken wandern im Shader unter die Stoffkante
        // (`Saumschnitt`). Aus dem Index fällt nur, was jenseits des Bands liegt.
        const einzug = Hauteinzug.setzen(inst.bodyMesh, maske, voll.index, { kanten: Saumschnitt.kanten(stoffe) });
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, einzug.weg);
        Hautverdeckung.indexSetzen(geo, neu.index, neu.gruppen);
        let verdeckt = 0;
        for (let i = 0; i < maske.length; i++) verdeckt += maske[i];
        const stand = { verdeckt, band: einzug.band, dreiecke: neu.entfernt, stuecke: stoffe.length,
                        ms: Math.round(performance.now() - t0) };
        Protokoll.debug('Hautverdeckung', `${verdeckt} Körperpunkte unter ${stoffe.length} `
            + `Stücken, ${einzug.band} davon im Saumband, ${neu.entfernt} Dreiecke ausgeblendet, `
            + `${stand.ms} ms`);
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

    /**
     * Die Stücke der Figur, jedes in der Lage des Körpers (Ruhelage). Ein
     * Daz-Stück zählt nur als Kleidung (`userData.art`, 20.09.2026): unter
     * Haar und Requisiten bleibt die Haut — ein Strang- oder Kartenhaar
     * verdeckt keine Kopfhaut, ein Dolch keine Hand.
     */
    static stoffe(inst) {
        const aus = [];
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const g = netz?.geometry;
            if (!g?.attributes?.position || !g.index) continue;
            if (!Hautverdeckung.zaehlt(netz)) continue;
            aus.push({ schluessel, punkte: g.attributes.position.array,
                       dreiecke: Hautverdeckung.vollerIndex(g) });
        }
        return aus;
    }

    /** Ohne `art` (GarmentCode, MakeHuman, UMA) wie bisher; mit `art` nur `kleidung`. */
    static zaehlt(netz) {
        const art = netz?.userData?.art;
        return !art || art === 'kleidung';
    }

    /** Ruhezeit nach der letzten Meldung; `_ausstehend`: inst -> Zeitgeber. */
    static RUHE_MS = 400;
    static _ausstehend = new Map();

    /**
     * Auf jedes Stück reagieren — die Vereinigung aller Stücke zählt.
     *
     * GEBÜNDELT: `GarmentcodeAnziehen.einhaengen` meldet erst das Entfernen
     * des alten Stücks, dann das neue, und beim Laden einer Szene kommen
     * mehrere Stücke nacheinander. Jede Meldung sofort zu rechnen hieße
     * dieselbe Maske mehrmals je Umlauf.
     */
    static einhaengen() {
        // Mit Ruhezeit (19.09.2026): Ein Umbau der Genesis-9-Figur holt Körper und
        // jedes Daz-Stück einzeln — jede Ankunft meldet, gerechnet wird EINMAL danach.
        Stueckereignis.hoeren(({ inst }) => Hautverdeckung.planen(inst));
        // Auch ein frisches Skelett (neuer Körper, Käfig → feine Stufe, 20.09.2026):
        // der neue Körper hat keine Maske, die Stücke melden sich nicht noch einmal.
        Skelettereignis.hoeren(({ inst }) => Hautverdeckung.planen(inst));
    }

    static planen(inst) {
        if (!inst) return;
        clearTimeout(Hautverdeckung._ausstehend.get(inst));
        Hautverdeckung._ausstehend.set(inst, setTimeout(() => {
            Hautverdeckung._ausstehend.delete(inst);
            try { Hautverdeckung.anwenden(inst); }
            catch (fehler) { Protokoll.warnung('Hautverdeckung', fehler.message); }
        }, Hautverdeckung.RUHE_MS));
    }
}

Hautverdeckung.einhaengen();
// Für Messungen aus der Konsole — die Szene lädt als ein Bündel.
window.__hautverdeckung = Hautverdeckung;
window.__hautmaske = Hautmaske;
