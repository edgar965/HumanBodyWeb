import { Eigenkleid } from './eigenkleid.js';
import { Eigenkleidwerte } from './eigenkleidwerte.js';
import { Eigenrock } from './eigenrock.js';
import { Koerperkoordinatenkarte } from './koerperkoordinatenkarte.js';
import { Protokoll } from './protokoll.js';
import { Skelettereignis } from './skelettereignis.js';

/**
 * Eigenkleider — die eigenen Stücke einer Genesis-9-Figur nach ihren Reglern (`kleid:<art>:…`, `Eigenkleidwerte`) anlegen, nachführen und abnehmen
 * (Stufe K2a, 25.10.2026).
 *
 * `anwenden(inst)` legt für jede angelegte Art ein `Eigenkleid` an (oder bindet das vorhandene neu) und nimmt abgelegte ab; gerufen beim Anlegen/Ablegen
 * (`Genesis9eigenkleidkasten`) und — als Nebenwirkung dieses Imports — nach jedem neuen Skelett einer Figur (`Skelettereignis`: erster Bau, Reglerzug, Stufenwechsel).
 * So kommt ein mit der Figur gespeichertes Stück beim Laden von selbst wieder. Ein Schieber im Zug ändert nur die Uniforms (`vorschau`), erst beim Loslassen schreibt
 * die Bedienung den Wert in die Regler (`Eigenkleidwerte.setzen`) — ohne Serveraufruf und ohne Neubau.
 */
export class Eigenkleider {

    static _je = new WeakMap();

    /** Die Stücke der Figur nach ihren Reglern; → die angelegten Arten. */
    static async anwenden(inst) {
        if (inst?.quelle !== 'genesis9') return [];
        const stuecke = Eigenkleider._je.get(inst) || {};
        Eigenkleider._je.set(inst, stuecke);
        const getragen = Eigenkleidwerte.getragen(inst);
        for (const art of Object.keys(stuecke)) {
            if (getragen.includes(art)) continue;
            stuecke[art].entfernen();
            delete stuecke[art];
        }
        if (!getragen.length) return [];
        const karte = await Koerperkoordinatenkarte.holen();
        for (const art of Eigenkleidwerte.getragen(inst)) {         // nach dem Warten noch einmal gelesen: inzwischen abgelegt?
            const stueck = stuecke[art] ||= art === 'rock' ? new Eigenrock(inst, art, karte) : new Eigenkleid(inst, art, karte);
            stueck.werte = Eigenkleidwerte.alle(inst, art);
            stueck.binden();
        }
        Eigenkleider.lage(inst);
        return Eigenkleidwerte.getragen(inst);
    }

    /** Luft zwischen Hose und darüber liegendem Oberteil (m) — gesetzt. */
    static LAGE_LUFT_M = 0.002;

    /**
     * Das Oberteil liegt über der Hose: Wo beide decken (Rumpfhöhe ab dem Bund), hält es mindestens den größten Sitz der Hose + deren Brückenabstand + Luft.
     * Ohne das stach die Hose am Gesäß durch das Oberteil (im Chrome gesehen an Mann1: Zickzack an der Hüfte, die Kettengrenze Rumpf/Bein entlang).
     */
    static lage(inst) {
        const oben = Eigenkleider.stueck(inst, 'oberteil');
        if (!oben) return;
        const hose = Eigenkleider.stueck(inst, 'hose');
        if (!hose) { oben.u.uKkLage.value.set(0, 0); return; }
        const w = Eigenkleidwerte.shaderwerte('hose', hose.werte);
        oben.u.uKkLage.value.set(Math.max(...w.sitz) + w.bruecke[0] + Eigenkleider.LAGE_LUFT_M, w.saum[0]);
    }

    static stueck(inst, art) {
        return Eigenkleider._je.get(inst)?.[art] || null;
    }

    /** Ein Wert im Zug: nur die Uniforms des angelegten Stücks; false, wenn es nicht angelegt ist. */
    static vorschau(inst, art, feld, wert) {
        const stueck = Eigenkleider.stueck(inst, art);
        if (!stueck) return false;
        stueck.werteAnwenden({ ...stueck.werte, [feld]: wert });
        Eigenkleider.lage(inst);
        return true;
    }

    /** Knopf „Drapieren“/„Grundform“ (Rock, Kleid): Wert setzen und den Lauf abwarten → `{ms, schritte, saum_mm, weite_mm}`, null (Grundform, überholt) oder false. */
    static async drapieren(inst, art, an) {
        Eigenkleidwerte.setzen(inst, art, 'drapiert', an ? 1 : 0);
        if (!Eigenkleider.vorschau(inst, art, 'drapiert', an ? 1 : 0)) return false;
        const s = Eigenkleider.stueck(inst, art), rock = s?.rock || s;
        return an && rock?.laeuft ? rock.laeuft : null;
    }
}

if (typeof document !== 'undefined') {
    Skelettereignis.hoeren(({ inst }) => {
        Eigenkleider.anwenden(inst).catch(fehler => Protokoll.fehler('Eigene Kleider', 'Stücke nicht angelegt', fehler));
    });
}
