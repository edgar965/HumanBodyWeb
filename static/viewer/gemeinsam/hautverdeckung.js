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
import { Hautmaskeersatz } from './hautmaskeersatz.js';
import { Hautrechnung } from './hautrechnung.js';
import { Hautarbeit } from './hautarbeit.js';
import { Hautanschmiegung } from './hautanschmiegung.js';
import { Stueckfeder } from './stueckfeder.js';
import { Stueckdeckung } from './stueckdeckung.js';
import { Stueckluecke } from './stueckluecke.js';
import { Stueckrand } from './stueckrand.js';
import { Stueckloch } from './stueckloch.js';
import { Hautloch } from './hautloch.js';
import { Figurhaut } from './figurhaut.js';
import { Stueckereignis } from './stueckereignis.js';
import { Skelettereignis } from './skelettereignis.js';
import { Figuraufbaustand } from './figuraufbaustand.js';
import { Protokoll } from './protokoll.js';
import { Hauteinzug } from './hauteinzug.js';

export class Hautverdeckung extends Figurhaut {

    /**
     * `true`: Unter einem Ersatzstück (Scham aus einer .blend) wird über `Hautmaskeersatz.innen` und `beruehrt` KEINE Haut entfernt, sie
     * sinkt nur auf seine Fläche (`hautanschmiegung.js`). Versucht am 09.10.2026 (Edgar: „keine helle, gesägte Zipfel an den Rändern";
     * Chrome, „cute girl", Haut mit und ohne Stück): Das Loch in der Haut blieb gleich — es entsteht zum größten Teil in `vorStueck`
     * (`Stueckdeckung`, Strahlen entlang der Hautnormale, 284–516 Dreiecke), nicht in `innen` — und der gezackte Stern aus ganzen Dreiecken
     * (Kante 4–8 mm, Spitzen bis 14 mm) um das glatte Stück bleibt. An den Leistenfalten steht die Hautnormale quer zur Blickrichtung:
     * die Deckung gilt entlang der Normale, der Betrachter sieht die Stelle von vorn, dort liegt Hintergrund. Darum `false`.
     */
    static HAUT_BLEIBT_UNTER_ERSATZ = false;

    /** Den Körper der Figur gegen alle ihre Stücke maskieren. `vorab`: die Rechnung aus dem Worker (`anwendenAsync`), sonst hier. */
    static anwenden(inst, vorab = null) {
        const geo = inst?.bodyMesh?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Hautverdeckung.merken(geo);
        inst._maskeAnzahl = Hautverdeckung.zaehlende(inst).length;      // so viele Stücke zählen in der Maske, die jetzt gezeigt wird (`freigeben`)
        const voll = geo.userData.indexVoll;
        // Verschweißte Stücke (Scham aus einer .blend, `stueckloch.js`) bringen ihr Loch mit: genau diese Dreiecke fallen weg, ohne Rechnung.
        const loecher = Stueckloch.maske(Hautverdeckung.zaehlende(inst), voll.index.length / 3);
        const stoffe = Hautverdeckung.stoffe(inst, true);
        Hautloch.naehen(geo, loecher, inst.bodyMesh);
        if (!stoffe.length) return loecher ? Hautloch.nurLoecher(inst, geo, voll, loecher) : Hautverdeckung.aufheben(inst);
        const t0 = performance.now();
        const pos = geo.attributes.position.array;
        const rechnung = vorab || Hautrechnung.rechnen(pos, voll.index, stoffe);
        // Der Randabstand eines Ersatzstücks entsteht bei der Rechnung am Stück (`Hautmaskeersatz.maskieren`); aus dem Worker kommt er als Feld.
        stoffe.forEach((stoff, i) => { if (rechnung.randabstaende[i]) stoff.randabstand = rechnung.randabstaende[i]; });
        const { ersatz, hoehe, rand, normalen, maske } = rechnung;
        geo.userData.hautVerdeckt = maske;
        // Verdeckte Haut neben der gezeichneten bleibt versenkt gezeichnet
        // (`Saumband`); die Randecken wandern im Shader unter die Stoffkante
        // (`Saumschnitt`). Aus dem Index fällt nur, was jenseits des Bands liegt.
        const einzug = Hauteinzug.eintragen(inst.bodyMesh, rechnung.einzug);
        const weg = einzug.weg || new Uint8Array(ersatz.length);
        const gesenkt = Hautverdeckung.anschmiegen(geo, pos, normalen, ersatz, hoehe, maske, voll.index, rand);
        const eingezogen = geo.getAttribute('einzug');
        if (loecher?.verschiebung && eingezogen) {                       // die Ringpunkte eines verschweißten Stücks: glatte Naht
            Stueckloch.verschieben(eingezogen.array, loecher.verschiebung);
            eingezogen.needsUpdate = true;
        }
        for (const stoff of stoffe) if (stoff.ersatz) Stueckfeder.setzen(stoff.netz);
        const wegVorher = Uint8Array.from(weg);
        if (Hautverdeckung.HAUT_BLEIBT_UNTER_ERSATZ) {
            for (let i = 0; i < weg.length; i++) if (ersatz[i]) weg[i] = 0;
        } else {
            Hautmaskeersatz.beruehrt(Hautmaskeersatz.innen(ersatz, maske, voll.index, rand), voll.index, weg);
        }
        const vor = Hautverdeckung.vorStueck(geo, pos, normalen, voll.index, stoffe);
        const splitter = Hautverdeckung.splitter(geo, pos, normalen, voll.index, maske, vor, stoffe);
        const vorStueck = splitter.weg;
        const luecke = Hautverdeckung.luecken(geo, pos, normalen, voll.index, weg, wegVorher, vorStueck, stoffe);
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, weg, Stueckloch.vereinen(vorStueck, loecher?.weg), luecke?.bleibt);
        Hautverdeckung.indexSetzen(geo, neu.index, neu.gruppen);
        let verdeckt = 0;
        for (let i = 0; i < maske.length; i++) verdeckt += maske[i];
        const stand = { verdeckt, band: einzug.band, dreiecke: neu.entfernt, stuecke: stoffe.length, gesenkt,
                        luecken: luecke ? luecke.offen : 0, splitter: splitter.splitter, ms: Math.round(performance.now() - t0),
                        rechenMs: rechnung.ms, imWorker: !!vorab, verschweisst: loecher ? loecher.schluessel : [] };
        Protokoll.debug('Hautverdeckung', `${verdeckt} Körperpunkte unter ${stoffe.length} `
            + `Stücken, ${einzug.band} davon im Saumband, ${gesenkt} auf ein Ersatzstück gesenkt, `
            + `${neu.entfernt} Dreiecke ausgeblendet (${stand.splitter} steile Splitter), `
            + `${stand.luecken} ohne Stück dahinter stehengelassen, ${stand.ms} ms auf dem Hauptfaden `
            + `(Rechnung ${stand.rechenMs} ms${vorab ? ' im Worker' : ''})`);
        return stand;
    }

    /**
     * Wie `anwenden`, aber gerechnet wird in einem Worker (`hautarbeit.js`); der Hauptfaden schreibt nur das Ergebnis. Ohne Worker
     * rechnet `anwenden` selbst. null, wenn der Auftrag überholt ist (`gueltig()` false: ein neuer Plan ist unterwegs).
     */
    static async anwendenAsync(inst, gueltig = () => true) {
        const geo = inst?.bodyMesh?.geometry;
        if (!geo?.attributes?.position || !geo.index) return null;
        Hautverdeckung.merken(geo);
        const stoffe = Hautverdeckung.stoffe(inst, true);
        if (!stoffe.length) return Hautverdeckung.anwenden(inst);       // nichts zu rechnen: nur das Loch eines verschweißten Stücks oder gar nichts
        const vorab = await Hautarbeit.rechnen(geo.attributes.position.array, geo.userData.indexVoll.index, stoffe);
        if (vorab === Hautarbeit.VERALTET || !gueltig() || inst.bodyMesh?.geometry !== geo) return null;
        // Dieselben Stücke in derselben Reihenfolge wie beim Abschicken — nur dann gehören `randabstaende` zu ihnen.
        const jetzt = Hautverdeckung.stoffe(inst, true).map((s) => s.schluessel).join('|');
        return Hautverdeckung.anwenden(inst, vorab && jetzt === stoffe.map((s) => s.schluessel).join('|') ? vorab : null);
    }

    /** Die Stücke, die die Haut verdecken dürfen, als `[schluessel, netz]` (`zaehlt`). */
    static zaehlende(inst) {
        return Object.entries(inst?.clothMeshes || {}).filter(([, netz]) => netz?.geometry?.index && Hautverdeckung.zaehlt(netz));
    }

    /** Steile Hautdreiecke auf einem Ersatzstück, die dessen Fläche verdecken (`stueckluecke.js`) — `{weg, splitter}`. */
    static splitter(geo, pos, normalen, index, maske, vorStueck, stoffe) {
        const eingezogen = geo.getAttribute('einzug');
        if (!eingezogen || !stoffe.some((s) => s.ersatz)) return { weg: vorStueck, splitter: 0 };
        return Stueckluecke.splitter(index, maske, eingezogen.array, vorStueck, pos, normalen, stoffe);
    }

    /**
     * Dreiecke, die nur durch die Nachbarschaft zum Ersatzstück wegfielen und keine Stückfläche dahinter haben (`stueckluecke.js`) —
     * `{bleibt, offen, geprueft}` oder null ohne Ersatzstück.
     */
    static luecken(geo, pos, normalen, index, weg, wegVorher, vorStueck, stoffe) {
        const eingezogen = geo.getAttribute('einzug');
        if (!eingezogen || !stoffe.some((s) => s.ersatz)) return null;
        return Stueckluecke.bleibt(index, weg, wegVorher, vorStueck, pos, eingezogen.array, normalen, stoffe);
    }

    /** Je Dreieck 1, wenn es nach dem Einzug vor dem Inneren eines Ersatzstücks liegt (`stueckdeckung.js`); null ohne Ersatzstück. */
    static vorStueck(geo, pos, normalen, index, stoffe) {
        const einzug = geo.getAttribute('einzug');
        const stuecke = stoffe.filter((s) => s.ersatz && s.randabstand);
        if (!einzug || !stuecke.length) return null;
        const weg = new Uint8Array(index.length / 3);
        for (const stoff of stuecke) Stueckdeckung.dreiecke(pos, einzug.array, normalen, index, stoff, Stueckrand.FEDER_M, weg);
        return weg;
    }

    /**
     * Haut unter und neben einem ERSATZSTÜCK (Scham): sie sinkt auf dessen Fläche und läuft neben ihm aus
     * (`hautanschmiegung.js`) — kein Saumband, kein Spalt, keine Stufe am gezackten Rand (gesehen 09.10.2026).
     * Der Ring Haut, den `Hautmaskeersatz.innen` stehen lässt, liegt damit auf dem Stück statt davor.
     */
    static anschmiegen(geo, pos, normalen, ersatz, hoehe, maske, dreiecke, rand) {
        const eingezogen = geo.getAttribute('einzug');
        if (!eingezogen || !ersatz.includes(1)) return 0;
        const senkung = Hautanschmiegung.senkung(pos, normalen, ersatz, hoehe, maske, dreiecke, rand);
        const n = Hautanschmiegung.eintragen(eingezogen.array, senkung, normalen, ersatz, maske);
        eingezogen.needsUpdate = true;
        return n;
    }

    /**
     * Kleidung ausgezogen oder ausgeblendet: die Haut darunter SOFORT ganz zeigen (Rainy, 10.10.2026: Flecken und Stufen in der nackten Haut,
     * bis die neue Maske gerechnet war). Voller Index, Einzug null — nur die Löcher verschweißter Stücke bleiben; die Maske für die Stücke, die
     * bleiben, kommt danach wie bisher. Preis: unter diesen steht die Haut bis dahin ungemaskt. Ursache und Zahlen: Tagebuch 2026-10-10.
     */
    static freigeben(inst) {
        const geo = inst?.bodyMesh?.geometry;
        const voll = geo?.userData?.indexVoll;
        if (!geo?.attributes?.position || !geo.index || !voll) return null;
        const loecher = Stueckloch.maske(Hautverdeckung.zaehlende(inst), voll.index.length / 3);
        Hautloch.naehen(geo, loecher, inst.bodyMesh);
        inst._maskeAnzahl = 0;                                          // gezeigt wird jetzt keine Maske mehr
        return loecher ? Hautloch.nurLoecher(inst, geo, voll, loecher) : Hautverdeckung.aufheben(inst);
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
    static stoffe(inst, ohneVerschweisste = false) {
        const aus = [];
        const anzahl = (inst?.bodyMesh?.geometry?.userData?.indexVoll?.index?.length || 0) / 3;
        for (const [schluessel, netz] of Object.entries(inst?.clothMeshes || {})) {
            const g = netz?.geometry;
            if (!g?.attributes?.position || !g.index) continue;
            if (!Hautverdeckung.zaehlt(netz)) continue;
            // Ein verschweißtes Stück (`stueckloch.js`) hat sein Loch fertig — es nimmt an der Rechnung nicht teil.
            if (ohneVerschweisste && Stueckloch.von(netz, anzahl)) continue;
            // `tiefe` (Scham aus einer .blend, 08.10.2026): ein Stück, das bis 25 mm HINTER der Figurfläche liegt (die Furche, die
            // die Figur überbrückt), verdeckt die Haut davor trotzdem; ohne Angabe gilt `Hautmaske.TIEFE_M`.
            // Ein Ersatzstück (mit `hautTiefe`) ist starr: kein freier Randstreifen, die Haut fällt bis zu seinem Rand weg
            // (gemessen 09.10.2026, „cute girl Scham": Strahl allein 111 Punkte, mit Abstandstest 6 mm 353 — die Haut stand
            // sonst neben und unter dem Stück und flimmerte an den Rändern).
            const ersatz = !!netz.userData?.hautTiefe;
            aus.push({ schluessel, punkte: g.attributes.position.array, tiefe: netz.userData?.hautTiefe || undefined,
                       dreiecke: Hautverdeckung.vollerIndex(g), starr: ersatz || Hautverdeckung.starr(schluessel),
                       nahe: ersatz ? Hautverdeckung.NAHE_ERSATZ_M : undefined, ersatz, netz });
        }
        return aus;
    }

    /**
     * STARRE Stücke (bisher nur der GarmentCode-Schuh, Schlüssel immer
     * `gc_schuh` — `GarmentCode.schuhdeutung` erkennt ihn serverseitig an
     * Kategorie/Maßen, der Name ist keine Produktbezeichnung) lassen keinen
     * Randstreifen frei (`hautmaske.js`, `RANDRINGE`). Der Streifen ist für
     * eine LOCKERE Stoffkante gedacht, die sich beim Bewegen hebt und sonst
     * ein Loch freigäbe — ein Schuh biegt sich am oberen Rand nicht so.
     *
     * BEFUND (27.09.2026, Damira1/Flats, Edgar mit Bild „im ursprungsmodell
     * geht die Haut nicht durch"): Auch mit dem Abstands-Fallback (`NAHE_M`)
     * blieb der Schuh bei 6,0 % Fremdfarbe (vorher 16,8 %) — knapp über der
     * Schwelle. Der Randstreifen an der Schuhöffnung war der Rest: ohne ihn
     * (probehalber `randringe:0` in der laufenden Szene) erkannte die Maske
     * 3.268 weitere Punkte als verdeckt, geschätzt genau dort.
     */
    static starr(schluessel) {
        return schluessel === 'gc_schuh';
    }

    /** Ohne `art` (GarmentCode, MakeHuman, UMA) wie bisher; mit `art` nur `kleidung`.
     *
     * AUSGEBLENDET = VERDECKT NICHTS (Edgar, 08.10.2026, mit Bild: „du hast keine Formen für die Schamlippen, den Hügel"): Die
     * Schalter „Kleidung aus" und „Stück ausblenden" setzen nur `visible = false`; die Maske blieb, die Haut unter dem Hosenbund
     * stand weiter unter dem Stoff (`Hauteinzug`) — Hügel und Schamlippen waren flach, rot gesäumt, zerrissen. Gesehen im
     * Chrome: Hose `visible: false`, `hautVerdeckt` gesetzt. Seither zählt nur, was sichtbar ist, und `menubar.js` meldet jede
     * Änderung (`sichtbarkeit`). */
    static zaehlt(netz) {
        if (netz?.visible === false) return false;
        const art = netz?.userData?.art;
        // Ein Stück, das Teile der Figur ERSETZT (Originalaugen, `Genesis9ersatz`), sitzt IN der Figur — es verdeckt keine Haut.
        if (netz?.userData?.ersetzt?.length) return false;
        return !art || art === 'kleidung';
    }

    /** Stücke wurden ein- oder ausgeblendet (`visible`): die Maske gilt nur für die sichtbaren — neu rechnen. */
    static sichtbarkeit(inst) {
        Hautverdeckung.planen(inst);
    }

    /** So nah (m) am Rand eines Ersatzstücks fällt die Haut weg — etwa ein Körperpunktabstand der Stufe 1 (4 mm). */
    static NAHE_ERSATZ_M = 0.006;

    /** Ruhezeit nach der letzten Meldung; `_ausstehend`: inst -> Zeitgeber. */
    static RUHE_MS = 400;
    /** So oft sieht die wartende Maske nach, ob das Nachladen einer Stufe fertig ist. */
    static NACHLADEN_MS = 500;
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
        // Jeder Plan überholt eine noch laufende Rechnung im Worker (`anwendenAsync` prüft die Nummer).
        inst._maskeVersion = (inst._maskeVersion || 0) + 1;
        clearTimeout(Hautverdeckung._ausstehend.get(inst));
        Hautverdeckung._ausstehend.set(inst, setTimeout(() => Hautverdeckung._rechnen(inst), Hautverdeckung.RUHE_MS));
    }

    /**
     * Rechnen — aber nicht mitten im Nachladen einer Stufe (Edgar, 09.10.2026: „die feine Stufe nur nach Ruhe, in kleinen
     * Häppchen"). Gemessen am feinen Körper (104.480 Punkte, 7 Stücke): `anwenden` 3,25 s auf dem Hauptfaden. Jedes Häppchen
     * der feinen Stufe (`Genesis9haeppchen`) meldete ein Stück und löste sie neu aus — zehnmal 3 s, daher die Lücken von
     * 3–9 s zwischen den Häppchen, obwohl der Bau selbst nur 1–160 ms brauchte. Läuft ein Nachladen
     * (`Figuraufbaustand.laeuft`; „grob gewählt" zählt nicht), wartet die Maske und wird EINMAL gerechnet, wenn es fertig ist.
     * Die Rechnung läuft im Worker (`anwendenAsync`): sie wartet nicht mehr auf Ruhe des Nutzers, vorher ein Block von 3–14 s.
     */
    static _rechnen(inst) {
        const nachladen = Figuraufbaustand.laeuft(inst) && !inst._grobHalt;
        if (nachladen) {
            Hautverdeckung._ausstehend.set(inst, setTimeout(() => Hautverdeckung._rechnen(inst), Hautverdeckung.NACHLADEN_MS));
            return;
        }
        Hautverdeckung._ausstehend.delete(inst);
        // Weniger Stücke als in der gezeigten Maske: Kleidung ist weg (ein Austausch hält die Zahl und bleibt, wie er war) — die Haut sofort zeigen.
        if (Hautverdeckung.zaehlende(inst).length < (inst._maskeAnzahl || 0)) Hautverdeckung.freigeben(inst);
        const lauf = inst._maskeVersion;
        Hautverdeckung.anwendenAsync(inst, () => inst._maskeVersion === lauf)
            .catch((fehler) => Protokoll.warnung('Hautverdeckung', fehler.message));
    }
}

Hautverdeckung.einhaengen();
// Für Messungen aus der Konsole — die Szene lädt als ein Bündel.
window.__hautverdeckung = Hautverdeckung;
window.__hautmaske = Hautmaske;
