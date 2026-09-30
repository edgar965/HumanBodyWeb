import { THREE } from './state.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Bereichsgedaechtnis } from './bereichsgedaechtnis.js';
import { Letztewahl } from './letztewahl.js';
import { Auswahlaura } from '../gemeinsam/auswahlaura.js';

/**
 * Starteinstellungen — was die Szene beim Laden aus den Servereinstellungen
 * übernimmt: Modellvorgabe, Anfangspose, MakeHuman-Vorgabekleidung, offene
 * Bereiche, Auswahlhelligkeit.
 *
 * Aus `boot.js init()` herausgeloest (Umbau 16.08.2026). Vorher wurden vier
 * dieser Werte als GLOBALE Variablen am `window` abgelegt —
 * `window._defaultPose`, `window._mhDefaults`, `window._mhTposeDisplacement`
 * (und `_defaultAnimUrl` im Zustand). Der Auftrag verlangt: ein Datensatz mit
 * mehr als drei Feldern, der seine Funktion verlässt, wird eine Klasse. Genau
 * das ist der Fall — die Werte werden an anderer Stelle wieder gelesen.
 *
 * `window._mhTposeDisplacement` bleibt zusätzlich gesetzt, weil
 * `mhproxy_anpassen.js` es dort liest.
 */
export class Starteinstellungen {

    /** So viele MakeHuman-Vorgabestücke kennt die Einstellungsseite. */
    static MH_PLAETZE = 4;
    /** Pose, die keine Umrechnung braucht. */
    static VORGABEPOSE = 'a_pose';
    /** Posennamen, die auf einen Serverpfad zeigen. */
    static POSENPFADE = { t_pose: 'rest_poses/t-pose' };

    constructor() {
        this.pose = Starteinstellungen.VORGABEPOSE;
        this.mhKleidung = [];
        this.tposeVerschiebung = '1';
    }

    /** Einstellungen holen und anwenden. Fehler bleiben ohne Folgen. */
    static async holen() {
        const werte = new Starteinstellungen();
        const daten = await Serverabruf.jsonOderNull('/api/settings/humanbody/');
        if (daten) werte.anwenden(daten);
        return werte;
    }

    anwenden(daten) {
        const eigene = daten.ui_prefs || {};
        // KEIN Standard-Modell und keine Standard-Animation mehr aus den Einstellungen
        // (Edgar, 30.09.2026: „entferne das Standardmodell und die Standard Animation.
        // Auf der Seite /Charakter/ soll immer nur der letzte geladene Modell und die
        // letzte Animation geladen werden"). Beides kommt jetzt aus `Letztewahl`
        // (`localStorage`), gefüllt beim Laden — `Startfigur` und `Letztewahl`
        // lesen dort. Die Spalten bleiben in der Datenbank stehen, werden aber weder
        // angezeigt noch gelesen.
        state._defaultAnimUrl = Letztewahl.animation();
        this.pose = eigene.default_pose || Starteinstellungen.VORGABEPOSE;
        this.mhKleidung = this._mhKleidung(eigene);
        this.tposeVerschiebung = eigene.mh_tpose_displacement ?? '1';
        // mhproxy_anpassen.js liest den Wert von hier.
        window._mhTposeDisplacement = this.tposeVerschiebung;
        this.bereicheOeffnen(daten.expanded_panels_scene);
        this.auswahlhelligkeit(daten.selection_opacity);
    }

    _mhKleidung(eigene) {
        const kleidung = [];
        for (let platz = 1; platz <= Starteinstellungen.MH_PLAETZE; platz++) {
            const kennung = eigene[`mh_default_${platz}`];
            if (kennung) kleidung.push(kennung);
        }
        return kleidung;
    }

    /**
     * Zuletzt offene Bereiche wiederherstellen. Modell- und Kleider-Reiter
     * bleiben unberührt — die bauen ihre Bereiche selbst auf.
     */
    bereicheOeffnen(offene) {
        if (!Array.isArray(offene)) return;
        // Gespeichert werden nur die OFFENEN. Ein Bereich, den es beim
        // letzten Speichern noch nicht gab, stand also nie in der Liste und
        // wurde zugeklappt — dauerhaft (08.09.2026: die Passform-
        // Voreinstellungen waren deshalb unauffindbar). `Bereichsgedaechtnis`
        // trennt „war zu" von „ist neu".
        const gesehen = Bereichsgedaechtnis.gesehen();
        const namen = [];
        for (const bereich of document.querySelectorAll(
                '.panel-section[data-panel-key]')) {
            if (bereich.closest('#tab-modell') || bereich.closest('#tab-kleider')) {
                continue;
            }
            const name = bereich.dataset.panelKey;
            namen.push(name);
            bereich.classList.toggle(
                'collapsed',
                Bereichsgedaechtnis.zuklappen(name, offene, gesehen));
        }
        Bereichsgedaechtnis.merken(namen);
    }

    /** Helligkeit, mit der Auswahl und Zeigen unter der Maus leuchten. */
    auswahlhelligkeit(wert) {
        if (typeof wert !== 'number') return;
        // Seit 25.09.2026 die Stärke der Auswahlanzeige (`gemeinsam/auswahlaura.js`);
        // das Eigenleuchten bleibt aus — es färbte den Stoff um, sichtbar war es kaum.
        Auswahlaura.deckkraft(wert);
    }

    /** Serverpfad der Anfangspose, oder null wenn keine gesetzt werden soll. */
    posenpfad() {
        if (!this.pose || this.pose === Starteinstellungen.VORGABEPOSE) return null;
        return Starteinstellungen.POSENPFADE[this.pose] || this.pose;
    }
}
