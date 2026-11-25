import { Genesis9felder } from './genesis9felder.js';

/**
 * Genesis9sofortzug — ein Reglerzug an der STEHENDEN Figur, in jedem Bild, ohne neues Netz (25.11.2026).
 *
 * Edgar, 25.11.2026: „die regler müssen alle viel schneller werden“, „alle regler unter 0,2 s“. Gemessen an EdgarNeu (Chrome): vom Zug bis zur neuen Figur 1,75 s (fünf Anfragen, 1,3–1,7 s
 * Server, dann der Neubau). Hier verschiebt der Browser die stehenden Netze selbst: je Regler holt er EINMAL ein dünnes Feld auf ihren Punkten (`Genesis9reglerfeld`, Server
 * `G9reglerzugfeld`), danach kostet ein Zug nur noch die Summe und die Normalen der berührten Punkte (`Genesis9felder.anwenden`, Gruppe `regler` — neben Gelenkkorrekturen und Mimik).
 *
 * JEDES NETZ HAT SEINEN STAND: `geometry.userData.reglerstand` ist die Reglerstellung, für die es gebaut wurde (`merken`). Gezeigt wird immer Stand → `inst.regler`; kommt der genaue Zug
 * und baut den Körper neu, während ein Stück noch das alte Netz trägt (oder Edgar schon weitergezogen hat), stimmt jedes für sich (`nachBau`).
 *
 * SEITEN: Ein Regler der Familien hb:/mh:/sx:/uma: hat für plus und minus verschiedene Morphe — je Kanal bis zu zwei Felder (`+`, `-`), beide linear ab 0. Ein Kanal, der nicht linear
 * ist (`alter:`), bekommt sein Feld je Wert (`n`): es gilt genau für `bis` und dazwischen im Verhältnis.
 */
export class Genesis9sofortzug {

    static GRUPPE = 'regler';
    /** Kanäle, deren Wirkung nicht mit dem Wert wächst: ihr Feld gilt je Wert. */
    static UNLINEAR = /^alter:/;
    /** Figur → Map(Kanal → {'+', '-', 'n': Eintrag}); ein Eintrag hat zwei Teile, `koerper` {von, bis, fassung, feld} und `rest` {von, bis, fassung, anhaenge, stuecke} (kommt danach). */
    static _felder = new WeakMap();

    /** Die Reglerstellung, für die diese Netze gebaut sind (nach jedem Bau, mit dem Stand der ANFRAGE). */
    static merken(netze, regler) {
        for (const netz of netze) if (netz?.geometry) netz.geometry.userData.reglerstand = regler;
    }

    static kanaele(inst) {
        if (!Genesis9sofortzug._felder.has(inst)) Genesis9sofortzug._felder.set(inst, new Map());
        return Genesis9sofortzug._felder.get(inst);
    }

    /** Teile eines Felds vom Server eintragen (`{koerper}` oder `{rest}`, `ziel`); der andere Teil bleibt, bis seiner kommt. */
    static eintragen(inst, kanal, seite, teile) {
        const je = Genesis9sofortzug.kanaele(inst), seiten = je.get(kanal) || {};
        je.set(kanal, { ...seiten, [seite]: { ...(seiten[seite] || {}), ...teile } });
    }

    /** Das Feld einer Seite — oder null. */
    static feld(inst, kanal, seite) {
        return Genesis9sofortzug.kanaele(inst).get(kanal)?.[seite] || null;
    }

    /** Für den ganzen Zug: rührt er dieses Stück nicht an, gilt es für den neuen Stand weiter (true) — sein Netz bleibt stehen. */
    static bleibt(inst, kennung) {
        const netze = Object.entries(inst.clothMeshes || {}).filter(([k]) => k.startsWith(`${kennung}/`)).map(([, n]) => n);
        if (!netze.length || !Genesis9sofortzug._felder.has(inst) || !Genesis9sofortzug.unberuehrt(inst, kennung)) return false;
        Genesis9sofortzug.merken(netze, { ...inst.regler });
        for (const netz of netze) netz.geometry.userData.lauf = inst._lauf;
        return true;
    }

    /** Auf allen Netzen der Figur zeigen, was `inst.regler` seit ihrem Bau bewegt hat. Gibt die Zahl der geschriebenen Netze. */
    static zeigen(inst) {
        let n = 0;
        for (const [netz, waehlen] of Genesis9sofortzug.netze(inst)) if (Genesis9sofortzug._netz(inst, netz, waehlen)) n += 1;
        return n;
    }

    /** `[netz, (eintrag) → [Teil, Feld]]` aller Netze, die ein Feld haben können — nicht, was der Stoffschwung je Bild setzt. */
    static *netze(inst) {
        if (inst?.bodyMesh) yield [inst.bodyMesh, e => [e.koerper, e.koerper?.feld]];
        for (const [schluessel, netz] of Object.entries(inst?.anhangNetze || {})) yield [netz, e => [e.rest, e.rest?.anhaenge[schluessel]]];
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const [, kennung, nummer] = schluessel.match(/^(.*)\/(\d+)$/) || [];
            if (kennung !== undefined && !netz?.userData?.stoff) yield [netz, e => [e.rest, e.rest?.stuecke[kennung]?.[Number(nummer)]]];
        }
    }

    static _netz(inst, netz, waehlen) {
        const geo = netz?.geometry, stand = geo?.userData?.reglerstand, lage = geo?.getAttribute('position');
        if (!stand || !lage) return false;
        const felder = {}, gewichte = {};
        for (const [kanal, seiten] of Genesis9sofortzug.kanaele(inst)) {
            const a = stand[kanal] ?? 0, w = inst.regler?.[kanal] ?? 0;
            if (a === w) continue;
            for (const [seite, weg] of Genesis9sofortzug.wege(kanal, a, w)) {
                const [teil, feld] = seiten[seite] ? waehlen(seiten[seite]) : [];
                if (!feld || feld.punkte !== lage.count) continue;
                const schluessel = `${kanal}|${seite}${teil.fassung}`;
                felder[schluessel] = feld;
                gewichte[schluessel] = weg / (teil.bis - teil.von);
            }
        }
        if (!Object.keys(gewichte).length) {
            if (!Genesis9sofortzug.zeigt(netz)) return false;
            Genesis9felder.entfernen(netz, Genesis9sofortzug.GRUPPE);
        } else if (!Genesis9felder.anwenden(netz, Genesis9sofortzug.GRUPPE, felder, gewichte, true)) return false;
        geo.boundingSphere = null;
        geo.boundingBox = null;
        return true;
    }

    /** Der Weg von `a` nach `w` je Seite: `[[seite, Weg], …]`. */
    static wege(kanal, a, w) {
        if (Genesis9sofortzug.UNLINEAR.test(kanal)) return [['n', w - a]];
        const plus = Math.max(w, 0) - Math.max(a, 0), minus = Math.min(w, 0) - Math.min(a, 0);
        return [['+', plus], ['-', minus]].filter(([, weg]) => Math.abs(weg) > 1e-9);
    }

    /** Trägt dieses Netz gerade eine Sofortschau? Dann folgt es dem Körper schon (`Kleidervorschau`). */
    static zeigt(netz) {
        return netz?.geometry?.userData?.felder?.gruppen.has(Genesis9sofortzug.GRUPPE) ?? false;
    }

    // ------------------------------------------------------------ was der genaue Zug noch tun muss

    /** Mehr gezogene Kanäle trägt ein Netz nicht auf Dauer — dann baut der genaue Zug es neu. */
    static HOECHSTENS = 12;

    /** `[Eintrag, Gewicht]` jedes Wegs vom Stand eines Netzes nach `inst.regler` — null, wenn zu einem ein Feld fehlt. */
    static _eintraege(inst, stand) {
        const aus = [], namen = new Set([...Object.keys(stand), ...Object.keys(inst.regler || {})]);
        for (const kanal of namen) {
            const a = stand[kanal] ?? 0, w = inst.regler?.[kanal] ?? 0;
            if (a === w) continue;
            for (const [seite, weg] of Genesis9sofortzug.wege(kanal, a, w)) {
                const e = Genesis9sofortzug.feld(inst, kanal, seite);
                if (!e?.koerper || !e.rest) return null;
                aus.push([e, weg / (e.koerper.bis - e.koerper.von)]);
            }
        }
        return aus;
    }

    /**
     * Steht der Körper mit der Sofortschau schon genau da (`G9reglerzugfeld.genau`)? Dann `{stuecke}`: die getragenen Stücke, die der Zug berührt und die der genaue Zug noch holt — sonst
     * null: der ganze Zug. Mit GarmentCode-Stücken immer null (sie werden nach dem Körper neu geformt, `Gcreglerfolge`).
     */
    static plan(inst) {
        const stand = inst?.bodyMesh?.geometry?.userData?.reglerstand, eintraege = stand && Genesis9sofortzug._eintraege(inst, stand);
        if (!eintraege || eintraege.length > Genesis9sofortzug.HOECHSTENS || Object.keys(inst.gcStuecke || {}).length) return null;
        if (eintraege.some(([e]) => !e.koerper.genau)) return null;
        return { eintraege, stuecke: inst.getragen().filter(kennung => !Genesis9sofortzug.unberuehrt(inst, kennung)) };
    }

    /** Sagt ein Feld des Körpers auf dem Weg vom Stand nach `inst.regler` schon, dass es nicht die ganze Wahrheit ist? */
    static ungenau(inst) {
        const stand = inst?.bodyMesh?.geometry?.userData?.reglerstand;
        if (!stand) return false;
        for (const [kanal, seiten] of Genesis9sofortzug.kanaele(inst)) {
            const a = stand[kanal] ?? 0, w = inst.regler?.[kanal] ?? 0;
            if (a !== w && Genesis9sofortzug.wege(kanal, a, w).some(([seite]) => seiten[seite]?.koerper?.genau === false)) return true;
        }
        return false;
    }

    /** Rührt, was seit dem Bau dieses Stücks gezogen wurde, es nicht an? Nur, wenn der Server das sagt. */
    static unberuehrt(inst, kennung) {
        const netze = Object.entries(inst.clothMeshes || {}).filter(([k]) => k.startsWith(`${kennung}/`)).map(([, n]) => n);
        const stand = netze[0]?.geometry?.userData?.reglerstand, eintraege = stand && Genesis9sofortzug._eintraege(inst, stand);
        if (!eintraege?.length) return Boolean(eintraege);
        return eintraege.every(([e]) => e.rest.ruhig && e.rest.stuecke[kennung]?.length > 0 && e.rest.stuecke[kennung].every(f => f === null));
    }

    /** Die Morphwerte der Figur auf den gezogenen Stand (für die Anzeige gesteuerter Regler) — der Server hat sie nicht neu geschickt. */
    static werte(inst, eintraege) {
        const geo = inst.bodyMesh.geometry, gebaut = geo.userData.morphwerteGebaut ??= { ...inst.morphwerte };
        const aus = { ...gebaut };
        for (const [e, gewicht] of eintraege) for (const [k, d] of Object.entries(e.koerper.wechsel || {})) aus[k] = (aus[k] ?? 0) + gewicht * d;
        for (const k of Object.keys(aus)) if (Math.abs(aus[k]) < 1e-9) delete aus[k];
        inst.morphwerte = aus;
    }

    /** Nach dem Bau neuer Netze: was seit ihrem Stand weitergezogen wurde, gleich wieder zeigen. Scheitert nie laut. */
    static nachBau(inst) {
        try {
            if (Genesis9sofortzug._felder.has(inst)) Genesis9sofortzug.zeigen(inst);
        } catch (fehler) {
            console.warn(`Genesis9sofortzug: ${fehler.message}`);
        }
    }
}
