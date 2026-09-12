/**
 * Körperdetails — Farben und Längen der kleinen Teile des HumanBody-Netzes:
 * Iris, Wimpern, Fingernägel, Fußnägel.
 *
 * WARUM (Edgar, 12.09.2026: „bei klick auf das Model … muss ich doch einen
 * Bereich haben wo ich die Farbe der Fingernägel, die Augenwimpern, die
 * Farbe der Augen usw einstellen kann? Länge der Augenlider, Fingernägel,
 * Fußnägel"): Das Netz führt diese Teile als eigene Materialgruppen
 * (`face_materials`: 2 Wimpern, 6 Iris, 9 Nägel Hand, 10 Nägel Fuß), gefärbt
 * bisher nur mit den festen Werten aus `koerpermaterialien.js`. Hier werden
 * sie je Figur einstellbar und mit dem Modell gespeichert (Feld `details`).
 *
 * FARBEN sind Materialfarben der Gruppen — kein Netzeingriff.
 *
 * LÄNGEN sind ein Eingriff in die Punkte, weil es dafür keine Morphs gibt
 * (gemessen 12.09.2026: 216 Morphs, darunter `Hands_NailsLength`, aber
 * nichts für Fußnägel oder Wimpern):
 *   - Wimpern sind 136 einzelne Streifen (1.360 Ecken, keine mit der Haut
 *     geteilt). Jeder Streifen wird entlang seiner Längsachse gestreckt, vom
 *     Ende aus, das dem Augapfel (Gruppe 4, Sklera, gleiche Seite) näher liegt.
 *   - Fußnägel sind 10 Stücke, die Wurzel teilt Ecken mit der Haut (118 von
 *     243). Die freien Ecken wandern entlang Wurzel → Spitze nach außen; die
 *     Wurzel bleibt, die Haut wird nicht mitgezogen.
 *   - Fingernägel haben den Morph `Hands_NailsLength`; der Regler dafür setzt
 *     den Morph (`Detailbedienung`), nicht die Punkte.
 * Die Streckung rechnet immer aus den GELIEFERTEN Punkten (nach jedem Morph-
 * Nachladen neu), nie aus schon gestreckten — darum kein Aufsummieren.
 *
 * Ohne Three.js: Materialien und Geometrie kommen als Objekte herein, die
 * Punkte als Float32Array — so läuft die Rechnung auch in Node (Test).
 *
 * Die Farben (Haut, Augen, Lippen, Zähne, Zunge, Nägel) und der Glanz stehen
 * seit 12.09.2026 in `detailfarben.js`; hier bleiben Vorgabe, Prüfung und die
 * Längen.
 */
import { Detailfarben } from './detailfarben.js';

export class Koerperdetails {

    /** Feld im Modell-JSON. */
    static FELD = 'details';

    /** Materialgruppen (Index = `face_materials`, siehe `koerpermaterialien.js`). */
    static GRUPPE = { haut: 0, wimpern: 2, sklera: 4, iris: 6, naegelHand: 9, naegelFuss: 10 };

    /** Vorgaben: Farben und Glanz aus `Detailfarben`, Längen 1 = wie geliefert.
     *  `brauen_staerke`: die gebauten Augenbrauen (`gemeinsam/augenbrauen.js`,
     *  12.09.2026) — das Netz hat keine, sie sind ein eigenes Netz je Figur. */
    static VORGABE = Object.freeze({
        ...Detailfarben.VORGABE,
        wimpern_laenge: 1.0, naegel_fuss_laenge: 1.0, brauen_staerke: 1.0,
    });

    /** Grenzen der Längenfaktoren; Glanz liegt in 0..1. */
    static LAENGE = { min: 0.5, max: 3.0 };

    /** Die Details aus Modelldaten — unbekannte Schlüssel fallen weg, Lücken füllt die Vorgabe. */
    static aus(daten) {
        const roh = (daten && daten[Koerperdetails.FELD]) || {};
        const aus = { ...Koerperdetails.VORGABE };
        for (const [name, wert] of Object.entries(roh)) {
            if (!(name in aus)) continue;
            const zahl = Number(wert);
            if (name.endsWith('_laenge') || name.endsWith('_staerke')) {
                if (Number.isFinite(zahl)) {
                    aus[name] = Math.min(Koerperdetails.LAENGE.max, Math.max(Koerperdetails.LAENGE.min, zahl));
                }
            } else if (name.endsWith('_glanz')) {
                if (Number.isFinite(zahl)) aus[name] = Math.min(1, Math.max(0, zahl));
            } else if (Detailfarben.istFarbe(wert)) {
                aus[name] = String(wert).toLowerCase();
            }
        }
        return aus;
    }

    /** True, wenn nichts von der Vorgabe abweicht — dann muss nichts gerechnet werden. */
    static istVorgabe(details) {
        return Object.entries(Koerperdetails.VORGABE).every(([k, v]) => details[k] === v);
    }

    // ------------------------------------------------------------- Farben

    /** Die Gruppenfarben und den Glanz setzen — siehe `Detailfarben`. */
    static faerben(materialien, details) {
        return Detailfarben.faerben(materialien, details);
    }

    // -------------------------------------------------------------- Plan

    /**
     * Der Plan einer Geometrie: je Wimpernstreifen und je Fußnagel die
     * beteiligten Ecken. Einmal je Topologie (Index + Gruppen), gemerkt unter
     * `geometrie.userData.detailplan`.
     */
    static plan(index, gruppen, punkte) {
        const ecken = (nummer) => {
            const menge = new Set();
            for (const g of gruppen) {
                if (g.materialIndex !== nummer) continue;
                for (let k = g.start; k < g.start + g.count; k++) menge.add(index[k]);
            }
            return menge;
        };
        const haut = ecken(Koerperdetails.GRUPPE.haut);
        const sklera = Koerperdetails._schwerpunkteJeSeite([...ecken(Koerperdetails.GRUPPE.sklera)], punkte);
        return {
            wimpern: Koerperdetails._teile(index, gruppen, Koerperdetails.GRUPPE.wimpern)
                .map(teil => ({ ecken: teil, sklera })),
            naegelFuss: Koerperdetails._teile(index, gruppen, Koerperdetails.GRUPPE.naegelFuss)
                .map(teil => ({ wurzel: teil.filter(e => haut.has(e)), frei: teil.filter(e => !haut.has(e)) })),
        };
    }

    /** Zusammenhängende Teile einer Gruppe (Ecken, die über Dreiecke verbunden sind). */
    static _teile(index, gruppen, nummer) {
        const eltern = new Map();
        const finden = (a) => {
            while (eltern.get(a) !== a) { eltern.set(a, eltern.get(eltern.get(a))); a = eltern.get(a); }
            return a;
        };
        const vereinen = (a, b) => { eltern.set(finden(a), finden(b)); };
        for (const g of gruppen) {
            if (g.materialIndex !== nummer) continue;
            for (let k = g.start; k + 2 < g.start + g.count; k += 3) {
                for (const e of [index[k], index[k + 1], index[k + 2]]) if (!eltern.has(e)) eltern.set(e, e);
                vereinen(index[k], index[k + 1]);
                vereinen(index[k], index[k + 2]);
            }
        }
        const teile = new Map();
        for (const e of eltern.keys()) {
            const w = finden(e);
            if (!teile.has(w)) teile.set(w, []);
            teile.get(w).push(e);
        }
        return [...teile.values()];
    }

    /** Schwerpunkt der Ecken links (x < 0) und rechts (x ≥ 0). */
    static _schwerpunkteJeSeite(ecken, p) {
        const summe = { links: [0, 0, 0, 0], rechts: [0, 0, 0, 0] };
        for (const e of ecken) {
            const s = p[3 * e] < 0 ? summe.links : summe.rechts;
            s[0] += p[3 * e]; s[1] += p[3 * e + 1]; s[2] += p[3 * e + 2]; s[3] += 1;
        }
        const mittel = (s) => (s[3] ? [s[0] / s[3], s[1] / s[3], s[2] / s[3]] : null);
        return { links: mittel(summe.links), rechts: mittel(summe.rechts) };
    }

    // ------------------------------------------------------------ Strecken

    /**
     * Die Längen auf die Punkte anwenden — IN PLACE auf `punkte`, das die
     * frisch gelieferten (ungestreckten) Lagen trägt.
     * @returns Zahl der bewegten Ecken
     */
    static strecken(punkte, plan, details) {
        let bewegt = 0;
        const fw = details.wimpern_laenge, ff = details.naegel_fuss_laenge;
        if (Math.abs(fw - 1) > 1e-6) {
            for (const streifen of plan.wimpern) bewegt += Koerperdetails._streifen(punkte, streifen, fw);
        }
        if (Math.abs(ff - 1) > 1e-6) {
            for (const nagel of plan.naegelFuss) bewegt += Koerperdetails._nagel(punkte, nagel, ff);
        }
        return bewegt;
    }

    /**
     * Ein Wimpernstreifen: das fernste Eckenpaar gibt die grobe Längsachse,
     * daran wird der Streifen in zwei Hälften geteilt; die Hälfte näher am
     * Augapfel ist die Wurzel. Gestreckt wird entlang Wurzel- → Spitzen-
     * schwerpunkt — nicht entlang der Diagonale des Paars, die bei einem
     * breiten Streifen schief liegt.
     */
    static _streifen(p, { ecken, sklera }, faktor) {
        let a = ecken[0], b = ecken[0], weit = -1;
        for (const i of ecken) {
            for (const j of ecken) {
                const d = Koerperdetails._abstand2(p, i, j);
                if (d > weit) { weit = d; a = i; b = j; }
            }
        }
        if (weit <= 0) return 0;
        const achse = [p[3 * b] - p[3 * a], p[3 * b + 1] - p[3 * a + 1], p[3 * b + 2] - p[3 * a + 2]];
        const t = (i) => (p[3 * i] - p[3 * a]) * achse[0] + (p[3 * i + 1] - p[3 * a + 1]) * achse[1]
                       + (p[3 * i + 2] - p[3 * a + 2]) * achse[2];
        const mitte = t(b) / 2;
        const seiteA = ecken.filter(i => t(i) <= mitte), seiteB = ecken.filter(i => t(i) > mitte);
        if (!seiteA.length || !seiteB.length) return 0;
        const sA = Koerperdetails._schwerpunkt(p, seiteA), sB = Koerperdetails._schwerpunkt(p, seiteB);
        const auge = p[3 * a] < 0 ? sklera.links : sklera.rechts;
        // Wurzel = die Hälfte näher am Augapfel; ohne Sklera die untere.
        const aWurzel = auge
            ? Koerperdetails._abstand2Punkte(sA, auge) <= Koerperdetails._abstand2Punkte(sB, auge)
            : sA[1] <= sB[1];
        return aWurzel ? Koerperdetails._laengs(p, ecken, sA, sB, faktor)
                       : Koerperdetails._laengs(p, ecken, sB, sA, faktor);
    }

    /** Ein Fußnagel: freie Ecken entlang Wurzel → Spitze nach außen. */
    static _nagel(p, { wurzel, frei }, faktor) {
        if (!wurzel.length || !frei.length) return 0;
        const w = Koerperdetails._schwerpunkt(p, wurzel), s = Koerperdetails._schwerpunkt(p, frei);
        return Koerperdetails._laengs(p, frei, w, s, faktor);
    }

    /** Ecken entlang der Achse `von → nach` um `faktor` strecken (Anteil längs der Achse). */
    static _laengs(p, ecken, von, nach, faktor) {
        const achse = [nach[0] - von[0], nach[1] - von[1], nach[2] - von[2]];
        const laenge = Math.hypot(...achse);
        if (laenge < 1e-9) return 0;
        for (let k = 0; k < 3; k++) achse[k] /= laenge;
        let bewegt = 0;
        for (const e of ecken) {
            const t = (p[3 * e] - von[0]) * achse[0] + (p[3 * e + 1] - von[1]) * achse[1]
                    + (p[3 * e + 2] - von[2]) * achse[2];
            if (t <= 0) continue;
            const schub = (faktor - 1) * t;
            p[3 * e] += schub * achse[0]; p[3 * e + 1] += schub * achse[1]; p[3 * e + 2] += schub * achse[2];
            bewegt += 1;
        }
        return bewegt;
    }

    static _schwerpunkt(p, ecken) {
        const s = [0, 0, 0];
        for (const e of ecken) { s[0] += p[3 * e]; s[1] += p[3 * e + 1]; s[2] += p[3 * e + 2]; }
        return s.map(x => x / ecken.length);
    }

    static _abstand2(p, i, j) {
        const dx = p[3 * i] - p[3 * j], dy = p[3 * i + 1] - p[3 * j + 1], dz = p[3 * i + 2] - p[3 * j + 2];
        return dx * dx + dy * dy + dz * dz;
    }

    static _abstand2Punkte(a, b) {
        const dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
        return dx * dx + dy * dy + dz * dz;
    }

    // ---------------------------------------------------- Three.js-Netz

    /** Alle Ecken, die die Längen bewegen können. */
    static _betroffene(plan) {
        const ecken = [];
        for (const streifen of plan.wimpern) ecken.push(...streifen.ecken);
        for (const nagel of plan.naegelFuss) ecken.push(...nagel.frei);
        return Uint32Array.from(ecken);
    }

    /** Die ungestreckten Lagen der betroffenen Ecken merken (aus `punkte`). */
    static _basisMerken(punkte, ecken) {
        const werte = new Float32Array(ecken.length * 3);
        for (let i = 0; i < ecken.length; i++) {
            const e = ecken[i];
            werte[3 * i] = punkte[3 * e]; werte[3 * i + 1] = punkte[3 * e + 1]; werte[3 * i + 2] = punkte[3 * e + 2];
        }
        return { ecken, werte };
    }

    static _basisZurueck(punkte, basis) {
        const { ecken, werte } = basis;
        for (let i = 0; i < ecken.length; i++) {
            const e = ecken[i];
            punkte[3 * e] = werte[3 * i]; punkte[3 * e + 1] = werte[3 * i + 1]; punkte[3 * e + 2] = werte[3 * i + 2];
        }
    }

    /**
     * Alles auf ein Körpernetz anwenden: Farben auf die Materialliste,
     * Längen auf `geometry.attributes.position`.
     *
     * Der Plan (welche Ecken zu welchem Streifen oder Nagel gehören) wird an
     * der Geometrie gemerkt, ebenso die UNGESTRECKTEN Lagen dieser Ecken
     * (`detailbasis`): Ein Regler kann dann ohne Serverlauf neu strecken —
     * erst zurück auf die Basis, dann mit dem neuen Faktor. `punkte` ist der
     * frisch gelieferte Puffer (Haken in `Netzpunkte.aktualisieren`); dann
     * ist ER die neue Basis. Ohne `punkte` gilt das Attribut als Basis, wenn
     * noch keine gemerkt ist — also nur direkt nach dem Bau.
     */
    static anwenden(netz, details, punkte = null) {
        if (!netz?.geometry || !details) return { farben: 0, bewegt: 0 };
        const farben = Koerperdetails.faerben(netz.material, details);
        const geo = netz.geometry;
        const index = geo.userData?.indexVoll?.index || geo.index?.array;
        const gruppen = geo.userData?.indexVoll?.gruppen || geo.groups;
        if (!index || !gruppen?.length) return { farben, bewegt: 0 };
        const ziel = punkte || geo.attributes.position.array;
        if (!geo.userData.detailplan) {
            geo.userData.detailplan = Koerperdetails.plan(index, gruppen, ziel);
            geo.userData.detailecken = Koerperdetails._betroffene(geo.userData.detailplan);
        }
        if (punkte || !geo.userData.detailbasis) {
            geo.userData.detailbasis = Koerperdetails._basisMerken(ziel, geo.userData.detailecken);
        } else {
            Koerperdetails._basisZurueck(ziel, geo.userData.detailbasis);
        }
        const bewegt = Koerperdetails.strecken(ziel, geo.userData.detailplan, details);
        if (!punkte) geo.attributes.position.needsUpdate = true;
        return { farben, bewegt };
    }
}
