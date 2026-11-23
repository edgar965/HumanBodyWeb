/**
 * Anatomieverdeckung — was vom Genital außen durch die Kleidung sticht, wird nicht gezeichnet (19.10.2026). Die Rechnung steht in `anatomiedurchstich.js`
 * (ohne Three.js, dort Befund und Messung); hier die Netzseite, gebaut wie `hautverdeckung.js`: der volle Index bleibt in `geometry.userData.indexVoll`,
 * gezeichnet wird ein Index ohne die Dreiecke, von denen eine Ecke außen liegt — dahinter liegt der Stoff, ein Loch entsteht nicht. Durchbrochener Stoff
 * (Spitze) zählt nicht mit: durch ihn sähe man die Löcher (`Stoffdeckung`).
 *
 * WANN: nach jeder Naht (`Hautloch.naehen` → `Hautloch.anatomieNachziehen`): sie läuft bei jeder Hautmaske, also nach jedem An- und Ausziehen und jedem
 * Ein-/Ausblenden, und sie legt den Einzug des Stücks fest, an dem die Rechnung hängt. Ohne Kleidung bekommt das Stück seinen vollen Index zurück.
 * Die Karten des Stücks (`Anatomiebacken`) rechnen immer auf dem VOLLEN Index.
 */
import { Anatomiedurchstich } from './anatomiedurchstich.js';
import { Anatomielage } from './anatomielage.js';
import { Figurhaut } from './figurhaut.js';
import { Hautmaske } from './hautmaske.js';
import { Hautverdeckung } from './hautverdeckung.js';
import { Protokoll } from './protokoll.js';
import { Stoffdeckung } from './stoffdeckung.js';

export class Anatomieverdeckung {

    /** Ruhezeit (ms): mehrere Nähte eines Umlaufs rechnen einmal. */
    static RUHE_MS = 150;
    static _ausstehend = new WeakMap();

    static planen(inst) {
        if (!inst) return;
        clearTimeout(Anatomieverdeckung._ausstehend.get(inst));
        Anatomieverdeckung._ausstehend.set(inst, setTimeout(() => {
            Anatomieverdeckung._ausstehend.delete(inst);
            try {
                Anatomieverdeckung.anwenden(inst);
            } catch (fehler) {
                Protokoll.warnung('Anatomieverdeckung', fehler.message);
            }
        }, Anatomieverdeckung.RUHE_MS));
    }

    /** Alle Anatomie-Stücke der Figur gegen ihre sichtbare, blickdichte Kleidung — gibt je Stück die Zahl der ausgeblendeten Dreiecke zurück. */
    static anwenden(inst) {
        const stoffe = Anatomieverdeckung.stoffe(inst);
        const stand = {};
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            if (!(netz?.userData?.hautTiefe > 0) || !netz.geometry?.index) continue;
            stand[schluessel] = Anatomieverdeckung._stueck(netz, stoffe);
        }
        return stand;
    }

    /**
     * Die sichtbare, blickdichte Kleidung als `[{pos, index}]`: Punkte wie gezeigt (`Anatomielage`) und der volle Index AUS DEMSELBEN NETZ. Dieselbe Auswahl wie
     * `Hautverdeckung.stoffe` (zählt, mit Index, kein Ersatzstück, nicht durchbrochen), aber ohne `Stueckschweissung` — die Platten schweißen und verfeinern ist
     * eine Sache der Hautmaske.
     *
     * BEFUND (21.11.2026, Ladezeit /foto-genesis/test/zauberer_kleidungsregeln_kopie_48/): Seit `Hautverdeckung.stoffe` grobe Stücke verfeinert (18.11.2026,
     * 3cddb71e) nahm diese Stelle die VERFEINERTEN Dreiecke (Umhang 22.665 → 318.567) zu den UNVERFEINERTEN Punkten (12.647): jedes Dreieck mit einer geteilten
     * Kante (über 15 mm) zeigte auf eine Kantenmitte jenseits der Punkte, bekam NaN-Ecken und kam in keine Gitterzelle — es verdeckte nichts; die kleinen
     * Dreiecke behielten ihre Punkte und zählten. Die Teilung kostete 0,45–3 s je Aufruf auf dem Hauptfaden. Im Tab am Zauberer: beide Fassungen 0 Dreiecke
     * ausgeblendet (das Glied liegt ganz in der Robe); mit der Robe um den Ansatz auf 0,9 zusammengezogen alt 0, neu 19 Dreiecke (bei 0,8 und 0,7 gleich).
     * Bis zum 18.11. war `dreiecke` der volle Index des Netzes (git log -L hautverdeckung.js) — so ist es hier wieder.
     */
    static stoffe(inst) {
        const aus = [];
        for (const netz of Object.values(Hautverdeckung.stuecke(inst))) {
            const g = netz?.geometry;
            if (!g?.attributes?.position || !g.index || !Hautverdeckung.zaehlt(netz)) continue;
            if (netz.userData?.hautTiefe || Stoffdeckung.durchbrochen(netz)) continue;
            aus.push({ pos: Anatomielage.lage(g), index: Hautverdeckung.vollerIndex(g) });
        }
        return aus;
    }

    static _stueck(netz, stoffe) {
        const geo = netz.geometry, voll = Figurhaut.merken(geo);
        const pos = Anatomielage.lage(geo), anker = stoffe.length ? Anatomiedurchstich.anker(pos, voll.index) : null;
        if (!anker) {
            if (geo.index.count !== voll.index.length) Figurhaut.indexSetzen(geo, voll.index.slice(), voll.gruppen);
            return 0;
        }
        const t0 = performance.now();
        const lagen = Anatomiedurchstich.lagen(pos, anker, stoffe, geo.attributes.normal?.array || null, Anatomiedurchstich.weite(pos, voll.index, anker));
        const weg = Anatomiedurchstich.dreiecke(voll.index, lagen);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, new Uint8Array(lagen.length), weg);
        Figurhaut.indexSetzen(geo, neu.index, neu.gruppen);
        if (neu.entfernt) {
            Protokoll.debug('Anatomieverdeckung', `${netz.name || 'Stück'}: ${neu.entfernt} Dreiecke stechen durch die Kleidung, ausgeblendet `
                + `(${Math.round(performance.now() - t0)} ms)`);
        }
        return neu.entfernt;
    }
}
