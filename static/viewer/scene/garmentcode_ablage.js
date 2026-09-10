import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Garmentstoff } from './garmentcode_stoff.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * GarmentCode-Stücke in der gespeicherten Szene.
 *
 * BEFUND (Edgar, 08.09.2026): „habe gerade das Modell mit GarmentCode
 * gespeichert, beim neu laden sind die Garment Code items weg."
 *
 * `CharacterInstance.toJSON` schreibt `cloth`, `garments`, `mh_proxy` und
 * `hair_style` — je Verfahren eine Liste. GarmentCode hatte keine: Die Stücke
 * hingen nur als Netz in der Gruppe und in `clothMeshes`, und beides wird
 * beim Speichern nicht angesehen. Kein Fehler, keine Meldung — beim Laden
 * stand die Figur nackt da.
 *
 * WAS GESPEICHERT WIRD, UND WARUM SO WENIG
 * ========================================
 * Nur `{stueck, rig_url, ordner, material}`. Das Netz selbst kommt beim
 * Laden wieder vom Server (`rig_url` → dieselbe Datei, die der Bau geholt
 * hat) — es hat 14.338 Punkte und 28.489 Dreiecke, das gehört nicht in eine
 * Szenendatei. Und es wird NICHT neu simuliert: Die Drapierung kostet
 * gemessen 24,5 s, das Nachladen der fertigen Datei Millisekunden.
 *
 * Der Preis ist eine Abhängigkeit vom Ergebnisordner. Fehlt er (aufgeräumt,
 * anderer Rechner), sagt das Laden es und lässt die Figur stehen — eine
 * Szene, die wegen eines fehlenden Kleidungsstücks gar nicht lädt, wäre
 * schlimmer.
 *
 * DAS MATERIAL WIRD AM NETZ ABGELESEN, nicht mitgeführt: Seit dem
 * 08.09.2026 lässt sich Farbe, Rauheit und Metallanteil je Stück einstellen
 * (`GarmentcodeMaterial`). Was am Netz steht, ist der Zustand — eine zweite
 * Buchführung daneben liefe irgendwann auseinander.
 */
export class GarmentcodeAblage {

    /** Der Name der Liste in der Szenendatei. */
    static FELD = 'garmentcode';

    /**
     * Ein frisch gebautes Stück in die Ablage der Figur schreiben.
     *
     * @param inst    Szeneninstanz (nicht der Reiter-Wrapper)
     * @param stueck  Name der Vorlage, z. B. `hose`
     * @param netz    die Antwort von `/api/garmentcode/drapieren/`
     */
    static merken(inst, stueck, netz) {
        if (!inst || !stueck || !netz?.rig_url) return false;
        if (!inst.gcStuecke) inst.gcStuecke = {};
        inst.gcStuecke[GarmentcodeAnziehen.schluessel(stueck)] = {
            stueck,
            rig_url: netz.rig_url,
            // Der Ordner ist für die Stoffvorschau nötig; sie bindet daraus
            // die Ergebnisdatei (`Stoffnachfuehrung.netzpfad`).
            ordner: netz.ordner || null,
        };
        return true;
    }

    /** Ein gelöschtes Stück aus der Ablage nehmen. */
    static vergessen(inst, schluessel) {
        if (!inst?.gcStuecke) return false;
        return delete inst.gcStuecke[schluessel];
    }

    /**
     * Die Liste für `toJSON` — mit dem Material, wie es JETZT am Netz steht.
     */
    static toJSON(inst) {
        const bestand = inst?.gcStuecke || {};
        return Object.keys(bestand).map((schluessel) => {
            const eintrag = bestand[schluessel];
            const netz = GarmentcodeAblage._netzVon(inst, eintrag);
            return {
                ...eintrag,
                material: GarmentcodeAblage._material(netz),
                // Ein Stück, dessen Netz nicht mehr hängt, ist entfernt
                // worden, ohne dass die Ablage es erfahren hat. Es wird
                // mitgeschrieben, aber als solches erkennbar.
                haengt: !!netz,
            };
        }).filter((e) => e.haengt);
    }

    /**
     * Die gespeicherten Stücke wieder anziehen.
     *
     * Nacheinander, nicht parallel: `GarmentcodeAnziehen.einhaengen` liest
     * das Skelett der Figur und schreibt in `clothMeshes` — zwei Läufe
     * gleichzeitig kämen sich dort in die Quere.
     *
     * @returns Anzahl der wiederhergestellten Stücke
     */
    static async laden(inst, liste) {
        if (!inst || !Array.isArray(liste) || !liste.length) return 0;
        inst.gcStuecke = inst.gcStuecke || {};
        // Erst das Skelett, dann anziehen — sonst hängt das Stück nach dem
        // Laden einer Szene als starres Netz, bis irgendwann eine Animation
        // lädt. Dieselbe Zeile wie in `garmentcode_drapieren.anziehen`
        // (08.09.2026: „warum denn der hinweistext: Figur hat kein
        // Skelett?? die hat doch skelett").
        if (!inst.isSkinned) fn.convertInstToSkinned?.(inst);
        let fertig = 0;
        for (const eintrag of liste) {
            if (!eintrag?.stueck || !eintrag?.rig_url) continue;
            try {
                await GarmentcodeAnziehen.anziehen(
                    inst, eintrag.rig_url, eintrag.stueck);
                inst.gcStuecke[GarmentcodeAnziehen.schluessel(eintrag.stueck)] = {
                    stueck: eintrag.stueck,
                    rig_url: eintrag.rig_url,
                    ordner: eintrag.ordner || null,
                };
                GarmentcodeAblage._materialSetzen(
                    inst.clothMeshes?.[
                        GarmentcodeAnziehen.schluessel(eintrag.stueck)],
                    eintrag.material);
                fertig += 1;
            } catch (fehler) {
                // Nicht durchwerfen: Eine Szene, die wegen eines fehlenden
                // Ergebnisordners nicht lädt, ist schlechter als eine ohne
                // dieses Kleidungsstück. Gemeldet wird es trotzdem.
                Protokoll.warnung('GarmentCode',
                    `„${eintrag.stueck}" nicht wiederherstellbar: `
                    + `${fehler.message || fehler}`);
            }
        }
        return fertig;
    }

    /**
     * Das Netz eines Eintrags — erst in `clothMeshes`, dann in der Gruppe.
     *
     * Zwei Wege, weil das Stück beides ist: Eintrag in `clothMeshes` (damit
     * es auswählbar und einzeln löschbar ist, 08.09.2026) UND Kind der
     * Figurgruppe. Nur den ersten zu fragen hiesse, ein Stück stillschweigend
     * nicht zu speichern, falls es dort einmal fehlt — und „nicht gespeichert"
     * ist genau der Befund, um den es hier geht.
     */
    static _netzVon(inst, eintrag) {
        const schluessel = GarmentcodeAnziehen.schluessel(eintrag.stueck);
        return inst.clothMeshes?.[schluessel]
            || inst.group?.getObjectByName(
                GarmentcodeAnziehen.name(eintrag.stueck))
            || null;
    }

    // -- Material -------------------------------------------------------------

    /** Als Text in der Szenendatei — `#rrggbb` liest sich beim Nachsehen. */
    static _material(netz) {
        const werte = Garmentstoff.werte(netz);
        if (!werte) return null;
        return {
            ...werte,
            farbe: werte.farbe === null ? null
                : `#${werte.farbe.toString(16).padStart(6, '0')}`,
        };
    }

    static _materialSetzen(netz, werte) {
        return Garmentstoff.auflegen(netz, werte) === 1;
    }
}
