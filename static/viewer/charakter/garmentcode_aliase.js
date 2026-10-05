import { fn } from '../gemeinsam/registrierung.js';

/**
 * GarmentcodeAliase — alte Stücknamen (`t-shirt`, `pumps`, `bleistiftrock` …) auf das Katalogstück.
 *
 * Edgar, 05.10.2026: „ich klicke auf das Objekt T-Shirt GarmentCode. In der Leiste links wird das aber
 * nicht aktiv, es ist ‚Schuhe' aktiv. Es sollte das Asset im Tab links angezeigt werden." Szenen von
 * vor dem 11.09.2026 führen ihre Stücke unter den alten Namen (`gc_t-shirt`); die Auswahl `#gc-vorlage`
 * kennt seitdem nur acht Katalogstücke (`oberteil`, `hose`, … `schuh`). `vorlageZeigen('t-shirt')` fand
 * keine Option, kehrte stumm zurück, und der Reiter blieb beim zuletzt gewählten Stück.
 *
 * Die Tabelle kommt vom Server (`/api/garmentcode/zustand/` → `aliase`: `{alt: [Stück, Form]}`,
 * `Katalog.aliase`) — keine zweite Liste im Browser, die auseinanderläuft.
 */
export class GarmentcodeAliase {

    static _tabelle = {};

    static setzen(aliase) {
        GarmentcodeAliase._tabelle = (aliase && typeof aliase === 'object') ? aliase : {};
    }

    /** Das Katalogstück hinter einem Namen: ein alter Name löst auf, alles andere bleibt. */
    static stueck(name) {
        return GarmentcodeAliase._tabelle[name]?.[0] || name;
    }

    /** Die Form hinter einem alten Namen als Herkunft eines Stücks ohne gemerkte Quelle — sonst `null`. */
    static form(name) {
        const schluessel = GarmentcodeAliase._tabelle[name]?.[1];
        return schluessel ? { art: 'form', schluessel } : null;
    }
}

fn.garmentcodeAliasForm = (name) => GarmentcodeAliase.form(name);
