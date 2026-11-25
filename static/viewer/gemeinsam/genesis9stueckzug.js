import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { Genesis9felder } from './genesis9felder.js';
import { Genesis9reglerfeld } from './genesis9reglerfeld.js';
import { Genesis9sofortzug } from './genesis9sofortzug.js';
import { Genesis9kleidung } from './genesis9kleidung.js';
import { Genesis9stueckstand } from './genesis9stueckstand.js';

/**
 * Genesis9stueckzug — ein Regler eines STÜCKS (Passform, eigene Formen, Haarachsen, Daz' Morphe) an dessen stehendem Netz (25.11.2026, Edgar: „alle regler unter 0,2 s“).
 *
 * Wie `Genesis9sofortzug` für die Figur: beim ersten Zug kommt das Feld des Reglers (`POST …/garderobe/<kennung>/reglerzug/`, `G9stueckzugfeld`), danach summiert der Browser; der genaue
 * Zug (Kollision, Lagen, Drapierung) folgt nach dem Loslassen. Gemessen an EdgarNeus Hose: genau 0,77 s. Ein Regler, der Punkte wegnimmt (Schnitt), hat kein Feld — er wartet auf den
 * genauen Zug.
 */
export class Genesis9stueckzug {

    /** Figur → Map(`kennung|kanal|seite` → {von, bis, fassung, teile} oder ein Versprechen darauf) */
    static _felder = new WeakMap();

    /** Den Regler stellen und zeigen; was an Feldern fehlt, holen. `werte`: die Werte, mit denen das Stück gleich neu angezogen wird. */
    static async ziehen(inst, kennung, regler, wert, werte) {
        if (inst?.quelle !== 'genesis9') return;
        Genesis9stueckstand.wunsch(inst, kennung, regler.name, wert, regler.vorgabe ?? 0);
        Genesis9stueckzug.zeigen(inst, kennung);
        const netz = Genesis9stueckzug._netze(inst, kennung)[0]?.[1], stand = netz?.geometry?.userData?.stueckstand;
        if (!stand) return;
        await Genesis9stueckzug._holenBis(inst, kennung, regler, wert, stand, werte);
        Genesis9stueckzug.zeigen(inst, kennung);
    }

    /** Das Feld schon holen, bevor gezogen wird (Zeiger auf dem Schieber). */
    static vorab(inst, kennung, regler, werte) {
        const stand = inst?.quelle === 'genesis9' && Genesis9stueckzug._netze(inst, kennung)[0]?.[1]?.geometry?.userData?.stueckstand;
        if (!stand) return;
        const a = stand[regler.name] ?? regler.vorgabe ?? 0;
        Genesis9stueckzug._holenBis(inst, kennung, regler, regler.max - a >= a - regler.min ? regler.max : regler.min, stand, werte);
    }

    static _holenBis(inst, kennung, regler, wert, stand, werte) {
        const a = stand[regler.name] ?? regler.vorgabe ?? 0;
        return Promise.all(Genesis9sofortzug.wege(regler.name, a, wert).map(([seite]) => {
            const vz = seite === '+' ? 1 : -1, ende = seite === '+' ? Math.max(regler.max, wert, 0.01) : Math.min(regler.min, wert, -0.01), von = a * vz > 0 ? a : 0;
            return Genesis9stueckzug._holen(inst, kennung, regler.name, seite, von, Math.abs(ende - von) > 0.02 ? ende : 0, { ...werte, regler: stand });
        }));
    }

    static _netze(inst, kennung) {
        return Object.entries(inst?.clothMeshes || {}).filter(([k, n]) => k.startsWith(`${kennung}/`) && !n?.userData?.stoff).map(([k, n]) => [Number(k.slice(kennung.length + 1)), n]);
    }

    static _ablage(inst) {
        if (!Genesis9stueckzug._felder.has(inst)) Genesis9stueckzug._felder.set(inst, new Map());
        return Genesis9stueckzug._felder.get(inst);
    }

    static _holen(inst, kennung, kanal, seite, von, bis, werte) {
        const ablage = Genesis9stueckzug._ablage(inst), schluessel = `${kennung}|${kanal}|${seite}`;
        if (!ablage.has(schluessel)) ablage.set(schluessel, Genesis9stueckzug._fragen(inst, kennung, kanal, von, bis, werte).then(e => { ablage.set(schluessel, e); }));
        return ablage.get(schluessel);
    }

    static async _fragen(inst, kennung, kanal, von, bis, werte) {
        try {
            const [, rumpf] = Genesis9kleidung.anfrage(inst, kennung, werte, null);
            const daten = await Serverabruf.netzSenden(`${inst.constructor.ADRESSE}garderobe/${encodeURIComponent(kennung)}/reglerzug/`, { rumpf, kanal, von, bis });
            if (daten.fehler) throw new Error(daten.fehler);
            return { von, bis, fassung: Genesis9reglerfeld._fassung += 1, teile: daten.teile.map(Genesis9reglerfeld._lesen) };
        } catch (fehler) {
            Protokoll.warnung('Genesis9stueckzug', `${kennung} ${kanal}: kein Sofortfeld (${fehler.message}) — der genaue Zug zeigt die Änderung`);
            return { von, bis, teile: [] };
        }
    }

    /** Auf den Netzen des Stücks zeigen, was seit ihrem Bau an seinen Reglern gezogen wurde. */
    static zeigen(inst, kennung) {
        const wuensche = Genesis9stueckstand.wuensche(inst, kennung), ablage = Genesis9stueckzug._felder.get(inst);
        if (!wuensche || !ablage) return;
        for (const [nummer, netz] of Genesis9stueckzug._netze(inst, kennung)) {
            const geo = netz.geometry, stand = geo.userData.stueckstand, lage = geo.getAttribute('position');
            if (!stand || !lage) continue;
            const felder = {}, gewichte = {};
            for (const [kanal, { wert, vorgabe }] of wuensche) {
                for (const [seite, weg] of Genesis9sofortzug.wege(kanal, stand[kanal] ?? vorgabe, wert)) {
                    const e = ablage.get(`${kennung}|${kanal}|${seite}`), feld = e?.teile?.[nummer];
                    if (!feld || feld.punkte !== lage.count || e.bis === e.von) continue;
                    felder[`${kanal}|${seite}${e.fassung}`] = feld;
                    gewichte[`${kanal}|${seite}${e.fassung}`] = weg / (e.bis - e.von);
                }
            }
            if (Object.keys(gewichte).length) Genesis9felder.anwenden(netz, Genesis9stueckstand.GRUPPE, felder, gewichte, true);
            else if (geo.userData.felder?.gruppen.has(Genesis9stueckstand.GRUPPE)) Genesis9felder.entfernen(netz, Genesis9stueckstand.GRUPPE);
            else continue;
            geo.boundingSphere = null;
            geo.boundingBox = null;
        }
    }
}
