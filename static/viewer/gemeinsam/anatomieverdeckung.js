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
        const stoffe = Hautverdeckung.stoffe(inst).filter((s) => !s.ersatz && !Stoffdeckung.durchbrochen(s.netz))
            .map((s) => ({ pos: Anatomielage.lage(s.netz.geometry), index: s.dreiecke }));
        const stand = {};
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            if (!(netz?.userData?.hautTiefe > 0) || !netz.geometry?.index) continue;
            stand[schluessel] = Anatomieverdeckung._stueck(netz, stoffe);
        }
        return stand;
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
