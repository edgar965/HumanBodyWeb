import { Fristabruf } from '../gemeinsam/fristabruf.js';
import { garmentcodeFortschritt } from './garmentcode_fortschritt.js';
import { GarmentcodeDrapierung } from './garmentcode_drapieren.js';
import { GarmentcodePanels } from './garmentcode_panels.js';
import { GarmentcodeVorschau3d } from './garmentcode_vorschau3d.js';
import { GarmentcodeAblauf } from './garmentcode_ablauf.js';
import { Laufwache } from '../gemeinsam/laufwache.js';

/**
 * GarmentcodeGemeinsam — mehrere Stücke in EINEM Lauf anziehen.
 *
 * WARUM ÜBERHAUPT (Edgar, 09.09.2026: „GarmentCode soll simulieren und die
 * anderen kennen", dann „mach das gleichzeitige Anziehen mehrere Stücke"):
 * Zwei getrennt drapierte Stücke wissen nichts voneinander — die
 * Stoff-gegen-Stoff-Kollision des Upstream gilt innerhalb EINES simulierten
 * Netzes. Im Bild stand der Hosenbund durch das T-Shirt hindurch.
 *
 * Gemessen im Überlappungsband, radial um die Körperachse: getrennt
 * simuliert liegt die Hose in 23,8 % der Fächer weiter aussen als das
 * T-Shirt (bis 32,5 mm), gemeinsam simuliert in 0,2 % (bis 3,2 mm).
 *
 * EIN AUFRUF, NICHT MEHRERE: Der Server baut die Schnitte selbst, vereint
 * sie zu einer Spezifikation und simuliert einmal. Ein Ablauf, der die
 * Schnitte einzeln über `/erzeugen/` holte, könnte sie zwischendurch mit
 * verschiedenen Körpermassen bauen — und genau das darf nicht passieren.
 */
export class GarmentcodeGemeinsam {

    /**
     * Die Frist. Gemessen kostet ein Paarlauf gut zwei Minuten; vier
     * Stücke entsprechend mehr. Ohne Frist bliebe der Reiter besetzt,
     * wenn die Antwort ausbleibt (Befund vom 09.09.2026, `fristabruf.js`).
     */
    static FRIST_S = 600;

    /**
     * Dauer je Stück für den Balken — er gewichtet danach. Eine zu kleine
     * Zahl lässt ihn am Anschlag stehen, und das liest sich als „hängt".
     *
     * GEMESSEN am Paarlauf über den Endpunkt (09.09.2026): 59,1 s für
     * Hose + T-Shirt, davon 39,4 s Simulation — also rund 30 s je Stück.
     * Bei mehr Stücken wächst die Simulation stärker als linear (mehr
     * Punkte UND mehr Kontakte); der Balken läuft dann in seinen Deckel
     * bei 97 %, und daneben steht, um wie viel er überzogen ist.
     */
    static ERWARTET_JE_STUECK_S = 30;

    /**
     * Die Liste bauen und der Figur anziehen.
     *
     * @param reiter  der `GarmentcodeReiter` (Laufwache, Figurdaten)
     * @param liste   die `Kombiliste`
     */
    static async bauen(reiter, liste) {
        const meldung = document.getElementById('gc-meldung');
        const darf = liste.darfBauen();
        if (!darf.ok) { meldung.textContent = darf.grund; return; }
        const wache = GarmentcodeAblauf.frei(reiter, meldung);
        if (!wache.darf) return;
        const figur = reiter.figur();
        if (!figur) {
            meldung.textContent = 'Keine Figur gewählt — bitte links in der '
                + 'Charakterliste eine anklicken.';
            return;
        }
        if (!reiter.drapierbereit) {
            meldung.textContent = 'Gemeinsam anziehen braucht die Simulation '
                + '— sie ist auf diesem Rechner nicht eingerichtet.';
            return;
        }
        const knoepfe = GarmentcodeAblauf.KNOEPFE
            .map((k) => document.getElementById(k)).filter(Boolean);
        const lauf = GarmentcodeAblauf.beginnen(reiter, knoepfe);
        try {
            await GarmentcodeGemeinsam._lauf(reiter, liste, figur, meldung);
        } catch (fehler) {
            if (Laufwache.aktuell(reiter, lauf)) {
                garmentcodeFortschritt.gescheitert(
                    'gemeinsam', String(fehler.message || fehler));
                meldung.textContent = `Fehler: ${fehler.message || fehler}`;
            }
        } finally {
            GarmentcodeAblauf.beenden(reiter, knoepfe, lauf);
        }
    }

    /** Der eigentliche Weg — abgesichert von `bauen`. */
    static async _lauf(reiter, liste, figur, meldung) {
        const namen = liste.eintraege.map((e) => e.titel).join(' + ');
        meldung.textContent = `Baue „${namen}" gemeinsam …`;
        garmentcodeFortschritt.starten(
            GarmentcodeGemeinsam.schritte(liste.anzahl));
        garmentcodeFortschritt.laeuft('gemeinsam');

        const daten = reiter.figurdaten(figur);
        daten.append('stuecke', JSON.stringify(liste.fuerServer()));
        const antwort = await Fristabruf.formular(
            '/api/garmentcode/gemeinsam/', daten,
            GarmentcodeGemeinsam.FRIST_S);
        if (antwort.fehler) {
            garmentcodeFortschritt.entfallen('einhaengen');
            garmentcodeFortschritt.gescheitert('gemeinsam', 'Fehler');
            meldung.textContent = `Fehlgeschlagen: ${antwort.fehler}`;
            return;
        }
        garmentcodeFortschritt.fertig(
            'gemeinsam', `${antwort.punkte} Punkte, ${antwort.dauer_s} s`);
        await GarmentcodeGemeinsam._einhaengen(figur, antwort, meldung);
    }

    /**
     * Die Stücke an die Figur hängen — dasselbe wie beim Einzelbau.
     *
     * Der Reihe nach und nicht nebenläufig: `GarmentcodeAnziehen` baut das
     * Skelett der Figur, falls es noch keines gibt. Zwei Aufrufe zugleich
     * bauten es zweimal.
     */
    static async _einhaengen(figur, antwort, meldung) {
        garmentcodeFortschritt.laeuft('einhaengen');
        // Was vom Einzelbau noch an der Figur hängt, weicht: Panels und
        // Vorschaunetz liegen an derselben Stelle wie der simulierte Stoff.
        GarmentcodePanels.entfernen(figur);
        GarmentcodeVorschau3d.entfernen(figur);
        const berichte = [];
        for (const stueck of antwort.stuecke || []) {
            berichte.push(await GarmentcodeGemeinsam._eines(figur, stueck));
        }
        garmentcodeFortschritt.fertig(
            'einhaengen', `${berichte.filter((b) => b.ok).length} von `
            + `${berichte.length} angezogen`);
        meldung.textContent = GarmentcodeGemeinsam.kurzbilanz(antwort,
                                                              berichte);
        meldung.title = GarmentcodeGemeinsam.bilanz(antwort, berichte);
    }

    /** Ein einzelnes Stück; ein Fehler stoppt die anderen nicht. */
    static async _eines(figur, stueck) {
        if (stueck.fehler || !stueck.rig_url) {
            return { ok: false, stueck,
                     grund: stueck.fehler || 'kein Netz geliefert' };
        }
        try {
            const getragen = await GarmentcodeDrapierung.einhaengen(
                figur, stueck, stueck.stueck);
            return { ok: true, stueck, getragen };
        } catch (fehler) {
            return { ok: false, stueck,
                     grund: String(fehler.message || fehler) };
        }
    }

    /** Der Schrittplan — je Stück eine gemessene Dauer. */
    static schritte(anzahl) {
        return [
            { schluessel: 'gemeinsam',
              erwartet: anzahl * GarmentcodeGemeinsam.ERWARTET_JE_STUECK_S,
              titel: `${anzahl} Stücke gemeinsam simulieren` },
            { schluessel: 'einhaengen', erwartet: 2, titel: 'Anziehen' },
        ];
    }

    /** Kurz im Reiter — der Hautabstand ist die Probe, dass etwas anliegt. */
    static kurzbilanz(antwort, berichte) {
        const gescheitert = berichte.filter((b) => !b.ok);
        const abstaende = berichte
            .filter((b) => b.ok && b.stueck.hautabstand_mm != null)
            .map((b) => Math.round(b.stueck.hautabstand_mm));
        const haut = abstaende.length
            ? `, ${Math.min(...abstaende)}–${Math.max(...abstaende)} mm zur Haut`
            : '';
        if (gescheitert.length) {
            return `${berichte.length - gescheitert.length} von `
                + `${berichte.length} angezogen${haut} — nicht geklappt: `
                + gescheitert.map((b) => b.stueck.stueck).join(', ');
        }
        return `Gemeinsam fertig in ${antwort.dauer_s} s${haut}`;
    }

    /** Ausführlich im Tooltip — je Stück eine Zeile. */
    static bilanz(antwort, berichte) {
        const zeilen = [
            `${berichte.length} Stücke in EINER Simulation — sie verdrängen `
            + 'sich gegenseitig, statt sich zu durchdringen.',
            `Gemeinsames Netz: ${antwort.punkte} Punkte, `
            + `${antwort.dreiecke} Dreiecke, ${antwort.dauer_s} s auf `
            + `${antwort.geraet || 'unbekanntem Gerät'}.`,
        ];
        for (const bericht of berichte) {
            zeilen.push(`• ${bericht.stueck.stueck}: `
                        + GarmentcodeGemeinsam.stueckzeile(bericht));
        }
        if (antwort.aus_der_haut) {
            zeilen.push(`${antwort.aus_der_haut} Punkte aus der Haut geholt.`);
        }
        return zeilen.join('\n');
    }

    /**
     * Eine Zeile je Stück.
     *
     * Eigene Fassung statt `GarmentcodeBilanz.bilanz`: Dort steht die
     * DAUER des Laufs in jeder Zeile, und die gibt es hier nur einmal für
     * alle. Zwei Stücke mit derselben Sekundenzahl läsen sich, als hätte
     * jedes so lange gebraucht.
     */
    static stueckzeile(bericht) {
        if (!bericht.ok) return bericht.grund;
        const abstand = Number(bericht.stueck.hautabstand_mm);
        const haut = isFinite(abstand)
            ? `, ${abstand.toFixed(0)} mm zur Haut` : '';
        const beweglich = bericht.getragen?.angezogen
            ? `, beweglich über ${bericht.getragen.zugeordnet} Knochen`
            : ', unbeweglich';
        return `${bericht.stueck.punkte} Punkte${haut}${beweglich}`;
    }
}
