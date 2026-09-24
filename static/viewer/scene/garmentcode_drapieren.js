import { Antwortnachholen } from '../gemeinsam/antwortnachholen.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Stoffvorschau } from './stoffvorschau.js';
import { GarmentcodeAblage } from './garmentcode_ablage.js';
import { GarmentcodeTitel } from './garmentcode_titel.js';
import { Charakterkoerper } from './charakter_koerper.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { fn } from '../gemeinsam/registrierung.js';
import { GarmentcodeBilanz } from './garmentcode_bilanz.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';
import { GarmentcodeSimulation } from './garmentcode_simulation.js';
import { Genesis9lagen } from '../gemeinsam/genesis9lagen.js';

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
        // Über die getragenen Stücke bauen (11.09.2026): Der Server
        // erweitert den Körper um sie. Das Stück, das gerade neu entsteht,
        // bleibt aussen vor — es ersetzt sein altes.
        if (document.getElementById('gc-ueber-getragene')?.checked !== false) {
            daten.append('getragen', JSON.stringify(
                GarmentcodeAblage.getragen(figur?.inst || figur, stueck)));
            GarmentcodeDrapierung.getrageneDaz(daten, figur?.inst || figur);
        }
        try {
            // MIT FRIST (09.09.2026): Eine Drapierung, deren Antwort nie
            // kommt, liess den Reiter besetzt und alle Knoepfe grau —
            // Begruendung und Logauszug in `gemeinsam/fristabruf.js`.
            // Reisst die Verbindung (Neustart des Dev-Servers, 20.09.2026),
            // wird die abgelegte Antwort nachgeholt statt neu gerechnet.
            const netz = await Antwortnachholen.formular(
                '/api/garmentcode/drapieren/', daten, undefined,
                (text) => { meldung.textContent = text; }, reiter.abbruch);
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

    /**
     * Die getragenen Daz-Stücke einer Genesis-9-Figur in die Stellung
     * (`regler_figur.stellung.getragen`, 24.09.2026, Edgar: „GarmentCode Pants
     * Harem zieht die Kleider bei Genesis nicht über existierende Genesis-
     * Kleider hoch"). Der Server rechnet ihre Netze wie beim Anziehen und legt
     * das neue Stück in der Nacharbeit darüber (`G9garmentfigur.getragene_stoffe`).
     */
    static getrageneDaz(daten, inst) {
        const getragen = Genesis9lagen.anfrage(inst?.kleidung, null).getragen;
        const roh = daten.get('regler_figur');
        if (inst?.quelle !== 'genesis9' || !getragen.length || !roh) return false;
        const regler = JSON.parse(roh);
        regler.stellung = { ...(regler.stellung || {}), getragen };
        daten.set('regler_figur', JSON.stringify(regler));
        return true;
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
        // Daz-Stücke über dem neuen Stück neu holen (Genesis 9, 24.09.2026).
        const nachgezogen = await Genesis9lagen.nachGcBau(figur?.inst || figur, stueck, netz.ueber_getragene)
            .catch(fehler => `Daz-Stücke nicht nachgezogen: ${fehler.message || fehler}`);
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
        if (typeof nachgezogen === 'string') meldung.textContent += ` · ${nachgezogen}`;
        else if (nachgezogen?.length) meldung.textContent += ` · darüber neu: ${nachgezogen.join(', ')}`;
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
     *
     * `quelle` (24.09.2026): wie `titel` — von außen NUR, wenn der Aufrufer
     * sie besser kennt als der DOM-Zustand (der gemeinsame Bau mehrerer
     * Stücke, `garmentcode_gemeinsam.js`, reicht bisher `null` durch wie
     * beim Titel); sonst kommt sie aus dem gerade offenen Reiter.
     */
    static async einhaengen(figur, netz, stueck, titel = null, quelle = null) {
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
        // Der Name, unter dem das Stück bestellt wurde (20.09.2026), und
        // seine Herkunft (24.09.2026) — Vorbild-Knopf oder Form-Häkchen,
        // damit ein späterer Klick auf das Stück dieselbe Wahl wiederfindet.
        titel = titel || netz.titel || GarmentcodeTitel.aktuell(stueck);
        quelle = quelle || GarmentcodeTitel.quelle();
        if (netz.rig_url) {
            // `inst`, nicht `figur.inst`: Die Zeile oben löst beide Formen
            // auf (Reiter-Wrapper `{id, inst}` ODER die Instanz selbst).
            // Mit `figur.inst` fiel der zweite Fall um — `undefined.group`
            // in `GarmentcodeAnziehen.einhaengen`, gemessen 09.09.2026.
            getragen = await GarmentcodeAnziehen.anziehen(
                inst, netz.rig_url, stueck, titel);
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
        GarmentcodeAblage.merken(inst, stueck, netz, titel, quelle);
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
     * da gibt es nichts nachzuziehen. Genesis 9 auch nicht (24.09.2026): Der
     * Stoffkanal bindet an das MakeHuman-Grundnetz — ein fremder Körper, dessen
     * Reglerzüge das Stück sonst mitgezogen hätten. Und nur, wenn der Server
     * einen Ergebnisordner gemeldet hat — ohne ihn findet er das Netz nicht.
     */
    static vorschauBinden(figur, netz, stueck) {
        // Beide Formen, wie in `einhaengen` — sonst bindet die Vorschau
        // stumm nicht, wenn die Instanz selbst hereingereicht wird.
        const inst = figur?.inst || figur;
        if (!inst || inst.quelle === 'smpl' || inst.quelle === 'genesis9' || !netz.ordner) return false;
        const gehaengt = inst.group?.getObjectByName(
            GarmentcodeAnziehen.name(stueck));
        if (!gehaengt) return false;
        return Stoffvorschau.binden(stueck, netz.ordner, gehaengt,
                                    Charakterkoerper.stellung(inst));
    }
}
