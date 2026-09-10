import { Fristabruf } from '../gemeinsam/fristabruf.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Stoffvorschau } from './stoffvorschau.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { fn } from '../gemeinsam/registrierung.js';
import { GarmentcodeBilanz } from './garmentcode_bilanz.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';
import { GarmentcodeSimulation } from './garmentcode_simulation.js';

/**
 * GarmentcodeDrapierung — den Stoff auf den Körper fallen lassen und ihn
 * der Figur anziehen.
 *
 * WARUM EIGENES MODUL (06.09.2026): Der Bau geht seit Edgars Ansage („bei
 * Bauen soll das Garment gleich auf den Körper gebracht werden, ohne extra
 * Klick") in einem Zug durch — Schnitt, Drapierung, Anziehen. Das ist zu
 * viel für `garmentcode.js`, das damit über 300 Zeilen ginge.
 *
 * Der Server drapiert seit demselben Tag auf dem Körper der GEWÄHLTEN Figur,
 * nicht auf GarmentCodes Durchschnittskörper. Deshalb nennt die Meldung den
 * gemessenen Abstand zur Haut: Er ist die Probe darauf, dass das Stück
 * wirklich anliegt (vorher: Median 27,4 mm, 31 % der Punkte über 5 cm).
 */
export class GarmentcodeDrapierung {

    /** Das Schnittmuster als 3D-Netz auf den Körper legen und anziehen. */
    static async drapieren(reiter, figur, spezifikation, meldung,
                           stueck) {
        garmentcodeFortschritt.laeuft('drape');
        // Die Figurdaten müssen mit: aus ihnen kommen der Körper, auf den
        // drapiert wird, und die Knochengewichte fürs Anziehen.
        const daten = reiter.figurdaten(figur);
        daten.append('spezifikation', spezifikation);
        // Hautabstand und Netzfeinheit aus den Reglern unter „Bauen"
        // (09.09.2026). Sie betreffen nur die Drapierung — deshalb hier und
        // nicht in `figurdaten`, das auch das Erzeugen eines Schnitts nutzt.
        GarmentcodeBauregler.anhaengen(daten);
        // Und die 42 Regler aus dem aufklappbaren Bereich darunter — davon
        // nur, was von der Vorgabe abweicht.
        GarmentcodeSimulation.anhaengen(daten);
        try {
            // MIT FRIST (09.09.2026): Eine Drapierung, deren Antwort nie
            // kommt, liess den Reiter besetzt und alle Knoepfe grau —
            // Begruendung und Logauszug in `gemeinsam/fristabruf.js`.
            const netz = await Fristabruf.formular(
                '/api/garmentcode/drapieren/', daten);
            if (netz.fehler) {
                garmentcodeFortschritt.entfallen('rig');
                garmentcodeFortschritt.gescheitert('drape', 'Fehler');
                meldung.textContent = `Schnitt fertig, Drapierung scheiterte: `
                    + `${netz.fehler}`;
                return;
            }
            garmentcodeFortschritt.fertig('drape',
                                          `${netz.punkte} Punkte, ${netz.dauer_s} s`);
            await GarmentcodeDrapierung.anziehen(figur, netz, meldung,
                                                 stueck);
        } catch (fehler) {
            garmentcodeFortschritt.entfallen('rig');
            garmentcodeFortschritt.gescheitert('drape',
                                               String(fehler.message || fehler));
            meldung.textContent = `Drapierung fehlgeschlagen: `
                + `${fehler.message || fehler}`;
        }
    }

    /** Das gerechnete Netz an die Figur hängen und Bilanz ziehen. */
    static async anziehen(figur, netz, meldung, stueck) {
        garmentcodeFortschritt.laeuft('rig');
        let getragen = null;
        try {
            getragen = await GarmentcodeDrapierung.einhaengen(figur, netz,
                                                             stueck);
        } catch (fehler) {
            garmentcodeFortschritt.gescheitert('rig',
                String(fehler.message || fehler));
            meldung.textContent = `Drapiert, aber nicht angezogen: `
                + `${fehler.message || fehler}`;
            return;
        }
        garmentcodeFortschritt.fertig('rig', getragen
            ? (getragen.angezogen
                ? `${getragen.zugeordnet} Knochen zugeordnet`
                : 'sichtbar, ohne Skinning')
            : 'nicht eingehängt');
        // Kurz sichtbar, ausführlich im Tooltip (Edgar, 08.09.2026: „mach
        // die vielen Texte aus dem Garment Code weg"). Die Zahlen sind die
        // Probe darauf, dass etwas anliegt — sie verschwinden nicht, sie
        // stehen nur nicht mehr im Weg.
        meldung.textContent = GarmentcodeBilanz.kurzbilanz(netz, getragen);
        meldung.title = GarmentcodeBilanz.bilanz(netz, getragen);
    }

    /**
     * Ein fertiges Stück an die Figur hängen — der Teil ohne Anzeige.
     *
     * HERAUSGELÖST AM 09.09.2026 für den gemeinsamen Lauf: Der bringt
     * mehrere Stücke aus EINER Simulation mit und hängt sie in einer
     * Schleife ein. Mit dem Fortschritt und der Meldung darin würde jedes
     * Stück die Zeile des vorigen überschreiben, und der Schritt „Anziehen"
     * ginge mehrfach auf und zu.
     *
     * Wirft bei einem Fehler weiter — der Aufrufer entscheidet, ob das den
     * ganzen Lauf beendet.
     */
    static async einhaengen(figur, netz, stueck) {
        // ERST DAS SKELETT (Edgar, 08.09.2026: „warum denn der hinweistext:
        // Figur hat kein Skelett?? die hat doch skelett").
        //
        // Er hat recht: Die Rigify-Daten liegen seit dem Seitenaufbau bereit
        // (`szenenaufbau.js`), nur wurde das Skelett bisher erst gebaut, wenn
        // eine Animation lud (`convertInstToSkinned`) oder Haare dazukamen
        // (`hair.js`). Wer ein Stück davor baute, bekam ein starres Netz und
        // eine Meldung, die nach einem Mangel der Figur klang.
        //
        // Dieselbe Zeile wie in `hair.js:50`, mit denselben Bedingungen —
        // eine erzeugte Figur (`generatedConfig`) hat kein DEF-Rig, dort
        // kehrt `convertInstToSkinned` von selbst um.
        const inst = figur?.inst || figur;
        if (inst && !inst.isSkinned) fn.convertInstToSkinned?.(inst);
        let getragen = null;
        if (netz.rig_url) {
            // `inst`, nicht `figur.inst`: Die Zeile oben löst beide Formen
            // auf (Reiter-Wrapper `{id, inst}` ODER die Instanz selbst).
            // Mit `figur.inst` fiel der zweite Fall um — `undefined.group`
            // in `GarmentcodeAnziehen.einhaengen`, gemessen 09.09.2026.
            getragen = await GarmentcodeAnziehen.anziehen(
                inst, netz.rig_url, stueck);
        }
        // Ab jetzt folgt das Stueck den Reglern, ohne neue Simulation
        // (Edgar, 08.09.2026: „mach mir auch einen 3D Vorschau der schnell
        // ist und synchron mit Regler geht"). Gebunden wird an GENAU den
        // Koerper, auf dem drapiert wurde — deshalb hier und nicht spaeter.
        // Frisch simuliert: Die Vorschauzeile gilt erst wieder, wenn ein
        // Regler bewegt wird.
        Stoffvorschau.hinweisAus();
        // In die Ablage der Figur, damit „Speichern" es findet
        // (08.09.2026: „beim neu laden sind die Garment Code items weg").
        GarmentcodeAblage.merken(inst, stueck, netz);
        // Das frisch eingehängte Stück bekommt ein neues Material mit den
        // Vorgabewerten. Ohne diesen Schritt spränge die eingestellte Farbe
        // bei jedem Bau zurück (08.09.2026).
        //
        // GENAU DIESES STÜCK, nicht alle (09.09.2026): Vorher stand hier
        // `anwenden(figur, false)`, und damit zog der Bau eines zweiten
        // Stücks die Farbe des ersten mit — auch die, die aus einer
        // gespeicherten Szene kam.
        GarmentcodeMaterial.aufStueck(figur, stueck);
        GarmentcodeDrapierung.vorschauBinden(figur, netz, stueck);
        return getragen;
    }

    /**
     * Das Stück an den Körper binden, damit es den Reglern folgt.
     *
     * Nur für HumanBody-Figuren: Ein SMPL-Referenzkörper hat keine Morphs,
     * da gibt es nichts nachzuziehen. Und nur, wenn der Server einen
     * Ergebnisordner gemeldet hat — ohne ihn findet er das Netz nicht.
     */
    static vorschauBinden(figur, netz, stueck) {
        // Beide Formen, wie in `einhaengen` — sonst bindet die Vorschau
        // stumm nicht, wenn die Instanz selbst hereingereicht wird.
        const inst = figur?.inst || figur;
        if (!inst || inst.quelle === 'smpl' || !netz.ordner) return false;
        const gehaengt = inst.group?.getObjectByName(
            GarmentcodeAnziehen.name(stueck));
        if (!gehaengt) return false;
        return Stoffvorschau.binden(stueck, netz.ordner, gehaengt,
                                    Charakterkoerper.stellung(inst));
    }
}
