import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Eigenhaut } from '../../gemeinsam/eigenhaut.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Genesis9netz } from '../../gemeinsam/genesis9netz.js';
import { Genesis9lagen } from '../../gemeinsam/genesis9lagen.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Genesis9aufbau } from '../../gemeinsam/genesis9aufbau.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Kleidfarbmischung } from '../../gemeinsam/kleidfarbmischung.js';
import { Stoffwerte } from '../../gemeinsam/stoffwerte.js';
import { Hautverdeckung } from '../../gemeinsam/hautverdeckung.js';
import { fn } from '../../gemeinsam/registrierung.js';

/**
 * Dazkleidung — ein Daz-Stück (Genesis 9) an einer HumanBody-Figur.
 *
 * WARUM (Edgar, 19.09.2026: „Umgekehrt auch Genesis Kleider auf HumanBody?"):
 * Die Daz-Garderobe im Assets-Reiter gibt es seit heute auch für eine
 * HumanBody-Figur. Der Server überträgt das Stück über die Paarung der
 * beiden Grundkörper (`core/dienste/g9aufhumanbody.py`) auf DIESE Figur
 * (Bauart, Morphs, Metaregler — wie der GarmentCode-Reiter sie schickt) und
 * liefert es in derselben Form wie für Genesis 9: Netz, Gruppen mit Daz'
 * Bildern, `hautgewichte` — nur mit DEF-Knochennamen.
 *
 * Gebunden wird an das Rigify-Skelett der Figur (`inst.rigifySkeleton`), das
 * ein HumanBody-Körper erst beim Animieren bekommt (`convertInstToSkinned`);
 * bis dahin hängt das Stück als starres Netz mit seinen Rohgewichten in
 * `userData`, und `nachbinden` holt es nach — dasselbe Muster wie
 * `GarmentcodeAnziehen`. Präfix `daz_` in `inst.clothMeshes`: eigenes Objekt,
 * auswählbar, einzeln löschbar; der Stand der Häkchen liegt in
 * `inst.dazKleidung` (Kennung → Werte).
 */
export class Dazkleidung {

    static ADRESSE = '/api/character/genesis9-figur/garderobe/';
    static PRAEFIX = 'daz_';

    /** Trägt diese Figur Daz-Stücke über diesen Weg (keine Genesis-9-Figur)? */
    static zustaendig(inst) {
        return !!inst && typeof inst.anziehenMitGriff !== 'function';
    }

    /** Kennung → Werte der getragenen Stücke — `kleidung` bei Genesis 9, sonst `dazKleidung`. */
    static kleidung(inst) {
        return (Dazkleidung.zustaendig(inst) ? inst.dazKleidung : inst?.kleidung) || {};
    }

    /** Anziehen auf der passenden Figurart — die Garderobe-Liste ruft nur dies. */
    static anziehenAuf(inst, kennung, werte) {
        return Dazkleidung.zustaendig(inst)
            ? Dazkleidung.anziehen(inst, kennung, werte)
            : inst.anziehenMitGriff(kennung, werte);
    }

    static ausziehenAuf(inst, kennung) {
        return Dazkleidung.zustaendig(inst)
            ? Dazkleidung.ausziehen(inst, kennung) : inst.ausziehen(kennung);
    }

    /** Die Figur, wie der Server sie braucht (`Garmentanfrage`-Felder). */
    static figur(inst) {
        const bauart = inst.bodyType || inst.body_type || '';
        return {
            figurart: 'humanbody',
            geschlecht: bauart.toLowerCase().startsWith('m') ? 'male' : (inst.gender || 'female'),
            bauart, morphs: inst.morphs || {}, meta: inst.meta || {},
        };
    }

    static async anziehen(inst, kennung, werte = null) {
        inst.dazKleidung = inst.dazKleidung || {};
        inst.dazKleidung[kennung] = { ...(werte || {}) };
        const daten = await Serverabruf.netzSenden(
            Genesis9aufbau.adresse(`${Dazkleidung.ADRESSE}${encodeURIComponent(kennung)}/netz/`, null), {
                ...Dazkleidung.figur(inst), variante: werte?.variante || '',
                stil: Genesis9lagen.stilliste(werte), regler_stueck: werte?.regler || {},
            });
        if (daten.fehler) throw new Error(daten.fehler);
        if (!inst.dazKleidung[kennung]) return 0;           // inzwischen ausgezogen
        Dazkleidung._weg(inst, kennung);
        const paare = [];
        (daten.teile || []).forEach((teil, nummer) => {
            const netz = Genesis9netz.bauen(teil, `${Dazkleidung.PRAEFIX}${kennung}_${nummer}`);
            paare.push([netz, teil]);
            netz.userData.hautgewichte = teil.hautgewichte || null;
            netz.userData.art = daten.art || null;          // kleidung | haar — wie `Genesis9kleidung`
            inst.clothMeshes[`${Dazkleidung.PRAEFIX}${kennung}/${nummer}`] =
                Dazkleidung.binden(inst, netz);
        });
        Genesis9kleidung.beschildern(inst, kennung, paare, 'Daz');   // ohne auf den Katalog zu warten
        Umfaerbung.stueck(inst, kennung, inst.dazKleidung[kennung]);   // eigene Farbe (24.09.2026)
        Kleidfarbmischung.anwenden(inst, kennung, inst.dazKleidung[kennung].regler);   // Textur der Mischung (30.09.2026)
        Stoffwerte.stueck(inst, kennung, inst.dazKleidung[kennung]);   // Rauheit, Metall, Gewebe
        Protokoll.debug('Dazkleidung', `${kennung} auf ${inst.id}: ${daten.teile?.length || 0} Teile`);
        if (daten.absatz) await Dazkleidung.absatz(inst, daten.absatz);
        Dazkleidung.hautNachziehen(inst);
        return daten.teile?.length || 0;
    }

    static ausziehen(inst, kennung) {
        Dazkleidung._weg(inst, kennung);
        if (inst.dazKleidung) delete inst.dazKleidung[kennung];
        if (inst.absatz?.quelle === `schuh:${kennung}`) Dazkleidung.absatz(inst, null);
        Dazkleidung.hautNachziehen(inst);
    }

    /**
     * Die Haut unter dem Stück nicht zeichnen (Edgar, 30.09.2026, Bild: GC T-Shirt auf einer
     * HumanBody-Figur, „die Brustwarzen schimmern durch"). Auf Genesis 9 meldet jedes
     * Daz-Stück sich seit dem 20.09.2026 (`Genesis9kleidung.melden`) und die Haut darunter
     * fällt weg; dieser Weg meldete nie — die Hautverdeckung rechnete hier nur, wenn
     * zufällig ein GarmentCode-Stück oder ein neues Skelett sie anstieß. Direkt und nicht
     * über das `Stueckereignis`: Auf das hört auch `GarmentcodeAbsatz`, und das setzte ohne
     * GarmentCode-Schuh den Absatz zurück — den einer Daz-Sandale eingeschlossen.
     */
    static hautNachziehen(inst) {
        Hautverdeckung.planen(inst);
    }

    /**
     * Ein Daz-Schuh mit Fußpose (Bardot Sandals): Der Server liefert den Absatz
     * (`winkel_grad`, `sprengung_grad`, `hebung_cm`, Quelle `schuh:<kennung>`),
     * die Figur bekommt ihn wie einen GarmentCode-Absatz — über die
     * Registrierung, weil `posenanwendung.js` über `skeleton.js` dieses Modul
     * schon erreicht (19.09.2026, Edgar: „Die Sandalen fitten nicht").
     */
    static async absatz(inst, info) {
        try {
            const befund = await fn.absatzSetzen?.(inst, info);
            if (befund && !befund.ok) Protokoll.warnung('Dazkleidung', `Absatz: ${befund.grund}`);
        } catch (fehler) {
            Protokoll.warnung('Dazkleidung', `Absatz: ${fehler.message}`);
        }
    }

    /** Binden, wenn die Figur ein Skelett hat — sonst starr, bis `nachbinden`. */
    static binden(inst, netz) {
        const skelett = inst.rigifySkeleton || null;
        const haut = netz.userData.hautgewichte;
        const gebunden = (skelett?.skeleton && haut)
            ? Eigenhaut.binden(netz, skelett, Dazkleidung.mitThreeNamen(haut, skelett)) : netz;
        Eigenhaut.einhaengen(inst.group, gebunden, skelett);
        return gebunden;
    }

    /**
     * Die Gewichte nennen die Knochen wie Blender (`DEF-breast.L`); die Three-Knochen
     * des Rigify-Skeletts heißen `DEF-breast_L`, nur `boneByName` kennt die Punkte.
     * `Eigenhaut.spaltenNummern` sucht nach `bone.name` — ohne Umschreiben fand es
     * 171 von 176 Knochen nicht (gemessen 19.09.2026). Im BVH Studio sind auch die
     * SCHLÜSSEL schon entschärft (`Clipanimation.namenEntschaerfen`: Punkt → Unterstrich,
     * 30.09.2026) — dort zählt die zweite Schreibweise.
     */
    static mitThreeNamen(haut, skelett) {
        const nach = skelett.boneByName || {};
        const knochen = n => (nach[n] || nach[n.replace(/\./g, '_')])?.name ?? n;
        return { ...haut, knochen: (haut.knochen || []).map(knochen) };
    }

    /** Nach dem Skelettaufbau (`convertInstToSkinned`): starre Daz-Stücke häuten. */
    static nachbinden(inst) {
        if (!inst?.rigifySkeleton?.skeleton || !inst.clothMeshes) return 0;
        let gebunden = 0;
        for (const [schluessel, netz] of Object.entries(inst.clothMeshes)) {
            if (!schluessel.startsWith(Dazkleidung.PRAEFIX) || !netz || netz.isSkinnedMesh
                || !netz.userData?.hautgewichte) continue;
            inst.group.remove(netz);
            inst.clothMeshes[schluessel] = Dazkleidung.binden(inst, netz);
            gebunden += 1;
        }
        return gebunden;
    }

    static _weg(inst, kennung) {
        for (const schluessel of Object.keys(inst.clothMeshes || {})) {
            if (schluessel.split('/')[0] === `${Dazkleidung.PRAEFIX}${kennung}`) {
                Netzentsorgung.ausAblage(inst.group, inst.clothMeshes, schluessel);
            }
        }
    }
}
