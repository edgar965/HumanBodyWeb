import { fn } from '../gemeinsam/registrierung.js';
import { Antwortnachholen } from '../gemeinsam/antwortnachholen.js';
import { garmentcodeRegler } from './garmentcode_regler.js';
import { GarmentcodeBauregler } from './garmentcode_bauregler.js';
import { GarmentcodeMaterial } from './garmentcode_material.js';
import { GarmentcodeTitel } from './garmentcode_titel.js';
import { GarmentcodeFigur } from './garmentcode_figur.js';
import { Dazkleidung } from './genesis9/dazkleidung.js';
import { Genesis9garderobe } from './genesis9/genesis9garderobe.js';

/**
 * GarmentcodeAlsgenesis — „Als Genesis-Stück speichern" im GarmentCode-Reiter (Weg 2).
 *
 * WARUM (Edgar, 25.09.2026: „bei GarmentCode habe ich ganz viele Einstellungen
 * gehabt, bei der Portierung zu Genesis der Garment Codes gibt es die alle
 * nicht"): Die 171 gebackenen Stücke tragen nur die Werte ihres Vorbilds. Hier
 * backt der Server den GERADE eingestellten Schnitt — Regler, Bauwerte, Titel,
 * Material — auf der gewählten Genesis-Figur (`POST /api/garmentcode/genesis/speichern/`,
 * `G9gceigenes.bauen`, ~30 s) als eigenes Genesis-Stück; danach zieht die gewählte
 * Figur es an, mit Rauheit, Metall und Gewebe als `werte.stoff`.
 *
 * Der Rückweg (Stück → Reiter) steht in `genesis9/gcherkunft.js`: er merkt sich
 * hier das Stück, von dem die Einstellung kam (`ziel`), und das neue ersetzt es
 * an der Figur. Ein Stück des Stapellaufs überschreibt der Server nie — ein neuer
 * Name bekommt eine Nummer.
 */
export class GarmentcodeAlsgenesis {

    static KNOPF = 'gc-als-genesis';
    static MELDUNG = 'gc-meldung';
    /** Frist für Schnitt + Drapierung + Schreiben (gemessen ~25–35 s je Stück). */
    static FRIST_S = 240;
    /** `{instId, kennung}` des Stücks, dessen Schnitt gerade im Reiter steht. */
    static ziel = null;
    static _laeuft = false;

    static einhaengen() {
        document.getElementById(GarmentcodeAlsgenesis.KNOPF)
            ?.addEventListener('click', () => GarmentcodeAlsgenesis.speichern());
    }

    /** Das Formular aus dem Stand des Reiters. */
    static formular(vorlage) {
        const daten = new FormData();
        const stand = GarmentcodeMaterial.stand;
        daten.append('vorlage', vorlage);
        daten.append('regler', garmentcodeRegler.alsJson());
        daten.append('bau', JSON.stringify(GarmentcodeBauregler.werte()));
        daten.append('titel', GarmentcodeTitel.aktuell(vorlage));
        daten.append('material', JSON.stringify({ farbe: stand.farbe, rauheit: stand.rauheit,
                                                  metall: stand.metall, gewebe: stand.gewebe }));
        daten.append('quelle', GarmentcodeTitel.quelle()?.schluessel || 'reiter');
        // Gebaut wird auf der Genesis-Figur des Reiters, wie „Bauen 2D + 3D"
        // (25.09.2026, `G9gcfigurbau`) — auf der Grundfigur legte das Folgen
        // Damiras Brustform in den Stoff. Keine Genesis-Figur: Grundfigur.
        const figur = GarmentcodeFigur.gewaehlt();
        if (figur?.inst?.quelle === 'genesis9') {
            const rf = GarmentcodeFigur.formulardaten(figur).get('regler_figur');
            if (rf) daten.append('regler_figur', rf);
        }
        return daten;
    }

    static async speichern() {
        const meldung = document.getElementById(GarmentcodeAlsgenesis.MELDUNG);
        const sagen = (text) => { if (meldung) meldung.textContent = text; };
        const vorlage = GarmentcodeMaterial.vorlage();
        if (!vorlage) { sagen('Erst eine Vorlage wählen.'); return null; }
        if (GarmentcodeAlsgenesis._laeuft) { sagen('Das Genesis-Stück wird schon gebaut …'); return null; }
        const knopf = document.getElementById(GarmentcodeAlsgenesis.KNOPF);
        GarmentcodeAlsgenesis._laeuft = true;
        if (knopf) knopf.disabled = true;
        sagen('Genesis-Stück wird gebaut: Schnitt, Drapierung auf der Figur, Schreiben (~30–60 s) …');
        try {
            const antwort = await Antwortnachholen.formular(
                '/api/garmentcode/genesis/speichern/', GarmentcodeAlsgenesis.formular(vorlage),
                GarmentcodeAlsgenesis.FRIST_S, sagen);
            if (antwort?.fehler) { sagen(`Fehlgeschlagen: ${antwort.fehler}`); return null; }
            sagen(`„${antwort.name}" liegt in der Garderobe (GC) — ${antwort.sekunden} s, ` +
                  `${antwort.haut_median_mm} mm zur Haut.`);
            await GarmentcodeAlsgenesis.anziehen(antwort);
            return antwort;
        } catch (fehler) {
            console.warn('GarmentcodeAlsgenesis:', fehler);
            sagen(`Fehlgeschlagen: ${fehler?.message || fehler}`);
            return null;
        } finally {
            GarmentcodeAlsgenesis._laeuft = false;
            if (knopf) knopf.disabled = false;
        }
    }

    /** Das neue Stück an die gewählte Figur — statt des Stücks, von dem der Schnitt kam. */
    static async anziehen(antwort) {
        const inst = GarmentcodeFigur.gewaehlt()?.inst;
        if (!inst) return false;
        const ziel = GarmentcodeAlsgenesis.ziel;
        if (ziel && ziel.instId === inst.id && ziel.kennung !== antwort.stueck
            && Dazkleidung.kleidung(inst)[ziel.kennung]) {
            Genesis9garderobe._ausziehen(inst, ziel.kennung);
        }
        Genesis9garderobe._anziehen(inst, antwort.stueck, { stoff: antwort.stoff || {} });
        GarmentcodeAlsgenesis.ziel = { instId: inst.id, kennung: antwort.stueck };
        await fn.refreshGenesis9Garderobe?.(inst);
        return true;
    }
}

GarmentcodeAlsgenesis.einhaengen();
fn.garmentcodeAlsGenesisZiel = (ziel) => { GarmentcodeAlsgenesis.ziel = ziel; };
// Für Proben im Tab (wie `__characters`).
if (typeof window !== 'undefined') window.__gcAlsGenesis = GarmentcodeAlsgenesis;
