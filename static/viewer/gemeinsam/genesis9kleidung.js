import { Serverabruf } from './serverabruf.js';
import { Genesis9netz } from './genesis9netz.js';
import { Genesis9aufbau } from './genesis9aufbau.js';
import { Genesis9lagen } from './genesis9lagen.js';
import { Stueckereignis } from './stueckereignis.js';
import { Oberflaechenbindung } from './oberflaechenbindung.js';
import { Umfaerbung } from './umfaerbung.js';
import { Stoffwerte } from './stoffwerte.js';
import { Reiterzuordnung } from './reiterzuordnung.js';

/**
 * Genesis9kleidung — Daz-Stücke einer Genesis-9-Figur anziehen und ausziehen,
 * über den getragenen Stücken darunter (`Genesis9lagen`).
 *
 * Herausgelöst aus `genesis9modell.js` (19.09.2026, 327 Zeilen), als die
 * Lagen dazukamen — Edgar: „das genesis T-Shirt ist an einigen Stellen
 * kaputt". Was die Lagen sind und warum, steht in `genesis9lagen.js`; hier
 * nur der Weg zum Server und die Netze.
 *
 * GEMELDET WIRD WIE EIN GARMENTCODE-STÜCK (`Stueckereignis`), sobald eines
 * an der Figur hängt: Dessen Haut- und Lagenmaske rechnet gegen ALLE Stücke
 * — kommt ein Daz-Hemd oder geht es, ist sie falsch. Ohne GarmentCode-Stück
 * bleibt es still: Die Lagen der Daz-Garderobe macht der Server, und die
 * Masken kosten auf Stufe 2 Sekunden (19.09.2026, Ärmelsaum-Befund).
 *
 * DAS SCHILD DER SCHWEBEANZEIGE (20.09.2026, Edgar: „der hover text bei Genesis
 * Kleidern ist falsch, der zeigt geometry (genesis) anstelle der Genesis asset
 * namen"): Der Server nennt je Teil den Daz-Geometrienamen (`geometry`, `Dress`,
 * `TL Rivet`); der Name des Stücks steht nur im Katalog (`{id, name}`). Der wird
 * einmal geholt und gemerkt — `anzeigename` — und mehrteilige Stücke tragen ihren
 * Teilnamen dahinter („Dancing Queen Dress · Dress").
 */
export class Genesis9kleidung {

    static KATALOG = '/api/character/genesis9-figur/garderobe/';
    static _stuecke = null;
    static _stueckeLauf = null;
    static _namen = null;

    static stilliste(werte) { return Genesis9lagen.stilliste(werte); }

    /**
     * Der volle Katalog — EIN Lauf für alle Aufrufer (23.09.2026, Edgar:
     * „Ladezeit deutlich länger als 12 s" / „mach das laden parallel und
     * asynchron"): Beim Start ziehen mehrere Stücke GLEICHZEITIG an (Jeans,
     * Shirt, Haar, Schuhe) und riefen bis dahin alle VIER ihren eigenen
     * Katalog-Fetch — `if (!_namen)` schützt nur gegen einen ZWEITEN Aufruf,
     * NACHDEM der erste fertig ist, nicht gegen vier, die noch vor dem
     * ersten `await` gleichzeitig starten. Die Katalog-View ist synchron
     * (Daphnes einer geteilter Thread) — vier gleichzeitige Aufrufe standen
     * hintereinander an: 1,62 + 2,07 + 0,69 + 0,99 s statt einmal ~0,3 s
     * (Serverlog 11:17:59–11:18:05). Jetzt merkt sich `_stueckeLauf` das
     * LAUFENDE Promise, alle warten auf dasselbe — UND `Genesis9garderobe.
     * liste()` (Assets-Reiter) nimmt DENSELBEN Katalog statt eines zweiten,
     * unabhängigen Fetches (zwei echte Serverrunden für dieselben Daten).
     */
    static async stuecke() {
        if (!Genesis9kleidung._stuecke) {
            if (!Genesis9kleidung._stueckeLauf) {
                Genesis9kleidung._stueckeLauf = Serverabruf.json(Genesis9kleidung.KATALOG)
                    .then((daten) => daten.stuecke || [])
                    .catch(() => []);
            }
            Genesis9kleidung._stuecke = await Genesis9kleidung._stueckeLauf;
        }
        return Genesis9kleidung._stuecke;
    }

    /** Der Name des Stücks aus dem Katalog — sonst die Kennung. */
    static async anzeigename(kennung) {
        if (!Genesis9kleidung._namen) {
            const stuecke = await Genesis9kleidung.stuecke();
            Genesis9kleidung._namen = Object.fromEntries(
                stuecke.map((s) => [s.id, s.name || s.id]));
        }
        return Genesis9kleidung._namen[kennung] || kennung;
    }

    /** Das Schild: Name des Stücks, bei mehreren Teilen mit Teilname (nie `geometry`). */
    static beschriftung(name, teilname, anzahl, herkunft = 'Genesis 9') {
        const teil = anzahl > 1 && teilname && teilname !== 'geometry' ? ` · ${teilname}` : '';
        return `${name}${teil} (${herkunft})`;
    }

    /**
     * Ein Stück anziehen — alle seine Teile, über den getragenen Stücken darunter.
     * `werte`: `{variante, stil, stile: {pose, laenge}, regler, griff}`.
     */
    static async anziehen(inst, kennung, werte, stufen, kaskade) {
        inst.kleidung[kennung] = { ...(werte || {}) };
        const lauf = inst._lauf;
        const daten = await Serverabruf.senden(Genesis9aufbau.adresse(
            `${inst.constructor.ADRESSE}garderobe/${encodeURIComponent(kennung)}/netz/`, stufen), {
                regler: inst.regler || {}, variante: werte?.variante || '',
                stil: Genesis9kleidung.stilliste(werte), regler_stueck: werte?.regler || {},
                pose: inst.pose, ausdruck: inst.ausdruck, griffe: inst.griffe(),
                ...Genesis9lagen.anfrage(inst.kleidung, kennung),
                gc_getragen: Genesis9lagen.gcGetragen(inst),
            });
        if (daten.fehler) throw new Error(daten.fehler);
        if (lauf !== inst._lauf || !inst.kleidung[kennung]) return 0;   // überholt oder ausgezogen
        inst._stueckWeg(kennung);
        const name = await Genesis9kleidung.anzeigename(kennung);
        (daten.teile || []).forEach((teil, nummer) => {
            const netz = Genesis9netz.bauen(teil, `genesis9_kleid_${kennung}_${nummer}`);
            netz.userData.beschriftung = Genesis9kleidung.beschriftung(name, teil.name, daten.teile.length);
            netz.userData.art = daten.art || null;          // kleidung | haar | requisit
            // Oberflaechenbindung (21.09.2026, Konzept Fitting): Attribute ans Netz;
            // verdrahtet wird beim Einhaengen (auch nach jedem Neubinden — DORT
            // steht `inst.bodyMesh` sicher, hier oft noch nicht: Koerper und
            // Kleidung laufen gleichzeitig, siehe `Oberflaechenbindung.anlegen`).
            Oberflaechenbindung.anlegen(netz, teil);
            inst.clothMeshes[`${kennung}/${nummer}`] = inst._einhaengen(netz, teil.hautgewichte);
        });
        Umfaerbung.stueck(inst, kennung, inst.kleidung[kennung]);    // eigene Farbe (24.09.2026)
        Stoffwerte.stueck(inst, kennung, inst.kleidung[kennung]);    // Rauheit, Metall, Gewebe (25.09.2026)
        await Genesis9lagen.nachziehen(inst, kennung, daten, stufen, kaskade);
        Genesis9kleidung.melden(inst, kennung, true);
        return daten.teile?.length || 0;
    }

    /**
     * Haut- und Lagenverdeckung nachziehen. Bis 20.09.2026 nur mit GarmentCode-
     * Stück — die Daz-Garderobe blieb ohne Maske („ihre Lagen macht der Server").
     * Edgar mit Bild (Olesia, Base Shirt −14,5/−2,7 cm im Tanz): Haut in Streifen
     * am unteren Rücken. Zwei Flächen, die 3 mm auseinanderliegen und getrennt
     * gehäutet werden, kommen sich an jedem Gelenk um Millimeter nahe — keine
     * Gewichte helfen (`hautmaske.js`, Befund vom 11.09.). Die Haut unter einem
     * Daz-Stück der Art `kleidung` wird deshalb genauso nicht gezeichnet
     * (`Hautverdeckung.stoffe` filtert nach `userData.art`); Stufe 1 mit Shirt
     * und Jeans 2,4 s einmal je Umbau. Die Lagenmaske bleibt GarmentCode-Sache.
     */
    static melden(inst, kennung, angezogen) {
        Stueckereignis.melden(inst, kennung, angezogen);
        return Object.keys(inst?.clothMeshes || {}).some((schluessel) => Reiterzuordnung.gcLive(schluessel));
    }

    /** Ausziehen; `neu`: die Figur wird ohnehin neu gebaut (Griffpose, eigene Knochen). */
    static async ausziehen(inst, kennung, neu) {
        inst._stueckWeg(kennung);
        delete inst.kleidung[kennung];
        if (neu) await inst.neuFormen();
        else await Genesis9lagen.nachAusziehen(inst, kennung);
        Genesis9kleidung.melden(inst, kennung, false);
    }
}
