import { Reitergedaechtnis } from './reitergedaechtnis.js';

/**
 * Die Bauwerte (Hautabstand, Netzfeinheit, Anliegen) JE VORLAGE merken.
 *
 * ANLASS (Edgar, 11.09.2026, nach „T-Shirt und Hose auf einmal gebaut"):
 * „Das T-Shirt sieht wie eine Leggins aus … als ob du die Bauparameter des
 * T-Shirts auch nicht übernommen hast." Gemessen: Die Rig-Datei des T-Shirts
 * trug Körpernormalen — es WAR angelegt, auf 2 mm. Der Regler „An die Haut
 * ziehen" hing bis dahin global im Reitergedächtnis: Das Leggings-Häkchen
 * setzte 2, der Wechsel auf das T-Shirt ließ die 2 stehen, „Stück
 * übernehmen" kopierte sie.
 *
 * Ein Bauwert beschreibt, wie DIESES Stück gebaut wird — wie seine
 * Schnittwerte (`Reitergedaechtnis.gcWerte`, je Vorlage). Also derselbe
 * Weg: Schlüssel `garmentcode/bau:<vorlage>`, gemerkt bei jedem Zug und
 * beim Setzen durch ein Preset, hergestellt beim Vorlagenwechsel
 * (`Garmentcodegedaechtnis.anwenden` → `GarmentcodeBauregler.herstellen`).
 * Die drei Felder stehen in `Gedaechtniswahl.JE_VORLAGE`, damit das
 * globale Gedächtnis sie nicht daneben noch einmal führt.
 */
export class GarmentcodeBaugedaechtnis {

    static schluessel(vorlage) {
        return `garmentcode/bau:${vorlage}`;
    }

    /** Die gerade gewählte Vorlage — aus dem DOM, ohne Importzyklus. */
    static vorlage() {
        return document.getElementById('gc-vorlage')?.value || null;
    }

    /** `{hautabstand_mm, aufloesung, anliegen_mm}` dieser Vorlage merken. */
    static merken(werte, vorlage = GarmentcodeBaugedaechtnis.vorlage()) {
        if (!vorlage || !werte) return false;
        return Reitergedaechtnis.setzen(
            GarmentcodeBaugedaechtnis.schluessel(vorlage), { ...werte });
    }

    /** Die gemerkten Bauwerte einer Vorlage — `{}` wenn keine. */
    static holen(vorlage) {
        const werte = vorlage ? Reitergedaechtnis.holen(
            GarmentcodeBaugedaechtnis.schluessel(vorlage)) : null;
        return (werte && typeof werte === 'object') ? werte : {};
    }
}
