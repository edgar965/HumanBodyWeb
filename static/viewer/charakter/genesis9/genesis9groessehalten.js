import { markDirty } from '../undo.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';

/**
 * Genesis9groessehalten — Schalter „Größe halten" im Genesis-Bedienfeld (R8, 25.10.2026; Konzept
 * `Docu/konzepte/2026-10-25_regler-engpaesse-und-zusammenspiel-konzept.md`, Abschnitt 2).
 *
 * Edgar: „die Regler müssen zusammenspielen, z.B. Kopf und Körpergröße hängen zusammen. Kopfregler machen die Figur kleiner … wenn sowas passiert, dann soll
 * die Figur größer gemacht werden an anderen Stellen." Ist der Schalter an, merkt sich die Figur ihre Größe (Scheitel bis Sohle, m). Zieht man danach einen
 * Genesis-Regler, rechnet der Server ZUERST den Ausgleich (`POST …/groesse-halten/`, `Genesis9/groessehalten.py`: Sekante auf `Proportion Legs Length`) und
 * erst danach baut die Figur EINMAL neu (`zug`, gerufen aus `Genesis9reglerzeile.setzen`) — ein Neubau statt zwei.
 *
 * Der Ausgleichsregler und „Proportion Height" gleichen nichts aus: Wer sie von Hand zieht, will die Größe ändern — sie wird danach die neue Sollgröße.
 * Das Fenster „Formen …" und die Nachformung (Ort) setzen mehrere Regler oder einen neuen Morph; sie rufen `umbauen`.
 *
 * Zustand an der Figur: `inst.groesseHalten = {an, soll_m, letzte}`; gespeichert werden nur `an` und `soll_m` (`Genesis9Figur.toJSON` → `groesse_halten`), `letzte`
 * (die letzte Antwort des Servers) lebt nur im Browser. Der Platz im Bedienfeld entsteht hier über der Werkzeugzeile der Reglerliste — eine Zeile in der
 * Vorlage bräuchte einen Serverneustart (Djangos Vorlagen-Zwischenspeicher).
 */
export class Genesis9groessehalten {

    static ADRESSE = '/api/character/genesis9-figur/groesse-halten/';
    /** Gleich `G9groessehalten.AUSGLEICH` (`Genesis9/groessehalten.py`). */
    static AUSGLEICH = 'body_bs_ProportionLegsLength';
    /** Regler, die die Größe ändern SOLLEN: von Hand gezogen setzen sie die neue Sollgröße, statt ausgeglichen zu werden (Edgar, 25.10.2026: „OK, mach das"). */
    static SETZT_SOLL = [Genesis9groessehalten.AUSGLEICH, 'body_bs_ProportionHeight'];
    static KENNUNG = 'prop-genesis9-groesse';

    /** Ist „Größe halten" an dieser Figur an (mit gültiger Sollgröße)? */
    static an(inst) {
        const z = inst?.groesseHalten;
        return Boolean(z?.an && Number(z.soll_m) > 0);
    }

    /** Die Zeile mit Schalter und Stand — über `#prop-genesis9-reglerkopf`, je Füllen neu (die Figur kann gewechselt haben). */
    static fuellen(inst) {
        const kopf = document.getElementById('prop-genesis9-reglerkopf');
        if (!kopf) {
            Protokoll.warnung('Genesis9groessehalten', 'Kein #prop-genesis9-reglerkopf — Schalter „Größe halten" fehlt');
            return;
        }
        let feld = document.getElementById(Genesis9groessehalten.KENNUNG);
        if (!feld) {
            feld = document.createElement('div');
            feld.id = Genesis9groessehalten.KENNUNG;
            feld.className = 'g9-reglerkopf';
            kopf.before(feld);
        }
        feld.dataset.figur = inst.id;
        feld.innerHTML = `
            <label class="g9-reglerschalter" title="Merkt sich die jetzige Körpergröße. Ändert ein Regler danach die Größe, stellt der Server „Proportion Legs Length" so nach, dass sie wieder stimmt (der Kopf bleibt, wie er ist).">
                <input type="checkbox" data-schalter="groesse"> Größe halten</label>
            <span class="gedaempft hb-font-size-0-72rem" data-feld="stand"></span>`;
        const schalter = feld.querySelector('input');
        schalter.checked = Genesis9groessehalten.an(inst);
        schalter.addEventListener('change', () => Genesis9groessehalten.schalten(inst, schalter));
        Genesis9groessehalten.anzeigen(inst);
    }

    /** An: Sollgröße vom Server messen lassen (dieselbe Rechnung wie der Ausgleich). Aus: Zustand weg. */
    static async schalten(inst, schalter) {
        if (!schalter.checked) {
            inst.groesseHalten = null;
            markDirty('Größe halten aus');
            Genesis9groessehalten.anzeigen(inst);
            return;
        }
        schalter.disabled = true;
        try {
            const antwort = await Serverabruf.senden(Genesis9groessehalten.ADRESSE, { regler: inst.regler || {} });
            if (antwort.fehler) throw new Error(antwort.fehler);
            if (!(antwort.hoehe_m > 0)) throw new Error('Server lieferte keine Größe');
            inst.groesseHalten = { an: true, soll_m: antwort.hoehe_m, letzte: null };
            markDirty('Größe halten an');
        } catch (fehler) {
            schalter.checked = false;
            inst.groesseHalten = { an: false, soll_m: 0, letzte: { fehler: fehler.message } };
            Protokoll.warnung('Genesis9groessehalten', `Größe nicht messbar: ${fehler.message}`);
        } finally {
            schalter.disabled = false;
        }
        Genesis9groessehalten.anzeigen(inst);
    }

    /**
     * Ein Reglerzug: `bauen` baut die Figur (`inst.reglerSetzen`). Ist der Schalter an, stellt der Server vorher den Ausgleichsregler in `inst.regler`.
     * `name`/`wert`: der gezogene Regler mit seinem neuen Wert (in `inst.regler` steht er erst nach `bauen`).
     */
    static async zug(inst, name, wert, bauen) {
        if (!Genesis9groessehalten.an(inst)) return bauen();
        if (Genesis9groessehalten.SETZT_SOLL.includes(name)) {
            const z = inst.groesseHalten;
            const fertig = await bauen();
            if (inst.hoehe > 0) z.soll_m = inst.hoehe;          // von Hand gezogen: die neue Größe gilt
            z.letzte = null;
            Genesis9groessehalten.anzeigen(inst);
            return fertig;
        }
        const regler = { ...(inst.regler || {}) };
        if (Math.abs(wert) < 1e-6) delete regler[name];
        else regler[name] = wert;
        return Genesis9groessehalten.umbauen(inst, name, bauen, regler);
    }

    /**
     * Ausgleich rechnen, dann `bauen` — auch für Wege, die mehrere Regler auf einmal setzen (Fenster „Formen …", Nachformung): dort steht `inst.regler`
     * schon, `regler` bleibt dann die Vorgabe. `grund` steht in der Anzeige („zuletzt nach …").
     */
    static async umbauen(inst, grund, bauen, regler = inst.regler || {}) {
        if (!Genesis9groessehalten.an(inst)) return bauen();
        const z = inst.groesseHalten;
        const start = performance.now();
        try {
            const antwort = await Serverabruf.senden(Genesis9groessehalten.ADRESSE, { regler, ziel_m: z.soll_m });
            if (antwort.fehler) throw new Error(antwort.fehler);
            inst.regler = inst.regler || {};
            if (Math.abs(antwort.wert) < 1e-6) delete inst.regler[Genesis9groessehalten.AUSGLEICH];
            else inst.regler[Genesis9groessehalten.AUSGLEICH] = antwort.wert;
            z.letzte = { ...antwort, regler: grund, abruf_ms: Math.round(performance.now() - start) };
        } catch (fehler) {
            z.letzte = { fehler: fehler.message };
            Protokoll.warnung('Genesis9groessehalten', `Ausgleich für ${grund} fehlgeschlagen: ${fehler.message}`);
        }
        const fertig = await bauen();
        Genesis9groessehalten.anzeigen(inst);
        return fertig;
    }

    /** Sollgröße (cm), letzte Abweichung (mm), Wert des Ausgleichsreglers — nur, wenn das Bedienfeld diese Figur zeigt. */
    static anzeigen(inst) {
        const feld = document.getElementById(Genesis9groessehalten.KENNUNG);
        const stand = feld?.querySelector('[data-feld="stand"]');
        if (!stand || feld.dataset.figur !== String(inst.id)) return;
        const z = inst.groesseHalten;
        const zahl = (w, stellen) => Number(w).toLocaleString('de-DE', { minimumFractionDigits: stellen, maximumFractionDigits: stellen });
        const teile = [];
        if (Genesis9groessehalten.an(inst)) teile.push(`Soll ${zahl(z.soll_m * 100, 1)} cm`);
        const letzte = z?.letzte;
        if (letzte?.fehler) teile.push(`Fehler: ${letzte.fehler}`);
        else if (letzte) {
            teile.push(`Abweichung ${zahl(letzte.abweichung_mm, 1)} mm`);
            teile.push(`Ausgleich Proportion Legs Length ${zahl(letzte.wert * 100, 1)} %`);
            teile.push(`${letzte.schritte} Schritte, ${zahl(letzte.ms, 0)} ms`);
            if (letzte.anschlag) teile.push('am Anschlag (±200 %) — Größe nicht erreicht');
        } else if (Genesis9groessehalten.an(inst)) {
            const w = inst.regler?.[Genesis9groessehalten.AUSGLEICH] || 0;
            teile.push(`Ausgleich Proportion Legs Length ${zahl(w * 100, 1)} %`);
        }
        stand.textContent = teile.join(' · ');
        // Der Ausgleich ist der GESTELLTE Wert; der Schieber zeigt die Summe mit den Formeln der Figur (`Genesis9reglerzeile.wert`).
        stand.title = letzte && !letzte.fehler
            ? `zuletzt nach „${letzte.regler}": Größe ${zahl(letzte.hoehe_m * 100, 2)} cm, Abruf ${letzte.abruf_ms} ms · `
              + 'Ausgleich = gestellter Wert, der Schieber zeigt die Summe mit den Formeln der Figur' : '';
    }
}
