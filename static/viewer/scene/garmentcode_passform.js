import { garmentcodePreset } from './garmentcode_preset.js';

/**
 * Passform — die Voreinstellungen für das ganze Kleidungsstück, oben im Reiter.
 *
 * Edgar, 08.09.2026: „Mach mir die Voreinstellungen für die Kleider, oben im
 * Tab, nach dem Farben bereich, mit Voreinstellungen für eng anliegend, und
 * 2 anderen."
 *
 * WARUM EIGENES MODUL: `garmentcode_regler.js` lag bei 303 Zeilen und wäre
 * mit diesem Teil auf 336 gewachsen — eine Datei wird beim Anfassen nicht
 * größer als ihre Grenze (`~/.claude/rules/struktur.md`).
 *
 * WARUM ÜBER `garmentcodePreset` UND NICHT EIGENSTÄNDIG: Die Mechanik ist
 * dieselbe wie bei den Gruppen-Presets — Häkchen setzt mehrere Regler,
 * Abhaken stellt den vorigen Stand wieder her, eine Änderung von Hand nimmt
 * das Häkchen weg. Vor allem aber der gegenseitige Ausschluss: „Eng
 * anliegend" (Passform) und „Weit fallend" (Ärmel) fassen beide
 * `sleeve.end_width` an. Zwei getrennte Bestände wüssten nichts voneinander,
 * und beide Kästchen stünden gehakt da, während nur eines gilt.
 */
export class GarmentcodePassform {

    /**
     * Beide Preset-Listen übernehmen und den Kasten zeichnen.
     *
     * Gruppen- und Passform-Presets kommen in EINEN Bestand — nur so greift
     * der Ausschluss über die Bereiche hinweg (siehe oben).
     *
     * @param antwort  die Antwort von `/api/garmentcode/regler/`
     * @param setzt    (werte) => void
     * @param liest    (pfad) => wert
     */
    static uebernehmen(antwort, setzt, liest, zuruecksetzt = null) {
        garmentcodePreset.setzen([...(antwort.presets || []),
                                  ...(antwort.passform || [])]);
        const gezeichnet = GarmentcodePassform.zeichnen(setzt, liest, zuruecksetzt);
        // Die FORM, die gerade gilt, bekommt ihr Häkchen (Rock: Bleistift-
        // rock, 11.09.2026) — erst im nächsten Umlauf, wenn das Gedächtnis
        // die gemerkten Werte dieser Vorlage eingetragen hat.
        setTimeout(() => GarmentcodePassform.formHaken(antwort.passform || [], liest), 0);
        return gezeichnet;
    }

    /**
     * Welche Form gilt? Die, deren Werte alle anliegen — oder die
     * Vorgabe des Stücks (`gehakt`), wenn kein Bausteinfeld gesetzt ist.
     * Nur, wenn noch keine Form gehakt ist (das Gedächtnis war zuerst).
     */
    static formHaken(presets, liest) {
        const formen = presets.filter((p) => p.form);
        if (!formen.length || formen.some((p) => garmentcodePreset.aktiv.has(p.schluessel))) {
            return null;
        }
        const passt = (p) => Object.entries(p.werte).every(([pfad, wert]) => liest(pfad) === wert);
        const leer = (p) => Object.keys(p.werte).every((pfad) => liest(pfad) === undefined);
        const treffer = formen.find(passt) || formen.find((p) => p.gehakt && leer(p));
        if (treffer) garmentcodePreset.anhaken([treffer.schluessel]);
        return treffer ? treffer.schluessel : null;
    }

    /**
     * Den Kasten zeichnen.
     *
     * @param setzt  (werte) => void — trägt die Werte in den Reglerbereich
     * @param liest  (pfad) => wert — der aktuell geltende Wert eines Pfades
     */
    static zeichnen(setzt, liest, zuruecksetzt = null) {
        const ziel = document.getElementById('gc-passform');
        if (!ziel) return false;
        ziel.innerHTML = '';
        const kasten = garmentcodePreset.kasten('passform', setzt, liest, zuruecksetzt);
        if (kasten) {
            ziel.appendChild(kasten);
            return true;
        }
        // Kein Preset ist hier die Regel, nicht der Ausnahmefall: Eine Hose
        // hat weder Rumpfweite noch Ärmel, ein Trägertop keinen von beiden.
        // Das zu sagen ist besser als ein leerer Kasten, der wie ein
        // Ladefehler aussieht.
        ziel.innerHTML = '<div class="hb-hinweis">Für dieses Stück gibt es '
            + 'keine Passform-Voreinstellung.</div>';
        return false;
    }
}
