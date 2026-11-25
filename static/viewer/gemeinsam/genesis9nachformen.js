import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';
import { base64ToFloat32 } from './kodierung.js';
import { Bauart } from './bauart.js';
import { Eigenhaut } from './eigenhaut.js';
import { Eigenkleidwerte } from './eigenkleidwerte.js';
import { Dazschnittwerte } from './dazschnittwerte.js';
import { Genesis9aufbau } from './genesis9aufbau.js';
import { Genesis9fototextur } from './genesis9fototextur.js';
import { Genesis9hautebenen } from './genesis9hautebenen.js';
import { Genesis9hautfalten } from './genesis9hautfalten.js';
import { Genesis9kleidung } from './genesis9kleidung.js';
import { Genesis9materialabruf } from './genesis9materialabruf.js';
import { Genesis9netz } from './genesis9netz.js';
import { Genesis9sofortzug } from './genesis9sofortzug.js';
import { Genesis9stueckstand } from './genesis9stueckstand.js';
import { Genesis9werte } from './genesis9werte.js';
import { Knochenkette } from './knochenkette.js';
import { Oberflaechenbindung } from './oberflaechenbindung.js';
import { Skelettereignis } from './skelettereignis.js';

/**
 * Genesis9nachformen — der genaue Zug eines Reglers IN DIE STEHENDEN NETZE (25.11.2026).
 *
 * Edgar, 25.11.2026: „fixe: Noch nicht unter 0,2 s: Genesis, genaues Ergebnis nach dem Loslassen … mit einer Bildlücke von 0,2–0,3 s“. Gemessen an EdgarNeu (Chrome): der genaue Zug baute
 * Körper, fünf Anhänge und vier Stücke neu — neue Netze, Materialien und Programme, das erste Bild danach brauchte 258 ms. Ein Reglerzug ändert aber nur Punkte, Normalen, Bindung und
 * Skelett. Hier bleiben Netz, Geometrie und Material; der Server schickt diese Felder in EINER Antwort (`G9nachformenapi`, 10 statt 18 MB in fünf), und alles erscheint
 * in EINEM Bild.
 *
 * WANN NICHT (dann der volle Bau wie bisher): GarmentCode-Stücke, eigene Kleider (`kleid:`), Stücke mit Eigen-Schnitt, eigene Knochen eines Stücks (Zöpfe), andere Knochen, Punktzahl oder
 * Materialgruppen als die stehenden. Ein einzelnes Stück mit Stoffschwung, Strähnen oder Glättung kommt für sich neu (`anziehen`).
 *
 * NEUE FELDER STATT KOPIEREN: `attribute.array` wird ersetzt — wer an der Punktliste gemerkt hat (`Hautdicke`), misst neu. Das Skelett entsteht neu wie bisher und meldet sich
 * (`Skelettereignis`): Masken, Gelenke und Haarnetze ziehen nach wie nach jedem Umbau.
 */
export class Genesis9nachformen {

    /** Trägt die Figur etwas, das am Bau neuer Netze hängt? */
    static geht(inst) {
        if (!inst?.bodyMesh?.isSkinnedMesh || !inst.skelett || inst.stufen < 1 || !inst.constructor.ADRESSE) return false;
        if (Object.keys(inst.gcStuecke || {}).length || (inst.eigeneKnochen || []).length || Eigenkleidwerte.getragen(inst).length) return false;
        return !inst.getragen().some(k => Object.keys(Dazschnittwerte.regler(inst, k)).some(n => n.startsWith(Dazschnittwerte.PRAEFIX)));
    }

    /**
     * Körper und die Stücke `kennungen` genau nachformen. `false`: geht hier nicht — der Aufrufer baut neu (es ist noch nichts verändert).
     * Überholt (ein neuer Zug läuft): true, ohne zu schreiben.
     */
    static async zug(inst, kennungen) {
        const lauf = inst._lauf = (inst._lauf || 0) + 1, reglerstand = { ...inst.regler };
        // Was niemand sieht (die Anatomie unter der Hose, die sie trägt; ausgeblendete Stücke), kommt danach für sich — darauf wartet der Zug nicht.
        const verborgen = kennungen.filter(k => Genesis9nachformen._verborgen(inst, k));
        const { koerper: daten, stuecke: geholt } = await Genesis9nachformen._holen(inst, Genesis9materialabruf.nutzlast(inst), kennungen.filter(k => !verborgen.includes(k)));
        if (lauf !== inst._lauf || !inst.bodyMesh) return true;
        if (!daten || !Genesis9nachformen._koerperPasst(inst, daten)) return false;
        Genesis9nachformen._koerper(inst, daten, reglerstand);
        const rest = Genesis9nachformen._anlegen(inst, geholt, lauf, reglerstand);
        Skelettereignis.melden(inst);
        Genesis9sofortzug.nachBau(inst);       // seit der Anfrage weitergezogen? gleich wieder zeigen
        await Genesis9nachformen._neuBauen(inst, rest);
        if (verborgen.length) {
            setTimeout(() => {
                if (lauf !== inst._lauf) return;                            // der nächste Zug nimmt sie mit
                Genesis9nachformen.stuecke(inst, verborgen).catch(fehler => Protokoll.warnung('Genesis9nachformen', `verborgene Stücke: ${fehler.message}`));
            }, 0);
        }
        return true;
    }

    /** Zeichnet niemand ein Netz dieses Stücks? */
    static _verborgen(inst, kennung) {
        const netze = Object.entries(inst.clothMeshes).filter(([k]) => k.startsWith(`${kennung}/`)).map(([, n]) => n);
        return netze.length > 0 && netze.every(n => n.visible === false);
    }

    /** Nur Stücke (der Körper steht schon genau da, `Genesis9sofortzug.plan`). */
    static async stuecke(inst, kennungen) {
        const lauf = inst._lauf, reglerstand = { ...inst.regler };
        if (!kennungen.length) return;
        const { stuecke: geholt } = await Genesis9nachformen._holen(inst, null, kennungen);
        if (lauf !== inst._lauf) return;
        const rest = Genesis9nachformen._anlegen(inst, geholt, lauf, reglerstand);
        Genesis9sofortzug.nachBau(inst);
        await Genesis9nachformen._neuBauen(inst, rest);
    }

    /** EINE Anfrage (`…/nachformen/`, `G9nachformenapi`): `{koerper, stuecke: {Kennung → Antwort | null}}`; ein Stück, das der Server nicht nachformt, kommt als null. */
    static async _holen(inst, rumpf, kennungen) {
        const daten = await Serverabruf.netzSenden(Genesis9aufbau.adresse(`${inst.constructor.ADRESSE}${encodeURIComponent(inst.figur)}/nachformen/`, null), {
            rumpf, stuecke: kennungen.map(kennung => ({ kennung, rumpf: Genesis9kleidung.anfrage(inst, kennung, inst.kleidung[kennung], null)[1] })),
        });
        if (daten.fehler) throw new Error(daten.fehler);
        return daten;
    }

    /** Die Antworten in ihre Netze; gibt die Kennungen, die neu gebaut werden müssen. */
    static _anlegen(inst, geholt, lauf, reglerstand) {
        const rest = [];
        for (const [kennung, daten] of Object.entries(geholt || {})) {
            if (!inst.kleidung[kennung]) continue;                          // inzwischen ausgezogen
            if (!daten || !Genesis9nachformen._stueck(inst, kennung, daten, lauf, reglerstand)) rest.push(kennung);
        }
        return rest;
    }

    static async _neuBauen(inst, kennungen) {
        await Promise.all(kennungen.map(k => inst.anziehen(k, inst.kleidung[k], null, false).catch(fehler => {
            Protokoll.warnung('Genesis 9', `${k} nicht geladen: ${fehler.message}`);
        })));
    }

    // ---------------------------------------------------------- Körper

    /** Dieselben Netze, Knochen und Gruppen wie die stehenden? Prüft nur. */
    static _koerperPasst(inst, daten) {
        const anhaenge = daten.anhaenge || [];
        if ((daten.stufen || 0) !== inst.stufen || (daten.skelett?.eigene || []).length || anhaenge.length !== Object.keys(inst.anhangNetze).length) return false;
        const namen = Knochenkette.bauplan(daten.skelett?.knochen).map(k => k.name), bones = inst.skelett.bones;
        if (namen.length !== bones.length || namen.some((n, i) => n !== bones[i].name)) return false;
        const wahl = Genesis9nachformen._wahl(inst);
        if (!Genesis9nachformen.passt(inst.bodyMesh, daten, Genesis9fototextur.gruppen(daten.gruppen, inst.fototextur, wahl))) return false;
        return anhaenge.every(a => inst.anhangNetze[a.schluessel]
            && Genesis9nachformen.passt(inst.anhangNetze[a.schluessel], a, Genesis9fototextur.anhang(a, inst.fototextur, wahl).gruppen));
    }

    static _wahl(inst) {
        return { haut: inst.haut, praesets: inst.praesets, augenGewaehlt: inst._augenGewaehlt, brauenstil: inst.brauenstil };
    }

    static _koerper(inst, daten, reglerstand) {
        inst.skelettBauen(daten.skelett);
        inst.eigeneKnochen = [];
        const netze = [[inst.bodyMesh, daten], ...(daten.anhaenge || []).map(a => [inst.anhangNetze[a.schluessel], a])];
        for (const [netz, d] of netze) {
            Genesis9nachformen._haut(inst, netz, d.hautgewichte);
            Genesis9nachformen._punkte(netz, d);
        }
        for (const netz of [...netze.map(([n]) => n), ...Object.values(inst.clothMeshes || {})]) {
            if (netz?.isSkinnedMesh && netz.userData.hautgewichte) netz.bind(inst.skelett.skeleton, netz.matrix);
        }
        Genesis9sofortzug.merken(netze.map(([n]) => n), reglerstand);
        delete inst.bodyMesh.geometry.userData.morphwerteGebaut;
        Genesis9werte.uebernehmen(inst, daten);
        Genesis9hautfalten.anwenden(inst).catch(fehler => Protokoll.warnung('Genesis9nachformen', `Hautfalten: ${fehler.message}`));
        Genesis9hautebenen.anwenden(inst).catch(fehler => Protokoll.warnung('Genesis9nachformen', `Hautebenen: ${fehler.message}`));
    }

    // ---------------------------------------------------------- Netze

    /** Gehört die Antwort zu diesem Netz: gleiche Punktzahl, gleiche Materialgruppen samt Bildern? */
    static passt(netz, daten, gruppen = daten.gruppen) {
        const geo = netz?.geometry, lage = geo?.attributes?.position;
        if (!lage || !geo.attributes.normal || !daten.normals || daten.art === 'strang' || netz.userData.stoff || daten.stoff || netz.userData.glaettVersatz) return false;
        return lage.count === daten.vertex_count && netz.userData.gruppenkennung === Genesis9netz.gruppenkennung(gruppen);
    }

    /** Punkte und Normalen der Antwort; was an der alten Lage hing, entsteht neu. */
    static _punkte(netz, daten) {
        const geo = netz.geometry;
        for (const [name, werte] of [['position', daten.vertices], ['normal', daten.normals]]) {
            const a = geo.attributes[name];
            a.array = base64ToFloat32(werte);
            a.needsUpdate = true;
        }
        delete geo.userData.felder;
        delete geo.userData.normalen;
        geo.boundingSphere = null;
        geo.boundingBox = null;
        if (geo.boundsTree) setTimeout(() => geo.boundsTree?.refit?.(), 0);      // der Suchbaum der Treffer (`Raycastbeschleunigung`) auf die neue Lage, nach dem Bild
    }

    /** Die Hautgewichte, wenn sie sich geändert haben (die Falte unter dem Kinn hängt an der Form). */
    static _haut(inst, netz, haut) {
        const alt = netz.userData.hautgewichte;
        if (!haut || !alt || Genesis9nachformen._gleich(alt, haut)) return;
        const spalte = Eigenhaut.spaltenNummern(haut.knochen, inst.skelett);
        if (!spalte) return;
        const { index, gewicht } = Eigenhaut.gewichte(haut), nummern = netz.geometry.attributes.skinIndex, gewichte = netz.geometry.attributes.skinWeight;
        for (let i = 0; i < nummern.array.length; i++) nummern.array[i] = spalte[index[i]] ?? 0;
        gewichte.array.set(gewicht);
        nummern.needsUpdate = gewichte.needsUpdate = true;
        netz.userData.hautgewichte = haut;
    }

    static _gleich(a, b) {
        if (!a || !b || a.knochen.length !== b.knochen.length || a.knochen.some((k, i) => k !== b.knochen[i])) return false;
        return Genesis9nachformen._felderGleich(a.skin_indices, b.skin_indices) && Genesis9nachformen._felderGleich(a.skin_weights, b.skin_weights);
    }

    /** Zwei Felder der Antwort, wortweise (sie liegen auf 8 Byte ausgerichtet, `Netzpaket`); als Text verglichen, wenn sie Text sind. */
    static _felderGleich(a, b) {
        if (!ArrayBuffer.isView(a) || !ArrayBuffer.isView(b)) return a === b;
        if (a.byteLength !== b.byteLength) return false;
        const worte = f => (f.byteOffset % 4 === 0 && f.byteLength % 4 === 0 ? new Uint32Array(f.buffer, f.byteOffset, f.byteLength / 4) : f);
        const x = worte(a), y = worte(b);
        if (x.length !== y.length) return false;
        for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) return false;
        return true;
    }

    // ---------------------------------------------------------- Stücke

    static _stueck(inst, kennung, daten, lauf, reglerstand) {
        const teile = daten.teile || [], netze = teile.map((_t, n) => inst.clothMeshes[`${kennung}/${n}`]);
        if (Object.keys(inst.clothMeshes).filter(k => k.startsWith(`${kennung}/`)).length !== teile.length) return false;
        if (!teile.every((t, n) => Genesis9nachformen.passt(netze[n], t) && Boolean(t.bindung) === Boolean(netze[n].geometry.userData.bindung)
            && (!t.hautgewichte || Genesis9nachformen._gleich(netze[n].userData.hautgewichte, t.hautgewichte)))) return false;
        teile.forEach((teil, n) => {
            const netz = netze[n];
            Genesis9nachformen._punkte(netz, teil);
            if (teil.bindung) Oberflaechenbindung.nachfuellen(inst, netz, teil);
            if (teil.glaettung?.kaefig) netz.userData.glaettung = { kaefig: base64ToFloat32(teil.glaettung.kaefig), stufen: teil.stufen || 0 };
            netz.userData.ersetzt = daten.ersetzt || [];
            netz.userData.hautTiefe = (daten.hautTiefeMm || 0) / 1000;
            netz.userData.hautLoch = daten.hautLoch?.dreiecke?.length ? daten.hautLoch : null;
            Bauart.eintragen(netz, daten);
            netz.geometry.userData.lauf = lauf;
            Genesis9sofortzug.merken([netz], reglerstand);
            Genesis9stueckstand.merken(inst, kennung, netz, inst.kleidung[kennung].regler);
        });
        inst.lagen[kennung] = { innen: daten.innen || [], aussen: daten.aussen || [] };
        return true;
    }
}

// Für `Genesis9aufbau.alles` (eingetragen hier — ein Import dorthin wäre ein Ring).
Genesis9aufbau.nachformen = Genesis9nachformen;
