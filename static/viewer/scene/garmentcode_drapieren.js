import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';

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

    /**
     * Ab hier sitzt ein Stück nicht mehr — dann sagt es die Meldung.
     *
     * 40 mm, nicht enger: Eine weite Hose kommt auf 21 mm und ist völlig
     * in Ordnung (06.09.2026 gemessen, Bundweite 1,0 und Ausstellung 1,0);
     * mit einer engeren Schwelle liest sich jeder weite Schnitt wie ein
     * Fehler. Auf dem falschen Körper lag der Wert bei 27 mm MEDIAN mit
     * 31 % der Punkte über 50 mm — das trifft diese Schwelle sicher.
     */
    static ABSTAND_WARNUNG_MM = 40;

    /** Das Schnittmuster als 3D-Netz auf den Körper legen und anziehen. */
    static async drapieren(reiter, figur, spezifikation, meldung,
                           stueck) {
        garmentcodeFortschritt.laeuft('drape');
        // Die Figurdaten müssen mit: aus ihnen kommen der Körper, auf den
        // drapiert wird, und die Knochengewichte fürs Anziehen.
        const daten = reiter.figurdaten(figur);
        daten.append('spezifikation', spezifikation);
        try {
            const netz = await Serverabruf.formular(
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
        if (netz.rig_url) {
            try {
                getragen = await GarmentcodeAnziehen.anziehen(
                    figur.inst, netz.rig_url, stueck);
            } catch (fehler) {
                garmentcodeFortschritt.gescheitert('rig',
                    String(fehler.message || fehler));
                meldung.textContent = `Drapiert, aber nicht angezogen: `
                    + `${fehler.message || fehler}`;
                return;
            }
        }
        garmentcodeFortschritt.fertig('rig', getragen
            ? (getragen.angezogen
                ? `${getragen.zugeordnet} Knochen zugeordnet`
                : 'sichtbar, ohne Skinning')
            : 'nicht eingehängt');
        meldung.textContent = GarmentcodeDrapierung.bilanz(netz, getragen);
    }

    /**
     * Was die Figur JETZT trägt — nicht, was gerechnet wurde.
     *
     * Der Hautabstand steht mit drin, weil er die einzige Zahl ist, die
     * „liegt an" belegt. Ein T-Shirt kommt auf wenige Millimeter; wird
     * daraus eine zweistellige Zahl, drapiert etwas auf dem falschen
     * Körper, ohne dass ein Fehler auftritt.
     */
    static bilanz(netz, getragen) {
        if (!getragen) {
            return `Drapiert (${netz.punkte} Punkte, ${netz.dauer_s} s), `
                + `aber NICHT an der Figur`;
        }
        const abstand = Number(netz.hautabstand_mm);
        const sitz = !isFinite(abstand) ? ''
            : (abstand <= GarmentcodeDrapierung.ABSTAND_WARNUNG_MM
                ? `, ${abstand.toFixed(0)} mm zur Haut`
                : `, steht ${abstand.toFixed(0)} mm ab — sitzt nicht`);
        // Auf einem SMPL-Referenzkörper (06.09.2026) gibt es weder Skelett
        // noch Korrektur — das ist der Weg des Online-Tools, und so heißt
        // es auch. „Unbeweglich" wäre dort keine Einschränkung, sondern
        // die Messlatte.
        const beweglich = netz.auf_figur === false
            ? `, auf dem Referenzkörper ${netz.drapierkoerper || ''} wie das Online-Tool`
            : (getragen.angezogen
                ? `, beweglich über ${getragen.zugeordnet} Knochen`
                : ', aber unbeweglich (Figur hat kein Skelett)');
        // Wie viele Punkte in der Haut steckten und herausgeholt wurden.
        // Ohne die Zahl bliebe unsichtbar, dass dieser Schritt überhaupt
        // stattfindet — und wie viel er zu tun hatte.
        const geholt = Number(netz.aus_der_haut) > 0
            ? `, ${netz.aus_der_haut} Punkte aus der Haut geholt` : '';
        return `Fertig: ${netz.punkte} Punkte, ${netz.dreiecke} Dreiecke `
            + `in ${netz.dauer_s} s${sitz}${geholt}${beweglich}`;
    }
}
