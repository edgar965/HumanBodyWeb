/**
 * GarmentcodeTitel — wie ein gebautes Stück in der Szene heißt.
 *
 * Edgar, 20.09.2026: „Wenn ich ein Asset mit einem Namen in Auftrag gebe,
 * dann soll es auch im 3D View so heissen, nicht generisch unterwäsche
 * (Garment Code)!!" Bis dahin trug jedes Stück den Schlüssel seiner Vorlage
 * (`unterwaesche`), auch wenn es nach dem Vorbild „Bandbikinislip" gebaut
 * war oder als Form „Höschen" angehakt.
 *
 * Der Titel kommt aus dem Reiter, in dieser Reihenfolge:
 *   1. das gewählte Vorbild aus der Kleiderbibliothek (Knopf `.active`),
 *   2. die angehakte Form (`form_*`, z. B. „Höschen"),
 *   3. der Titel der Vorlage aus der Auswahlliste („Unterwäsche"),
 *   4. der Schlüssel selbst.
 * Der SCHLÜSSEL des Stücks (`gc_unterwaesche`) bleibt: Er ist die Adresse
 * in `clothMeshes` und in der Ablage; nur die Beschriftung ändert sich. Ein
 * Stück, das aus einer Szenendatei zurückkommt, bringt seinen Titel mit
 * (`titel` im Eintrag der Ablage) — der Reiter zeigt dann etwas anderes.
 *
 * `quelle()` (24.09.2026, Edgar: „wenn ich ein Garment Code anklicke, soll
 * die Toolbox links exakt zu dem hinspringen … in der Kleiderbibliothek das
 * Garment Code selektieren, oder die Checkboxen aktivieren") liefert dieselbe
 * Herkunft als KENNUNG statt Anzeigetext — die eindeutige Adresse, mit der
 * `garmentcode_stueckquelle.js` später den Knopf wiederfindet.
 */
export class GarmentcodeTitel {

    /** Der Titel, den das nächste gebaute Stück dieser Vorlage bekommt. */
    static aktuell(stueck) {
        return GarmentcodeTitel.vorbild()
            || GarmentcodeTitel.form()
            || GarmentcodeTitel.vorlage(stueck)
            || String(stueck || 'Kleidung');
    }

    /** Das gewählte Vorbild — oder ''. */
    static vorbild() {
        const knopf = document.querySelector('#gc-vorbilder .vorbild-knopf.active');
        return knopf ? knopf.textContent.trim() : '';
    }

    /** Die angehakte Form (das erste angehakte `form_*`-Kästchen) — oder ''. */
    static form() {
        const kaestchen = document.querySelector(
            '#gc-passform input[data-preset^="form_"]:checked');
        const zeile = kaestchen?.closest('label') || kaestchen?.parentElement;
        return zeile ? zeile.textContent.trim() : '';
    }

    /** Der Titel der Vorlage aus `#gc-vorlage` — oder ''. */
    static vorlage(stueck) {
        const auswahl = document.getElementById('gc-vorlage');
        const eintrag = [...(auswahl?.options || [])].find((o) => o.value === stueck);
        return eintrag ? eintrag.textContent.trim() : '';
    }

    /** Die Beschriftung eines Netzes: der Titel, dahinter die Herkunft. */
    static beschriftung(titel, stueck) {
        return `${titel || stueck || 'Kleidung'} (GarmentCode)`;
    }

    /** Die Herkunft des GERADE gebauten Stücks als Kennung — oder `null`
     *  bei freien Reglern ohne Vorbild oder Form. */
    static quelle() {
        const vorbild = document.querySelector('#gc-vorbilder .vorbild-knopf.active');
        if (vorbild?.dataset.schluessel) {
            return { art: 'vorbild', schluessel: vorbild.dataset.schluessel };
        }
        const form = document.querySelector('#gc-passform input[data-preset^="form_"]:checked');
        if (form?.dataset.preset) {
            return { art: 'form', schluessel: form.dataset.preset };
        }
        return null;
    }
}
