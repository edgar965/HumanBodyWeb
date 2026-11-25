import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { base64ToFloat32, base64ToUint32 } from './kodierung.js';
import { Genesis9felder } from './genesis9felder.js';
import { Genesis9hautebenen } from './genesis9hautebenen.js';
import { Genesis9hautfalten } from './genesis9hautfalten.js';
import { Genesis9kleidung } from './genesis9kleidung.js';
import { Genesis9materialabruf } from './genesis9materialabruf.js';
import { Genesis9sofortzug } from './genesis9sofortzug.js';

/**
 * Genesis9reglerfeld — das Feld eines Reglers vom Server holen (25.11.2026, `POST …/<figur>/reglerzug/`, `G9reglerzugfeld`), einmal je Kanal und Seite; gezeigt wird es von
 * `Genesis9sofortzug`. Erst der Körper, dann Anhänge und Stücke: der Körper steht nach der halben Zeit. Eine Anfrage zur Zeit je Kanal und Seite — zieht Edgar weiter, während sie
 * läuft, gilt danach der letzte Wert.
 */
export class Genesis9reglerfeld {

    /** Figur → Map(Schlüssel → Versprechen) der laufenden Anfragen. */
    static _laufend = new WeakMap();
    static _fassung = 0;
    /** Punktzahl → [0, 1, 2 …]: ein Feld, das jeden Punkt bewegt, kommt ohne Nummern. */
    static _alle = new Map();

    /**
     * Alles holen, was für den Stand `inst.regler` an den Kanälen `kanaele` noch fehlt, und zeigen, sobald es da ist.
     * @param grenzen  `{kanal: {min, max}}` — bis wohin das Feld reicht (Vorgabe −1 … 1)
     */
    static async nachziehen(inst, kanaele, grenzen = {}) {
        const stand = Genesis9reglerfeld.stand(inst);
        if (!stand) return;
        const anfragen = [];
        for (const kanal of kanaele) {
            for (const [seite, von, bis] of Genesis9reglerfeld.fehlend(inst, kanal, stand, inst.regler?.[kanal] ?? 0, grenzen[kanal])) {
                anfragen.push(Genesis9reglerfeld.holen(inst, kanal, seite, von, bis, stand));
            }
        }
        if (!anfragen.length) return;
        await Promise.all(anfragen);
        // ein unlinearer Kanal, der inzwischen weitergezogen wurde: sein Feld gilt je Wert
        const weiter = kanaele.filter(k => Genesis9sofortzug.UNLINEAR.test(k) && Genesis9sofortzug.feld(inst, k, 'n')?.ziel !== (inst.regler?.[k] ?? 0));
        if (weiter.length && Genesis9reglerfeld.stand(inst) === stand) await Genesis9reglerfeld.nachziehen(inst, weiter, grenzen);
    }

    /** Die Stellung der Figur im Server rechnen lassen, bevor der erste Regler gezogen wird (aus dem Antwortvorrat geladen, kennt sie dieser Serverprozess nicht) — leise. */
    static async wecken(inst) {
        const stand = Genesis9reglerfeld.stand(inst);
        if (!stand || !inst.constructor.ADRESSE) return;
        try {
            await Serverabruf.senden(`${inst.constructor.ADRESSE}${encodeURIComponent(inst.figur)}/reglerzug/`,
                                     { rumpf: { ...Genesis9materialabruf.nutzlast(inst), regler: stand }, teil: 'wecken', stuecke: Genesis9reglerfeld.stuecke(inst) });
        } catch (fehler) {
            Protokoll.debug('Genesis9reglerfeld', `nicht geweckt: ${fehler.message}`);
        }
    }

    /** Warten, bis keine Anfrage dieser Figur mehr läuft — höchstens `frist` ms, und nur, bis feststeht, dass der Körper ohnehin genau nachgerechnet wird (`Genesis9sofortzug.ungenau`). */
    static async abwarten(inst, frist) {
        const ende = performance.now() + frist;
        while (Genesis9reglerfeld._laufend.get(inst)?.size && performance.now() < ende && !Genesis9sofortzug.ungenau(inst)) {
            await new Promise(weiter => setTimeout(weiter, 10));
        }
    }

    /** Das Feld des Reglers schon holen, bevor gezogen wird (Zeiger über dem Schieber): die Seite, auf die er am weitesten gehen kann. */
    static async vorab(inst, kanal, grenzen) {
        const stand = Genesis9reglerfeld.stand(inst);
        if (!stand || Genesis9sofortzug.UNLINEAR.test(kanal)) return;
        const a = stand[kanal] ?? 0, { min, max } = Genesis9reglerfeld.bereich(grenzen);
        const ziel = max - a >= a - min ? max : min;
        for (const [seite, von, bis] of Genesis9reglerfeld.fehlend(inst, kanal, stand, ziel, grenzen)) await Genesis9reglerfeld.holen(inst, kanal, seite, von, bis, stand);
    }

    /** Die Stellung, in der der Körper steht — null, solange es keinen mit Stand gibt. */
    static stand(inst) {
        return inst?.bodyMesh?.geometry?.userData?.reglerstand || null;
    }

    static bereich(grenzen) {
        const min = Number(grenzen?.min), max = Number(grenzen?.max);
        return { min: Number.isFinite(min) ? min : -1, max: Number.isFinite(max) ? max : 1 };
    }

    /** `[seite, von, bis]` der Felder, die der Weg zum Wert `w` braucht und die es noch nicht gibt. */
    static fehlend(inst, kanal, stand, w, grenzen) {
        const a = stand[kanal] ?? 0, { min, max } = Genesis9reglerfeld.bereich(grenzen);
        const aus = [];
        for (const [seite, weg] of Genesis9sofortzug.wege(kanal, a, w)) {
            if (seite === 'n') {
                if (Genesis9sofortzug.feld(inst, kanal, 'n')?.ziel !== w && Math.abs(weg) > 1e-9) aus.push(['n', a, w]);
                continue;
            }
            if (Genesis9sofortzug.feld(inst, kanal, seite)?.rest) continue;
            const vz = seite === '+' ? 1 : -1, ende = seite === '+' ? Math.max(max, w, 0.01) : Math.min(min, w, -0.01);
            const von = a * vz > 0 ? a : 0;                                  // ab dem Stand, wenn er auf dieser Seite liegt (seine Stellung hält der Server noch), sonst ab 0
            aus.push([seite, von, Math.abs(ende - von) > 0.02 ? ende : 0]);
        }
        return aus;
    }

    static holen(inst, kanal, seite, von, bis, stand) {
        if (!Genesis9reglerfeld._laufend.has(inst)) Genesis9reglerfeld._laufend.set(inst, new Map());
        const laufend = Genesis9reglerfeld._laufend.get(inst), schluessel = `${kanal}|${seite}`;
        if (!laufend.has(schluessel)) {
            laufend.set(schluessel, Genesis9reglerfeld._holen(inst, kanal, seite, { kanal, von, bis }, stand).finally(() => laufend.delete(schluessel)));
        }
        return laufend.get(schluessel);
    }

    static async _holen(inst, kanal, seite, zug, stand) {
        const t0 = performance.now();
        try {
            const rumpf = { ...Genesis9materialabruf.nutzlast(inst), regler: stand }, bis = zug.bis;
            const anfrage = Genesis9reglerfeld._fragen(inst, { ...zug, rumpf, teil: 'koerper' });
            setTimeout(() => Genesis9felder.vorbereiten(inst.bodyMesh), 0);      // solange der Server rechnet: Ruhelage und Nachbarn der Normalen
            const daten = await anfrage;
            if (!daten) return;
            Genesis9sofortzug.eintragen(inst, kanal, seite, { ziel: bis, koerper: { ...Genesis9reglerfeld._kopf(daten), genau: daten.genau, wechsel: daten.wechsel, feld: Genesis9reglerfeld._lesen(daten.koerper) } });
            Genesis9sofortzug.zeigen(inst);
            if (seite === 'n' && (inst.regler?.[kanal] ?? 0) === bis) Genesis9reglerfeld._aussehen(inst, daten.alter_aussehen);
            const koerperMs = Math.round(performance.now() - t0);
            if (seite === 'n' && (inst.regler?.[kanal] ?? 0) !== bis) return;    // schon weitergezogen: der nächste Wert bringt den Rest
            const rest = await Genesis9reglerfeld._fragen(inst, { ...zug, rumpf, teil: 'rest', stuecke: Genesis9reglerfeld.stuecke(inst) });
            const je = (o, f) => Object.fromEntries(Object.entries(o || {}).map(([k, v]) => [k, f(v)]));
            Genesis9sofortzug.eintragen(inst, kanal, seite, { rest: { ...Genesis9reglerfeld._kopf(rest || daten),
                anhaenge: je(rest?.anhaenge, Genesis9reglerfeld._lesen), stuecke: je(rest?.stuecke, teile => teile.map(Genesis9reglerfeld._lesen)) } });
            Genesis9sofortzug.zeigen(inst);
            Protokoll.debug('Genesis9reglerfeld', `${kanal} ${seite}: Körper ${koerperMs} ms, alles ${Math.round(performance.now() - t0)} ms`);
        } catch (fehler) {
            Protokoll.warnung('Genesis9reglerfeld', `${kanal}: kein Sofortfeld (${fehler.message}) — der genaue Zug zeigt die Änderung`);
        }
    }

    /** Falten, Altersflecken und graues Haar folgen dem Alter gleich mit der Form, nicht erst im genauen Zug (25.11.2026, Edgar: „Altersfalten erscheinen erst dann“ → „fixe“). */
    static _aussehen(inst, wert) {
        if (!Number.isFinite(wert) || inst.alterAussehen === wert) return;
        inst.alterAussehen = wert;
        for (const [name, schicht] of [['Hautfalten', Genesis9hautfalten], ['Hautebenen', Genesis9hautebenen]]) {
            schicht.anwenden(inst).catch(fehler => Protokoll.warnung('Genesis9reglerfeld', `${name}: ${fehler.message}`));
        }
    }

    /** Eine Hälfte des Felds — null, wenn der Server den Wert auf die Grenzen des Kanals zurücknimmt und kein Weg bleibt. */
    static async _fragen(inst, auftrag) {
        const daten = await Serverabruf.netzSenden(`${inst.constructor.ADRESSE}${encodeURIComponent(inst.figur)}/reglerzug/`, auftrag);
        if (daten.fehler) throw new Error(daten.fehler);
        return Math.abs(daten.bis - daten.von) > 1e-9 ? daten : null;
    }

    static _kopf(daten) {
        return { von: daten.von, bis: daten.bis, ruhig: daten.ruhig, fassung: Genesis9reglerfeld._fassung += 1 };
    }

    static _lesen(f) {
        if (!f || f.offen) return f || null;
        return { n: f.n ? base64ToUint32(f.n) : Genesis9reglerfeld._jeder(f.punkte), d: base64ToFloat32(f.d), punkte: f.punkte };
    }

    static _jeder(anzahl) {
        if (!Genesis9reglerfeld._alle.has(anzahl)) Genesis9reglerfeld._alle.set(anzahl, Uint32Array.from({ length: anzahl }, (_, i) => i));
        return Genesis9reglerfeld._alle.get(anzahl);
    }

    /** Die getragenen Stücke, wie der Server sie für die volle Antwort bekommt (`Genesis9kleidung.anfrage`). */
    static stuecke(inst) {
        return inst.getragen().map(kennung => {
            const [, rumpf] = Genesis9kleidung.anfrage(inst, kennung, inst.kleidung[kennung], null);
            return { kennung, stil: rumpf.stil, regler_stueck: rumpf.regler_stueck };
        });
    }
}
